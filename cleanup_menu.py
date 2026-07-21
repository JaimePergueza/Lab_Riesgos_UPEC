import unreal

path = "/Game/FirstPerson/Menus/WP_MenuPrincipal"

# Obtener jerarquia actual
snapshots = unreal.WidgetService.get_widget_snapshot(path)
all_names = [s.widget_name for s in snapshots]
print("Widgets actuales:", all_names)

# Elementos a eliminar (los que agregamos mal)
to_remove = [
    "Img_DarkOverlay", "Img_Grid", "Img_BadgeRing", "Img_Separator",
    "Img_CornerTL", "Img_CornerTR", "Img_CornerBL", "Img_CornerBR",
    "Txt_BadgeLabel", "Txt_Subtitulo", "LogoUPEC"
]
for name in to_remove:
    if name in all_names:
        unreal.WidgetService.remove_component(path, name)
        print(f"Eliminado: {name}")

unreal.EditorAssetLibrary.save_asset(path)

# Verificar resultado
snapshots2 = unreal.WidgetService.get_widget_snapshot(path)
print("Widgets restantes:", [s.widget_name for s in snapshots2])
