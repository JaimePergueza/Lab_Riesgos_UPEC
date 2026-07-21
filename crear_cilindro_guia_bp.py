import unreal

# ============================================================
# BP_CilindroGuia: cada actor se oculta solo cuando el
# jugador lo pasa (compara su Y con la del jugador en Tick)
# NO usa Array_Get -> sin problemas de wildcard
# ============================================================

bp_path = "/Game/FirstPerson/Blueprints/BP_CilindroGuia"
graph = "EventGraph"
mesh_path = "/Game/Maps/_GENERATED/freddy/Cylinder_AE0D16C6"

# Borrar si existe
if unreal.EditorAssetLibrary.does_asset_exist(bp_path):
    unreal.EditorAssetLibrary.delete_asset(bp_path)

factory = unreal.BlueprintFactory()
factory.set_editor_property("parent_class", unreal.Actor)
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
asset_tools.create_asset("BP_CilindroGuia", "/Game/FirstPerson/Blueprints", unreal.Blueprint, factory)
unreal.EditorAssetLibrary.save_asset(bp_path)
print("BP_CilindroGuia creado")

# Agregar StaticMeshComponent con el cilindro amarillo
comp_ok = unreal.BlueprintService.add_component(bp_path, "StaticMeshComponent", "Mesh_Cilindro")
print("add_component:", comp_ok)
if comp_ok:
    unreal.BlueprintService.set_component_property(bp_path, "Mesh_Cilindro", "StaticMesh", mesh_path)
    print("StaticMesh asignado")

# Obtener Tick node existente
nodes = unreal.BlueprintService.get_nodes_in_graph(bp_path, graph)
tick_id = None
for n in nodes:
    if "Tick" in n.node_title and n.node_type == "K2Node_Event" and tick_id is None:
        tick_id = n.node_id
print("Tick ID:", tick_id)

# ============================================================
# EVENT TICK:
# GetPlayerCharacter -> GetActorLocation -> BreakVector -> PlayerY
# GetActorLocation(self) -> BreakVector -> OwnY
# Greater(OwnY, PlayerY) -> SetActorHiddenInGame(self, bool)
# ============================================================

# GetPlayerCharacter
get_pc = unreal.BlueprintService.add_function_call_node(
    bp_path, graph, "GameplayStatics", "GetPlayerCharacter", -100, 400)

# GetActorLocation del jugador
get_ploc = unreal.BlueprintService.add_function_call_node(
    bp_path, graph, "Actor", "K2_GetActorLocation", 200, 400)
unreal.BlueprintService.connect_nodes(bp_path, graph, get_pc, "ReturnValue", get_ploc, "self")

# BreakVector jugador -> PlayerY
break_p = unreal.BlueprintService.add_function_call_node(
    bp_path, graph, "KismetMathLibrary", "BreakVector", 500, 400)
unreal.BlueprintService.connect_nodes(bp_path, graph, get_ploc, "ReturnValue", break_p, "InVec")

# GetActorLocation de ESTE actor (self - tipado como BP_CilindroGuia)
get_own_loc = unreal.BlueprintService.add_function_call_node(
    bp_path, graph, "Actor", "K2_GetActorLocation", -100, 600)
# self es automatico (el propio actor)

# BreakVector propio -> OwnY
break_own = unreal.BlueprintService.add_function_call_node(
    bp_path, graph, "KismetMathLibrary", "BreakVector", 200, 600)
unreal.BlueprintService.connect_nodes(bp_path, graph, get_own_loc, "ReturnValue", break_own, "InVec")

# Greater(OwnY > PlayerY) => cilindro esta detras del jugador => ocultar
gt = unreal.BlueprintService.add_function_call_node(
    bp_path, graph, "KismetMathLibrary", "Greater_FloatFloat", 500, 600)
unreal.BlueprintService.connect_nodes(bp_path, graph, break_own, "Y", gt, "A")
unreal.BlueprintService.connect_nodes(bp_path, graph, break_p,   "Y", gt, "B")

# SetActorHiddenInGame(self, bool) - self es este actor, tipado correcto
sh = unreal.BlueprintService.add_function_call_node(
    bp_path, graph, "Actor", "SetActorHiddenInGame", 800, 500)
unreal.BlueprintService.connect_nodes(bp_path, graph, gt, "ReturnValue", sh, "bNewHidden")

# Encadenar exec: Tick -> get_own_loc no necesita exec (pura) -> sh
unreal.BlueprintService.connect_nodes(bp_path, graph, tick_id, "then", sh, "execute")
print("Tick chain OK (self es tipado, sin wildcard)")

# Compilar
result = unreal.BlueprintService.compile_blueprint(bp_path)
unreal.EditorAssetLibrary.save_asset(bp_path)
errors = getattr(result, 'errors', []) if result else []
print(f"Compilado - errors: {len(errors)}")
for e in errors[:3]:
    print("  E:", str(e)[:100])
print("BP_CilindroGuia LISTO")
