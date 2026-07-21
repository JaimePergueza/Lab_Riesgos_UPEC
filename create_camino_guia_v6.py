import unreal

bp_path = "/Game/FirstPerson/Blueprints/BP_CaminoGuia"
graph = "EventGraph"

# Borrar y recrear limpio
if unreal.EditorAssetLibrary.does_asset_exist(bp_path):
    unreal.EditorAssetLibrary.delete_asset(bp_path)

factory = unreal.BlueprintFactory()
factory.set_editor_property("parent_class", unreal.Actor)
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
asset_tools.create_asset("BP_CaminoGuia", "/Game/FirstPerson/Blueprints", unreal.Blueprint, factory)
unreal.EditorAssetLibrary.save_asset(bp_path)
print("BP creado")

# Obtener nodos de evento existentes (NO crear duplicados)
nodes = unreal.BlueprintService.get_nodes_in_graph(bp_path, graph)
tick_id = None
for n in nodes:
    if "Tick" in n.node_title and n.node_type == "K2Node_Event" and tick_id is None:
        tick_id = n.node_id
print(f"Tick existente: {tick_id}")

# ============================================================
# TICK usando build_graph con from_ correcto
# Estructura por cilindro: GetAllActors -> Array_Get ->
#   CastToStaticMeshActor (resuelve tipo) ->
#   GetActorLocation -> BreakVector -> Greater -> Branch ->
#   True: SetActorHiddenInGame(true)
# ============================================================

# GetAllActorsWithTag (una sola vez, compartido por todos)
get_tag_node = unreal.BlueprintService.add_function_call_node(
    bp_path, graph, "GameplayStatics", "GetAllActorsWithTag", -100, 400)
unreal.BlueprintService.set_node_pin_value(bp_path, graph, get_tag_node, "Tag", "CilindroGuia")

# GetPlayerCharacter -> GetActorLocation -> BreakVector -> PlayerY
get_pc   = unreal.BlueprintService.add_function_call_node(bp_path, graph, "GameplayStatics", "GetPlayerCharacter", -100, 600)
get_ploc = unreal.BlueprintService.add_function_call_node(bp_path, graph, "Actor", "K2_GetActorLocation", 200, 600)
break_p  = unreal.BlueprintService.add_function_call_node(bp_path, graph, "KismetMathLibrary", "BreakVector", 500, 600)
unreal.BlueprintService.connect_nodes(bp_path, graph, get_pc,   "ReturnValue", get_ploc, "self")
unreal.BlueprintService.connect_nodes(bp_path, graph, get_ploc, "ReturnValue", break_p,  "InVec")

# Conectar Tick -> GetAllActors
unreal.BlueprintService.connect_nodes(bp_path, graph, tick_id, "then", get_tag_node, "execute")

prev_exec = get_tag_node

for i in range(13):
    yp = 900 + i * 350

    # Array_Get(i) - wildcard pero se resuelve via cast
    ag = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "KismetArrayLibrary", "Array_Get", 350, yp)
    unreal.BlueprintService.set_node_pin_value(bp_path, graph, ag, "Index", str(i))
    unreal.BlueprintService.connect_nodes(bp_path, graph, get_tag_node, "OutActors", ag, "TargetArray")

    # Cast to StaticMeshActor -> salida tipada como StaticMeshActor (subclase de Actor)
    cast_n = unreal.BlueprintService.add_cast_node(bp_path, graph, "StaticMeshActor", 600, yp)
    unreal.BlueprintService.connect_nodes(bp_path, graph, ag, "Item", cast_n, "Object")
    print(f"  [{i}] Cast node: {cast_n}")

    # GetActorLocation del cilindro (usando el output tipado del cast)
    # Pin del cast output: "As Static Mesh Actor"
    cl = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "Actor", "K2_GetActorLocation", 900, yp)
    unreal.BlueprintService.connect_nodes(bp_path, graph, cast_n, "As Static Mesh Actor", cl, "self")

    # BreakVector -> CylY
    bc = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "KismetMathLibrary", "BreakVector", 1150, yp)
    unreal.BlueprintService.connect_nodes(bp_path, graph, cl, "ReturnValue", bc, "InVec")

    # Greater(CylY, PlayerY) => cilindro detras del jugador => ocultar
    gt = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "KismetMathLibrary", "Greater_FloatFloat", 1400, yp)
    unreal.BlueprintService.connect_nodes(bp_path, graph, bc,      "Y", gt, "A")
    unreal.BlueprintService.connect_nodes(bp_path, graph, break_p, "Y", gt, "B")

    # SetActorHiddenInGame usando el output tipado del cast
    sh = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "Actor", "SetActorHiddenInGame", 1650, yp)
    unreal.BlueprintService.connect_nodes(bp_path, graph, cast_n, "As Static Mesh Actor", sh, "self")
    unreal.BlueprintService.connect_nodes(bp_path, graph, gt, "ReturnValue", sh, "bNewHidden")

    # Exec chain: prev_exec -> cast (que tiene exec) -> set_hidden
    unreal.BlueprintService.connect_nodes(bp_path, graph, prev_exec, "then", cast_n, "execute")
    unreal.BlueprintService.connect_nodes(bp_path, graph, cast_n, "then", sh, "execute")
    prev_exec = sh

print("Tick chain OK")

# ============================================================
# CUSTOM EVENT: DestruirCamino
# ============================================================
de = unreal.BlueprintService.add_custom_event_node(bp_path, graph, "DestruirCamino", -400, 5500)
print(f"DestruirCamino: {de}")

get_destroy = unreal.BlueprintService.add_function_call_node(
    bp_path, graph, "GameplayStatics", "GetAllActorsWithTag", -100, 5500)
unreal.BlueprintService.set_node_pin_value(bp_path, graph, get_destroy, "Tag", "CilindroGuia")
unreal.BlueprintService.connect_nodes(bp_path, graph, de, "then", get_destroy, "execute")

prev_d = get_destroy
for i in range(13):
    yd = 5600 + i * 130
    agd = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "KismetArrayLibrary", "Array_Get", 200, yd)
    unreal.BlueprintService.set_node_pin_value(bp_path, graph, agd, "Index", str(i))
    unreal.BlueprintService.connect_nodes(bp_path, graph, get_destroy, "OutActors", agd, "TargetArray")

    dd = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "Actor", "K2_DestroyActor", 500, yd)
    unreal.BlueprintService.connect_nodes(bp_path, graph, agd, "Item", dd, "self")
    unreal.BlueprintService.connect_nodes(bp_path, graph, prev_d, "then", dd, "execute")
    prev_d = dd

ds = unreal.BlueprintService.add_function_call_node(
    bp_path, graph, "Actor", "K2_DestroyActor", 800, 5500)
unreal.BlueprintService.connect_nodes(bp_path, graph, prev_d, "then", ds, "execute")
print("DestruirCamino OK")

# Compilar
result = unreal.BlueprintService.compile_blueprint(bp_path)
unreal.EditorAssetLibrary.save_asset(bp_path)
# Contar errores en el resultado
errors = getattr(result, 'errors', []) if result else []
warnings_list = getattr(result, 'warnings', []) if result else []
print(f"Compilado - errors: {len(errors)}, warnings: {len(warnings_list)}")
if errors:
    for e in errors[:5]:
        print(f"  ERROR: {str(e)[:100]}")
if warnings_list:
    print(f"  Warnings (primeros 3): {str(warnings_list[:3])[:300]}")
print("LISTO")
