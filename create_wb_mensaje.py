import unreal

# ============================================================
# WB_MensajePuerta — mensaje contextual al llegar a la puerta
# ============================================================
widget_path = "/Game/FirstPerson/Menus/WB_MensajePuerta"
font_bold = "/Game/Fab/Audios/Fuentes/CaviarDreams_Bold_Font.CaviarDreams_Bold_Font"
font_regular = "/Game/Fab/Audios/Fuentes/CaviarDreams_Font.CaviarDreams_Font"

# Crear el widget blueprint
factory = unreal.WidgetBlueprintFactory()
factory.set_editor_property("parent_class", unreal.UserWidget)
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
widget = asset_tools.create_asset("WB_MensajePuerta", "/Game/FirstPerson/Menus",
                                   unreal.WidgetBlueprint, factory)
print("Widget creado:", widget is not None)

# ---- Jerarquia ----
# CanvasPanel (root)
#   Img_Fondo        — panel oscuro de fondo
#   VBox_Content     — VerticalBox con todo el contenido
#     Txt_Titulo     — "LABORATORIO DE MICROBIOLOGIA Y BIOTECNOLOGIA"
#     Txt_Mensaje    — texto largo de contexto
#     Btn_Comenzar   — boton accion
#       Txt_Btn      — texto del boton

p = widget_path

# Root canvas
unreal.WidgetService.add_component(p, "CanvasPanel", "Root", "", True)

# Panel fondo oscuro (card centrada 900x420)
fondo_brush = (
    "(TintColor=(SpecifiedColor=(R=0.004,G=0.018,B=0.047,A=0.92)),"
    "DrawAs=RoundedBox,ImageType=FullColor,ImageSize=(X=2048.0,Y=2048.0),Margin=(),"
    "OutlineSettings=(CornerRadii=(X=8.0,Y=8.0,Z=8.0,W=8.0),"
    "Color=(SpecifiedColor=(R=0.0,G=0.706,B=0.847,A=0.35)),Width=1.5,bUseBrushTransparency=True),"
    "UVRegion=(Min=(X=0.0,Y=0.0),Max=(X=0.0,Y=0.0),bIsValid=False))"
)
unreal.WidgetService.add_component(p, "Image", "Img_Fondo", "Root", False)
unreal.WidgetService.set_property(p, "Img_Fondo", "Brush", fondo_brush)
unreal.WidgetService.set_property(p, "Img_Fondo", "Anchor Min X", "0.5")
unreal.WidgetService.set_property(p, "Img_Fondo", "Anchor Min Y", "0.5")
unreal.WidgetService.set_property(p, "Img_Fondo", "Anchor Max X", "0.5")
unreal.WidgetService.set_property(p, "Img_Fondo", "Anchor Max Y", "0.5")
unreal.WidgetService.set_property(p, "Img_Fondo", "Position X", "-450")
unreal.WidgetService.set_property(p, "Img_Fondo", "Position Y", "-220")
unreal.WidgetService.set_property(p, "Img_Fondo", "Size X", "900")
unreal.WidgetService.set_property(p, "Img_Fondo", "Size Y", "440")
unreal.WidgetService.set_property(p, "Img_Fondo", "ZOrder", "0")
print("Fondo OK")

# VerticalBox contenido (centrada)
unreal.WidgetService.add_component(p, "VerticalBox", "VBox_Content", "Root", False)
unreal.WidgetService.set_property(p, "VBox_Content", "Anchor Min X", "0.5")
unreal.WidgetService.set_property(p, "VBox_Content", "Anchor Min Y", "0.5")
unreal.WidgetService.set_property(p, "VBox_Content", "Anchor Max X", "0.5")
unreal.WidgetService.set_property(p, "VBox_Content", "Anchor Max Y", "0.5")
unreal.WidgetService.set_property(p, "VBox_Content", "Position X", "-400")
unreal.WidgetService.set_property(p, "VBox_Content", "Position Y", "-195")
unreal.WidgetService.set_property(p, "VBox_Content", "Size X", "800")
unreal.WidgetService.set_property(p, "VBox_Content", "Size Y", "390")
unreal.WidgetService.set_property(p, "VBox_Content", "ZOrder", "1")
print("VBox OK")

