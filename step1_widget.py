import unreal

p = "/Game/FirstPerson/Menus/WB_MensajePuerta"

# Verificar si ya existe
if unreal.EditorAssetLibrary.does_asset_exist(p):
    print("WB_MensajePuerta ya existe, saltando creacion")
else:
    factory = unreal.WidgetBlueprintFactory()
    factory.set_editor_property("parent_class", unreal.UserWidget)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    tools.create_asset("WB_MensajePuerta", "/Game/FirstPerson/Menus", unreal.WidgetBlueprint, factory)
    print("WB_MensajePuerta creado")

# Estructura basica
unreal.WidgetService.add_component(p, "CanvasPanel", "Root", "", True)
unreal.WidgetService.add_component(p, "VerticalBox", "VBox", "Root", False)
unreal.WidgetService.add_component(p, "TextBlock", "Txt_Titulo", "VBox", False)
unreal.WidgetService.add_component(p, "TextBlock", "Txt_Mensaje", "VBox", False)
unreal.WidgetService.add_component(p, "Button", "Btn_Comenzar", "VBox", False)
unreal.WidgetService.add_component(p, "TextBlock", "Txt_Btn", "Btn_Comenzar", False)
print("Estructura OK")

unreal.EditorAssetLibrary.save_asset(p)
print("Guardado paso 1")
