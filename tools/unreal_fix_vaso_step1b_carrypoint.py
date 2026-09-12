import unreal

BP_FPC = "/Game/FirstPerson/Blueprints/BP_FirstPersonCharacter"

print("Creando o corrigiendo VasoCarryPoint...")
if not unreal.BlueprintService.component_exists(BP_FPC, "VasoCarryPoint"):
    if not unreal.BlueprintService.add_component(BP_FPC, "SceneComponent", "VasoCarryPoint", ""):
        raise RuntimeError("No se pudo crear VasoCarryPoint sin padre")

if not unreal.BlueprintService.reparent_component(BP_FPC, "VasoCarryPoint", "FirstPersonCamera"):
    raise RuntimeError("No se pudo reparentar VasoCarryPoint a FirstPersonCamera")

unreal.BlueprintService.set_component_property(BP_FPC, "VasoCarryPoint", "RelativeLocation", "(X=35.0,Y=18.0,Z=-10.0)")
unreal.BlueprintService.set_component_property(BP_FPC, "VasoCarryPoint", "RelativeRotation", "(Pitch=0.0,Yaw=0.0,Roll=0.0)")
compile_result = unreal.BlueprintService.compile_blueprint(BP_FPC)
print(f"Compile FPC step1b: {compile_result}")
asset = unreal.load_asset(BP_FPC)
unreal.EditorAssetLibrary.save_loaded_asset(asset, False)
print("Step1b listo.")
