# Retomar — Fase B.1: Prompt de recoger fragmentos (escena de limpieza)

## 0. VERIFICAR CONEXIÓN PRIMERO
Antes de tocar nada, ejecutar vía VibeUE:
```python
import unreal
print(unreal.SystemLibrary.get_engine_version())
```
Si falla → detenerse y avisar. No modificar nada.

## REGLA CRÍTICA (memoria del proyecto)
Editar nodos de Blueprint SIEMPRE con `unreal.BlueprintService` (vía `mcp__VibeUE__execute_python_code`).
NUNCA usar ctypes / pywin32 / Computer Use / edición o reimport de T3D. El T3D solo para LECTURA/diagnóstico (export con `unreal.AssetExportTask`, leer con encoding utf-16).

## CONTEXTO — Escena de limpieza (NO está en CLAUDE.md)
Flujo ya implementado y funcionando en `BP_FirstPersonCharacter` (`/Game/FirstPerson/Blueprints/BP_FirstPersonCharacter`, grafo `EventGraph`):
- Letreros → tomar tacho → colocar tacho (prompt congelado corregido) → tomar pinza con R (la pinza se adjunta a `PinzaCarryPoint` y aparece en cámara).
- El prompt de interacción usa: variable `WidgetInteractPrompt` (contenedor, tipo `WBP_InteractPrompt_C`) + `PromptText` (TextBlock DENTRO de `WBP_InteractPrompt_C`, se accede con member-get: `add_member_get_node(BP,"EventGraph","WBP_InteractPrompt_C","PromptText")` con `self` ← Get WidgetInteractPrompt).
- `ActorInteractuable` (object) = actor mirado para interactuar. `ActorMiradoActual` (object) = NO usar para fragmentos.
- `bPinzaTomada` (bool) ya existe en FPC y queda en true al tomar la pinza.

Assets:
- BP_MatrazRota: `/Game/Fab/EscenaLimpieza/EstacionDerrames/MatrasRotaaglb/StaticMeshes/BP_MatrazRota`
- BP_Pinza: `/Game/Fab/EscenaLimpieza/EstacionDerrames/PinzaRecoger/StaticMeshes/BP_Pinza`
- BP_TachoCort: `/Game/Fab/EscenaLimpieza/EstacionDerrames/TachoCortopun/StaticMeshes/BP_TachoCort`
- Manager: `/Game/Lab/Blueprints/BP_EscenaLimpiezaManager` (vars: `bFragmentosActivados`, `FragmentosTotal:int`, `FragmentosRecogidos:int`, `MatrazRotaRef`, `PinzaRef`, `bPinzaTomada`) → para Fase B.2, NO ahora.
- Interfaz: `/Game/Lab/Blueprints/BPI_LimpiezaCallbacks` (solo `OnTachoColocado` existe).

## DIAGNÓSTICO YA HECHO (no repetir)
- `HitActor = BP_MatrazRota`, `HitComponent = PiezaN` (confirmado en logs PIE). Las Pieza1–Pieza6 son StaticMeshComponents internos (no actores), bloquean el canal Visibility, y el LineTrace de EventTick los golpea.
- EventTick: `LineTraceSingle` = nodo CallFunction_31; `BreakHitResult` = CallFunction_32 (pins de salida `HitActor` y `HitComponent`).
- En EventTick ya existe un **Cast a BP_Pinza** (rama del prompt "Tomar pinza"), creado en esta serie, **NodeGuid estable = `9299680044BA8793AD736B9993664ED3`**. Su pin `CastFailed` actualmente va al Cast de BP_ItemEPP (siguiente en el ladder).
  - ⚠️ Los nombres internos (K2Node_DynamicCast_N) y GUIDs de nodos preexistentes cambian entre exports. Re-exportar el FPC y re-confirmar a qué nodo va `CastFailed` de `9299680044BA8793AD736B9993664ED3` ANTES de cortar.
  - NO confundir con el Cast a BP_Pinza de IA_Recoger (tomar con R) — ese NO se toca.
- `FragmentoMiradoActual` NO existe → hay que crearla.

## OBJETIVO DE ESTA SESIÓN: SOLO Fase B.1 (prompt + guardar componente mirado)
NO implementar recoger con R / ocultar pieza / desactivar colisión / contador / manager / animación / líquido / toallas.

