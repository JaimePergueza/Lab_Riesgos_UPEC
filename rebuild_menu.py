import unreal

path = "/Game/FirstPerson/Menus/WP_MenuPrincipal"
logo_path = "/Game/FirstPerson/FOTOS/logo_upec.logo_upec"
font_bold = "/Game/Fab/Audios/Fuentes/CaviarDreams_Bold_Font.CaviarDreams_Bold_Font"

def solid_brush(r, g, b, a):
    return (
        f"(TintColor=(SpecifiedColor=(R={r},G={g},B={b},A={a})),"
        "DrawAs=RoundedBox,ImageType=FullColor,ImageSize=(X=2048.0,Y=2048.0),Margin=(),"
        "OutlineSettings=(CornerRadii=(X=0.0,Y=0.0,Z=0.0,W=0.0),"
        "Color=(SpecifiedColor=(R=0.0,G=0.0,B=0.0,A=0.0)),Width=0.0,bUseBrushTransparency=True),"
        "UVRegion=(Min=(X=0.0,Y=0.0),Max=(X=0.0,Y=0.0),bIsValid=False))"
    )

def tex_brush(obj_path, w=256, h=256):
    return (
        "(TintColor=(SpecifiedColor=(R=1.0,G=1.0,B=1.0,A=1.0)),"
        "DrawAs=Image,ImageType=FullColor,"
        f"ImageSize=(X={w}.0,Y={h}.0),Margin=(),"
        f"ResourceObject=\"/Script/Engine.Texture2D'{obj_path}'\","
        "OutlineSettings=(CornerRadii=(X=0.0,Y=0.0,Z=0.0,W=0.0),"
        "Color=(SpecifiedColor=(R=0.0,G=0.0,B=0.0,A=0.0)),RoundingType=HalfHeightRadius),"
        "UVRegion=(Min=(X=0.0,Y=0.0),Max=(X=0.0,Y=0.0),bIsValid=False))"
    )

def place(name, x, y, w, h, z):
    unreal.WidgetService.set_property(path, name, "Position X", str(x))
    unreal.WidgetService.set_property(path, name, "Position Y", str(y))
    unreal.WidgetService.set_property(path, name, "Size X", str(w))
    unreal.WidgetService.set_property(path, name, "Size Y", str(h))
    unreal.WidgetService.set_property(path, name, "ZOrder", str(z))

# NOTE: For NEW elements, anchor stays at default (0,0) = top-left.
# Positions are absolute pixels. Canvas = 1920x1080, content centered at X=960.

# 1. Dark panel behind content (card)
unreal.WidgetService.add_component(path, "Image", "Img_Panel", "CanvasPanel_9", False)
unreal.WidgetService.set_property(path, "Img_Panel", "Brush", solid_brush(0.004, 0.018, 0.047, 0.82))
place("Img_Panel", 360, 185, 1200, 680, 1)
print("Panel OK")

# 2. Logo UPEC
unreal.WidgetService.add_component(path, "Image", "LogoUPEC", "CanvasPanel_9", False)
unreal.WidgetService.set_property(path, "LogoUPEC", "Brush", tex_brush(logo_path))
place("LogoUPEC", 900, 228, 120, 120, 5)
print("Logo OK")

# 3. Badge ring (circulo alrededor del logo)
ring_brush = (
    "(TintColor=(SpecifiedColor=(R=0.0,G=0.706,B=0.847,A=0.2)),"
    "DrawAs=RoundedBox,ImageType=FullColor,ImageSize=(X=2048.0,Y=2048.0),Margin=(),"
    "OutlineSettings=(CornerRadii=(X=65.0,Y=65.0,Z=65.0,W=65.0),"
    "Color=(SpecifiedColor=(R=0.0,G=0.706,B=0.847,A=0.65)),Width=2.0,bUseBrushTransparency=True),"
    "UVRegion=(Min=(X=0.0,Y=0.0),Max=(X=0.0,Y=0.0),bIsValid=False))"
)
unreal.WidgetService.add_component(path, "Image", "Img_Ring", "CanvasPanel_9", False)
unreal.WidgetService.set_property(path, "Img_Ring", "Brush", ring_brush)
place("Img_Ring", 893, 221, 134, 134, 4)
print("Ring OK")

