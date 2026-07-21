import unreal

bp_path = "/Game/FirstPerson/Blueprints/BP_CaminoGuia"
graph = "EventGraph"

# --- Crear el Blueprint ---
factory = unreal.BlueprintFactory()
factory.set_editor_property("parent_class", unreal.Actor)
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
bp = asset_tools.create_asset(
    "BP_CaminoGuia",
    "/Game/FirstPerson/Blueprints",
    unreal.Blueprint,
    factory
)
unreal.EditorAssetLibrary.save_asset(bp_path)
print("BP_CaminoGuia creado")

# --- Agregar variable MisCilindros (Array of Actor) ---
unreal.BlueprintService.add_variable(bp_path, "MisCilindros", "Actor", True)
print("Variable MisCilindros creada")

# =============================================================
# EVENT GRAPH: BeginPlay Chain
# BeginPlay -> GetAllActorsWithTag -> SetVar -> SetTimer
# =============================================================
begin_play = unreal.BlueprintService.add_event_node(bp_path, graph, "ReceiveBeginPlay", -400.0, 0.0)
print("BeginPlay:", begin_play)

get_actors = unreal.BlueprintService.add_function_call_node(bp_path, graph, "GameplayStatics", "GetAllActorsWithTag", -100.0, 0.0)
print("GetAllActorsWithTag:", get_actors)

# Set variable node
set_var = unreal.BlueprintService.add_variable_set_node(bp_path, graph, "MisCilindros", 250.0, 0.0)
print("SetVar:", set_var)

# SetTimerByFunctionName
set_timer = unreal.BlueprintService.add_function_call_node(bp_path, graph, "KismetSystemLibrary", "SetTimerByFunctionName", 500.0, 0.0)
print("SetTimer:", set_timer)

# Conectar BeginPlay chain
unreal.BlueprintService.connect_nodes(bp_path, graph, begin_play, "then", get_actors, "execute")
unreal.BlueprintService.connect_nodes(bp_path, graph, get_actors, "then", set_var, "execute")
unreal.BlueprintService.connect_nodes(bp_path, graph, get_actors, "OutActors", set_var, "MisCilindros")
unreal.BlueprintService.connect_nodes(bp_path, graph, set_var, "then", set_timer, "execute")

# Configurar pines del timer
unreal.BlueprintService.set_node_pin_value(bp_path, graph, get_actors, "Tag", "CilindroGuia")
unreal.BlueprintService.set_node_pin_value(bp_path, graph, set_timer, "FunctionName", "ActualizarVisibilidad")
unreal.BlueprintService.set_node_pin_value(bp_path, graph, set_timer, "Time", "0.2")
unreal.BlueprintService.set_node_pin_value(bp_path, graph, set_timer, "bLooping", "true")
print("BeginPlay chain configurada")

# =============================================================
# CUSTOM EVENT: ActualizarVisibilidad
# =============================================================
update_event = unreal.BlueprintService.add_custom_event_node(bp_path, graph, "ActualizarVisibilidad", -400.0, 600.0)
print("CustomEvent ActualizarVisibilidad:", update_event)

# GetPlayerCharacter -> GetActorLocation -> BreakVector -> PlayerY
get_player = unreal.BlueprintService.add_function_call_node(bp_path, graph, "GameplayStatics", "GetPlayerCharacter", -100.0, 600.0)
get_player_loc = unreal.BlueprintService.add_function_call_node(bp_path, graph, "Actor", "K2_GetActorLocation", 200.0, 600.0)
break_player = unreal.BlueprintService.add_function_call_node(bp_path, graph, "KismetMathLibrary", "BreakVector", 450.0, 600.0)
print("GetPlayer nodes:", get_player, get_player_loc, break_player)

unreal.BlueprintService.connect_nodes(bp_path, graph, update_event, "then", get_player_loc, "execute")
unreal.BlueprintService.connect_nodes(bp_path, graph, get_player, "ReturnValue", get_player_loc, "self")
unreal.BlueprintService.connect_nodes(bp_path, graph, get_player_loc, "ReturnValue", break_player, "InVec")
print("Player chain conectada")

# Get variable MisCilindros
get_var = unreal.BlueprintService.add_variable_get_node(bp_path, graph, "MisCilindros", 700.0, 600.0)
print("GetVar:", get_var)

# =============================================================
# POR CADA CILINDRO (unrolled para 13):
# Array_Get(i) -> GetActorLocation -> BreakVector -> CylY
# Greater(CylY, PlayerY) -> SetActorHiddenInGame
# (si CylY > PlayerY, el jugador ya paso el circulo -> ocultar)
# =============================================================
prev_exec = get_player_loc  # encadenar exec pins

