import unreal

bp_path = "/Game/FirstPerson/Blueprints/BP_Baliza"

# Obtener el CDO para modificar componentes
bp = unreal.load_asset(bp_path)
gen_class = bp.generated_class()

# Modificar Luz_Haz (SpotLight) via Blueprint defaults
# Usar BlueprintService para set component property
unreal.BlueprintService.set_component_property(bp_path, "Luz_Haz", "Intensity", "8000.0")
unreal.BlueprintService.set_component_property(bp_path, "Luz_Haz", "LightColor", "(R=0,G=180,B=216,A=255)")
unreal.BlueprintService.set_component_property(bp_path, "Luz_Haz", "AttenuationRadius", "3000.0")
unreal.BlueprintService.set_component_property(bp_path, "Luz_Haz", "InnerConeAngle", "3.0")
unreal.BlueprintService.set_component_property(bp_path, "Luz_Haz", "OuterConeAngle", "8.0")
# Rotar hacia arriba (pitch = -90)
unreal.BlueprintService.set_component_property(bp_path, "Luz_Haz", "RelativeRotation", "(Pitch=-90.0,Yaw=0.0,Roll=0.0)")
print("Luz_Haz configurada")

# Modificar Luz_Base (PointLight)
unreal.BlueprintService.set_component_property(bp_path, "Luz_Base", "Intensity", "1200.0")
unreal.BlueprintService.set_component_property(bp_path, "Luz_Base", "LightColor", "(R=0,G=180,B=216,A=255)")
unreal.BlueprintService.set_component_property(bp_path, "Luz_Base", "AttenuationRadius", "500.0")
print("Luz_Base configurada")

# Variable para controlar activacion
unreal.BlueprintService.add_variable(bp_path, "bActiva", "bool")
unreal.BlueprintService.set_variable_default(bp_path, "bActiva", "true")
print("Variable bActiva agregada")

unreal.BlueprintService.compile_blueprint(bp_path)
unreal.EditorAssetLibrary.save_asset(bp_path)
print("BP_Baliza luces OK")
