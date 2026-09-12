import unreal

BP_FPC = "/Game/FirstPerson/Blueprints/BP_FirstPersonCharacter"
GRAPH = "EventGraph"


def get_nodes():
    return {node.node_id: node for node in unreal.BlueprintService.get_nodes_in_graph(BP_FPC, GRAPH)}


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
    available = [pin.pin_name for pin in get_pins(node_id)]
    raise RuntimeError(f"No encontré pin '{needle}' en {node_id}. Disponibles: {available}")


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


def delete_node_if_exists(node_id: str) -> None:
    if node_id in get_nodes():
        unreal.BlueprintService.delete_node(BP_FPC, GRAPH, node_id)


def set_pin(node_id: str, needle: str, value: str) -> None:
    actual_pin = find_pin(node_id, needle, True)
    if not unreal.BlueprintService.set_node_pin_value(BP_FPC, GRAPH, node_id, actual_pin, value):
        raise RuntimeError(f"No se pudo configurar {node_id}:{actual_pin} = {value}")


def add_get_var(var_name: str, x: float, y: float) -> str:
    node_id = unreal.BlueprintService.add_get_variable_node(BP_FPC, GRAPH, var_name, x, y)
    if not node_id:
        raise RuntimeError(f"No se pudo crear Get {var_name}")
    return node_id


def add_set_var(var_name: str, x: float, y: float) -> str:
    node_id = unreal.BlueprintService.add_set_variable_node(BP_FPC, GRAPH, var_name, x, y)
    if not node_id:
        raise RuntimeError(f"No se pudo crear Set {var_name}")
    return node_id


def add_branch(x: float, y: float) -> str:
    node_id = unreal.BlueprintService.add_branch_node(BP_FPC, GRAPH, x, y)
    if not node_id:
        raise RuntimeError("No se pudo crear Branch")
    return node_id


def add_print(text: str, x: float, y: float) -> str:
    node_id = unreal.BlueprintService.add_print_string_node(BP_FPC, GRAPH, x, y)
    if not node_id:
        raise RuntimeError("No se pudo crear PrintString")
    set_pin(node_id, "InString", text)
    return node_id


def add_call(owner_class: str, function_name: str, x: float, y: float) -> str:
    node_id = unreal.BlueprintService.add_function_call_node(BP_FPC, GRAPH, owner_class, function_name, x, y)
    if not node_id:
        raise RuntimeError(f"No se pudo crear {owner_class}.{function_name}")
    return node_id


def add_compare(kind: str, value_type: str, x: float, y: float) -> str:
    node_id = unreal.BlueprintService.add_comparison_node(BP_FPC, GRAPH, kind, value_type, x, y)
    if not node_id:
        raise RuntimeError(f"No se pudo crear comparación {kind}")
    return node_id


print("Parcheando rama del matraz caliente en BP_FirstPersonCharacter...")

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

for node_id in [
    "7AF849914B01BA49AE399B89E10DBB34",
    "57E44E204C419EC0F0E8FAAC53D4E6A9",
    "9BCA702E45BC8A0F6967BEA241EC5CF0",
    "5C99443941A9FD8C3F876DAAC3F33BCF",
    "123672B9464FB05F3816ACA5E597C865",
    "6104A98047508C89651E47A14AAEC5F4",
    "81C5F76442471EB730C1A3B3043C1301",
    "4C6A5C304BBDB77CDE689E9C53999BD0",
    "A7BEF60643490EAD21A80084C9C23018",
    "A6ECD91B43F511F87D0BC7BC730FAC80",
    "189E7C684AD36A2D7B1D6C86609D7610",
    "71FF4E254B3DFC5D8BA3A7B7EAF0DCCC",
    "0CFF435C44FC3BABCEDF7C80E92EF8B4",
    "2CC017B741D4FB8FC347499296B6F478",
    "480284634E0D7810EA82F1AB31252143",
    "7364870A4E676F1E9301B8868935B2CA",
    "327982214CD4107FEEC979AD9A5769E1",
    "D519EA1F4B4D35ACA389CC98E13F0593",
    "EF7F637E467E52B3CF2F1781CA84C0E7",
    "6A963D7641D04D4566C98E9806469B0C",
    "350A8DF34FDCF26C61F1C494CC0C1F59",
    "D347675B4C5E690719FC42A7CF215534",
    "891A15964233EF9FBDECCA8D6E5F68F4",
    "829449EB4BDD02B747DCD6864185178F",
    "D4D9CC674F569C10F3A4F2B0470C3A53",
    "80E68B8C449853FD3900BE80488A84DC",
    "8C05041A40E821C1E7CAC1AA6262059D",
    "5019A34B46E4CFA1D1A99E8C3128DC9D",
    "838A3BB34AE71C1911ECAAB4CB727BAD",
    "7A4BF4364058CD413A4873AC71B5AA90",
    "FF1A2954464873F480FD2EA8512256C7",
]:
    delete_node_if_exists(node_id)

get_transport = add_get_var("bEstaSiendoTransportado", 1850.0, 5660.0)
transport_branch = add_branch(2100.0, 5800.0)
get_gloves = add_get_var("TieneGuantesTermicos", 3000.0, 5660.0)
get_carry_point = add_get_var("VasoCarryPoint", 4700.0, 5450.0)
set_transport_true = add_set_var("bEstaSiendoTransportado", 5350.0, 5550.0)
set_pin(set_transport_true, "bEstaSiendoTransportado", "true")

