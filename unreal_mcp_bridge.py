"""
UnrealMCP Bridge — conecta Claude Code con el plugin UnrealMCP de UE5
Puerto TCP: 127.0.0.1:55557
"""

import json
import socket
from mcp.server.fastmcp import FastMCP

UNREAL_HOST = "127.0.0.1"
UNREAL_PORT = 55557

app = FastMCP("unreal-mcp")


def send_command(command_type: str, params: dict) -> dict:
    """Envia un comando al servidor TCP de Unreal y retorna la respuesta."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(10)
            sock.connect((UNREAL_HOST, UNREAL_PORT))
            message = json.dumps({"type": command_type, "params": params}) + "\n"
            sock.sendall(message.encode("utf-8"))

            response_data = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                try:
                    json.loads(response_data.decode("utf-8").strip())
                    break
                except json.JSONDecodeError:
                    continue

            return json.loads(response_data.decode("utf-8").strip())
    except ConnectionRefusedError:
        return {"status": "error", "error": "No se puede conectar a Unreal Editor. Asegurate de que el proyecto este abierto."}
    except socket.timeout:
        return {"status": "error", "error": "Timeout: Unreal Editor no respondio en 10 segundos."}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def r(response: dict) -> str:
    return json.dumps(response, indent=2, ensure_ascii=False)


# ─── EDITOR ──────────────────────────────────────────────────────────────────

@app.tool()
def ping() -> str:
    """Verifica que la conexion con Unreal Editor esta activa."""
    return r(send_command("ping", {}))


@app.tool()
def get_actors_in_level() -> str:
    """Obtiene todos los actores en el nivel actual de Unreal."""
    return r(send_command("get_actors_in_level", {}))


@app.tool()
def find_actors_by_name(pattern: str) -> str:
    """Busca actores en el nivel por nombre o patron.

    Args:
        pattern: Nombre o parte del nombre del actor a buscar.
    """
    return r(send_command("find_actors_by_name", {"pattern": pattern}))


@app.tool()
def spawn_actor(name: str, type: str = "CUBE", location_x: float = 0.0, location_y: float = 0.0, location_z: float = 0.0) -> str:
    """Coloca un actor en el nivel.

    Args:
        name: Nombre del nuevo actor.
        type: Tipo (CUBE, SPHERE, POINT_LIGHT, etc).
        location_x: Posicion X en cm.
        location_y: Posicion Y en cm.
        location_z: Posicion Z en cm.
    """
    return r(send_command("spawn_actor", {"name": name, "type": type, "location": [location_x, location_y, location_z]}))


@app.tool()
def delete_actor(name: str) -> str:
    """Elimina un actor del nivel por nombre.

    Args:
        name: Nombre exacto del actor a eliminar.
    """
    return r(send_command("delete_actor", {"name": name}))


@app.tool()
def set_actor_transform(name: str, location_x: float = 0.0, location_y: float = 0.0, location_z: float = 0.0,
                        rotation_pitch: float = 0.0, rotation_yaw: float = 0.0, rotation_roll: float = 0.0,
                        scale_x: float = 1.0, scale_y: float = 1.0, scale_z: float = 1.0) -> str:
    """Mueve, rota y escala un actor en el nivel.

    Args:
        name: Nombre del actor.
        location_x/y/z: Posicion en cm.
        rotation_pitch/yaw/roll: Rotacion en grados.
        scale_x/y/z: Escala (1.0 = normal).
    """
    return r(send_command("set_actor_transform", {
        "name": name,
        "location": [location_x, location_y, location_z],
        "rotation": [rotation_pitch, rotation_yaw, rotation_roll],
        "scale": [scale_x, scale_y, scale_z]
    }))


@app.tool()
def get_actor_properties(name: str) -> str:
    """Obtiene las propiedades de un actor en el nivel.

    Args:
        name: Nombre del actor.
    """
    return r(send_command("get_actor_properties", {"name": name}))


@app.tool()
def focus_viewport(name: str) -> str:
    """Enfoca el viewport de Unreal en un actor.

    Args:
        name: Nombre del actor a enfocar.
    """
    return r(send_command("focus_viewport", {"actor_name": name}))


@app.tool()
def take_screenshot(filename: str = "screenshot") -> str:
    """Toma una captura del viewport de Unreal.

    Args:
        filename: Nombre del archivo sin extension.
    """
    return r(send_command("take_screenshot", {"filename": filename}))


# ─── BLUEPRINTS ───────────────────────────────────────────────────────────────

@app.tool()
def create_blueprint(name: str, parent_class: str = "Actor", path: str = "/Game/Blueprints") -> str:
    """Crea un nuevo Blueprint en el proyecto.

    Args:
        name: Nombre del Blueprint (ej: BP_MiObjeto).
        parent_class: Clase padre (Actor, Pawn, Character, etc).
        path: Ruta en Content Browser.
    """
    return r(send_command("create_blueprint", {"name": name, "parent_class": parent_class, "path": path}))


@app.tool()
def add_component_to_blueprint(blueprint_name: str, component_type: str, component_name: str) -> str:
    """Agrega un componente a un Blueprint.

    Args:
        blueprint_name: Nombre del Blueprint.
        component_type: Tipo (StaticMeshComponent, BoxComponent, etc).
        component_name: Nombre del componente.
    """
    return r(send_command("add_component_to_blueprint", {
        "blueprint_name": blueprint_name,
        "component_type": component_type,
        "component_name": component_name
    }))


@app.tool()
def compile_blueprint(blueprint_name: str) -> str:
    """Compila un Blueprint para aplicar cambios.

    Args:
        blueprint_name: Nombre del Blueprint.
    """
    return r(send_command("compile_blueprint", {"blueprint_name": blueprint_name}))


@app.tool()
def set_blueprint_property(blueprint_name: str, property_name: str, property_value: str) -> str:
    """Establece una propiedad en un Blueprint.

    Args:
        blueprint_name: Nombre del Blueprint.
        property_name: Nombre de la propiedad.
        property_value: Valor como string.
    """
    return r(send_command("set_blueprint_property", {
        "blueprint_name": blueprint_name,
        "property_name": property_name,
        "property_value": property_value
    }))


@app.tool()
def set_physics_properties(blueprint_name: str, component_name: str = "",
                           collision_enabled: bool = True, collision_profile: str = "",
                           simulate_physics: bool = False) -> str:
    """Configura fisicas y colision en los componentes de un Blueprint.
    Si no se indica component_name, aplica a TODOS los componentes.

    Args:
        blueprint_name: Nombre del Blueprint.
        component_name: Nombre del componente (vacio = todos).
        collision_enabled: True para activar colision, False para desactivarla.
        collision_profile: Perfil de colision (NoCollision, BlockAll, OverlapAll, etc).
        simulate_physics: True para activar simulacion de fisica.
    """
    params = {"blueprint_name": blueprint_name, "simulate_physics": simulate_physics}
    if component_name:
        params["component_name"] = component_name
    params["collision_enabled"] = collision_enabled
    if collision_profile:
        params["collision_profile"] = collision_profile
    return r(send_command("set_physics_properties", params))


# ─── NODOS BLUEPRINT ─────────────────────────────────────────────────────────

@app.tool()
def add_blueprint_event_node(blueprint_name: str, event_name: str) -> str:
    """Agrega un nodo de evento al Blueprint (BeginPlay, Tick, etc).

    Args:
        blueprint_name: Nombre del Blueprint.
        event_name: Evento (ReceiveBeginPlay, ReceiveTick, ActorBeginOverlap, etc).
    """
    return r(send_command("add_blueprint_event_node", {"blueprint_name": blueprint_name, "event_name": event_name}))


@app.tool()
def add_blueprint_function_node(blueprint_name: str, function_name: str,
                                target: str = "self", parameter_values: dict = {}) -> str:
    """Agrega un nodo de funcion al Blueprint.

    Args:
        blueprint_name: Nombre del Blueprint.
        function_name: Funcion a llamar (SetActorEnableCollision, PrintString, etc).
        target: Objetivo (self u otro).
        parameter_values: Valores de parametros como dict (ej: {"NewActorEnableCollision": false}).
    """
    return r(send_command("add_blueprint_function_node", {
        "blueprint_name": blueprint_name,
        "function_name": function_name,
        "target": target,
        "parameter_values": parameter_values
    }))


@app.tool()
def connect_blueprint_nodes(blueprint_name: str, source_node_id: str, source_pin: str,
                            target_node_id: str, target_pin: str) -> str:
    """Conecta dos nodos en el grafo de un Blueprint.

    Args:
        blueprint_name: Nombre del Blueprint.
        source_node_id: ID del nodo origen.
        source_pin: Pin de salida (ej: then, execute).
        target_node_id: ID del nodo destino.
        target_pin: Pin de entrada (ej: execute).
    """
    return r(send_command("connect_blueprint_nodes", {
        "blueprint_name": blueprint_name,
        "source_node_id": source_node_id,
        "source_pin": source_pin,
        "target_node_id": target_node_id,
        "target_pin": target_pin
    }))


@app.tool()
def find_blueprint_nodes(blueprint_name: str, node_type: str = "function", function_name: str = "") -> str:
    """Busca nodos existentes en el grafo de un Blueprint.

    Args:
        blueprint_name: Nombre del Blueprint.
        node_type: Tipo de nodo (function, event).
        function_name: Nombre de la funcion a buscar.
    """
    return r(send_command("find_blueprint_nodes", {
        "blueprint_name": blueprint_name,
        "node_type": node_type,
        "function_name": function_name
    }))


# ─── PROYECTO ─────────────────────────────────────────────────────────────────

@app.tool()
def create_input_mapping(action_name: str, key: str) -> str:
    """Crea un mapeo de input en el proyecto.

    Args:
        action_name: Nombre de la accion (ej: Interactuar).
        key: Tecla (ej: E, SpaceBar, LeftMouseButton).
    """
    return r(send_command("create_input_mapping", {"action_name": action_name, "key": key}))


# ─── UMG / UI ────────────────────────────────────────────────────────────────

@app.tool()
def create_umg_widget_blueprint(name: str, path: str = "/Game/UI") -> str:
    """Crea un Widget Blueprint (UI/HUD) en el proyecto.

    Args:
        name: Nombre del widget (ej: WB_HUD).
        path: Ruta en Content Browser.
    """
    return r(send_command("create_umg_widget_blueprint", {"name": name, "path": path}))


@app.tool()
def add_text_block_to_widget(widget_name: str, text_block_name: str, text: str = "Texto",
                             position_x: float = 0.0, position_y: float = 0.0) -> str:
    """Agrega un TextBlock a un Widget Blueprint.

    Args:
        widget_name: Nombre del widget.
        text_block_name: Nombre del TextBlock.
        text: Texto a mostrar.
        position_x/y: Posicion en el canvas.
    """
    return r(send_command("add_text_block_to_widget", {
        "widget_name": widget_name,
        "text_block_name": text_block_name,
        "text": text,
        "position": {"x": position_x, "y": position_y}
    }))


@app.tool()
def add_button_to_widget(widget_name: str, button_name: str, position_x: float = 0.0,
                         position_y: float = 0.0, size_x: float = 200.0, size_y: float = 60.0) -> str:
    """Agrega un Button a un Widget Blueprint.

    Args:
        widget_name: Nombre del widget.
        button_name: Nombre del boton.
        position_x/y: Posicion en canvas.
        size_x/y: Tamaño del boton.
    """
    return r(send_command("add_button_to_widget", {
        "widget_name": widget_name,
        "button_name": button_name,
        "position": {"x": position_x, "y": position_y},
        "size": {"x": size_x, "y": size_y}
    }))


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run()