# Linea decorativa superior (cyan)
sep_brush = (
    "(TintColor=(SpecifiedColor=(R=0.0,G=0.706,B=0.847,A=0.7)),"
    "DrawAs=RoundedBox,ImageType=FullColor,ImageSize=(X=2048.0,Y=2048.0),Margin=(),"
    "OutlineSettings=(CornerRadii=(X=0.0,Y=0.0,Z=0.0,W=0.0),"
    "Color=(SpecifiedColor=(R=0.0,G=0.0,B=0.0,A=0.0)),Width=0.0,bUseBrushTransparency=True),"
    "UVRegion=(Min=(X=0.0,Y=0.0),Max=(X=0.0,Y=0.0),bIsValid=False))"
)
unreal.WidgetService.add_component(p, "Image", "Img_Sep", "VBox_Content", False)
unreal.WidgetService.set_property(p, "Img_Sep", "Brush", sep_brush)
unreal.WidgetService.set_property(p, "Img_Sep", "Size X", "Fill")
unreal.WidgetService.set_property(p, "Img_Sep", "Size Y", "Automatic")
print("Sep OK")

# Titulo del modulo
unreal.WidgetService.add_component(p, "TextBlock", "Txt_Titulo", "VBox_Content", False)
unreal.WidgetService.set_property(p, "Txt_Titulo", "Text", "MODULO 1 — INGRESO AL LABORATORIO")
unreal.WidgetService.set_property(p, "Txt_Titulo", "Font.Size", "18")
unreal.WidgetService.set_property(p, "Txt_Titulo", "Font.FontObject", font_bold)
unreal.WidgetService.set_property(p, "Txt_Titulo", "Font.TypefaceFontName", "Regular")
unreal.WidgetService.set_property(p, "Txt_Titulo", "ColorAndOpacity", "(SpecifiedColor=(R=0.0,G=0.706,B=0.847,A=1.0))")
unreal.WidgetService.set_property(p, "Txt_Titulo", "Justification", "Center")
print("Titulo OK")

# Mensaje principal
msg = ("Usted realizara una practica en el laboratorio.\n"
       "Antes de ingresar, debe cumplir las normas de seguridad,\n"
       "seleccionar el EPP adecuado, reconocer riesgos\n"
       "y responder correctamente a situaciones de peligro.")
unreal.WidgetService.add_component(p, "TextBlock", "Txt_Mensaje", "VBox_Content", False)
unreal.WidgetService.set_property(p, "Txt_Mensaje", "Text", msg)
unreal.WidgetService.set_property(p, "Txt_Mensaje", "Font.Size", "16")
unreal.WidgetService.set_property(p, "Txt_Mensaje", "Font.FontObject", font_regular)
unreal.WidgetService.set_property(p, "Txt_Mensaje", "Font.TypefaceFontName", "Regular")
unreal.WidgetService.set_property(p, "Txt_Mensaje", "ColorAndOpacity", "(SpecifiedColor=(R=0.88,G=0.88,B=0.88,A=1.0))")
unreal.WidgetService.set_property(p, "Txt_Mensaje", "Justification", "Center")
unreal.WidgetService.set_property(p, "Txt_Mensaje", "AutoWrapText", "true")
print("Mensaje OK")

