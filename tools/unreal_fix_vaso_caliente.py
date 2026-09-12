import unreal

BP_FPC = "/Game/FirstPerson/Blueprints/BP_FirstPersonCharacter"
BP_VASO = "/Game/Fab/BP_ActoresJuego/VasoJuego"

GRAPH = "EventGraph"


def log(message: str) -> None:
    print(message)


def ok(value, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def ensure_variable(bp_path: str, name: str, var_type: str, default_value: str = "") -> None:
    if unreal.BlueprintService.variable_exists(bp_path, name):
        if default_value != "":
            unreal.BlueprintService.set_variable_default_value(bp_path, name, default_value)
        return
    ok(
        unreal.BlueprintService.add_variable(bp_path, name, var_type, default_value),
        f"No se pudo crear la variable {name} en {bp_path}",
    )


def ensure_component(bp_path: str, component_type: str, component_name: str, parent_name: str = "") -> None:
    if unreal.BlueprintService.component_exists(bp_path, component_name):
        return
    ok(
        unreal.BlueprintService.add_component(bp_path, component_type, component_name, parent_name),
        f"No se pudo crear el componente {component_name} en {bp_path}",
    )


def get_nodes(bp_path: str, graph_name: str):
    return {node.node_id: node for node in unreal.BlueprintService.get_nodes_in_graph(bp_path, graph_name)}


def get_pins(bp_path: str, graph_name: str, node_id: str):
    return unreal.BlueprintService.get_node_pins(bp_path, graph_name, node_id)


def find_pin(bp_path: str, graph_name: str, node_id: str, needle: str, is_input=None) -> str:
    needle_lower = needle.lower()
    for pin in get_pins(bp_path, graph_name, node_id):
        if is_input is not None and pin.is_input != is_input:
            continue
        if pin.pin_name.lower() == needle_lower:
            return pin.pin_name
    for pin in get_pins(bp_path, graph_name, node_id):
        if is_input is not None and pin.is_input != is_input:
            continue
        if needle_lower in pin.pin_name.lower():
            return pin.pin_name
    available = [pin.pin_name for pin in get_pins(bp_path, graph_name, node_id)]
    raise RuntimeError(f"No encontré pin '{needle}' en nodo {node_id}. Disponibles: {available}")


def safe_disconnect(bp_path: str, graph_name: str, node_id: str, needle: str, is_input=None) -> None:
    try:
        pin_name = find_pin(bp_path, graph_name, node_id, needle, is_input=is_input)
        unreal.BlueprintService.disconnect_pin(bp_path, graph_name, node_id, pin_name)
    except Exception:
        pass


def connect(bp_path: str, graph_name: str, src_node: str, src_pin: str, dst_node: str, dst_pin: str) -> None:
    src_name = find_pin(bp_path, graph_name, src_node, src_pin, is_input=False)
    dst_name = find_pin(bp_path, graph_name, dst_node, dst_pin, is_input=True)
    ok(
        unreal.BlueprintService.connect_nodes(bp_path, graph_name, src_node, src_name, dst_node, dst_name),
        f"No se pudo conectar {src_node}:{src_name} -> {dst_node}:{dst_name}",
    )


def set_pin(bp_path: str, graph_name: str, node_id: str, pin_name: str, value: str) -> None:
    pin = find_pin(bp_path, graph_name, node_id, pin_name, is_input=True)
    ok(
        unreal.BlueprintService.set_node_pin_value(bp_path, graph_name, node_id, pin, value),
        f"No se pudo configurar {node_id}:{pin} con {value}",
    )


def delete_node_if_exists(bp_path: str, graph_name: str, node_id: str) -> None:
    existing = get_nodes(bp_path, graph_name)
    if node_id in existing:
        ok(
            unreal.BlueprintService.delete_node(bp_path, graph_name, node_id),
            f"No se pudo eliminar el nodo {node_id} en {bp_path}",
        )


def add_get_var(bp_path: str, graph_name: str, var_name: str, x: float, y: float) -> str:
    node_id = unreal.BlueprintService.add_get_variable_node(bp_path, graph_name, var_name, x, y)
    ok(node_id, f"No se pudo crear Get {var_name}")
    return node_id


def add_set_var(bp_path: str, graph_name: str, var_name: str, x: float, y: float) -> str:
    node_id = unreal.BlueprintService.add_set_variable_node(bp_path, graph_name, var_name, x, y)
    ok(node_id, f"No se pudo crear Set {var_name}")
    return node_id


def add_branch(bp_path: str, graph_name: str, x: float, y: float) -> str:
    node_id = unreal.BlueprintService.add_branch_node(bp_path, graph_name, x, y)
    ok(node_id, "No se pudo crear Branch")
    return node_id


def add_print(bp_path: str, graph_name: str, text: str, x: float, y: float) -> str:
    node_id = unreal.BlueprintService.add_print_string_node(bp_path, graph_name, x, y)
    ok(node_id, "No se pudo crear PrintString")
    set_pin(bp_path, graph_name, node_id, "InString", text)
    return node_id


def add_call(bp_path: str, graph_name: str, owner_class: str, function_name: str, x: float, y: float) -> str:
    node_id = unreal.BlueprintService.add_function_call_node(bp_path, graph_name, owner_class, function_name, x, y)
    ok(node_id, f"No se pudo crear la llamada {owner_class}.{function_name}")
    return node_id


def add_compare(bp_path: str, graph_name: str, kind: str, value_type: str, x: float, y: float) -> str:
    node_id = unreal.BlueprintService.add_comparison_node(bp_path, graph_name, kind, value_type, x, y)
    ok(node_id, f"No se pudo crear comparación {kind}")
    return node_id


def compile_and_save(bp_path: str) -> None:
    result = unreal.BlueprintService.compile_blueprint(bp_path)
    log(f"Compile {bp_path}: {result}")
    asset = unreal.load_asset(bp_path)
    ok(asset is not None, f"No se pudo cargar el asset {bp_path} para guardar")
    ok(unreal.EditorAssetLibrary.save_loaded_asset(asset, False), f"No se pudo guardar {bp_path}")


def patch_player_variables_and_component() -> None:
    log("Preparando variables y carry point del jugador...")
    ensure_variable(BP_FPC, "TieneGuantesTermicos", "bool", "false")
    ensure_variable(BP_FPC, "bEstaSiendoTransportado", "bool", "false")
    ensure_component(BP_FPC, "SceneComponent", "VasoCarryPoint", "FirstPersonCamera")
    unreal.BlueprintService.set_component_property(BP_FPC, "VasoCarryPoint", "RelativeLocation", "(X=35.0,Y=18.0,Z=-10.0)")
    unreal.BlueprintService.set_component_property(BP_FPC, "VasoCarryPoint", "RelativeRotation", "(Pitch=0.0,Yaw=0.0,Roll=0.0)")


def patch_glove_pickup_chain() -> None:
    log("Parcheando recogida de guantes en BP_FirstPersonCharacter...")
    set_gloves = add_set_var(BP_FPC, GRAPH, "TieneGuantesTermicos", 1500.0, 5000.0)
    set_pin(BP_FPC, GRAPH, set_gloves, "TieneGuantesTermicos", "true")

    cast_gloves = "F7391FAD4B80C700A7870EB6888D8729"
    print_gloves = "8F39CD80407CEAC04DCA53AD9D39B1BE"

    safe_disconnect(BP_FPC, GRAPH, cast_gloves, "then", is_input=False)
    connect(BP_FPC, GRAPH, cast_gloves, "then", set_gloves, "execute")
    connect(BP_FPC, GRAPH, set_gloves, "then", print_gloves, "execute")


def patch_flask_interaction_chain() -> None:
    log("Parcheando rama del matraz caliente en BP_FirstPersonCharacter...")

    # Nodos existentes que vamos a conservar/reutilizar.
    cast_vaso = "8818E4934F86B52809FDE0B4BBBD9497"
    glove_branch = "FEADA76242A2A49BB2BB658AA40DAFEA"
    get_heat_source = "A8FE21304A817DE299AF9CBE982CFA84"
    get_heat_on = "F5C450BB4FF54C6E0FF38CA1F6813ED3"
    not_heat_on = "A03636B448A21390E50B85AE8ACCBEC2"
    heat_branch = "5366489F4A1DD00E95F72D9176ECC9A4"
    print_gloves_warning = "B70F05F346AF9D1AF4F2939CB9C875D5"
    print_success = "F51A9DD2406CBECBAAB07893FCB95780"
    print_heat_warning = "96CA93924240364174A21A84165B79DB"
    get_mesh = "308C8D564AB292EB3A11FEAAC804DAA4"
    set_sim_false = "0F742E8C429AB7741424978145FA4921"
    set_gravity_false = "DECD6B97415FF34562ECDDA2762FA95F"
    attach_to_component = "FC0FCD4F4FFFF0E0D061F3A723010FAD"

    # Nodos incorrectos/obsoletos que quitamos del flujo actual.
    old_nodes = [
        "7AF849914B01BA49AE399B89E10DBB34",  # GetActorOfClass(BP_GuantesTermicos)
        "57E44E204C419EC0F0E8FAAC53D4E6A9",  # IsValid guantes
        "9BCA702E45BC8A0F6967BEA241EC5CF0",  # NOT guantes
        "5C99443941A9FD8C3F876DAAC3F33BCF",  # OR bool antiguo
        "123672B9464FB05F3816ACA5E597C865",  # Attach Actor To Actor
        "6104A98047508C89651E47A14AAEC5F4",  # SetActorHiddenInGame
        "81C5F76442471EB730C1A3B3043C1301",  # SetActorRelativeLocation
        "4C6A5C304BBDB77CDE689E9C53999BD0",  # Attach Component To Component
        "A7BEF60643490EAD21A80084C9C23018",  # GetRootComponent 1
        "A6ECD91B43F511F87D0BC7BC730FAC80",  # GetRootComponent 2
        "189E7C684AD36A2D7B1D6C86609D7610",  # GetPlayerCharacter viejo
    ]
    for node_id in old_nodes:
        delete_node_if_exists(BP_FPC, GRAPH, node_id)

    get_transport = add_get_var(BP_FPC, GRAPH, "bEstaSiendoTransportado", 1850.0, 5660.0)
    transport_branch = add_branch(BP_FPC, GRAPH, 2100.0, 5800.0)
    get_gloves = add_get_var(BP_FPC, GRAPH, "TieneGuantesTermicos", 3000.0, 5660.0)
    get_carry_point = add_get_var(BP_FPC, GRAPH, "VasoCarryPoint", 4700.0, 5450.0)
    set_transport_true = add_set_var(BP_FPC, GRAPH, "bEstaSiendoTransportado", 5350.0, 5550.0)
    set_pin(BP_FPC, GRAPH, set_transport_true, "bEstaSiendoTransportado", "true")

    # Drop chain.
    get_all_meta = add_call(BP_FPC, GRAPH, "GameplayStatics", "GetAllActorsWithTag", 2450.0, 6100.0)
    array_get_meta = add_call(BP_FPC, GRAPH, "KismetArrayLibrary", "Array_Get", 2720.0, 6250.0)
    get_distance = add_call(BP_FPC, GRAPH, "Actor", "GetDistanceTo", 3060.0, 6230.0)
    distance_branch = add_branch(BP_FPC, GRAPH, 3600.0, 6100.0)
    compare_distance = add_compare(BP_FPC, GRAPH, "LessEqual", "Float", 3360.0, 6240.0)
    set_pin(BP_FPC, GRAPH, compare_distance, "B", "180.0")

    detach_drop = add_call(BP_FPC, GRAPH, "Actor", "DetachFromActor", 3900.0, 5950.0)
    detach_finish = add_call(BP_FPC, GRAPH, "Actor", "DetachFromActor", 3900.0, 6400.0)

    set_sim_true = add_call(BP_FPC, GRAPH, "PrimitiveComponent", "SetSimulatePhysics", 4220.0, 6400.0)
    set_pin(BP_FPC, GRAPH, set_sim_true, "bSimulate", "true")
    set_gravity_true = add_call(BP_FPC, GRAPH, "PrimitiveComponent", "SetEnableGravity", 4500.0, 6400.0)
    set_pin(BP_FPC, GRAPH, set_gravity_true, "bGravityEnabled", "true")

    get_meta_location = add_call(BP_FPC, GRAPH, "Actor", "GetActorLocation", 4180.0, 5950.0)
    snap_to_destination = add_call(BP_FPC, GRAPH, "Actor", "K2_SetActorLocation", 4500.0, 5950.0)
    set_pin(BP_FPC, GRAPH, snap_to_destination, "bSweep", "false")
    set_pin(BP_FPC, GRAPH, snap_to_destination, "bTeleport", "true")

    set_transport_false_a = add_set_var(BP_FPC, GRAPH, "bEstaSiendoTransportado", 4840.0, 5950.0)
    set_pin(BP_FPC, GRAPH, set_transport_false_a, "bEstaSiendoTransportado", "false")
    set_transport_false_b = add_set_var(BP_FPC, GRAPH, "bEstaSiendoTransportado", 4840.0, 6400.0)
    set_pin(BP_FPC, GRAPH, set_transport_false_b, "bEstaSiendoTransportado", "false")

    print_destination_ok = add_print(BP_FPC, GRAPH, "Muestra colocada correctamente en el punto destino", 5150.0, 5950.0)
    print_drop_ok = add_print(BP_FPC, GRAPH, "Matraz soltado", 5150.0, 6400.0)

    # Reconfigurar mensajes existentes.
    set_pin(BP_FPC, GRAPH, print_gloves_warning, "InString", "Debe colocarse los guantes térmicos")
    set_pin(BP_FPC, GRAPH, print_heat_warning, "InString", "Debe apagar la estufa antes de manipular el matraz")
    set_pin(BP_FPC, GRAPH, print_success, "InString", "Toma siempre el matraz por el cuello y la base")

    # Limpiamos conexiones de los nodos reutilizados.
    for node_id, pin_name, is_input in [
        (glove_branch, "execute", True),
        (glove_branch, "Condition", True),
        (glove_branch, "then", False),
        (glove_branch, "else", False),
        (heat_branch, "execute", True),
        (heat_branch, "Condition", True),
        (heat_branch, "then", False),
        (heat_branch, "else", False),
        (print_success, "then", False),
        (set_gravity_false, "then", False),
        (attach_to_component, "Parent", True),
        (attach_to_component, "then", False),
    ]:
        safe_disconnect(BP_FPC, GRAPH, node_id, pin_name, is_input=is_input)

    # Pickup: primero branch de transporte, luego guantes, luego fuente de calor.
    connect(BP_FPC, GRAPH, cast_vaso, "then", transport_branch, "execute")
    connect(BP_FPC, GRAPH, get_transport, "bEstaSiendoTransportado", transport_branch, "Condition")

    connect(BP_FPC, GRAPH, transport_branch, "else", glove_branch, "execute")
    connect(BP_FPC, GRAPH, get_gloves, "TieneGuantesTermicos", glove_branch, "Condition")
    connect(BP_FPC, GRAPH, glove_branch, "else", print_gloves_warning, "execute")
    connect(BP_FPC, GRAPH, glove_branch, "then", get_heat_source, "execute")

    connect(BP_FPC, GRAPH, get_heat_source, "ReturnValue", get_heat_on, "self")
    connect(BP_FPC, GRAPH, get_heat_source, "then", heat_branch, "execute")
    connect(BP_FPC, GRAPH, get_heat_on, "bEncendida", not_heat_on, "A")
    connect(BP_FPC, GRAPH, not_heat_on, "ReturnValue", heat_branch, "Condition")
    connect(BP_FPC, GRAPH, heat_branch, "then", print_success, "execute")
    connect(BP_FPC, GRAPH, heat_branch, "else", print_heat_warning, "execute")

    connect(BP_FPC, GRAPH, print_success, "then", set_sim_false, "execute")
    connect(BP_FPC, GRAPH, set_gravity_false, "then", attach_to_component, "execute")
    connect(BP_FPC, GRAPH, get_carry_point, "VasoCarryPoint", attach_to_component, "Parent")
    connect(BP_FPC, GRAPH, attach_to_component, "then", set_transport_true, "execute")

    set_pin(BP_FPC, GRAPH, set_sim_false, "bSimulate", "false")
    set_pin(BP_FPC, GRAPH, set_gravity_false, "bGravityEnabled", "false")
    set_pin(BP_FPC, GRAPH, attach_to_component, "LocationRule", "SnapToTarget")
    set_pin(BP_FPC, GRAPH, attach_to_component, "RotationRule", "SnapToTarget")
    set_pin(BP_FPC, GRAPH, attach_to_component, "ScaleRule", "KeepWorld")
    set_pin(BP_FPC, GRAPH, attach_to_component, "bWeldSimulatedBodies", "false")

    # Drop: si ya está transportando, al interactuar otra vez se suelta o se entrega.
    connect(BP_FPC, GRAPH, transport_branch, "then", get_all_meta, "execute")
    set_pin(BP_FPC, GRAPH, get_all_meta, "Tag", "MetaZoneVaso")
    set_pin(BP_FPC, GRAPH, array_get_meta, "Index", "0")

    connect(BP_FPC, GRAPH, get_all_meta, "OutActors", array_get_meta, "TargetArray")
    connect(BP_FPC, GRAPH, cast_vaso, "AsVaso", get_distance, "self")
    connect(BP_FPC, GRAPH, array_get_meta, "Item", get_distance, "OtherActor")
    connect(BP_FPC, GRAPH, get_distance, "ReturnValue", compare_distance, "A")

    connect(BP_FPC, GRAPH, get_all_meta, "then", distance_branch, "execute")
    connect(BP_FPC, GRAPH, compare_distance, "ReturnValue", distance_branch, "Condition")

    connect(BP_FPC, GRAPH, distance_branch, "then", detach_finish, "execute")
    connect(BP_FPC, GRAPH, distance_branch, "else", detach_drop, "execute")

    connect(BP_FPC, GRAPH, cast_vaso, "AsVaso", detach_finish, "self")
    connect(BP_FPC, GRAPH, cast_vaso, "AsVaso", detach_drop, "self")

    connect(BP_FPC, GRAPH, array_get_meta, "Item", get_meta_location, "self")
    connect(BP_FPC, GRAPH, cast_vaso, "AsVaso", snap_to_destination, "self")
    connect(BP_FPC, GRAPH, get_meta_location, "ReturnValue", snap_to_destination, "NewLocation")

    connect(BP_FPC, GRAPH, detach_finish, "then", snap_to_destination, "execute")
    connect(BP_FPC, GRAPH, snap_to_destination, "then", set_transport_false_a, "execute")
    connect(BP_FPC, GRAPH, set_transport_false_a, "then", print_destination_ok, "execute")

    connect(BP_FPC, GRAPH, detach_drop, "then", set_sim_true, "execute")
    connect(BP_FPC, GRAPH, cast_vaso, "AsVaso", get_mesh, "self")
    connect(BP_FPC, GRAPH, get_mesh, "SM_ErlenmeyerFlask", set_sim_true, "self")
    connect(BP_FPC, GRAPH, get_mesh, "SM_ErlenmeyerFlask", set_gravity_true, "self")
    connect(BP_FPC, GRAPH, set_sim_true, "then", set_gravity_true, "execute")
    connect(BP_FPC, GRAPH, set_gravity_true, "then", set_transport_false_b, "execute")
    connect(BP_FPC, GRAPH, set_transport_false_b, "then", print_drop_ok, "execute")


def remove_old_vaso_offset_node() -> None:
    log("Eliminando AddActorLocalOffset obsoleto de VasoJuego...")
    delete_node_if_exists(BP_VASO, GRAPH, "53100CE244E71FF379D90386F5A44308")


def main() -> None:
    patch_player_variables_and_component()
    patch_glove_pickup_chain()
    patch_flask_interaction_chain()
    remove_old_vaso_offset_node()
    compile_and_save(BP_FPC)
    compile_and_save(BP_VASO)
    log("Fix del matraz caliente aplicado.")


main()
