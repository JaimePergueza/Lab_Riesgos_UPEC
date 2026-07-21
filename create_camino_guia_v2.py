import unreal

bp_path = "/Game/FirstPerson/Blueprints/BP_CaminoGuia"
graph = "EventGraph"

# Eliminar si ya existe
if unreal.EditorAssetLibrary.does_asset_exist(bp_path):
    unreal.EditorAssetLibrary.delete_asset(bp_path)

factory = unreal.BlueprintFactory()
factory.set_editor_property("parent_class", unreal.Actor)
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
bp = asset_tools.create_asset("BP_CaminoGuia", "/Game/FirstPerson/Blueprints", unreal.Blueprint, factory)
unreal.EditorAssetLibrary.save_asset(bp_path)
print("BP creado")

# Variable MisCilindros (array de Actor)
unreal.BlueprintService.add_variable(bp_path, "MisCilindros", "Actor", True)
print("Variable OK")

# ========================
# BEGINPLAY: llenar array
# ========================
bp_evt = unreal.BlueprintService.add_event_node(bp_path, graph, "ReceiveBeginPlay", -400, 0)
get_tag = unreal.BlueprintService.add_function_call_node(bp_path, graph, "GameplayStatics", "GetAllActorsWithTag", -100, 0)
set_var = unreal.BlueprintService.add_set_variable_node(bp_path, graph, "MisCilindros", 300, 0)
print("BeginPlay nodes:", bp_evt, get_tag, set_var)

unreal.BlueprintService.set_node_pin_value(bp_path, graph, get_tag, "Tag", "CilindroGuia")
unreal.BlueprintService.connect_nodes(bp_path, graph, bp_evt, "then", get_tag, "execute")
unreal.BlueprintService.connect_nodes(bp_path, graph, get_tag, "then", set_var, "execute")
unreal.BlueprintService.connect_nodes(bp_path, graph, get_tag, "OutActors", set_var, "MisCilindros")
print("BeginPlay chain OK")

# ========================
# EVENTTICK: visibilidad
# ========================
tick_evt = unreal.BlueprintService.add_event_node(bp_path, graph, "ReceiveTick", -400, 900)
print("Tick evt:", tick_evt)

# GetPlayerCharacter -> GetActorLocation -> BreakVector (PlayerY)
get_pc = unreal.BlueprintService.add_function_call_node(bp_path, graph, "GameplayStatics", "GetPlayerCharacter", -100, 900)
get_ploc = unreal.BlueprintService.add_function_call_node(bp_path, graph, "Actor", "K2_GetActorLocation", 200, 900)
break_p = unreal.BlueprintService.add_function_call_node(bp_path, graph, "KismetMathLibrary", "BreakVector", 500, 900)

unreal.BlueprintService.connect_nodes(bp_path, graph, get_pc, "ReturnValue", get_ploc, "self")
unreal.BlueprintService.connect_nodes(bp_path, graph, get_ploc, "ReturnValue", break_p, "InVec")
print("Player loc chain OK - Y output = PlayerY")

# GetVar MisCilindros
get_mis = unreal.BlueprintService.add_get_variable_node(bp_path, graph, "MisCilindros", 750, 900)
print("GetVar:", get_mis)

# Unrolled por cada cilindro (13)
prev_exec = tick_evt
for i in range(13):
    yp = 1100 + i * 260

    # Array_Get(i)
    ag = unreal.BlueprintService.add_function_call_node(bp_path, graph, "KismetArrayLibrary", "Array_Get", 750, yp)
    unreal.BlueprintService.set_node_pin_value(bp_path, graph, ag, "Index", str(i))
    unreal.BlueprintService.connect_nodes(bp_path, graph, get_mis, "MisCilindros", ag, "TargetArray")

    # GetActorLocation del cilindro
    cl = unreal.BlueprintService.add_function_call_node(bp_path, graph, "Actor", "K2_GetActorLocation", 1050, yp)
    unreal.BlueprintService.connect_nodes(bp_path, graph, ag, "Item", cl, "self")

    # BreakVector cilindro
    bc = unreal.BlueprintService.add_function_call_node(bp_path, graph, "KismetMathLibrary", "BreakVector", 1300, yp)
    unreal.BlueprintService.connect_nodes(bp_path, graph, cl, "ReturnValue", bc, "InVec")

    # Greater(CylY, PlayerY) -> cilindro detras del jugador -> ocultar
    gt = unreal.BlueprintService.add_function_call_node(bp_path, graph, "KismetMathLibrary", "Greater_FloatFloat", 1550, yp)
    unreal.BlueprintService.connect_nodes(bp_path, graph, bc, "Y", gt, "A")
    unreal.BlueprintService.connect_nodes(bp_path, graph, break_p, "Y", gt, "B")

    # SetActorHiddenInGame
    sh = unreal.BlueprintService.add_function_call_node(bp_path, graph, "Actor", "SetActorHiddenInGame", 1800, yp)
    unreal.BlueprintService.connect_nodes(bp_path, graph, ag, "Item", sh, "self")
    unreal.BlueprintService.connect_nodes(bp_path, graph, gt, "ReturnValue", sh, "bNewHidden")
    unreal.BlueprintService.connect_nodes(bp_path, graph, prev_exec, "then", sh, "execute")
    prev_exec = sh
    print(f"  Cil {i}: ag={ag} sh={sh}")

print("Tick chain OK")

# ========================
# CUSTOM EVENT: DestruirCamino
# ========================
de = unreal.BlueprintService.add_custom_event_node(bp_path, graph, "DestruirCamino", -400, 5500)
get_mis2 = unreal.BlueprintService.add_get_variable_node(bp_path, graph, "MisCilindros", -100, 5500)
print("DestruirCamino evt:", de)

prev_d = de
for i in range(13):
    yd = 5600 + i * 130
    agd = unreal.BlueprintService.add_function_call_node(bp_path, graph, "KismetArrayLibrary", "Array_Get", 200, yd)
    unreal.BlueprintService.set_node_pin_value(bp_path, graph, agd, "Index", str(i))
    unreal.BlueprintService.connect_nodes(bp_path, graph, get_mis2, "MisCilindros", agd, "TargetArray")

    dd = unreal.BlueprintService.add_function_call_node(bp_path, graph, "Actor", "K2_DestroyActor", 500, yd)
    unreal.BlueprintService.connect_nodes(bp_path, graph, agd, "Item", dd, "self")
    unreal.BlueprintService.connect_nodes(bp_path, graph, prev_d, "then", dd, "execute")
    prev_d = dd

# Destruir este actor tambien
ds = unreal.BlueprintService.add_function_call_node(bp_path, graph, "Actor", "K2_DestroyActor", 800, 5500)
unreal.BlueprintService.connect_nodes(bp_path, graph, prev_d, "then", ds, "execute")
print("DestruirCamino OK")

unreal.BlueprintService.compile_blueprint(bp_path)
unreal.EditorAssetLibrary.save_asset(bp_path)
print("BP_CaminoGuia LISTO")
