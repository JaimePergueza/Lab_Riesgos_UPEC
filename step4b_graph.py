import unreal

bp = "/Game/FirstPerson/Blueprints/BP_TriggerPuerta"
g = "EventGraph"

# On Component Begin Overlap (TriggerBox)
overlap = unreal.BlueprintService.add_event_node(bp, g, "OnComponentBeginOverlap", 0.0, 0.0)
print("Overlap event:", overlap)

# Cast to BP_FirstPersonCharacter
cast = unreal.BlueprintService.add_cast_node(bp, g, "BP_FirstPersonCharacter", 300.0, 0.0)
print("Cast:", cast)

# Do Once
do_once = unreal.BlueprintService.add_function_call_node(bp, g, "KismetMathLibrary", "DoOnce", 550.0, 0.0)
print("DoOnce:", do_once)

# Create WB_MensajePuerta Widget
create_w = unreal.BlueprintService.add_function_call_node(bp, g, "WidgetBlueprintLibrary", "Create", 800.0, 0.0)
print("CreateWidget:", create_w)

# Add to Viewport
add_vp = unreal.BlueprintService.add_function_call_node(bp, g, "UserWidget", "AddToViewport", 1100.0, 0.0)
print("AddToViewport:", add_vp)

# Get Player Controller (para mouse cursor)
get_pc = unreal.BlueprintService.add_function_call_node(bp, g, "GameplayStatics", "GetPlayerController", 1100.0, 200.0)
print("GetPC:", get_pc)

# Set Show Mouse Cursor
set_cursor = unreal.BlueprintService.add_function_call_node(bp, g, "PlayerController", "SetShowMouseCursor", 1400.0, 0.0)
print("SetCursor:", set_cursor)

# Set Input Mode Game And UI
set_input = unreal.BlueprintService.add_function_call_node(bp, g, "WidgetBlueprintLibrary", "SetInputMode_GameAndUIEx", 1700.0, 0.0)
print("SetInput:", set_input)

# Conectar todo
unreal.BlueprintService.connect_nodes(bp, g, overlap, "then", cast, "execute")
unreal.BlueprintService.connect_nodes(bp, g, overlap, "Other Actor", cast, "Object")
unreal.BlueprintService.connect_nodes(bp, g, cast, "then", do_once, "execute")
unreal.BlueprintService.connect_nodes(bp, g, do_once, "Completed", create_w, "execute")
unreal.BlueprintService.connect_nodes(bp, g, create_w, "then", add_vp, "execute")
unreal.BlueprintService.connect_nodes(bp, g, create_w, "ReturnValue", add_vp, "self")
unreal.BlueprintService.connect_nodes(bp, g, add_vp, "then", set_cursor, "execute")
unreal.BlueprintService.connect_nodes(bp, g, set_cursor, "then", set_input, "execute")
print("Conexiones OK")

unreal.BlueprintService.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_asset(bp)
print("BP_TriggerPuerta graph COMPLETO")
