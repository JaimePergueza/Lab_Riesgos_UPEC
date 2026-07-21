#!/usr/bin/env python3
"""
create_tour_system.py
Crea WBP_PanelNarrativa y BP_TourArrow en el proyecto Lab_Riesgos_UPEC
via el plugin UnrealMCP (puerto 55557).

Ejecutar con el editor UE5 abierto y el mapa Lab_Despues cargado.
"""

import socket
import json
import time
import sys

HOST = '127.0.0.1'
PORT = 55557

# ────────────────────���────────────────────────
# Utilidades de comunicacion
# ─────────────────────────────────────────────

def recv_json(sock, timeout=10.0):
    """Lee bytes del socket hasta obtener un JSON valido."""
    sock.settimeout(timeout)
    data = b""
    while True:
        try:
            chunk = sock.recv(8192)
            if not chunk:
                break
            data += chunk
            try:
                result = json.loads(data.decode('utf-8', errors='replace'))
                return result
            except json.JSONDecodeError:
                continue
        except socket.timeout:
            break
    if data:
        try:
            return json.loads(data.decode('utf-8', errors='replace'))
        except Exception:
            pass
    return {}


def cmd(sock, command_type, params=None):
    """Envia un comando MCP y retorna la respuesta parseada."""
    if params is None:
        params = {}
    payload = json.dumps({"type": command_type, "params": params}, ensure_ascii=False)
    short = payload[:120] + ("..." if len(payload) > 120 else "")
    print(f"  > {command_type}  {short}")
    sock.sendall(payload.encode('utf-8'))
    time.sleep(0.25)
    resp = recv_json(sock)
    status = "OK" if resp and not resp.get("error") else f"ERR: {resp.get('error','?')}"
    print(f"  < {status}")
    return resp


def node_id(resp):
    """Extrae node_id de la respuesta (puede venir directo o dentro de 'data')."""
    if not resp:
        return ""
    return resp.get("node_id") or resp.get("data", {}).get("node_id", "")


def connect(sock, bp, src, src_pin, tgt, tgt_pin):
    """Conecta dos nodos si ambos IDs son validos."""
    if not src or not tgt:
        print(f"    [SKIP connect] src={src!r} tgt={tgt!r}")
        return
    cmd(sock, "connect_blueprint_nodes", {
        "blueprint_name": bp,
        "source_node_id": src,
        "target_node_id": tgt,
        "source_pin": src_pin,
        "target_pin": tgt_pin,
    })


