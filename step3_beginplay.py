import unreal

char_bp = "/Game/FirstPerson/Blueprints/BP_FirstPersonCharacter"
graph = "EventGraph"

# Verificar si ya hay BeginPlay
nodes = unreal.BlueprintService.get_nodes_in_graph(char_bp, graph)
has_begin = any("BeginPlay" in n.node_title for n in nodes)

if has_begin:
    print("BeginPlay ya existe, saltando")
else:
    # Agregar Event BeginPlay
    begin_node = unreal.BlueprintService.add_event_node(char_bp, graph, "ReceiveBeginPlay", -800.0, 2500.0)
    print("BeginPlay node:", begin_node)

    # Delay 1 segundo para que todo cargue
    delay_node = unreal.BlueprintService.add_function_call_node(char_bp, graph, "KismetSystemLibrary", "Delay", -500.0, 2500.0)
    unreal.BlueprintService.set_node_pin_value(char_bp, graph, delay_node, "Duration", "1.0")
    print("Delay node:", delay_node)

    # Get All Actors Of Class (BP_Bienvenida)
    get_actors = unreal.BlueprintService.add_function_call_node(char_bp, graph, "GameplayStatics", "GetAllActorsOfClass", -100.0, 2500.0)
    print("GetAllActors node:", get_actors)

    # Conectar: BeginPlay -> Delay -> GetAllActors
    unreal.BlueprintService.connect_nodes(char_bp, graph, begin_node, "then", delay_node, "execute")
    unreal.BlueprintService.connect_nodes(char_bp, graph, delay_node, "then", get_actors, "execute")
    print("Conexiones OK")

    unreal.BlueprintService.compile_blueprint(char_bp)
    unreal.EditorAssetLibrary.save_asset(char_bp)
    print("BP_FirstPersonCharacter guardado con BeginPlay")