for i in range(13):
    x_offset = 700.0 + i * 0.0   # mismo X, diferente Y para layout vertical
    y_offset = 800.0 + i * 220.0  # separar cada ciclo verticalmente

    # Array_Get(index i)
    arr_get = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "KismetArrayLibrary", "Array_Get",
        x_offset, y_offset
    )
    unreal.BlueprintService.set_node_pin_value(bp_path, graph, arr_get, "Index", str(i))
    unreal.BlueprintService.connect_nodes(bp_path, graph, get_var, "MisCilindros", arr_get, "TargetArray")

    # GetActorLocation del cilindro
    cyl_loc = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "Actor", "K2_GetActorLocation",
        x_offset + 300.0, y_offset
    )
    unreal.BlueprintService.connect_nodes(bp_path, graph, arr_get, "Item", cyl_loc, "self")

    # BreakVector del cilindro
    break_cyl = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "KismetMathLibrary", "BreakVector",
        x_offset + 550.0, y_offset
    )
    unreal.BlueprintService.connect_nodes(bp_path, graph, cyl_loc, "ReturnValue", break_cyl, "InVec")

    # Greater(CylY, PlayerY) -> si cilindro esta DETRAS del jugador -> ocultar
    greater = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "KismetMathLibrary", "Greater_FloatFloat",
        x_offset + 800.0, y_offset
    )
    unreal.BlueprintService.connect_nodes(bp_path, graph, break_cyl, "Y", greater, "A")
    unreal.BlueprintService.connect_nodes(bp_path, graph, break_player, "Y", greater, "B")

    # SetActorHiddenInGame
    set_hidden = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "Actor", "SetActorHiddenInGame",
        x_offset + 1050.0, y_offset
    )
    unreal.BlueprintService.connect_nodes(bp_path, graph, arr_get, "Item", set_hidden, "self")
    unreal.BlueprintService.connect_nodes(bp_path, graph, greater, "ReturnValue", set_hidden, "bNewHidden")

    # Encadenar exec: prev_exec -> set_hidden
    unreal.BlueprintService.connect_nodes(bp_path, graph, prev_exec, "then", set_hidden, "execute")
    prev_exec = set_hidden

    print(f"Cilindro {i}: arr_get={arr_get}, set_hidden={set_hidden}")

# =============================================================
# FUNCION PUBLICA: DestruirCamino (llamada por el trigger)
# =============================================================
destroy_event = unreal.BlueprintService.add_custom_event_node(bp_path, graph, "DestruirCamino", -400.0, 3800.0)
print("CustomEvent DestruirCamino:", destroy_event)

# GetAllActorsWithTag -> ForEach -> DestroyActor + Destroy self
get_to_destroy = unreal.BlueprintService.add_function_call_node(
    bp_path, graph, "GameplayStatics", "GetAllActorsWithTag", -100.0, 3800.0
)
unreal.BlueprintService.set_node_pin_value(bp_path, graph, get_to_destroy, "Tag", "CilindroGuia")

# Destroy each (unrolled para 13)
unreal.BlueprintService.connect_nodes(bp_path, graph, destroy_event, "then", get_to_destroy, "execute")
get_var2 = unreal.BlueprintService.add_variable_get_node(bp_path, graph, "MisCilindros", 250.0, 3800.0)

prev_d = get_to_destroy
for i in range(13):
    y_d = 3900.0 + i * 120.0
    arr_get_d = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "KismetArrayLibrary", "Array_Get", 500.0, y_d
    )
    unreal.BlueprintService.set_node_pin_value(bp_path, graph, arr_get_d, "Index", str(i))
    unreal.BlueprintService.connect_nodes(bp_path, graph, get_to_destroy, "OutActors", arr_get_d, "TargetArray")

    destroy_d = unreal.BlueprintService.add_function_call_node(
        bp_path, graph, "Actor", "K2_DestroyActor", 800.0, y_d
    )
    unreal.BlueprintService.connect_nodes(bp_path, graph, arr_get_d, "Item", destroy_d, "self")
    unreal.BlueprintService.connect_nodes(bp_path, graph, prev_d, "then", destroy_d, "execute")
    prev_d = destroy_d

# Destroy self (BP_CaminoGuia)
destroy_self = unreal.BlueprintService.add_function_call_node(
    bp_path, graph, "Actor", "K2_DestroyActor", 1100.0, 3800.0
)
unreal.BlueprintService.connect_nodes(bp_path, graph, prev_d, "then", destroy_self, "execute")
# self pin gets implicit actor reference

print("DestruirCamino chain creada")

# Compilar y guardar
unreal.BlueprintService.compile_blueprint(bp_path)
unreal.EditorAssetLibrary.save_asset(bp_path)
print("BP_CaminoGuia COMPLETO y guardado")