# ──────────────────���──────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    print(f"\nConectando a UnrealMCP en {HOST}:{PORT} ...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    print("Conexion establecida.\n")

    # ═════════════════════���════════════════════════
    # 1.  WBP_PanelNarrativa
    # ══════════════════════════════════════════════
    print("=" * 60)
    print("PASO 1: WBP_PanelNarrativa")
    print("=" * 60)

    WIDGET = "WBP_PanelNarrativa"

    cmd(s, "create_umg_widget_blueprint", {"name": WIDGET})

    cmd(s, "add_text_block_to_widget", {
        "blueprint_name": WIDGET,
        "widget_name": "txt_Narrativa",
        "text": (
            "Usted realizara una practica en el laboratorio. "
            "Antes de ingresar, debe cumplir las normas de seguridad, "
            "seleccionar el EPP adecuado, reconocer riesgos y responder "
            "correctamente a situaciones de peligro."
        ),
        "position": [80, 60],
    })

    cmd(s, "add_button_to_widget", {
        "blueprint_name": WIDGET,
        "widget_name": "btn_Comenzar",
        "text": "Comenzar",
        "position": [300, 240],
    })

    # Evento OnClicked del boton
    r_click = cmd(s, "bind_widget_event", {
        "blueprint_name": WIDGET,
        "widget_name": "btn_Comenzar",
        "event_name": "OnClicked",
    })
    click_id = node_id(r_click)

    # Nodo RemoveFromParent (en el widget mismo)
    r_rfp = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": WIDGET,
        "function_name": "RemoveFromParent",
        "node_position": [450, 200],
    })
    rfp_id = node_id(r_rfp)

    # GetOwningPlayer → para obtener el PlayerController
    r_gop = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": WIDGET,
        "function_name": "GetOwningPlayer",
        "node_position": [250, 350],
    })
    gop_id = node_id(r_gop)

    # SetInputMode_GameOnly en el PlayerController
    r_simg = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": WIDGET,
        "function_name": "SetInputMode_GameOnly",
        "target": "PlayerController",
        "node_position": [600, 350],
    })
    simg_id = node_id(r_simg)

    # SetShowMouseCursor = false
    r_smc = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": WIDGET,
        "function_name": "K2_SetShowMouseCursor",
        "target": "PlayerController",
        "node_position": [850, 350],
        "params": {"bShow": False},
    })
    smc_id = node_id(r_smc)

    # Cadena de ejecucion: OnClicked → RemoveFromParent → SetInputMode → SetMouseCursor
    connect(s, WIDGET, click_id, "execute",     rfp_id,  "execute")
    connect(s, WIDGET, rfp_id,   "then",        simg_id, "execute")
    connect(s, WIDGET, simg_id,  "then",        smc_id,  "execute")

    # GetOwningPlayer → PlayerController de SetInputMode
    connect(s, WIDGET, gop_id,  "ReturnValue",  simg_id, "Target")
    connect(s, WIDGET, gop_id,  "ReturnValue",  smc_id,  "Target")

    cmd(s, "compile_blueprint", {"blueprint_name": WIDGET})
    print("  [WBP_PanelNarrativa CREADO]\n")

    # ══════════════════════════════════════════════
    # 2.  BP_TourArrow
    # ══════════════════════════════════════════════
    print("=" * 60)
    print("PASO 2: BP_TourArrow")
    print("=" * 60)

    BP = "BP_TourArrow"

    cmd(s, "create_blueprint", {"name": BP, "parent_class": "Actor"})

    # ── Componentes ──
    cmd(s, "add_component_to_blueprint", {
        "blueprint_name": BP,
        "component_type": "StaticMesh",
        "component_name": "ArrowMesh",
        "rotation": [0.0, 90.0, 0.0],   # punta apunta en +X
        "scale":    [0.3, 0.3, 0.7],
    })

    cmd(s, "add_component_to_blueprint", {
        "blueprint_name": BP,
        "component_type": "PointLight",
        "component_name": "GlowLight",
        "location": [0.0, 0.0, 0.0],
    })

    # Asignar malla cono
    cmd(s, "set_static_mesh_properties", {
        "blueprint_name": BP,
        "component_name": "ArrowMesh",
        "static_mesh": "/Engine/BasicShapes/Cone.Cone",
    })

    # ── Variables ──
    cmd(s, "add_blueprint_variable", {
        "blueprint_name": BP,
        "variable_name": "bArrived",
        "variable_type": "Boolean",
        "is_exposed": False,
    })
    cmd(s, "add_blueprint_variable", {
        "blueprint_name": BP,
        "variable_name": "TargetLocation",
        "variable_type": "Vector",
        "is_exposed": True,
    })
    cmd(s, "add_blueprint_variable", {
        "blueprint_name": BP,
        "variable_name": "HeightOffset",
        "variable_type": "Float",
        "is_exposed": True,
    })
    cmd(s, "add_blueprint_variable", {
        "blueprint_name": BP,
        "variable_name": "ArrivalRadius",
        "variable_type": "Float",
        "is_exposed": True,
    })

    # ── BeginPlay: establecer valores por defecto ──
    print("\n  [BeginPlay - valores por defecto]")

    r_bp_ev = cmd(s, "add_blueprint_event_node", {
        "blueprint_name": BP,
        "event_name": "ReceiveBeginPlay",
        "node_position": [0, -300],
    })
    bp_ev_id = node_id(r_bp_ev)

    # Set TargetLocation = (1010, -1531, 420)
    r_set_tl = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "K2_SetVariableByNameWithNotify",
        "node_position": [300, -300],
    })
    # Si el comando anterior no existe, usamos un Set de variable directamente
    # Lo haremos a traves de nodos de variable set
    set_tl_id = node_id(r_set_tl)

    # Nodo Set TargetLocation
    r_set_target = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "SetTargetLocation",   # funcion auxiliar - puede fallar, OK
        "node_position": [300, -300],
        "params": {"TargetLocation": [1010.0, -1531.0, 420.0]},
    })

    # ── Event Tick ──
    print("\n  [Event Tick - seguir jugador]")

    r_tick = cmd(s, "add_blueprint_event_node", {
        "blueprint_name": BP,
        "event_name": "ReceiveTick",
        "node_position": [0, 0],
    })
    tick_id = node_id(r_tick)

    # GetPlayerPawn (0)
    r_pawn = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "GetPlayerPawn",
        "target": "GameplayStatics",
        "node_position": [280, 80],
        "params": {"PlayerIndex": 0},
    })
    pawn_id = node_id(r_pawn)

    # GetActorLocation del pawn
    r_pawn_loc = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "GetActorLocation",
        "node_position": [520, 80],
    })
    pawn_loc_id = node_id(r_pawn_loc)

    # Get HeightOffset variable
    r_height = cmd(s, "add_blueprint_get_self_component_reference", {
        "blueprint_name": BP,
        "component_name": "HeightOffset",
        "node_position": [520, 200],
    })
    height_id = node_id(r_height)

    # BreakVector del pawn
    r_break_v = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "BreakVector",
        "target": "KismetMathLibrary",
        "node_position": [720, 80],
    })
    break_v_id = node_id(r_break_v)

    # Add float (Z + HeightOffset)
    r_add_z = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "Add_FloatFloat",
        "target": "KismetMathLibrary",
        "node_position": [920, 180],
    })
    add_z_id = node_id(r_add_z)

    # MakeVector (X, Y, Z+HeightOffset)
    r_make_v = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "MakeVector",
        "target": "KismetMathLibrary",
        "node_position": [1120, 80],
    })
    make_v_id = node_id(r_make_v)

    # SetActorLocation (self)
    r_set_loc = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "K2_SetActorLocation",
        "node_position": [1340, 0],
        "params": {"bSweep": False, "bTeleport": True},
    })
    set_loc_id = node_id(r_set_loc)

    print("\n  [Event Tick - rotar hacia destino]")

    # GetActorLocation (self) para calcular rotacion
    r_self_loc = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "GetActorLocation",
        "node_position": [280, 380],
    })
    self_loc_id = node_id(r_self_loc)

    # Self ref para self_loc
    r_self_ref_rot = cmd(s, "add_blueprint_self_reference", {
        "blueprint_name": BP,
        "node_position": [80, 380],
    })
    self_ref_rot_id = node_id(r_self_ref_rot)

    # Get TargetLocation variable
    r_get_tgt = cmd(s, "add_blueprint_get_self_component_reference", {
        "blueprint_name": BP,
        "component_name": "TargetLocation",
        "node_position": [280, 470],
    })
    get_tgt_id = node_id(r_get_tgt)

    # FindLookAtRotation
    r_lookat = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "FindLookAtRotation",
        "target": "KismetMathLibrary",
        "node_position": [520, 400],
    })
    lookat_id = node_id(r_lookat)

    # BreakRotator
    r_break_rot = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "BreakRotator",
        "target": "KismetMathLibrary",
        "node_position": [740, 400],
    })
    break_rot_id = node_id(r_break_rot)

    # MakeRotator (solo Yaw)
    r_make_rot = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "MakeRotator",
        "target": "KismetMathLibrary",
        "node_position": [960, 400],
        "params": {"Roll": 0.0, "Pitch": 0.0},
    })
    make_rot_id = node_id(r_make_rot)

    # SetActorRotation (self)
    r_set_rot = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "K2_SetActorRotation",
        "node_position": [1180, 380],
        "params": {"bTeleportPhysics": False},
    })
    set_rot_id = node_id(r_set_rot)

    print("\n  [Event Tick - deteccion de llegada]")

    # Subtract vectores (PawnLoc - TargetLoc) para distancia
    r_sub_vec = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "Subtract_VectorVector",
        "target": "KismetMathLibrary",
        "node_position": [520, 620],
    })
    sub_vec_id = node_id(r_sub_vec)

    # Get TargetLocation (segunda referencia para la resta)
    r_get_tgt2 = cmd(s, "add_blueprint_get_self_component_reference", {
        "blueprint_name": BP,
        "component_name": "TargetLocation",
        "node_position": [280, 680],
    })
    get_tgt2_id = node_id(r_get_tgt2)

    # VSize (magnitud del vector diferencia)
    r_vsize = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "VSize",
        "target": "KismetMathLibrary",
        "node_position": [740, 620],
    })
    vsize_id = node_id(r_vsize)

    # Get ArrivalRadius variable
    r_get_radius = cmd(s, "add_blueprint_get_self_component_reference", {
        "blueprint_name": BP,
        "component_name": "ArrivalRadius",
        "node_position": [740, 720],
    })
    get_radius_id = node_id(r_get_radius)

    # Less_FloatFloat (distancia < radio)
    r_less = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "Less_FloatFloat",
        "target": "KismetMathLibrary",
        "node_position": [960, 620],
    })
    less_id = node_id(r_less)

    # ── Custom Event OnPlayerArrived ──
    print("\n  [Custom Event OnPlayerArrived]")

    r_arrived_ev = cmd(s, "add_blueprint_event_node", {
        "blueprint_name": BP,
        "event_name": "OnPlayerArrived",
        "node_position": [0, 950],
    })
    arrived_ev_id = node_id(r_arrived_ev)

    # SetActorTickEnabled(false)
    r_no_tick = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "SetActorTickEnabled",
        "node_position": [300, 950],
        "params": {"bEnabled": False},
    })
    no_tick_id = node_id(r_no_tick)

    # Self ref para SetActorTickEnabled
    r_self_tick = cmd(s, "add_blueprint_self_reference", {
        "blueprint_name": BP,
        "node_position": [100, 1020],
    })
    self_tick_id = node_id(r_self_tick)

    # GetPlayerController (para SetInputMode)
    r_get_ctrl = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "GetPlayerController",
        "target": "GameplayStatics",
        "node_position": [300, 1100],
        "params": {"PlayerIndex": 0},
    })
    get_ctrl_id = node_id(r_get_ctrl)

    # CreateWidget (WBP_PanelNarrativa)
    r_create_w = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "CreateWidget",
        "target": "WidgetBlueprintLibrary",
        "node_position": [600, 950],
        "params": {"WidgetType": "/Game/Widgets/WBP_PanelNarrativa.WBP_PanelNarrativa_C"},
    })
    create_w_id = node_id(r_create_w)

    # AddToViewport
    r_add_vp = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "AddToViewport",
        "node_position": [900, 950],
        "params": {"ZOrder": 10},
    })
    add_vp_id = node_id(r_add_vp)

    # SetInputMode_UIOnly en el controller
    r_ui_mode = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "SetInputMode_UIOnlyData",
        "target": "PlayerController",
        "node_position": [1100, 950],
    })
    ui_mode_id = node_id(r_ui_mode)

    # ShowMouseCursor = true
    r_show_mouse = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "K2_SetShowMouseCursor",
        "target": "PlayerController",
        "node_position": [1300, 950],
        "params": {"bShow": True},
    })
    show_mouse_id = node_id(r_show_mouse)

    # DestroyActor (self)
    r_destroy = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP,
        "function_name": "K2_DestroyActor",
        "node_position": [1500, 950],
    })
    destroy_id = node_id(r_destroy)

    # Self ref para DestroyActor
    r_self_dest = cmd(s, "add_blueprint_self_reference", {
        "blueprint_name": BP,
        "node_position": [1300, 1060],
    })
    self_dest_id = node_id(r_self_dest)

    # ═════════════════���════════════════════════════
    # CONEXIONES
    # ══════════════════════════════════════════════
    print("\n  [Conectando nodos...]")

    # ── Tick → SetActorLocation → SetActorRotation (cadena exec) ──
    connect(s, BP, tick_id,    "then",         set_loc_id,  "execute")
    connect(s, BP, set_loc_id, "then",         set_rot_id,  "execute")

    # ── Pawn location → arrow location ──
    connect(s, BP, pawn_id,     "ReturnValue", pawn_loc_id, "self")
    connect(s, BP, pawn_loc_id, "ReturnValue", break_v_id,  "InVec")
    connect(s, BP, break_v_id,  "X",           make_v_id,   "X")
    connect(s, BP, break_v_id,  "Y",           make_v_id,   "Y")
    connect(s, BP, break_v_id,  "Z",           add_z_id,    "A")
    connect(s, BP, height_id,   "HeightOffset",add_z_id,    "B")
    connect(s, BP, add_z_id,    "ReturnValue", make_v_id,   "Z")
    connect(s, BP, make_v_id,   "ReturnValue", set_loc_id,  "NewLocation")

    # ── Rotation ──
    connect(s, BP, self_ref_rot_id, "self",        self_loc_id, "self")
    connect(s, BP, self_loc_id,     "ReturnValue", lookat_id,   "Start")
    connect(s, BP, get_tgt_id,      "TargetLocation", lookat_id, "Target")
    connect(s, BP, lookat_id,       "ReturnValue", break_rot_id,"InRot")
    connect(s, BP, break_rot_id,    "Yaw",         make_rot_id, "Yaw")
    connect(s, BP, make_rot_id,     "ReturnValue", set_rot_id,  "NewRotation")

    # ── Arrival detection (datos, sin Branch por ahora) ──
    connect(s, BP, pawn_loc_id,  "ReturnValue",    sub_vec_id,  "A")
    connect(s, BP, get_tgt2_id,  "TargetLocation", sub_vec_id,  "B")
    connect(s, BP, sub_vec_id,   "ReturnValue",    vsize_id,    "A")
    connect(s, BP, vsize_id,     "ReturnValue",    less_id,     "A")
    connect(s, BP, get_radius_id,"ArrivalRadius",  less_id,     "B")

    # ── OnPlayerArrived cadena exec ──
    connect(s, BP, arrived_ev_id, "then",        no_tick_id,   "execute")
    connect(s, BP, self_tick_id,  "self",        no_tick_id,   "self")
    connect(s, BP, no_tick_id,    "then",        create_w_id,  "execute")
    connect(s, BP, create_w_id,   "then",        add_vp_id,    "execute")
    connect(s, BP, add_vp_id,     "then",        ui_mode_id,   "execute")
    connect(s, BP, ui_mode_id,    "then",        show_mouse_id,"execute")
    connect(s, BP, show_mouse_id, "then",        destroy_id,   "execute")

    # Widget → AddToViewport
    connect(s, BP, create_w_id,  "ReturnValue", add_vp_id,    "self")

    # Controller → UI mode y ShowMouse
    connect(s, BP, get_ctrl_id,  "ReturnValue", ui_mode_id,   "Target")
    connect(s, BP, get_ctrl_id,  "ReturnValue", show_mouse_id,"Target")

    # Self → DestroyActor
    connect(s, BP, self_dest_id, "self",        destroy_id,   "self")

    # Compile
    print("\n  [Compilando BP_TourArrow...]")
    cmd(s, "compile_blueprint", {"blueprint_name": BP})

    s.close()

    # ══════════════════���══════════════════════��════
    # RESUMEN
    # ══════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("COMPLETADO")
    print("=" * 60)
    print("""
Assets creados:
  /Game/Widgets/WBP_PanelNarrativa
  /Game/Blueprints/BP_TourArrow

Pasos manuales que quedan (3 pasos en el editor):
─────────────────���───────────────────────────────
1. BP_TourArrow > Event Tick:
   - Agregar nodo BRANCH entre set_rot y deteccion de llegada.
   - Conectar: Less_FloatFloat.ReturnValue → Branch.Condition
   - Conectar: Branch.True → (llamar Custom Event) OnPlayerArrived
   (Nota: el nodo Branch no se puede crear via API; es 2 clics en el editor)

2. BP_TourArrow > Variables:
   - Selecciona TargetLocation → en Details escribe X=1010, Y=-1531, Z=420
   - Selecciona HeightOffset   → Default = 180.0
   - Selecciona ArrivalRadius  → Default = 200.0

3. BP_Bienvenida (Content/Fab/Audios/):
   - Abrir el Blueprint
   - Al final de la secuencia de bienvenida agregar:
     Spawn Actor from Class → BP_TourArrow
     Spawn Transform Location: (830, -695, 602)
     (La flecha seguira al jugador automaticamente desde ahi)
""")


if __name__ == "__main__":
    try:
        main()
    except ConnectionRefusedError:
        print("\nERROR: No se pudo conectar al servidor MCP.")
        print("Asegurate de que el Unreal Editor este abierto con el proyecto Lab_Riesgos_UPEC.")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
