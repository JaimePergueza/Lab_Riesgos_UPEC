import unreal

BP_VASO = "/Game/Fab/BP_ActoresJuego/VasoJuego"
GRAPH = "EventGraph"
OLD_OFFSET_NODE = "53100CE244E71FF379D90386F5A44308"
INTERACT_NODE = "A01A73CA44BCCEDD63258D8CBA4B47B1"
GLOVE_BRANCH = "670AE47943E09DCDB03E00BEB9F2C809"
GLOVE_WARNING_PRINT = "A0F835574401766C578F09AB0C1D6AFE"
OLD_GLOVE_GET = "A80F98274BB7FA050ECE3898BE977182"
OLD_GLOVE_IS_VALID = "252E23154A357ABEF591B7ACAFC3DB92"
OLD_GLOVE_NOT = "E2EC9D7645D5851F206D2AA44A69347E"
PREV_GET_PLAYER = "067F3A644898F38CBABC9999A7ACF8FC"
PREV_CAST_PLAYER = "786967644C729246731904910149345F"
PREV_GET_PLAYER_GLOVES = "03B3D5C844E91F245CB7FFBEEEB71863"


def get_nodes():
    return {node.node_id: node for node in unreal.BlueprintService.get_nodes_in_graph(BP_VASO, GRAPH)}


def get_pins(node_id: str):
    return unreal.BlueprintService.get_node_pins(BP_VASO, GRAPH, node_id)


def find_pin(node_id: str, needle: str, is_input=None) -> str:
    needle_lower = needle.lower()
    for pin in get_pins(node_id):
        if is_input is not None and pin.is_input != is_input:
            continue
        if pin.pin_name.lower() == needle_lower:
            return pin.pin_name
    for pin in get_pins(node_id):
        if is_input is not None and pin.is_input != is_input:
            continue
        if needle_lower in pin.pin_name.lower():
            return pin.pin_name
    available = [pin.pin_name for pin in get_pins(node_id)]
    raise RuntimeError(f"No encontré pin '{needle}' en {node_id}. Disponibles: {available}")


def connect(src_node: str, src_pin: str, dst_node: str, dst_pin: str) -> None:
    actual_src = find_pin(src_node, src_pin, False)
    actual_dst = find_pin(dst_node, dst_pin, True)
    if not unreal.BlueprintService.connect_nodes(BP_VASO, GRAPH, src_node, actual_src, dst_node, actual_dst):
        raise RuntimeError(f"No se pudo conectar {src_node}:{actual_src} -> {dst_node}:{actual_dst}")


def safe_disconnect(node_id: str, needle: str, is_input=None) -> None:
    try:
        pin = find_pin(node_id, needle, is_input)
        unreal.BlueprintService.disconnect_pin(BP_VASO, GRAPH, node_id, pin)
    except Exception:
        pass


def delete_node_if_exists(node_id: str) -> None:
    if node_id in get_nodes():
        unreal.BlueprintService.delete_node(BP_VASO, GRAPH, node_id)


print("Actualizando validación de guantes en VasoJuego...")
delete_node_if_exists(PREV_GET_PLAYER)
delete_node_if_exists(PREV_CAST_PLAYER)
delete_node_if_exists(PREV_GET_PLAYER_GLOVES)
get_player = unreal.BlueprintService.add_function_call_node(BP_VASO, GRAPH, "GameplayStatics", "GetPlayerCharacter", 560.0, 2750.0)
cast_player = unreal.BlueprintService.add_cast_node(BP_VASO, GRAPH, "BP_FirstPersonCharacter_C", 860.0, 2700.0)
get_player_gloves = unreal.BlueprintService.add_member_get_node(
    BP_VASO,
    GRAPH,
    "BP_FirstPersonCharacter_C",
    "TieneGuantesTermicos",
    1180.0,
    2620.0,
)

if not get_player or not cast_player or not get_player_gloves:
    raise RuntimeError("No se pudieron crear los nodos nuevos de validación de guantes")

safe_disconnect(GLOVE_BRANCH, "execute", True)
safe_disconnect(GLOVE_BRANCH, "Condition", True)

connect(get_player, "ReturnValue", cast_player, "Object")
connect(cast_player, "As", get_player_gloves, "self")
connect(cast_player, "then", GLOVE_BRANCH, "execute")
connect(get_player_gloves, "TieneGuantesTermicos", GLOVE_BRANCH, "Condition")
connect(cast_player, "CastFailed", GLOVE_WARNING_PRINT, "execute")

delete_node_if_exists(OLD_GLOVE_GET)
delete_node_if_exists(OLD_GLOVE_IS_VALID)
delete_node_if_exists(OLD_GLOVE_NOT)

if OLD_OFFSET_NODE in get_nodes():
    print("Eliminando AddActorLocalOffset obsoleto de VasoJuego...")
    unreal.BlueprintService.delete_node(BP_VASO, GRAPH, OLD_OFFSET_NODE)
else:
    print("El nodo AddActorLocalOffset ya no existe en VasoJuego.")

compile_result = unreal.BlueprintService.compile_blueprint(BP_VASO)
print(f"Compile VasoJuego step4: {compile_result}")
asset = unreal.load_asset(BP_VASO)
unreal.EditorAssetLibrary.save_loaded_asset(asset, False)
print("Step4 listo.")