get_vaso_location = add_call("Actor", "GetActorLocation", 2720.0, 6230.0)
get_distance = add_call("KismetMathLibrary", "Vector_Distance", 3060.0, 6230.0)
compare_distance = add_compare("LessEqual", "Float", 3360.0, 6240.0)
set_pin(compare_distance, "B", "180.0")
distance_branch = add_branch(3600.0, 6100.0)
detach_drop = add_call("Actor", "DetachFromActor", 3900.0, 5950.0)
detach_finish = add_call("Actor", "DetachFromActor", 3900.0, 6400.0)
set_sim_true = add_call("PrimitiveComponent", "SetSimulatePhysics", 4220.0, 6400.0)
set_pin(set_sim_true, "bSimulate", "true")
set_gravity_true = add_call("PrimitiveComponent", "SetEnableGravity", 4500.0, 6400.0)
set_pin(set_gravity_true, "bGravityEnabled", "true")
snap_to_destination = add_call("Actor", "K2_SetActorLocation", 4500.0, 5950.0)
set_pin(snap_to_destination, "bSweep", "false")
set_pin(snap_to_destination, "bTeleport", "true")
set_pin(snap_to_destination, "NewLocation", "(X=2233.0,Y=-930.0,Z=402.0)")
set_transport_false_a = add_set_var("bEstaSiendoTransportado", 4840.0, 5950.0)
set_pin(set_transport_false_a, "bEstaSiendoTransportado", "false")
set_transport_false_b = add_set_var("bEstaSiendoTransportado", 4840.0, 6400.0)
set_pin(set_transport_false_b, "bEstaSiendoTransportado", "false")
print_destination_ok = add_print("Muestra colocada correctamente en el punto destino", 5150.0, 5950.0)
print_drop_ok = add_print("Matraz soltado", 5150.0, 6400.0)

set_pin(print_gloves_warning, "InString", "Debe colocarse los guantes térmicos")
set_pin(print_heat_warning, "InString", "Debe apagar la estufa antes de manipular el matraz")
set_pin(print_success, "InString", "Toma siempre el matraz por el cuello y la base")

for node_id, pin_name, is_input in [
    (cast_vaso, "then", False),
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
    safe_disconnect(node_id, pin_name, is_input)

connect(cast_vaso, "then", transport_branch, "execute")
connect(get_transport, "bEstaSiendoTransportado", transport_branch, "Condition")

connect(transport_branch, "else", glove_branch, "execute")
connect(get_gloves, "TieneGuantesTermicos", glove_branch, "Condition")
connect(glove_branch, "else", print_gloves_warning, "execute")
connect(glove_branch, "then", get_heat_source, "execute")
connect(get_heat_source, "ReturnValue", get_heat_on, "self")
connect(get_heat_source, "then", heat_branch, "execute")
connect(get_heat_on, "bEncendida", not_heat_on, "A")
connect(not_heat_on, "ReturnValue", heat_branch, "Condition")
connect(heat_branch, "then", print_success, "execute")
connect(heat_branch, "else", print_heat_warning, "execute")
connect(print_success, "then", set_sim_false, "execute")
connect(set_gravity_false, "then", attach_to_component, "execute")
connect(get_carry_point, "VasoCarryPoint", attach_to_component, "Parent")
connect(attach_to_component, "then", set_transport_true, "execute")

set_pin(set_sim_false, "bSimulate", "false")
set_pin(set_gravity_false, "bGravityEnabled", "false")
set_pin(attach_to_component, "LocationRule", "SnapToTarget")
set_pin(attach_to_component, "RotationRule", "SnapToTarget")
set_pin(attach_to_component, "ScaleRule", "KeepWorld")
set_pin(attach_to_component, "bWeldSimulatedBodies", "false")

connect(cast_vaso, "AsVaso", get_vaso_location, "self")
connect(get_vaso_location, "ReturnValue", get_distance, "V1")
set_pin(get_distance, "V2", "(X=2233.0,Y=-930.0,Z=402.0)")
connect(get_distance, "ReturnValue", compare_distance, "A")
connect(transport_branch, "then", distance_branch, "execute")
connect(compare_distance, "ReturnValue", distance_branch, "Condition")
connect(distance_branch, "then", detach_finish, "execute")
connect(distance_branch, "else", detach_drop, "execute")
connect(cast_vaso, "AsVaso", detach_finish, "self")
connect(cast_vaso, "AsVaso", detach_drop, "self")
connect(cast_vaso, "AsVaso", snap_to_destination, "self")
connect(detach_finish, "then", snap_to_destination, "execute")
connect(snap_to_destination, "then", set_transport_false_a, "execute")
connect(set_transport_false_a, "then", print_destination_ok, "execute")
connect(cast_vaso, "AsVaso", get_mesh, "self")
connect(get_mesh, "SM_ErlenmeyerFlask", set_sim_true, "self")
connect(get_mesh, "SM_ErlenmeyerFlask", set_gravity_true, "self")
connect(detach_drop, "then", set_sim_true, "execute")
connect(set_sim_true, "then", set_gravity_true, "execute")
connect(set_gravity_true, "then", set_transport_false_b, "execute")
connect(set_transport_false_b, "then", print_drop_ok, "execute")

compile_result = unreal.BlueprintService.compile_blueprint(BP_FPC)
print(f"Compile FPC step3: {compile_result}")
asset = unreal.load_asset(BP_FPC)
unreal.EditorAssetLibrary.save_loaded_asset(asset, False)
print("Step3 listo.")
