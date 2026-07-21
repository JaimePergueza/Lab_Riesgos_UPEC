#!/usr/bin/env python3
"""
create_tour_nodes.py  –  Solo crea nodos Blueprint via UnrealMCP (puerto 55557)
Los assets (WBP_PanelNarrativa, BP_TourArrow) ya fueron creados por VibeUE Python.

Ejecutar con el editor UE5 abierto.
"""

import socket, json, time, sys

HOST, PORT = '127.0.0.1', 55557

# ───────────────────────────────────────────────
def recv_json(sock, timeout=10.0):
    sock.settimeout(timeout)
    data = b""
    while True:
        try:
            chunk = sock.recv(8192)
            if not chunk:
                break
            data += chunk
            try:
                return json.loads(data.decode('utf-8', errors='replace'))
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

def cmd(sock, t, params=None):
    p = params or {}
    payload = json.dumps({"type": t, "params": p}, ensure_ascii=False)
    print(f"  > {t}")
    sock.sendall(payload.encode('utf-8'))
    time.sleep(0.3)
    r = recv_json(sock)
    ok = "OK" if r and not r.get("error") else f"ERR:{r.get('error','?')}"
    print(f"  < {ok}")
    return r

def nid(r):
    if not r: return ""
    return r.get("node_id") or r.get("data", {}).get("node_id", "")

def conn(s, bp, src, sp, tgt, tp):
    if not src or not tgt:
        print(f"    [skip] {sp}->{tp}  src={src!r} tgt={tgt!r}")
        return
    cmd(s, "connect_blueprint_nodes", {
        "blueprint_name": bp,
        "source_node_id": src, "source_pin": sp,
        "target_node_id": tgt, "target_pin": tp,
    })

