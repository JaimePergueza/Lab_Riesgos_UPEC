import unreal

bp_path = "/Game/FirstPerson/Blueprints/BP_Baliza"

# Crear Blueprint Actor
if unreal.EditorAssetLibrary.does_asset_exist(bp_path):
    print("BP_Baliza ya existe")
else:
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    tools.create_asset("BP_Baliza", "/Game/FirstPerson/Blueprints", unreal.Blueprint, factory)
    print("BP_Baliza creado")

# Agregar componentes
# SceneComponent como root
unreal.BlueprintService.add_component(bp_path, "SceneComponent", "Root")
print("Root OK")

# SpotLight apuntando hacia arriba — haz vertical
unreal.BlueprintService.add_component(bp_path, "SpotLightComponent", "Luz_Haz", "Root")
print("Luz_Haz agregada")

# PointLight en la base — glow
unreal.BlueprintService.add_component(bp_path, "PointLightComponent", "Luz_Base", "Root")
print("Luz_Base agregada")

# Compilar y guardar
unreal.BlueprintService.compile_blueprint(bp_path)
unreal.EditorAssetLibrary.save_asset(bp_path)
print("BP_Baliza compilado y guardado")