# 4. Badge label
unreal.WidgetService.add_component(path, "TextBlock", "Txt_BadgeLabel", "CanvasPanel_9", False)
unreal.WidgetService.set_property(path, "Txt_BadgeLabel", "Text", "UNIVERSIDAD POLITECNICA ESTATAL DEL CARCHI")
unreal.WidgetService.set_property(path, "Txt_BadgeLabel", "Font.Size", "11")
unreal.WidgetService.set_property(path, "Txt_BadgeLabel", "Font.FontObject", font_bold)
unreal.WidgetService.set_property(path, "Txt_BadgeLabel", "Font.TypefaceFontName", "Regular")
unreal.WidgetService.set_property(path, "Txt_BadgeLabel", "ColorAndOpacity", "(SpecifiedColor=(R=0.0,G=0.706,B=0.847,A=0.72))")
unreal.WidgetService.set_property(path, "Txt_BadgeLabel", "Justification", "Center")
place("Txt_BadgeLabel", 630, 362, 660, 18, 5)
print("BadgeLabel OK")

# 5. Separator line
unreal.WidgetService.add_component(path, "Image", "Img_Sep", "CanvasPanel_9", False)
unreal.WidgetService.set_property(path, "Img_Sep", "Brush", solid_brush(0.0, 0.706, 0.847, 0.45))
place("Img_Sep", 760, 386, 400, 1, 5)
print("Sep OK")

# 6. Subtitulo (debajo de los botones)
unreal.WidgetService.add_component(path, "TextBlock", "Txt_Sub", "CanvasPanel_9", False)
unreal.WidgetService.set_property(path, "Txt_Sub", "Text", "LABORATORIO DE MICROBIOLOGIA Y BIOTECNOLOGIA")
unreal.WidgetService.set_property(path, "Txt_Sub", "Font.Size", "14")
unreal.WidgetService.set_property(path, "Txt_Sub", "Font.FontObject", font_bold)
unreal.WidgetService.set_property(path, "Txt_Sub", "Font.TypefaceFontName", "Regular")
unreal.WidgetService.set_property(path, "Txt_Sub", "ColorAndOpacity", "(SpecifiedColor=(R=0.0,G=0.706,B=0.847,A=0.78))")
unreal.WidgetService.set_property(path, "Txt_Sub", "Justification", "Center")
place("Txt_Sub", 560, 656, 800, 22, 5)
print("Subtitulo OK")

# 7. TITULO existente (anchor ya es 0.5,0.5 de sesion anterior — ajustar offsets)
unreal.WidgetService.set_property(path, "titulosimulador", "Position X", "-480")
unreal.WidgetService.set_property(path, "titulosimulador", "Position Y", "-110")
unreal.WidgetService.set_property(path, "titulosimulador", "Size X", "960")
unreal.WidgetService.set_property(path, "titulosimulador", "Size Y", "140")
unreal.WidgetService.set_property(path, "titulosimulador", "ZOrder", "5")
unreal.WidgetService.set_property(path, "titulosimulador", "Font.Size", "44")

# 8. BOTONES existentes
unreal.WidgetService.set_property(path, "VerticalBox_0", "Position X", "-145")
unreal.WidgetService.set_property(path, "VerticalBox_0", "Position Y", "65")
unreal.WidgetService.set_property(path, "VerticalBox_0", "Size X", "290")
unreal.WidgetService.set_property(path, "VerticalBox_0", "Size Y", "200")
unreal.WidgetService.set_property(path, "VerticalBox_0", "ZOrder", "5")
print("Existentes OK")

unreal.EditorAssetLibrary.save_asset(path)
print("GUARDADO OK")