# ───────────────────────────────────────────────
def main():
    print(f"\nConectando a UnrealMCP {HOST}:{PORT} ...")
    s = socket.socket()
    s.connect((HOST, PORT))
    print("Conectado.\n")

    # ═══════════════════════════════════════════
    # WBP_PanelNarrativa  (en /Game/Widgets/)
    # ═══════════════════════════════════════════
    print("="*55)
    print("WBP_PanelNarrativa - TextBlock + Button + Eventos")
    print("="*55)

    W = "WBP_PanelNarrativa"

    cmd(s, "create_umg_widget_blueprint", {"name": W})

    cmd(s, "add_text_block_to_widget", {
        "blueprint_name": W,
        "widget_name": "txt_Narrativa",
        "text": ("Usted realizara una practica en el laboratorio. "
                 "Antes de ingresar, debe cumplir las normas de seguridad, "
                 "seleccionar el EPP adecuado, reconocer riesgos y responder "
                 "correctamente a situaciones de peligro."),
        "position": [80, 60],
    })

    cmd(s, "add_button_to_widget", {
        "blueprint_name": W,
        "widget_name": "btn_Comenzar",
        "text": "Comenzar",
        "position": [300, 240],
    })

    # Evento OnClicked
    r = cmd(s, "bind_widget_event", {
        "blueprint_name": W,
        "widget_name": "btn_Comenzar",
        "event_name": "OnClicked",
    })
    click_id = nid(r)

    # RemoveFromParent
    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": W,
        "function_name": "RemoveFromParent",
        "node_position": [450, 200],
    })
    rfp_id = nid(r)

    # GetOwningPlayer
    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": W,
        "function_name": "GetOwningPlayer",
        "node_position": [250, 350],
    })
    gop_id = nid(r)

    # SetInputMode_GameOnly
    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": W,
        "function_name": "SetInputMode_GameOnly",
        "target": "PlayerController",
        "node_position": [600, 350],
    })
    sim_id = nid(r)

    # Cadena exec: OnClicked -> RemoveFromParent -> SetInputMode
    conn(s, W, click_id, "execute",      rfp_id,  "execute")
    conn(s, W, rfp_id,   "then",         sim_id,  "execute")
    conn(s, W, gop_id,   "ReturnValue",  sim_id,  "Target")

    cmd(s, "compile_blueprint", {"blueprint_name": W})
    print("  [WBP_PanelNarrativa LISTO]\n")

    # ═══════════════════════════════════════════
    # BP_TourArrow  (en /Game/Tour/ - buscado por Asset Registry)
    # ═══════════════════════════════════════════
    print("="*55)
    print("BP_TourArrow - Grafo Event Tick + OnPlayerArrived")
    print("="*55)

    BP = "BP_TourArrow"

    # ── Event Tick ──────────────────────────────
    r = cmd(s, "add_blueprint_event_node", {
        "blueprint_name": BP, "event_name": "ReceiveTick",
        "node_position": [0, 0],
    })
    tick_id = nid(r)

    # GetPlayerPawn(0)
    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "GetPlayerPawn",
        "target": "GameplayStatics", "node_position": [280, 80],
        "params": {"PlayerIndex": 0},
    })
    pawn_id = nid(r)

    # GetActorLocation del pawn
    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "GetActorLocation",
        "node_position": [500, 80],
    })
    pawn_loc_id = nid(r)

    # Get HeightOffset var
    r = cmd(s, "add_blueprint_get_self_component_reference", {
        "blueprint_name": BP, "component_name": "HeightOffset",
        "node_position": [500, 200],
    })
    height_id = nid(r)

    # BreakVector
    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "BreakVector",
        "target": "KismetMathLibrary", "node_position": [720, 80],
    })
    bvec_id = nid(r)

    # Add_FloatFloat (Z + HeightOffset)
    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "Add_FloatFloat",
        "target": "KismetMathLibrary", "node_position": [920, 200],
    })
    addz_id = nid(r)

    # MakeVector
    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "MakeVector",
        "target": "KismetMathLibrary", "node_position": [1120, 80],
    })
    mkv_id = nid(r)

    # K2_SetActorLocation (self)
    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "K2_SetActorLocation",
        "node_position": [1340, 0],
        "params": {"bSweep": False, "bTeleport": True},
    })
    setloc_id = nid(r)

    # ── Rotacion ────────────────────────────────
    # GetActorLocation self
    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "GetActorLocation",
        "node_position": [280, 400],
    })
    self_loc_id = nid(r)

    r = cmd(s, "add_blueprint_self_reference", {
        "blueprint_name": BP, "node_position": [80, 430],
    })
    self_ref_id = nid(r)

    # Get TargetLocation var
    r = cmd(s, "add_blueprint_get_self_component_reference", {
        "blueprint_name": BP, "component_name": "TargetLocation",
        "node_position": [280, 490],
    })
    tgt_id = nid(r)

    # FindLookAtRotation
    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "FindLookAtRotation",
        "target": "KismetMathLibrary", "node_position": [520, 420],
    })
    lookat_id = nid(r)

    # BreakRotator
    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "BreakRotator",
        "target": "KismetMathLibrary", "node_position": [740, 420],
    })
    brot_id = nid(r)

    # MakeRotator (solo Yaw)
    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "MakeRotator",
        "target": "KismetMathLibrary", "node_position": [960, 420],
        "params": {"Roll": 0.0, "Pitch": 0.0},
    })
    mkrot_id = nid(r)

    # K2_SetActorRotation
    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "K2_SetActorRotation",
        "node_position": [1180, 380],
        "params": {"bTeleportPhysics": False},
    })
    setrot_id = nid(r)

    # ── Deteccion de llegada ─────────────────────
    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "Subtract_VectorVector",
        "target": "KismetMathLibrary", "node_position": [520, 640],
    })
    sub_id = nid(r)

    r = cmd(s, "add_blueprint_get_self_component_reference", {
        "blueprint_name": BP, "component_name": "TargetLocation",
        "node_position": [280, 700],
    })
    tgt2_id = nid(r)

    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "VSize",
        "target": "KismetMathLibrary", "node_position": [740, 640],
    })
    vs_id = nid(r)

    r = cmd(s, "add_blueprint_get_self_component_reference", {
        "blueprint_name": BP, "component_name": "ArrivalRadius",
        "node_position": [740, 740],
    })
    rad_id = nid(r)

    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "Less_FloatFloat",
        "target": "KismetMathLibrary", "node_position": [960, 640],
    })
    less_id = nid(r)

    # ── Custom Event OnPlayerArrived ─────────────
    print("\n  [OnPlayerArrived event chain]")

    r = cmd(s, "add_blueprint_event_node", {
        "blueprint_name": BP, "event_name": "OnPlayerArrived",
        "node_position": [0, 950],
    })
    arr_ev_id = nid(r)

    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "SetActorTickEnabled",
        "node_position": [300, 950],
        "params": {"bEnabled": False},
    })
    notick_id = nid(r)

    r = cmd(s, "add_blueprint_self_reference", {
        "blueprint_name": BP, "node_position": [100, 1030],
    })
    self_tick_id = nid(r)

    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "GetPlayerController",
        "target": "GameplayStatics", "node_position": [300, 1100],
        "params": {"PlayerIndex": 0},
    })
    ctrl_id = nid(r)

    # CreateWidget – clase WBP_PanelNarrativa
    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "Create",
        "target": "WidgetBlueprintLibrary", "node_position": [600, 950],
        "params": {"WidgetType": "/Game/Widgets/WBP_PanelNarrativa_C"},
    })
    cw_id = nid(r)

    # AddToViewport
    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "AddToViewport",
        "node_position": [900, 950],
        "params": {"ZOrder": 10},
    })
    avp_id = nid(r)

    # SetInputMode_UIOnly
    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "SetInputMode_UIOnlyData",
        "target": "PlayerController", "node_position": [1100, 950],
    })
    uim_id = nid(r)

    # ShowMouseCursor = true
    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "K2_SetShowMouseCursor",
        "target": "PlayerController", "node_position": [1300, 950],
        "params": {"bShow": True},
    })
    smc_id = nid(r)

    # DestroyActor self
    r = cmd(s, "add_blueprint_function_node", {
        "blueprint_name": BP, "function_name": "K2_DestroyActor",
        "node_position": [1500, 950],
    })
    dest_id = nid(r)

    r = cmd(s, "add_blueprint_self_reference", {
        "blueprint_name": BP, "node_position": [1300, 1060],
    })
    self_dest_id = nid(r)

    # ── CONEXIONES ──────────────────────────────
    print("\n  [Conectando nodos...]")

    # Tick exec -> SetActorLocation -> SetActorRotation
    conn(s, BP, tick_id,    "then",           setloc_id,  "execute")
    conn(s, BP, setloc_id,  "then",           setrot_id,  "execute")

    # Pawn location chain
    conn(s, BP, pawn_id,    "ReturnValue",    pawn_loc_id,"self")
    conn(s, BP, pawn_loc_id,"ReturnValue",    bvec_id,    "InVec")
    conn(s, BP, bvec_id,    "X",              mkv_id,     "X")
    conn(s, BP, bvec_id,    "Y",              mkv_id,     "Y")
    conn(s, BP, bvec_id,    "Z",              addz_id,    "A")
    conn(s, BP, height_id,  "HeightOffset",   addz_id,    "B")
    conn(s, BP, addz_id,    "ReturnValue",    mkv_id,     "Z")
    conn(s, BP, mkv_id,     "ReturnValue",    setloc_id,  "NewLocation")

    # Rotation chain
    conn(s, BP, self_ref_id,"self",           self_loc_id,"self")
    conn(s, BP, self_loc_id,"ReturnValue",    lookat_id,  "Start")
    conn(s, BP, tgt_id,     "TargetLocation", lookat_id,  "Target")
    conn(s, BP, lookat_id,  "ReturnValue",    brot_id,    "InRot")
    conn(s, BP, brot_id,    "Yaw",            mkrot_id,   "Yaw")
    conn(s, BP, mkrot_id,   "ReturnValue",    setrot_id,  "NewRotation")

    # Arrival detection data
    conn(s, BP, pawn_loc_id,"ReturnValue",    sub_id,     "A")
    conn(s, BP, tgt2_id,    "TargetLocation", sub_id,     "B")
    conn(s, BP, sub_id,     "ReturnValue",    vs_id,      "A")
    conn(s, BP, vs_id,      "ReturnValue",    less_id,    "A")
    conn(s, BP, rad_id,     "ArrivalRadius",  less_id,    "B")

    # OnPlayerArrived chain
    conn(s, BP, arr_ev_id,  "then",           notick_id,  "execute")
    conn(s, BP, self_tick_id,"self",          notick_id,  "self")
    conn(s, BP, notick_id,  "then",           cw_id,      "execute")
    conn(s, BP, cw_id,      "then",           avp_id,     "execute")
    conn(s, BP, cw_id,      "ReturnValue",    avp_id,     "self")
    conn(s, BP, avp_id,     "then",           uim_id,     "execute")
    conn(s, BP, uim_id,     "then",           smc_id,     "execute")
    conn(s, BP, smc_id,     "then",           dest_id,    "execute")
    conn(s, BP, ctrl_id,    "ReturnValue",    uim_id,     "Target")
    conn(s, BP, ctrl_id,    "ReturnValue",    smc_id,     "Target")
    conn(s, BP, self_dest_id,"self",          dest_id,    "self")

    cmd(s, "compile_blueprint", {"blueprint_name": BP})
    print("  [BP_TourArrow LISTO]\n")

    s.close()

    print("="*55)
    print("COMPLETADO")
    print("="*55)
    print("""
Assets listos en el editor:
  /Game/Widgets/WBP_PanelNarrativa  (texto + boton Comenzar)
  /Game/Tour/BP_TourArrow            (flecha + logica)

Pasos manuales que QUEDAN (3 acciones en el editor):
-----------------------------------------------------
1. BP_TourArrow > Event Tick:
   - Agregar nodo BRANCH
   - Condition = Less_FloatFloat.ReturnValue
   - Branch.True  -> llamar Custom Event "OnPlayerArrived"
   (La condicion Less_FloatFloat ya esta calculada y visible)

2. BP_Bienvenida (Content/Fab/Audios/):
   - Al FINAL de la secuencia de bienvenida agregar:
     Spawn Actor from Class -> BP_TourArrow
     Spawn Transform Location: X=830, Y=-695, Z=602
   - El actor seguira al jugador automaticamente desde ahi.
""")

if __name__ == "__main__":
    try:
        main()
    except ConnectionRefusedError:
        print("\nERROR: No se pudo conectar al servidor MCP.")
        print("Asegurate de que el Unreal Editor este abierto.")
        sys.exit(1)
    except Exception as e:
        import traceback; traceback.print_exc()
        sys.exit(1)
