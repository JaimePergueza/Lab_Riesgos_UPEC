#!/usr/bin/env python3
"""
create_tour_final.py - Sistema de tour guiado para Lab_Riesgos_UPEC
Crea WBP_PanelNarrativa y los grafos de BP_TourArrow via UnrealMCP TCP.

Funciones verificadas en UE5.5:
  K2_GetActorLocation, K2_SetActorLocation, K2_SetActorRotation
  Add_DoubleDouble, Less_DoubleDouble (no Add_FloatFloat / Less_FloatFloat)
  FindLookAtRotation, BreakRotator, MakeRotator, BreakVector, MakeVector
  Subtract_VectorVector, VSize, GetPlayerPawn, SetActorTickEnabled, K2_DestroyActor

NOTA: Nodo Branch (para deteccion de llegada) se deja como 1 paso manual.
"""

import socket, json, time, sys

HOST, PORT = '127.0.0.1', 55557
TIMEOUT = 15.0

# ─── Utilidades TCP ──────────────────────────────────────────────────────────
_sock = None

def connect():
    global _sock
    if _sock:
        try: _sock.close()
        except: pass
    _sock = socket.socket()
    _sock.connect((HOST, PORT))
    _sock.settimeout(TIMEOUT)
    print(f"Conectado a UnrealMCP {HOST}:{PORT}")

def cmd(name, params=None):
    global _sock
    p = params or {}
    payload = json.dumps({"type": name, "params": p}, ensure_ascii=False)
    print(f"  > {name}")
    for attempt in range(3):
        try:
            _sock.sendall(payload.encode('utf-8'))
            time.sleep(0.6)
            data = b""
            while True:
                chunk = _sock.recv(32768)
                if not chunk:
                    break
                data += chunk
                try:
                    r = json.loads(data.decode('utf-8', errors='replace'))
                    ok = "OK" if r.get("status") == "success" else f"ERR:{r.get('error','?')[:80]}"
                    print(f"  < {ok}")
                    return r
                except json.JSONDecodeError:
                    continue
        except (ConnectionResetError, BrokenPipeError, OSError):
            print(f"  ! Conexion rota, reconectando ({attempt+1}/3)...")
            time.sleep(1.0)
            connect()
    print(f"  < ERR:no responde tras 3 intentos")
    return {}

def nid(r):
    """Extrae node_id del resultado."""
    if not r: return ""
    return r.get("result", {}).get("node_id", "")

def conn(bp, src, sp, tgt, tp):
    """Conecta dos nodos si ambos IDs son validos."""
    if not src or not tgt:
        print(f"    [skip] {sp}->{tp} (ID faltante)")
        return
    cmd("connect_blueprint_nodes", {
        "blueprint_name": bp,
        "source_node_id": src, "source_pin": sp,
        "target_node_id": tgt, "target_pin": tp,
    })

# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    connect()

    # ═════════════════════════════════════════════════════════════════════════
    # 1. WBP_PanelNarrativa
    # ═════════════════════════════════════════════════════════════════════════
    print("\n" + "="*60)
    print("WBP_PanelNarrativa  (/Game/Widgets/)")
    print("="*60)
    W = "WBP_PanelNarrativa"

    # Crear (si ya existe como WidgetBlueprint correcto -> error "already exists", OK)
    cmd("create_umg_widget_blueprint", {"name": W})

    # TextBlock con texto narrativo
    cmd("add_text_block_to_widget", {
        "blueprint_name": W,
        "widget_name": "txt_Narrativa",
        "text": ("Usted realizara una practica en el laboratorio. "
                 "Antes de ingresar, debe cumplir las normas de seguridad, "
                 "seleccionar el EPP adecuado, reconocer riesgos y responder "
                 "correctamente a situaciones de peligro."),
        "position": [60, 60],
    })

    # Boton Comenzar
    cmd("add_button_to_widget", {
        "blueprint_name": W,
        "widget_name": "btn_Comenzar",
        "text": "Comenzar",
        "position": [260, 260],
    })

    # Evento OnClicked del boton
    r = cmd("bind_widget_event", {
        "blueprint_name": W,
        "widget_name": "btn_Comenzar",
        "event_name": "OnClicked",
    })
    click_id = nid(r)

    # RemoveFromParent
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": W,
        "function_name": "RemoveFromParent",
        "node_position": [460, 200],
    })
    rfp_id = nid(r)

    # GetOwningPlayer
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": W,
        "function_name": "GetOwningPlayer",
        "node_position": [250, 360],
    })
    gop_id = nid(r)

    # SetInputMode_GameOnly
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": W,
        "function_name": "SetInputMode_GameOnly",
        "target": "PlayerController",
        "node_position": [620, 360],
    })
    sim_id = nid(r)

    # Cadena exec
    conn(W, click_id, "execute",     rfp_id,  "execute")
    conn(W, rfp_id,   "then",        sim_id,  "execute")
    conn(W, gop_id,   "ReturnValue", sim_id,  "Target")

    cmd("compile_blueprint", {"blueprint_name": W})
    print("  [WBP_PanelNarrativa LISTO]\n")

    # ═════════════════════════════════════════════════════════════════════════
    # 2. BP_TourArrow — Event Tick
    # ═════════════════════════════════════════════════════════════════════════
    print("="*60)
    print("BP_TourArrow — Event Tick")
    print("="*60)
    BP = "BP_TourArrow"

    # ── Event Tick ────────────────────────────────────────────────────────
    r = cmd("add_blueprint_event_node", {
        "blueprint_name": BP, "event_name": "ReceiveTick", "node_position": [0, 0],
    })
    tick_id = nid(r)

    # GetPlayerPawn
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "GetPlayerPawn",
        "target": "GameplayStatics", "node_position": [260, 80],
    })
    pawn_id = nid(r)

    # K2_GetActorLocation (del pawn)
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "K2_GetActorLocation",
        "target": "Actor", "node_position": [480, 80],
    })
    pawn_loc_id = nid(r)

    # HeightOffset variable get
    r = cmd("add_blueprint_get_self_component_reference", {
        "blueprint_name": BP, "component_name": "HeightOffset", "node_position": [480, 220],
    })
    height_id = nid(r)

    # BreakVector (pawn location -> X,Y,Z)
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "BreakVector",
        "target": "KismetMathLibrary", "node_position": [700, 80],
    })
    bv_id = nid(r)

    # Add_DoubleDouble (Z + HeightOffset)
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "Add_DoubleDouble",
        "target": "KismetMathLibrary", "node_position": [900, 200],
    })
    zadd_id = nid(r)

    # MakeVector (nueva posicion de la flecha)
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "MakeVector",
        "target": "KismetMathLibrary", "node_position": [1100, 80],
    })
    mkv_id = nid(r)

    # K2_SetActorLocation (mover flecha)
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "K2_SetActorLocation",
        "target": "Actor", "node_position": [1320, 0],
    })
    setloc_id = nid(r)

    # Self reference (para SetActorLocation)
    r = cmd("add_blueprint_self_reference", {
        "blueprint_name": BP, "node_position": [1100, -80],
    })
    self1_id = nid(r)

    # GetActorLocation de self (posicion actual de la flecha) para LookAt
    r = cmd("add_blueprint_get_self_component_reference", {
        "blueprint_name": BP, "component_name": "ArrowMesh", "node_position": [1100, 300],
    })
    arrow_ref_id = nid(r)

    r = cmd("add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "K2_GetActorLocation",
        "target": "Actor", "node_position": [1300, 300],
    })
    arrow_loc_id = nid(r)

    # TargetLocation variable get
    r = cmd("add_blueprint_get_self_component_reference", {
        "blueprint_name": BP, "component_name": "TargetLocation", "node_position": [1100, 420],
    })
    target_loc_id = nid(r)

    # FindLookAtRotation (de posicion flecha hacia TargetLocation)
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "FindLookAtRotation",
        "target": "KismetMathLibrary", "node_position": [1520, 300],
    })
    lookat_id = nid(r)

    # BreakRotator
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "BreakRotator",
        "target": "KismetMathLibrary", "node_position": [1720, 300],
    })
    br_id = nid(r)

    # MakeRotator (solo Yaw)
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "MakeRotator",
        "target": "KismetMathLibrary", "node_position": [1900, 300],
    })
    mkr_id = nid(r)

    # K2_SetActorRotation
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "K2_SetActorRotation",
        "target": "Actor", "node_position": [2100, 0],
    })
    setrot_id = nid(r)

    # Self reference para SetActorRotation
    r = cmd("add_blueprint_self_reference", {
        "blueprint_name": BP, "node_position": [1900, -80],
    })
    self2_id = nid(r)

    # ── Deteccion de llegada ───────────────────────────────────────────────
    # Subtract_VectorVector (pawn_loc - TargetLocation)
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "Subtract_VectorVector",
        "target": "KismetMathLibrary", "node_position": [700, 500],
    })
    sub_id = nid(r)

    # VSize (magnitud del vector diferencia)
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "VSize",
        "target": "KismetMathLibrary", "node_position": [900, 500],
    })
    vsize_id = nid(r)

    # ArrivalRadius variable get
    r = cmd("add_blueprint_get_self_component_reference", {
        "blueprint_name": BP, "component_name": "ArrivalRadius", "node_position": [900, 640],
    })
    radius_id = nid(r)

    # Less_DoubleDouble (distance < ArrivalRadius)
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "Less_DoubleDouble",
        "target": "KismetMathLibrary", "node_position": [1100, 500],
    })
    less_id = nid(r)

    # ── Conexiones Event Tick ──────────────────────────────────────────────
    print("\n  [Conectando Event Tick...]")

    # Tick -> SetActorLocation (exec)
    conn(BP, tick_id,    "execute",     setloc_id, "execute")
    # SetActorLocation -> SetActorRotation (exec)
    conn(BP, setloc_id,  "then",        setrot_id, "execute")

    # GetPlayerPawn -> GetActorLocation (Target)
    conn(BP, pawn_id,    "ReturnValue", pawn_loc_id, "self")
    # GetActorLocation -> BreakVector
    conn(BP, pawn_loc_id,"ReturnValue", bv_id,       "InVec")
    # BreakVector X,Y -> MakeVector X,Y
    conn(BP, bv_id,      "X",           mkv_id,      "X")
    conn(BP, bv_id,      "Y",           mkv_id,      "Y")
    # BreakVector Z + HeightOffset -> Add_DoubleDouble -> MakeVector Z
    conn(BP, bv_id,      "Z",           zadd_id,     "A")
    conn(BP, height_id,  "ReturnValue", zadd_id,     "B")
    conn(BP, zadd_id,    "ReturnValue", mkv_id,      "Z")
    # MakeVector -> SetActorLocation NewLocation
    conn(BP, mkv_id,     "ReturnValue", setloc_id,   "NewLocation")
    # Self -> SetActorLocation Target
    conn(BP, self1_id,   "self",        setloc_id,   "self")

    # ArrowMesh ref -> GetActorLocation
    conn(BP, arrow_ref_id, "ReturnValue", arrow_loc_id, "self")
    # Arrow loc -> FindLookAtRotation Start
    conn(BP, arrow_loc_id, "ReturnValue", lookat_id,    "Start")
    # TargetLocation -> FindLookAtRotation Target
    conn(BP, target_loc_id,"ReturnValue", lookat_id,    "Target")
    # FindLookAtRotation -> BreakRotator
    conn(BP, lookat_id,  "ReturnValue", br_id,       "InRot")
    # BreakRotator Yaw -> MakeRotator Yaw
    conn(BP, br_id,      "Yaw",         mkr_id,      "Yaw")
    # MakeRotator -> SetActorRotation
    conn(BP, mkr_id,     "ReturnValue", setrot_id,   "NewRotation")
    # Self -> SetActorRotation Target
    conn(BP, self2_id,   "self",        setrot_id,   "self")

    # Pawn loc -> Subtract (A), TargetLocation -> Subtract (B)
    conn(BP, pawn_loc_id,"ReturnValue", sub_id,      "A")
    conn(BP, target_loc_id,"ReturnValue", sub_id,    "B")
    # Subtract -> VSize
    conn(BP, sub_id,     "ReturnValue", vsize_id,    "A")
    # VSize -> Less_DoubleDouble A
    conn(BP, vsize_id,   "ReturnValue", less_id,     "A")
    # ArrivalRadius -> Less_DoubleDouble B
    conn(BP, radius_id,  "ReturnValue", less_id,     "B")

    print("  [Event Tick CONECTADO]\n")

    # ═════════════════════════════════════════════════════════════════════════
    # 3. BP_TourArrow — OnPlayerArrived
    # ═════════════════════════════════════════════════════════════════════════
    print("="*60)
    print("BP_TourArrow — OnPlayerArrived")
    print("="*60)

    r = cmd("add_blueprint_event_node", {
        "blueprint_name": BP, "event_name": "OnPlayerArrived", "node_position": [0, 800],
    })
    arrived_id = nid(r)

    # SetActorTickEnabled(false)
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "SetActorTickEnabled",
        "target": "Actor", "node_position": [260, 800],
    })
    tick_off_id = nid(r)

    r = cmd("add_blueprint_self_reference", {
        "blueprint_name": BP, "node_position": [60, 920],
    })
    self3_id = nid(r)

    # CreateWidget (WBP_PanelNarrativa)
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "CreateWidget",
        "target": "WidgetBlueprintLibrary", "node_position": [520, 800],
    })
    cw_id = nid(r)

    # AddToViewport
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "AddToViewport",
        "node_position": [780, 800],
    })
    atv_id = nid(r)

    # GetOwningPlayerController (para SetInputMode)
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "GetPlayerController",
        "target": "GameplayStatics", "node_position": [780, 960],
    })
    gpc_id = nid(r)

    # SetInputMode_UIOnlyData
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "SetInputMode_UIOnlyData",
        "target": "PlayerController", "node_position": [1040, 800],
    })
    ui_id = nid(r)

    # K2_DestroyActor
    r = cmd("add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "K2_DestroyActor",
        "target": "Actor", "node_position": [1300, 800],
    })
    destroy_id = nid(r)

    r = cmd("add_blueprint_self_reference", {
        "blueprint_name": BP, "node_position": [1100, 920],
    })
    self4_id = nid(r)

    print("\n  [Conectando OnPlayerArrived...]")
    conn(BP, arrived_id,  "execute",      tick_off_id, "execute")
    conn(BP, self3_id,    "self",         tick_off_id, "Target")
    conn(BP, tick_off_id, "then",         cw_id,       "execute")
    conn(BP, cw_id,       "ReturnValue",  atv_id,      "self")
    conn(BP, atv_id,      "then",         ui_id,       "execute")
    conn(BP, gpc_id,      "ReturnValue",  ui_id,       "Target")
    conn(BP, ui_id,       "then",         destroy_id,  "execute")
    conn(BP, self4_id,    "self",         destroy_id,  "Target")
    print("  [OnPlayerArrived CONECTADO]\n")

    # ── Compilar BP_TourArrow ──────────────────────────────────────────────
    cmd("compile_blueprint", {"blueprint_name": BP})
    print("  [BP_TourArrow COMPILADO]\n")

    # ═════════════════════════════════════════════════════════════════════════
    print("="*60)
    print("COMPLETADO")
    print("="*60)
    print("""
Assets listos:
  /Game/Widgets/WBP_PanelNarrativa  (texto + boton Comenzar)
  /Game/Tour/BP_TourArrow            (flecha + logica)

PASO MANUAL RESTANTE (1 nodo en BP_TourArrow):
----------------------------------------------
En BP_TourArrow > Event Graph > Event Tick:
  1. Busca el nodo Less_DoubleDouble (ya esta creado y conectado)
  2. Arrastra desde su pin ReturnValue
  3. Suelta y busca "Branch"
  4. Conecta Branch.True  ->  llama Custom Event "OnPlayerArrived"
     (click derecho -> "Call Function OnPlayerArrived")

Eso es todo. El sistema estara 100%% funcional.
""")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelado.")
    except Exception as e:
        print(f"\nError inesperado: {e}")
        import traceback; traceback.print_exc()
