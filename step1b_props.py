import unreal

p = "/Game/FirstPerson/Menus/WB_MensajePuerta"
fb = "/Game/Fab/Audios/Fuentes/CaviarDreams_Bold_Font.CaviarDreams_Bold_Font"
fr = "/Game/Fab/Audios/Fuentes/CaviarDreams_Font.CaviarDreams_Font"

# Titulo
unreal.WidgetService.set_property(p, "Txt_Titulo", "Text", "MODULO 1 - INGRESO AL LABORATORIO")
unreal.WidgetService.set_property(p, "Txt_Titulo", "Font.Size", "22")
unreal.WidgetService.set_property(p, "Txt_Titulo", "Font.FontObject", fb)
unreal.WidgetService.set_property(p, "Txt_Titulo", "Font.TypefaceFontName", "Regular")
unreal.WidgetService.set_property(p, "Txt_Titulo", "ColorAndOpacity", "(SpecifiedColor=(R=0.0,G=0.706,B=0.847,A=1.0))")
unreal.WidgetService.set_property(p, "Txt_Titulo", "Justification", "Center")
print("Titulo OK")

# Mensaje
msg = "Usted realizara una practica en el laboratorio. Antes de ingresar, debe cumplir las normas de seguridad, seleccionar el EPP adecuado, reconocer riesgos y responder correctamente a situaciones de peligro."
unreal.WidgetService.set_property(p, "Txt_Mensaje", "Text", msg)
unreal.WidgetService.set_property(p, "Txt_Mensaje", "Font.Size", "16")
unreal.WidgetService.set_property(p, "Txt_Mensaje", "Font.FontObject", fr)
unreal.WidgetService.set_property(p, "Txt_Mensaje", "Font.TypefaceFontName", "Regular")
unreal.WidgetService.set_property(p, "Txt_Mensaje", "ColorAndOpacity", "(SpecifiedColor=(R=0.88,G=0.88,B=0.88,A=1.0))")
unreal.WidgetService.set_property(p, "Txt_Mensaje", "Justification", "Center")
unreal.WidgetService.set_property(p, "Txt_Mensaje", "AutoWrapText", "true")
print("Mensaje OK")

# Boton Comenzar — estilo cyan
btn = (
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
    "NormalPadding=(Left=40.0,Top=14.0,Right=40.0,Bottom=14.0),"
    "PressedPadding=(Left=40.0,Top=15.0,Right=40.0,Bottom=13.0),"
    "PressedSlateSound=(),ClickedSlateSound=(),HoveredSlateSound=())"
)
unreal.WidgetService.set_property(p, "Btn_Comenzar", "WidgetStyle", btn)

# Texto del boton
unreal.WidgetService.set_property(p, "Txt_Btn", "Text", "COMENZAR")
unreal.WidgetService.set_property(p, "Txt_Btn", "Font.Size", "20")
unreal.WidgetService.set_property(p, "Txt_Btn", "Font.FontObject", fb)
unreal.WidgetService.set_property(p, "Txt_Btn", "Font.TypefaceFontName", "Regular")
unreal.WidgetService.set_property(p, "Txt_Btn", "ColorAndOpacity", "(SpecifiedColor=(R=1.0,G=1.0,B=1.0,A=1.0))")
unreal.WidgetService.set_property(p, "Txt_Btn", "Justification", "Center")
print("Boton OK")

# VBox posicion — centrada
unreal.WidgetService.set_property(p, "VBox", "Position X", "460")
unreal.WidgetService.set_property(p, "VBox", "Position Y", "280")
unreal.WidgetService.set_property(p, "VBox", "Size X", "1000")
unreal.WidgetService.set_property(p, "VBox", "Size Y", "500")

unreal.EditorAssetLibrary.save_asset(p)
print("WB_MensajePuerta COMPLETO")
