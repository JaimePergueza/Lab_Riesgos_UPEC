import unreal

path = "/Game/FirstPerson/Menus/WP_MenuPrincipal"
ui = "/Game/FirstPerson/Menus/UI_Assets"

def brush(asset_name, w=32, h=32, alpha=1.0):
    full = f"{ui}/{asset_name}.{asset_name}"
    return (
        f"(TintColor=(SpecifiedColor=(R=1.0,G=1.0,B=1.0,A={alpha})),"
        f"DrawAs=Image,ImageType=FullColor,ImageSize=(X={w}.0,Y={h}.0),Margin=(),"
        f"ResourceObject=\"/Script/Engine.Texture2D'{full}'\","
        f"OutlineSettings=(CornerRadii=(X=0.0,Y=0.0,Z=0.0,W=0.0),"
        f"Color=(SpecifiedColor=(R=0.0,G=0.0,B=0.0,A=0.0)),RoundingType=HalfHeightRadius),"
        f"UVRegion=(Min=(X=0.0,Y=0.0),Max=(X=0.0,Y=0.0),bIsValid=False))"
    )

def full_screen(name, z):
    unreal.WidgetService.set_property(path, name, "Anchor Min X", "0")
    unreal.WidgetService.set_property(path, name, "Anchor Min Y", "0")
    unreal.WidgetService.set_property(path, name, "Anchor Max X", "1")
    unreal.WidgetService.set_property(path, name, "Anchor Max Y", "1")
    unreal.WidgetService.set_property(path, name, "Position X", "0")
    unreal.WidgetService.set_property(path, name, "Position Y", "0")
    unreal.WidgetService.set_property(path, name, "Size X", "0")
    unreal.WidgetService.set_property(path, name, "Size Y", "0")
    unreal.WidgetService.set_property(path, name, "ZOrder", str(z))

def anchor_center(name, px, py, sx, sy, z):
    unreal.WidgetService.set_property(path, name, "Anchor Min X", "0.5")
    unreal.WidgetService.set_property(path, name, "Anchor Min Y", "0.5")
    unreal.WidgetService.set_property(path, name, "Anchor Max X", "0.5")
    unreal.WidgetService.set_property(path, name, "Anchor Max Y", "0.5")
    unreal.WidgetService.set_property(path, name, "Position X", str(px))
    unreal.WidgetService.set_property(path, name, "Position Y", str(py))
    unreal.WidgetService.set_property(path, name, "Size X", str(sx))
    unreal.WidgetService.set_property(path, name, "Size Y", str(sy))
    unreal.WidgetService.set_property(path, name, "ZOrder", str(z))

# === 1. DARK OVERLAY (sobre el video) ===
unreal.WidgetService.add_component(path, "Image", "Img_DarkOverlay", "CanvasPanel_9", False)
unreal.WidgetService.set_property(path, "Img_DarkOverlay", "Brush", brush("T_DarkOverlay", 1920, 1080))
full_screen("Img_DarkOverlay", 1)
print("DarkOverlay OK")

# === 2. GRID OVERLAY ===
unreal.WidgetService.add_component(path, "Image", "Img_Grid", "CanvasPanel_9", False)
unreal.WidgetService.set_property(path, "Img_Grid", "Brush", brush("T_GridOverlay", 1920, 1080, 0.6))
full_screen("Img_Grid", 2)
print("Grid OK")

# === 3. BADGE RING (detras del logo, mismo centro) ===
unreal.WidgetService.add_component(path, "Image", "Img_BadgeRing", "CanvasPanel_9", False)
unreal.WidgetService.set_property(path, "Img_BadgeRing", "Brush", brush("T_BadgeRing", 256, 256))
anchor_center("Img_BadgeRing", -68, -308, 136, 136, 4)
print("BadgeRing OK")

# === 4. SEPARATOR LINE ===
unreal.WidgetService.add_component(path, "Image", "Img_Separator", "CanvasPanel_9", False)
unreal.WidgetService.set_property(path, "Img_Separator", "Brush", brush("T_Separator", 512, 4))
anchor_center("Img_Separator", -180, -165, 360, 6, 5)
print("Separator OK")

# === 5. CORNER BRACKETS ===
corners = [
    ("Img_CornerTL", "T_Corner_TL", "0", "0", "0", "0",  "0", "10", "10", "60", "60"),
    ("Img_CornerTR", "T_Corner_TR", "1", "0", "1", "0",  "0", "-70","10", "60", "60"),
    ("Img_CornerBL", "T_Corner_BL", "0", "1", "0", "1",  "0", "10","-70","60", "60"),
    ("Img_CornerBR", "T_Corner_BR", "1", "1", "1", "1",  "0", "-70","-70","60","60"),
]
for name, tex, ax, ay, bx, by, z, px, py, sx, sy in corners:
    unreal.WidgetService.add_component(path, "Image", name, "CanvasPanel_9", False)
    unreal.WidgetService.set_property(path, name, "Brush", brush(tex, 80, 80))
    unreal.WidgetService.set_property(path, name, "Anchor Min X", ax)
    unreal.WidgetService.set_property(path, name, "Anchor Min Y", ay)
    unreal.WidgetService.set_property(path, name, "Anchor Max X", bx)
    unreal.WidgetService.set_property(path, name, "Anchor Max Y", by)
    unreal.WidgetService.set_property(path, name, "Position X", px)
    unreal.WidgetService.set_property(path, name, "Position Y", py)
    unreal.WidgetService.set_property(path, name, "Size X", sx)
    unreal.WidgetService.set_property(path, name, "Size Y", sy)
    unreal.WidgetService.set_property(path, name, "ZOrder", "6")
print("Corners OK")

# === 6. LOGO — asegurar que este sobre el badge ring ===
unreal.WidgetService.set_property(path, "LogoUPEC", "ZOrder", "5")
print("Logo ZOrder OK")

# === 7. BADGE LABEL TEXT ===
unreal.WidgetService.add_component(path, "TextBlock", "Txt_BadgeLabel", "CanvasPanel_9", False)
unreal.WidgetService.set_property(path, "Txt_BadgeLabel", "Text", "UNIVERSIDAD POLITÉCNICA ESTATAL DEL CARCHI")
unreal.WidgetService.set_property(path, "Txt_BadgeLabel", "Font.Size", "12")
unreal.WidgetService.set_property(path, "Txt_BadgeLabel", "ColorAndOpacity", "(SpecifiedColor=(R=0.0,G=0.706,B=0.847,A=0.72))")
unreal.WidgetService.set_property(path, "Txt_BadgeLabel", "Justification", "Center")
anchor_center("Txt_BadgeLabel", -280, -145, 560, 20, 5)
print("BadgeLabel OK")

# === 8. SUBTITULO ===
unreal.WidgetService.add_component(path, "TextBlock", "Txt_Subtitulo", "CanvasPanel_9", False)
unreal.WidgetService.set_property(path, "Txt_Subtitulo", "Text", "LABORATORIO DE MICROBIOLOGÍA Y BIOTECNOLOGÍA")
unreal.WidgetService.set_property(path, "Txt_Subtitulo", "Font.Size", "16")
unreal.WidgetService.set_property(path, "Txt_Subtitulo", "ColorAndOpacity", "(SpecifiedColor=(R=0.0,G=0.706,B=0.847,A=0.78))")
unreal.WidgetService.set_property(path, "Txt_Subtitulo", "Justification", "Center")
anchor_center("Txt_Subtitulo", -350, -5, 700, 24, 5)
print("Subtitulo OK")

# Guardar
unreal.EditorAssetLibrary.save_asset(path)
print("GUARDADO OK")
