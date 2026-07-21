import unreal

bp = "/Game/FirstPerson/Blueprints/BP_Baliza"

# Configurar SpotLight Luz_Haz — haz vertical cyan
unreal.BlueprintService.set_component_property(bp, "Luz_Haz", "Intensity", "8000.0")
unreal.BlueprintService.set_component_property(bp, "Luz_Haz", "LightColor", "(R=0,G=180,B=216,A=255)")
unreal.BlueprintService.set_component_property(bp, "Luz_Haz", "AttenuationRadius", "3000.0")
unreal.BlueprintService.set_component_property(bp, "Luz_Haz", "InnerConeAngle", "3.0")
unreal.BlueprintService.set_component_property(bp, "Luz_Haz", "OuterConeAngle", "8.0")
unreal.BlueprintService.set_component_property(bp, "Luz_Haz", "RelativeRotation", "(Pitch=-90.0,Yaw=0.0,Roll=0.0)")
print("SpotLight OK")

# Configurar PointLight Luz_Base — glow en el suelo
unreal.BlueprintService.set_component_property(bp, "Luz_Base", "Intensity", "1200.0")
unreal.BlueprintService.set_component_property(bp, "Luz_Base", "LightColor", "(R=0,G=180,B=216,A=255)")
unreal.BlueprintService.set_component_property(bp, "Luz_Base", "AttenuationRadius", "500.0")
print("PointLight OK")

# Variable default
unreal.BlueprintService.set_variable_default(bp, "bActiva", "true")

# EventGraph: BeginPlay -> Set Luz_Haz Visibility (bActiva)
# Simple: en BeginPlay solo asegurar que las luces esten visibles
nodes = unreal.BlueprintService.get_nodes_in_graph(bp, "EventGraph")
print("Nodos existentes:", len(nodes))

# Agregar nodo BeginPlay si no existe
has_begin = any("BeginPlay" in n.node_title for n in nodes)
if not has_begin:
    bp_node = unreal.BlueprintService.add_node(bp, "EventGraph", "K2Node_Event", 0, 0)
    print("BeginPlay agregado? check manual")

unreal.BlueprintService.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_asset(bp)
print("BP_Baliza configurado y guardado")
