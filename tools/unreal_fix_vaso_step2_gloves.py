import unreal

BP_FPC = "/Game/FirstPerson/Blueprints/BP_FirstPersonCharacter"
GRAPH = "EventGraph"


def get_pins(node_id: str):
    return unreal.BlueprintService.get_node_pins(BP_FPC, GRAPH, node_id)


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
    raise RuntimeError(f"No encontré pin '{needle}' en {node_id}")


def connect(src_node: str, src_pin: str, dst_node: str, dst_pin: str) -> None:
    actual_src = find_pin(src_node, src_pin, False)
    actual_dst = find_pin(dst_node, dst_pin, True)
    if not unreal.BlueprintService.connect_nodes(BP_FPC, GRAPH, src_node, actual_src, dst_node, actual_dst):
        raise RuntimeError(f"No se pudo conectar {src_node}:{actual_src} -> {dst_node}:{actual_dst}")


def safe_disconnect(node_id: str, needle: str, is_input=None) -> None:
    try:
        pin = find_pin(node_id, needle, is_input)
        unreal.BlueprintService.disconnect_pin(BP_FPC, GRAPH, node_id, pin)
    except Exception:
        pass


def set_pin(node_id: str, needle: str, value: str) -> None:
    actual_pin = find_pin(node_id, needle, True)
    if not unreal.BlueprintService.set_node_pin_value(BP_FPC, GRAPH, node_id, actual_pin, value):
        raise RuntimeError(f"No se pudo configurar {node_id}:{actual_pin}")


def add_set_var(var_name: str, x: float, y: float) -> str:
    node_id = unreal.BlueprintService.add_set_variable_node(BP_FPC, GRAPH, var_name, x, y)
    if not node_id:
        raise RuntimeError(f"No se pudo crear Set {var_name}")
    return node_id


print("Parcheando recogida de guantes en BP_FirstPersonCharacter...")
cast_gloves = "F7391FAD4B80C700A7870EB6888D8729"
print_gloves = "8F39CD80407CEAC04DCA53AD9D39B1BE"

set_gloves = add_set_var("TieneGuantesTermicos", 1500.0, 5000.0)
set_pin(set_gloves, "TieneGuantesTermicos", "true")
set_legacy_gloves = add_set_var("bTieneGuantesTermicos", 1740.0, 5000.0)
set_pin(set_legacy_gloves, "bTieneGuantesTermicos", "true")

safe_disconnect(cast_gloves, "then", False)
connect(cast_gloves, "then", set_gloves, "execute")
connect(set_gloves, "then", set_legacy_gloves, "execute")
connect(set_legacy_gloves, "then", print_gloves, "execute")

compile_result = unreal.BlueprintService.compile_blueprint(BP_FPC)
print(f"Compile FPC step2: {compile_result}")
asset = unreal.load_asset(BP_FPC)
unreal.EditorAssetLibrary.save_loaded_asset(asset, False)
print("Step2 listo.")