# Boton Comenzar
btn_style = (
    "(Normal=(TintColor=(SpecifiedColor=(R=0.0,G=0.572,B=0.769,A=1.0)),"
    "DrawAs=RoundedBox,ImageType=FullColor,ImageSize=(X=2048.0,Y=2048.0),Margin=(),"
    "OutlineSettings=(CornerRadii=(X=4.0,Y=4.0,Z=4.0,W=4.0),"
    "Color=(SpecifiedColor=(R=0.0,G=0.706,B=0.847,A=0.5)),Width=1.0,bUseBrushTransparency=True),"
    "UVRegion=(Min=(X=0.0,Y=0.0),Max=(X=0.0,Y=0.0),bIsValid=False)),"
    "Hovered=(TintColor=(SpecifiedColor=(R=0.0,G=0.706,B=0.847,A=1.0)),"
    "DrawAs=RoundedBox,ImageSize=(X=2048.0,Y=2048.0),Margin=(),"
    "OutlineSettings=(CornerRadii=(X=4.0,Y=4.0,Z=4.0,W=4.0),"
    "Color=(SpecifiedColor=(R=0.0,G=0.847,B=1.0,A=1.0)),Width=1.5,bUseBrushTransparency=True),"
    "UVRegion=(Min=(X=0.0,Y=0.0),Max=(X=0.0,Y=0.0),bIsValid=False)),"
    "Pressed=(TintColor=(SpecifiedColor=(R=0.0,G=0.4,B=0.55,A=1.0)),"
    "DrawAs=RoundedBox,ImageSize=(X=32.0,Y=32.0),Margin=(),"
    "OutlineSettings=(CornerRadii=(X=4.0,Y=4.0,Z=4.0,W=4.0),"
    "Color=(SpecifiedColor=(R=0.0,G=0.5,B=0.7,A=1.0)),Width=1.0,bUseBrushTransparency=True),"
    "UVRegion=(Min=(X=0.0,Y=0.0),Max=(X=0.0,Y=0.0),bIsValid=False)),"
    "Disabled=(TintColor=(SpecifiedColor=(R=0.3,G=0.3,B=0.3,A=1.0)),"
    "ImageSize=(X=0.0,Y=0.0),Margin=(),"
    "OutlineSettings=(CornerRadii=(X=0.0,Y=0.0,Z=0.0,W=0.0),"
    "Color=(SpecifiedColor=(R=0.0,G=0.0,B=0.0,A=0.0)),RoundingType=HalfHeightRadius),"
    "UVRegion=(Min=(X=0.0,Y=0.0),Max=(X=0.0,Y=0.0),bIsValid=False)),"
    "NormalForeground=(SpecifiedColor=(R=1.0,G=1.0,B=1.0,A=1.0)),"
    "HoveredForeground=(SpecifiedColor=(R=1.0,G=1.0,B=1.0,A=1.0)),"
    "PressedForeground=(SpecifiedColor=(R=1.0,G=1.0,B=1.0,A=1.0)),"
    "DisabledForeground=(SpecifiedColor=(R=0.5,G=0.5,B=0.5,A=1.0)),"
    "NormalPadding=(Left=12.0,Top=14.0,Right=12.0,Bottom=14.0),"
    "PressedPadding=(Left=12.0,Top=15.0,Right=12.0,Bottom=13.0),"
    "PressedSlateSound=(),ClickedSlateSound=(),HoveredSlateSound=())"
)
unreal.WidgetService.add_component(p, "Button", "Btn_Comenzar", "VBox_Content", False)
unreal.WidgetService.set_property(p, "Btn_Comenzar", "WidgetStyle", btn_style)
print("Btn_Comenzar OK")

unreal.WidgetService.add_component(p, "TextBlock", "Txt_Btn", "Btn_Comenzar", False)
unreal.WidgetService.set_property(p, "Txt_Btn", "Text", "COMENZAR  MODULO 1")
unreal.WidgetService.set_property(p, "Txt_Btn", "Font.Size", "18")
unreal.WidgetService.set_property(p, "Txt_Btn", "Font.FontObject", font_bold)
unreal.WidgetService.set_property(p, "Txt_Btn", "Font.TypefaceFontName", "Regular")
unreal.WidgetService.set_property(p, "Txt_Btn", "ColorAndOpacity", "(SpecifiedColor=(R=1.0,G=1.0,B=1.0,A=1.0))")
unreal.WidgetService.set_property(p, "Txt_Btn", "Justification", "Center")
print("Txt_Btn OK")

# Hacer Btn_Comenzar variable para poder bindear en BP
unreal.WidgetService.set_component_as_variable(p, "Btn_Comenzar", True)
unreal.WidgetService.set_component_as_variable(p, "Txt_Mensaje", True)

unreal.EditorAssetLibrary.save_asset(p)
print("WB_MensajePuerta GUARDADO OK")
