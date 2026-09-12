import unreal

BP_FPC = "/Game/FirstPerson/Blueprints/BP_FirstPersonCharacter"


def ensure_variable(bp_path: str, name: str, var_type: str, default_value: str = "") -> None:
    if unreal.BlueprintService.variable_exists(bp_path, name):
        if default_value != "":
            unreal.BlueprintService.set_variable_default_value(bp_path, name, default_value)
        return
    if not unreal.BlueprintService.add_variable(bp_path, name, var_type, default_value):
        raise RuntimeError(f"No se pudo crear la variable {name}")


print("Preparando variables del jugador para el matraz caliente...")
ensure_variable(BP_FPC, "TieneGuantesTermicos", "bool", "false")
ensure_variable(BP_FPC, "bEstaSiendoTransportado", "bool", "false")
compile_result = unreal.BlueprintService.compile_blueprint(BP_FPC)
print(f"Compile FPC step1: {compile_result}")
asset = unreal.load_asset(BP_FPC)
unreal.EditorAssetLibrary.save_loaded_asset(asset, False)
print("Step1 listo.")
