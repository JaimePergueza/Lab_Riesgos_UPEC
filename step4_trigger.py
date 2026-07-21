import unreal

# ============================================================
# BP_TriggerPuerta — trigger que muestra WB_MensajePuerta
# ============================================================
bp_path = "/Game/FirstPerson/Blueprints/BP_TriggerPuerta"

if not unreal.EditorAssetLibrary.does_asset_exist(bp_path):
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    tools.create_asset("BP_TriggerPuerta", "/Game/FirstPerson/Blueprints", unreal.Blueprint, factory)
    print("BP_TriggerPuerta creado")
else:
    print("BP_TriggerPuerta ya existe")

# Componentes
unreal.BlueprintService.add_component(bp_path, "SceneComponent", "Root")
unreal.BlueprintService.add_component(bp_path, "BoxComponent", "TriggerBox", "Root")
print("Componentes OK")

# Configurar box collision
unreal.BlueprintService.set_component_property(bp_path, "TriggerBox", "BoxExtent", "(X=150.0,Y=150.0,Z=150.0)")
unreal.BlueprintService.set_component_property(bp_path, "TriggerBox", "CollisionProfileName", "OverlapAllDynamic")
unreal.BlueprintService.set_component_property(bp_path, "TriggerBox", "bGenerateOverlapEvents", "true")
print("Box config OK")

# Variable para widget ref
unreal.BlueprintService.add_variable(bp_path, "MensajeRef", "WB_MensajePuerta")
print("Variable MensajeRef OK")

unreal.BlueprintService.compile_blueprint(bp_path)
unreal.EditorAssetLibrary.save_asset(bp_path)
print("BP_TriggerPuerta guardado")
