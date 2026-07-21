import unreal

bp_path = "/Game/FirstPerson/Blueprints/BP_CaminoGuia"
graph = "EventGraph"

# Borrar y recrear desde cero
if unreal.EditorAssetLibrary.does_asset_exist(bp_path):
    unreal.EditorAssetLibrary.delete_asset(bp_path)

factory = unreal.BlueprintFactory()
factory.set_editor_property("parent_class", unreal.Actor)
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
asset_tools.create_asset("BP_CaminoGuia", "/Game/FirstPerson/Blueprints", unreal.Blueprint, factory)
unreal.EditorAssetLibrary.save_asset(bp_path)
print("BP_CaminoGuia creado limpio")

# Variable array de actores
unreal.BlueprintService.add_variable(bp_path, "MisCilindros", "AActor", "", is_array=True)
print("Variable MisCilindros OK")

# ============================================================
# Obtener IDs de los nodos de evento YA EXISTENTES
# (NO crear nuevos BeginPlay/Tick, usar los del template)
# ============================================================
nodes = unreal.BlueprintService.get_nodes_in_graph(bp_path, graph)
begin_play_id = None
tick_id = None
for n in nodes:
    if n.node_type == "K2Node_Event":
        t = n.node_title
        if "BeginPlay" in t and begin_play_id is None:
            begin_play_id = n.node_id
        elif "Tick" in t and tick_id is None:
            tick_id = n.node_id

print(f"BeginPlay existente: {begin_play_id}")
print(f"Tick existente: {tick_id}")

# ============================================================
# BEGINPLAY: GetAllActorsWithTag -> SetVar(MisCilindros)
# ============================================================
get_tag = unreal.BlueprintService.add_function_call_node(bp_path, graph, "GameplayStatics", "GetAllActorsWithTag", -100, 0)
set_var = unreal.BlueprintService.add_set_variable_node(bp_path, graph, "MisCilindros", 350, 0)
unreal.BlueprintService.set_node_pin_value(bp_path, graph, get_tag, "Tag", "CilindroGuia")

unreal.BlueprintService.connect_nodes(bp_path, graph, begin_play_id, "then", get_tag, "execute")
unreal.BlueprintService.connect_nodes(bp_path, graph, get_tag, "then", set_var, "execute")
unreal.BlueprintService.connect_nodes(bp_path, graph, get_tag, "OutActors", set_var, "MisCilindros")
print("BeginPlay chain OK")

# ============================================================
# TICK: ocultar circulos ya pasados por el jugador
# ============================================================
# GetPlayerCharacter -> GetActorLocation -> BreakVector -> PlayerY
get_pc   = unreal.BlueprintService.add_function_call_node(bp_path, graph, "GameplayStatics", "GetPlayerCharacter", -100, 600)
get_ploc = unreal.BlueprintService.add_function_call_node(bp_path, graph, "Actor", "K2_GetActorLocation", 200, 600)
break_p  = unreal.BlueprintService.add_function_call_node(bp_path, graph, "KismetMathLibrary", "BreakVector", 500, 600)
unreal.BlueprintService.connect_nodes(bp_path, graph, get_pc,   "ReturnValue", get_ploc, "self")
unreal.BlueprintService.connect_nodes(bp_path, graph, get_ploc, "ReturnValue", break_p,  "InVec")

# GetVar MisCilindros (lectura)
get_mis = unreal.BlueprintService.add_get_variable_node(bp_path, graph, "MisCilindros", 500, 700)

# Desplegar en Y para que no se solapen nodos
prev_exec = tick_id
for i in range(13):
    yp = 900 + i * 280

    # Array_Get(i)
    ag = unreal.BlueprintService.add_function_call_node(bp_path, graph, "KismetArrayLibrary", "Array_Get", 500, yp)
    unreal.BlueprintService.set_node_pin_value(bp_path, graph, ag, "Index", str(i))
    unreal.BlueprintService.connect_nodes(bp_path, graph, get_mis, "MisCilindros", ag, "TargetArray")

    # GetActorLocation del cilindro
    cl = unreal.BlueprintService.add_function_call_node(bp_path, graph, "Actor", "K2_GetActorLocation", 800, yp)
    unreal.BlueprintService.connect_nodes(bp_path, graph, ag, "Item", cl, "self")

    # BreakVector cilindro -> CylY
    bc = unreal.BlueprintService.add_function_call_node(bp_path, graph, "KismetMathLibrary", "BreakVector", 1050, yp)
    unreal.BlueprintService.connect_nodes(bp_path, graph, cl, "ReturnValue", bc, "InVec")

    # Greater(CylY > PlayerY) => cilindro detras del jugador => ocultar
    gt = unreal.BlueprintService.add_function_call_node(bp_path, graph, "KismetMathLibrary", "Greater_FloatFloat", 1300, yp)
    unreal.BlueprintService.connect_nodes(bp_path, graph, bc,      "Y", gt, "A")
    unreal.BlueprintService.connect_nodes(bp_path, graph, break_p, "Y", gt, "B")
    print(f"  [{i}] Greater node: {gt}")

    # SetActorHiddenInGame
    sh = unreal.BlueprintService.add_function_call_node(bp_path, graph, "Actor", "SetActorHiddenInGame", 1600, yp)
    unreal.BlueprintService.connect_nodes(bp_path, graph, ag, "Item", sh, "self")
    unreal.BlueprintService.connect_nodes(bp_path, graph, gt, "ReturnValue", sh, "bNewHidden")
    unreal.BlueprintService.connect_nodes(bp_path, graph, prev_exec, "then", sh, "execute")
    prev_exec = sh

print("Tick chain completa")

# ============================================================
# CUSTOM EVENT: DestruirCamino
# ============================================================
de      = unreal.BlueprintService.add_custom_event_node(bp_path, graph, "DestruirCamino", -400, 5000)
get_mis2 = unreal.BlueprintService.add_get_variable_node(bp_path, graph, "MisCilindros", -100, 5000)
print(f"DestruirCamino: {de}")

prev_d = de
for i in range(13):
    yd = 5100 + i * 120
    agd = unreal.BlueprintService.add_function_call_node(bp_path, graph, "KismetArrayLibrary", "Array_Get", 200, yd)
    unreal.BlueprintService.set_node_pin_value(bp_path, graph, agd, "Index", str(i))
    unreal.BlueprintService.connect_nodes(bp_path, graph, get_mis2, "MisCilindros", agd, "TargetArray")

    dd = unreal.BlueprintService.add_function_call_node(bp_path, graph, "Actor", "K2_DestroyActor", 500, yd)
    unreal.BlueprintService.connect_nodes(bp_path, graph, agd, "Item", dd, "self")
    unreal.BlueprintService.connect_nodes(bp_path, graph, prev_d, "then", dd, "execute")
    prev_d = dd

# Destruirse a si mismo
ds = unreal.BlueprintService.add_function_call_node(bp_path, graph, "Actor", "K2_DestroyActor", 800, 5000)
unreal.BlueprintService.connect_nodes(bp_path, graph, prev_d, "then", ds, "execute")
print("DestruirCamino chain OK")

# Compilar y guardar
result = unreal.BlueprintService.compile_blueprint(bp_path)
unreal.EditorAssetLibrary.save_asset(bp_path)
print(f"Compilado: {result}")
print("BP_CaminoGuia LISTO")
