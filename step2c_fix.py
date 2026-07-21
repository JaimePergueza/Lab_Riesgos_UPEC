import unreal

bp = "/Game/FirstPerson/Blueprints/BP_Baliza"

# Configurar SpotLight Luz_Haz
unreal.BlueprintService.set_component_property(bp, "Luz_Haz", "Intensity", "8000.0")
unreal.BlueprintService.set_component_property(bp, "Luz_Haz", "LightColor", "(R=0,G=180,B=216,A=255)")
unreal.BlueprintService.set_component_property(bp, "Luz_Haz", "AttenuationRadius", "3000.0")
unreal.BlueprintService.set_component_property(bp, "Luz_Haz", "InnerConeAngle", "3.0")
unreal.BlueprintService.set_component_property(bp, "Luz_Haz", "OuterConeAngle", "8.0")
unreal.BlueprintService.set_component_property(bp, "Luz_Haz", "RelativeRotation", "(Pitch=-90.0,Yaw=0.0,Roll=0.0)")
print("SpotLight config OK")

# Configurar PointLight Luz_Base
unreal.BlueprintService.set_component_property(bp, "Luz_Base", "Intensity", "1200.0")
unreal.BlueprintService.set_component_property(bp, "Luz_Base", "LightColor", "(R=0,G=180,B=216,A=255)")
unreal.BlueprintService.set_component_property(bp, "Luz_Base", "AttenuationRadius", "500.0")
print("PointLight config OK")

# Variable default
unreal.BlueprintService.set_variable_default_value(bp, "bActiva", "true")
print("bActiva default = true")

unreal.BlueprintService.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_asset(bp)
print("BP_Baliza guardado")