### Pasos aprobados
1. **Crear variable** en FPC: `FragmentoMiradoActual` tipo `UPrimitiveComponent` (referencia a objeto). Usar `bs.add_variable(FPC,"FragmentoMiradoActual","UPrimitiveComponent")` (verificar el tipo resultante).

2. **Insertar rama en EventTick** en `pinzaCast(9299680044BA8793AD736B9993664ED3).CastFailed`:
   - Cortar el wire `pinzaCast.CastFailed → CastItemEPP` (con `disconnect_pin`).
   - Crear `matrazCast = add_cast_node(FPC,"EventGraph","BP_MatrazRota_C")` (si falla por nombre, probar path completo del asset).
   - `BreakHitResult(CallFunction_32).HitActor → matrazCast.Object`
   - `pinzaCast.CastFailed → matrazCast.execute`
   - `matrazCast.CastFailed → CastItemEPP.execute` (reconectar ladder original)

3. **Dentro de matrazCast.then:**
   - `Branch bPinzaTomada` (Get bPinzaTomada → Condition).
     - `false → CastItemEPP.execute`
   - `true →` check de nombre de pieza:
     - `GetObjectName(KismetSystemLibrary)` sobre `HitComponent` (de BreakHitResult_32) → string. (Confirmar que devuelve "PiezaN"; en logs el componente sale como "Pieza3".)
     - `Contains(KismetStringLibrary)` (`InStr`=resultado, `SubStr`="Pieza") → bool → `Branch`.
       - `false → CastItemEPP.execute`
       - `true →` mostrar prompt:
         - `SetText(TextBlock)` self←member-get PromptText (self←Get WidgetInteractPrompt); `InText="Recoger fragmento de vidrio [R]"`
         - `SetVisibility(Widget)` self←Get WidgetInteractPrompt; `InVisibility=Visible`
         - `Set ActorInteractuable` = `matrazCast.AsBP MatrazRota` (NO ActorMiradoActual)
         - `Set FragmentoMiradoActual` = `BreakHitResult_32.HitComponent`

4. **Compilar** `bs.compile_blueprint(FPC)` → debe dar 0 errores / 0 warnings.
5. **Guardar** `unreal.EditorAssetLibrary.save_asset(FPC)`.
6. **Leer logs**, reportar.

## NO TOCAR
IA_Recoger, lógica de tomar pinza, PinzaCarryPoint, BP_Pinza, tacho, cilindro del tacho, letreros, manager (salvo lectura), BP_MatrazRota (salvo lectura), fragmentos (salvo lectura), video, sonido, EPP, matraz/autoclave, EventTick de pinza (solo extender en el punto indicado), limpieza general de prints. No usar `ActorMiradoActual`. Si se corta un wire, reconectar SIEMPRE a CastItemEPP.

## PRUEBA ESPERADA (B.1)
1. Completar letreros → tomar y colocar tacho → tomar pinza.
2. Mirar Pieza1–6 del BP_MatrazRota → aparece "Recoger fragmento de vidrio [R]".
3. Mirar otra parte del derrame (no PiezaN) → NO aparece ese prompt.
4. Presionar R todavía NO recoge nada (eso es Fase B.2).

## DESPUÉS (Fase B.2, NO ahora)
Con R sobre FragmentoMiradoActual: ocultar pieza + desactivar su colisión + `FragmentosRecogidos++` (usar contador del manager) + mensaje "Fragmento depositado...". Al completar todas: mensaje "Fragmentos grandes retirados correctamente. Continúe con la absorción del líquido derramado."

## NOTAS DE ESTADO (último guardado de esta serie)
- BP_FirstPersonCharacter compila 0/0, guardado.
- BP_Pinza: Mobility de DefaultSceneRoot/PinzaRecoger/BoxCollision_Interact = Movable (asset). La INSTANCIA en el nivel Lab_Despues también se forzó a Movable y se guardó el nivel (el cambio de asset no propagaba al actor ya colocado).
- Rotación de la pinza al tomarla: nodo SetActorRelativeRotation = (Pitch=-45, Yaw=90, Roll=90) → "0, 90, 0"/"-45, 90, 90" en formato pin "P, Y, R". Ajuste visual pendiente (las puntas aún no quedan hacia abajo) — el usuario lo dejó para después.
- Artefactos de diagnóstico (solo lectura) en `D:/BP_Audit_Export/` (T3D en utf-16).
