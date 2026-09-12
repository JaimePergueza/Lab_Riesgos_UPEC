import unreal


TOUCH_INTERFACE = "/Game/Mobile/Input/TI_MobileControls"
ICON_E = "/Game/Mobile/UI/Textures/Touch_Interact_E"
ICON_R = "/Game/Mobile/UI/Textures/Touch_Collect_R"
ICON_PAUSE = "/Game/Mobile/UI/Textures/Touch_Pause"


def set_vec2(control, name, x, y):
    control.set_editor_property(name, unreal.Vector2D(x, y))


touch_interface = unreal.load_asset(TOUCH_INTERFACE)
textures = [unreal.load_asset(path) for path in (ICON_E, ICON_R, ICON_PAUSE)]

if touch_interface is None:
    raise RuntimeError(f"No se pudo cargar {TOUCH_INTERFACE}")
if any(texture is None for texture in textures):
    raise RuntimeError(f"Faltan iconos: {textures}")

# Estos iconos son UI fija: no necesitan streaming ni mipmaps.
for texture in textures:
    texture.set_editor_property("never_stream", True)
    texture.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    texture.set_editor_property("srgb", True)

controls = list(touch_interface.get_editor_property("controls"))
if len(controls) != 5:
    raise RuntimeError(f"Se esperaban 5 controles y se encontraron {len(controls)}")

# Joystick de movimiento: esquina inferior izquierda.
set_vec2(controls[0], "center", 138.0, -138.0)
set_vec2(controls[0], "visual_size", 152.0, 152.0)
set_vec2(controls[0], "thumb_size", 76.0, 76.0)
set_vec2(controls[0], "interaction_size", 205.0, 180.0)

# Joystick de cámara: esquina inferior derecha.
set_vec2(controls[1], "center", -155.0, -145.0)
set_vec2(controls[1], "visual_size", 152.0, 152.0)
set_vec2(controls[1], "thumb_size", 76.0, 76.0)
set_vec2(controls[1], "interaction_size", 205.0, 180.0)

# Acciones: separadas del joystick derecho y con un área táctil mayor a la imagen.
action_layout = (
    (controls[2], textures[0], -365.0, -135.0, 108.0, 138.0),
    (controls[3], textures[1], -345.0, -285.0, 108.0, 138.0),
    (controls[4], textures[2], -78.0, 78.0, 78.0, 104.0),
)

for control, texture, x, y, visual, interaction in action_layout:
    control.set_editor_property("image1", texture)
    control.set_editor_property("image2", None)
    control.set_editor_property("treat_as_button", True)
    set_vec2(control, "center", x, y)
    set_vec2(control, "visual_size", visual, visual)
    set_vec2(control, "thumb_size", visual, visual)
    set_vec2(control, "interaction_size", interaction, interaction)

touch_interface.set_editor_property("controls", controls)
unreal.EditorAssetLibrary.save_asset(TOUCH_INTERFACE, only_if_is_dirty=False)
for path in (ICON_E, ICON_R, ICON_PAUSE):
    unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)

print("MOBILE_TOUCH_CONFIGURED")
for index, control in enumerate(controls):
    key = control.get_editor_property("main_input_key").export_text()
    image = control.get_editor_property("image1")
    print(index, key, image.get_path_name() if image else None,
          control.get_editor_property("center"),
          control.get_editor_property("visual_size"),
          control.get_editor_property("interaction_size"))
