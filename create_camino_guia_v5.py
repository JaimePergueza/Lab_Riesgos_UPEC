import unreal

bp_path = "/Game/FirstPerson/Blueprints/BP_CaminoGuia"
graph = "EventGraph"

# Borrar y recrear
if unreal.EditorAssetLibrary.does_asset_exist(bp_path):
    unreal.EditorAssetLibrary.delete_asset(bp_path)

factory = unreal.BlueprintFactory()
factory.set_editor_property("parent_class", unreal.Actor)
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
asset_tools.create_asset("BP_CaminoGuia", "/Game/FirstPerson/Blueprints", unreal.Blueprint, factory)
unreal.EditorAssetLibrary.save_asset(bp_path)
print("BP creado")

# Obtener IDs de eventos ya existentes (NO crear duplicados)
nodes = unreal.BlueprintService.get_nodes_in_graph(bp_path, graph)
begin_play_id = None
tick_id = None
for n in nodes:
    if n.node_type == "K2Node_Event":
        if "BeginPlay" in n.node_title and begin_play_id is None:
            begin_play_id = n.node_id
        elif "Tick" in n.node_title and tick_id is None:
            tick_id = n.node_id
print(f"BeginPlay: {begin_play_id}")
print(f"Tick:      {tick_id}")

# ============================================================
# TICK: Cada frame calcula visibilidad de los 13 cilindros
# Usa GetAllActorsWithTag directamente -> tipo AActor resuelto
# ============================================================

# GetAllActorsWithTag("CilindroGuia") — fuente tipada de AActor array
get_tag_tick = unreal.BlueprintService.add_function_call_node(
    bp_path, graph, "GameplayStatics", "GetAllActorsWithTag", -100, 500)
unreal.BlueprintService.set_node_pin_value(bp_path, graph, get_tag_tick, "Tag", "CilindroGuia")

# GetPlayerCharacter -> GetActorLocation -> BreakVector -> PlayerY
get_pc   = unreal.BlueprintService.add_function_call_node(bp_path, graph, "GameplayStatics", "GetPlayerCharacter", -100, 700)
get_ploc = unreal.BlueprintService.add_function_call_node(bp_path, graph, "Actor", "K2_GetActorLocation", 200, 700)
break_p  = unreal.BlueprintService.add_function_call_node(bp_path, graph, "KismetMathLibrary", "BreakVector", 500, 700)
unreal.BlueprintService.connect_nodes(bp_path, graph, get_pc,   "ReturnValue", get_ploc, "self")
unreal.BlueprintService.connect_nodes(bp_path, graph, get_ploc, "ReturnValue", break_p,  "InVec")

# Conectar Tick -> GetAllActorsWithTag
unreal.BlueprintService.connect_nodes(bp_path, graph, tick_id, "then", get_tag_tick, "execute")

# Unroll 13 cilindros
prev_exec = get_tag_tick
for i in range(13):
    yp = 900 + i * 270

    # Array_Get(OutActors, i) — OutActors es TArray<AActor*> -> tipo determinado
    ag = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "KismetArrayLibrary", "Array_Get", 500, yp)
    unreal.BlueprintService.set_node_pin_value(bp_path, graph, ag, "Index", str(i))
    unreal.BlueprintService.connect_nodes(bp_path, graph, get_tag_tick, "OutActors", ag, "TargetArray")

    # GetActorLocation cilindro
    cl = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "Actor", "K2_GetActorLocation", 800, yp)
    unreal.BlueprintService.connect_nodes(bp_path, graph, ag, "Item", cl, "self")

    # BreakVector -> CylY
    bc = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "KismetMathLibrary", "BreakVector", 1050, yp)
    unreal.BlueprintService.connect_nodes(bp_path, graph, cl, "ReturnValue", bc, "InVec")

    # Greater(CylY, PlayerY) => cilindro detras => ocultar
    gt = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "KismetMathLibrary", "Greater_FloatFloat", 1300, yp)
    unreal.BlueprintService.connect_nodes(bp_path, graph, bc,      "Y", gt, "A")
    unreal.BlueprintService.connect_nodes(bp_path, graph, break_p, "Y", gt, "B")

    # SetActorHiddenInGame
    sh = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "Actor", "SetActorHiddenInGame", 1600, yp)
    unreal.BlueprintService.connect_nodes(bp_path, graph, ag, "Item", sh, "self")
    unreal.BlueprintService.connect_nodes(bp_path, graph, gt, "ReturnValue", sh, "bNewHidden")
    unreal.BlueprintService.connect_nodes(bp_path, graph, prev_exec, "then", sh, "execute")
    prev_exec = sh

print("Tick chain OK")

# ============================================================
# BEGINPLAY: no necesario (GetAllActorsWithTag va en Tick)
# Solo conectar por si acaso en caso de que haya lógica futura
# ============================================================

# ============================================================
# CUSTOM EVENT: DestruirCamino
# ============================================================
de = unreal.BlueprintService.add_custom_event_node(bp_path, graph, "DestruirCamino", -400, 5000)
print(f"DestruirCamino: {de}")

# GetAllActorsWithTag para destruir los cilindros
get_destroy = unreal.BlueprintService.add_function_call_node(
    bp_path, graph, "GameplayStatics", "GetAllActorsWithTag", -100, 5000)
unreal.BlueprintService.set_node_pin_value(bp_path, graph, get_destroy, "Tag", "CilindroGuia")
unreal.BlueprintService.connect_nodes(bp_path, graph, de, "then", get_destroy, "execute")

prev_d = get_destroy
for i in range(13):
    yd = 5100 + i * 120
    agd = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "KismetArrayLibrary", "Array_Get", 200, yd)
    unreal.BlueprintService.set_node_pin_value(bp_path, graph, agd, "Index", str(i))
    unreal.BlueprintService.connect_nodes(bp_path, graph, get_destroy, "OutActors", agd, "TargetArray")

    dd = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "Actor", "K2_DestroyActor", 500, yd)
    unreal.BlueprintService.connect_nodes(bp_path, graph, agd, "Item", dd, "self")
    unreal.BlueprintService.connect_nodes(bp_path, graph, prev_d, "then", dd, "execute")
    prev_d = dd

# Destruir este actor
ds = unreal.BlueprintService.add_function_call_node(
    bp_path, graph, "Actor", "K2_DestroyActor", 800, 5000)
unreal.BlueprintService.connect_nodes(bp_path, graph, prev_d, "then", ds, "execute")
print("DestruirCamino OK")

# Compilar
result = unreal.BlueprintService.compile_blueprint(bp_path)
unreal.EditorAssetLibrary.save_asset(bp_path)
print(f"Compilado: {result}")
print("LISTO")
