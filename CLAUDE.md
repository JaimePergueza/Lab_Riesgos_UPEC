# Proyecto VR — Prevención de Riesgos Laborales UPEC
## Contexto general

Tesis de grado: sistema de realidad virtual para prevención de riesgos laborales en el laboratorio de microbiología y biotecnología de la Universidad Politécnica Estatal del Carchi (UPEC). El objetivo es medir aceptación y usabilidad (TAM / SUS).

- Motor: **Unreal Engine 5**
- Conexión MCP disponible via **VibeUE** (`mcp__VibeUE__execute_python_code`, `manage_asset`, etc.) — transporte HTTP en `http://127.0.0.1:8088/mcp` (token en `.mcp.json`)
- Verificar siempre la conexión MCP antes de cualquier tarea para no malgastar tokens
- ⚙️ **Estabilidad de conexión:** `EditorPerformanceSettings → bThrottleCPUWhenNotForeground = False` (aplicado 2026-05-29). Con esto el editor NO estrangula la CPU al perder el foco, evitando que el servidor HTTP de VibeUE se congele al hacer alt-tab. **No volver a activar "Use Less CPU when in Background".** Mantener la ventana del editor visible (no minimizada) durante operaciones largas.
- Mapa activo de trabajo: `/Game/Maps/Lab_Despues.Lab_Despues`

---

## Mapas del proyecto

| Mapa | Descripción |
|------|-------------|
| `Lab/Maps/Scene` | Escena base / referencia |
| `Maps/Lab_Principal` | Laboratorio SIN medidas de seguridad |
| `Maps/Lab_Despues` | Laboratorio CON medidas de seguridad (**mapa activo**) |

---

## Flujo del juego — Lab_Despues

```
[PlayerStart] (1110,-1531,420)
     │
     ▼
[BP_Bienvenida] (773,-1045,538)
     │  → Box trigger → audio bienvenida + subtítulos → Delay → RemoveWidget
     ▼
[BP_TourArrow_Guia] (830,-525,262)  ← FLECHA 1 (siempre visible al inicio)
     │  → Guía al jugador hacia el área de EPPs
     ▼
[BP_PuertaPrincipal] (1110,-1531,420)
     │  → Abre con Lerp al entrar en zona
     │  → Muestra: "Dirígete al área de EPPs"
     │  → Referencias: CylinderActor, GuiaInicial
     ▼
[BP_MetaZone] (1266,-1888,305)  ← Zona trigger área EPPs
     │  → OnOverlap: activa ProximaFlecha (BP_TourArrow)
     │  → Delay → K2_DestroyActor (se autodestruye)
     ▼
[BP_TourArrow] (1266,-1878,350)  ← FLECHA 2 (debe iniciar OCULTA)
     │  → Custom event: MostrarFlecha
     │  → FindLookAtRotation hacia objetivo
     ▼
[5 x BP_ItemEPP] — Área EPPs (~1257,-1942)
     │  Orden obligatorio: Gorro(0) → Bata(1) → Mascarilla(2) → Guantes(3) → Gafas(4)
     │  → IndiceOrden valida la secuencia
     │  → Error: "Orden incorrecto: recoge los EPPs en orden"
     │  → Éxito: "¡Todos los EPPs colocados! La puerta se abre."
     ▼
[9 x BP_PuertaInteriorAuto] — Puertas interiores
     │  → Requieren TieneEPPs (verifican con GetAllActorsWithTag)
     │  → RequiereEPPs bloquea si no hay EPPs
     │  → Muestra ClaseAlerta si el jugador no tiene EPPs
     ▼
[BP_MetaZone_Destino] (1010,-1531,303)  ← Zona destino
```

NPCs en escena: `NPC_Lab` y `BP_NPC_Lab2` — patrullan entre `PuntoA` ↔ `PuntoB` (lógica Tick).

---

## Inventario de Blueprints (72 total)

### BPs activos en Lab_Despues (30 instancias)

| BP | Instancias | Eventos activos | Estado |
|----|-----------|-----------------|--------|
| `BP_PuertaInteriorAuto` | 9 | ComponentBoundEvents (overlap) | ✅ |
| `BP_Light_01` | 6 | — | ✅ |
| `BP_ItemEPP` | 5 | `ReceiveBeginPlay` | ✅ |
| `BP_TourArrow` | 2 | `ReceiveActorBeginOverlap` + Custom `MostrarFlecha` | ✅ |
| `BP_MetaZone` | 2 | `ReceiveActorBeginOverlap` | ✅ |
| `BP_NPC_Lab` / `BP_NPC_Lab2` | 1+1 | `ReceiveTick` | ✅ (lógica idéntica) |
| `BP_Bienvenida` | 1 | `ComponentBeginOverlap` | ✅ |
| `BP_PuertaPrincipal` | 1 | ComponentBoundEvents | ⚠️ tiene PrintString debug |
| `BP_Centrifuge` | 1 | **TODOS deshabilitados** | 🔴 código muerto |
| `LabPr1` | 1 | **TODOS deshabilitados** | ✅ (solo props estáticos) |
| `BP_MetaZone_Destino` | 1 | `ReceiveActorBeginOverlap` | ✅ |

### BPs en el proyecto pero NO en Lab_Despues

| BP | Ruta | Observación |
|----|------|-------------|
| `BP_GuiaNavegacion` | `/Game/Lab/Blueprints/` | Tick activo, BeginPlay disabled. Var: `SiguienteGuia`. No colocado en escena |
| `BP_CilindroDestructible` | `/Game/Lab/Blueprints/` | Destrúyese al overlap. Relacionado con commit "second EPP guide". No colocado |
| `BP_FirstPersonCharacter` | `/Game/FirstPerson/Blueprints/` | Personaje jugador |
| `BP_GameInstance` | `/Game/FirstPerson/Blueprints/` | Game instance global |
| `BP_FirstPersonGameMode` | `/Game/FirstPerson/Blueprints/` | Game mode |
| `BP_FirstPersonPlayerController` | `/Game/FirstPerson/Blueprints/` | Controlador |

---

## Variables clave por BP

| BP | Variables importantes |
|----|-----------------------|
| `BP_FirstPersonCharacter` | `TieneEPPs`, `EPP_Contador`, `ActorMiradoActual`, `CachedIndice`, `WidgetInteractPrompt`, `ReferenciaPausa` |
| `BP_ItemEPP` | `NombreItem`, `bEsEPP`, `IndiceOrden`, `PrevioEPP`, `AvisoOffsetZ`, `MeshEscala` |
| `BP_TourArrow` | `bArrived`, `TargetLocation`, `HeightOffset`, `ArrivalRadius`, `bAutoShow` |
| `BP_MetaZone` | `ProximaFlecha` (referencia al siguiente BP_TourArrow) |
| `BP_PuertaInteriorAuto` | `PuertaAbierta`, `PuertaCerrada`, `EstaAdentro`, `RequiereEPPs`, `FoundLlave`, `ClaseAlerta` |
| `BP_PuertaPrincipal` | `PuertaAbierta`, `PuertaCerrada`, `CylinderActor`, `GuiaInicial`, `WidgetPuerta` |
| `BP_NPC_Lab/2` | `PuntoA`, `PuntoB`, `bGoingToB` |
| `BP_Centrifuge` | `CoverAngle`, `NumberOfTubes`, `TubesPlaced` (sin usar — deshabilitado) |
| `BP_GuiaNavegacion` | `SiguienteGuia` |

---

## Cambios realizados (2026-05-03)

### ✅ BP_PuertaInteriorAuto — lógica EPP definitiva
Modificado via VibeUE MCP. La puerta con `RequiereEPPs=True` ahora **nunca** abre sin EPPs.

**Bug eliminado**: El flujo anterior tenía un `IF(EstaAdentro)` que siempre caía al `.else` (porque `EstaAdentro` nunca se inicializa a `true`), disparando `Timeline.Play` una vez sin chequeo de EPPs. Ese chequeo se bypaseó completamente: `E.Pressed → IF(RequiereEPPs)` directo.

**Flujo final**:
```
BeginOverlap → Cast → EnableInput → CreateWidget(ClasePrompt=PuertaWidgetBlueprint)
                                          → AddToViewport  [PROMPT "Presiona E"]
                                          → RemoveFromParent.self (limpieza al salir)

E_Key.Pressed → IF(RequiereEPPs)
    ├─ true  → CastFPC → GetTieneEPPs → IF(TieneEPPs)
    │             ├─ TieneEPPs=true  → SetEstaAdentro → Timeline.Play [ABRE]
    │             └─ TieneEPPs=false → CreateWidget(ClaseAlerta=WB_AlertaEPP)
    │                                       → AddToViewport [ALERTA — NO ABRE]
    └─ false → SetEstaAdentro → Timeline.Play [ABRE directo, sin EPP]
```

**Variables**:
- `ClaseAlerta`: `WB_AlertaEPP_C` (alerta cuando intentas sin EPPs)
- `ClasePrompt`: `PuertaWidgetBlueprint_C` (prompt al acercarte) ← variable nueva añadida

**Nodos**:
- 2 chains de CreateWidget+AddToViewport separadas (prompt y alerta no se mezclan)
- `PrintString` debug eliminado
- IF(EstaAdentro) queda orfano (sin exec entrante) — no afecta runtime, opcional borrar

### ✅ WB_AlertaEPP — textos actualizados
- `TextoTitulo`: "⚠ Alerta" (era "⚠ ACCESO BLOQUEADO")
- `TextoSubtitulo`: "Primero debe colocarse el equipo de EPPs" (era "Debes recoger los EPPs antes de salir del área")
- El widget ya tenía animación fade-in y auto-destrucción a los 3 segundos.

### ✅ Guía a CilindroMeta tras recoger EPPs (2026-05-03 segunda sesión)

**Objetivo**: Tras colectar los 5 EPPs en orden, mostrar flecha guía hacia `CilindroMeta` en `(2147,-973,304)`. Cuando el jugador pisa el cilindro: destruir flecha + cilindro visible + mostrar mensaje "Vamos a mover la muestra" 3 segundos.

**Modificaciones realizadas:**

1. **`BP_CilindroDestructible`** (`/Game/Lab/Blueprints/BP_CilindroDestructible`) — extendido:
   - 2 variables nuevas (instance editable): `FlechaGuia: BP_TourArrow_C`, `CilindroVisual: Actor`
   - Flujo BeginOverlap: `Cast a Character → PrintString("Vamos a mover la muestra", duración 3.0s) → DestroyActor(FlechaGuia) → DestroyActor(CilindroVisual) → DestroyActor(self)`
   - BeginPlay original (esconde el actor) intacto

2. **`BP_FirstPersonCharacter.AgregarEPP`** — extendido tras `PrintString "¡Todos los EPPs colocados!"`:
   - `GetAllActorsWithTag("ArrowMuestra")` → `Array_Get[0]` → `SetActorHiddenInGame(false)` → `SetActorTickEnabled(true)`
   - Esto desoculta y reactiva el Tick de la flecha guía cuando el jugador termina los EPPs

3. **Actores colocados en `Lab_Despues`** (✅ guardados):
   - `BP_TourArrow_Muestra` en `(1300,-1850,350)` — tag `ArrowMuestra`, `TargetLocation=(2147,-973,304)`, `bAutoShow=false`, hidden inicialmente
   - `BP_CilindroDestructible_Meta` en `(2147,-973,304)` — tag `CilindroMetaTrigger`, `FlechaGuia` apunta al BP_TourArrow_Muestra, `CilindroVisual` apunta al StaticMeshActor `CilindroMeta` existente

**Mensaje**: Se usa `PrintString` (3s, en pantalla). No se creó widget custom (intentado duplicar WB_AlertaEPP → WB_MoverMuestra pero los subobjetos del WidgetTree no quedaron accesibles vía Python tras la duplicación).

### ⚠️ Crash y recuperación
- Durante `save_current_level()` la primera vez ocurrió un assertion failure (`KismetReinstanceUtilities.cpp Line 2478, NewActor != nullptr`) seguido de access violations.
- Causa probable: reinstanciar de actores tras compilar BP_CilindroDestructible con nuevas variables.
- Quedó archivo corrupto **untracked** en `Content/__ExternalActors__/Maps/Lab_Despues/C/7B/HTJ64ZBEHRVY4XUFI25V20.uasset` (LabPr1_C, serial size mismatch). **Borrado manualmente** — no afectó a git porque nunca estuvo trackeado.
- Tras reiniciar editor: nivel carga normal, todos los actores spawneados sobrevivieron, todos los Blueprints sobrevivieron. **Nivel guardado OK** la segunda vez vía `LevelEditorSubsystem.save_current_level()`.

---

## Escena de Limpieza (Fase B) — recogida de fragmentos de vidrio (2026-05-28/29)

Escena posterior al incidente: matraz roto `BP_MatrazRota` con piezas internas `Pieza1`–`Pieza6` (StaticMeshComponents). Todo en `BP_FirstPersonCharacter` vía VibeUE/BlueprintService. Flujo previo ya funcional: letreros → tomar/colocar tacho cortopunzante → tomar pinza.

### Fase B.1 — Prompt al mirar el fragmento (EventTick) ✅
Detección por line-trace en `Evento Tick`. Mirando una pieza con la pinza tomada:
- Condición: `HitActor == BP_MatrazRota` **y** `bPinzaTomada == true` **y** `GetObjectName(HitComponent)` contiene "Pieza".
- Muestra "Recoger fragmento de vidrio [R]" (SetText sobre el TextBlock `PromptText` dentro de `WidgetInteractPrompt`), fija `ActorInteractuable = BP_MatrazRota` y guarda el componente mirado en `FragmentoMiradoActual`.
- Insertado en la escalera de casts del Tick, en `Cast BP_Pinza(detección).CastFailed`; las rutas de fallo continúan a `Cast BP_ItemEPP`.

### Fase B.2 — Recoger con R (IA_Recoger) ✅
Al presionar R mirando un fragmento (`ActorInteractuable == BP_MatrazRota`, pinza tomada, `FragmentoMiradoActual` válido, nombre contiene "Pieza"):
- `SetVisibility(false)` + `SetCollisionEnabled(NoCollision)` **sobre el componente** `FragmentoMiradoActual` (NO sobre todo el actor) → la pieza desaparece y deja de bloquear el line-trace.
- `FragmentosRecogidos += 1`; compara el valor **actualizado** (getter fresco tras el Set) contra `FragmentosTotal`.
- PrintString: "Fragmento depositado en el tacho cortopunzante." o, al llegar a 6, "Fragmentos grandes retirados correctamente. Continúe con la absorción del líquido derramado."
- Limpia `FragmentoMiradoActual=None`, `ActorInteractuable=None`, `WidgetInteractPrompt=Collapsed`.
- Insertado en `IA_Recoger` en `Cast BP_Pinza[39D002D9].CastFailed` (pin libre → no se cortó ningún wire). El cast nuevo usa `ActorInteractuable` como Object (no HitActor).

### Variables nuevas en BP_FirstPersonCharacter
`FragmentoMiradoActual : PrimitiveComponent`, `FragmentosRecogidos : int = 0`, `FragmentosTotal : int = 6`.

### Pendiente (Fase B.3+, NO implementado)
Animación del fragmento hacia el tacho, efectos/sonido, toallas, líquido, ajuste de las colisiones convexas de las piezas (el prompt aparece en una zona algo amplia), y mover el contador al `BP_EscenaLimpiezaManager` vía interfaz.

> Detalle fino (GUIDs de nodos, gotchas de la API) en la memoria persistente `project_thesis_context.md`.

---

## ⏭️ Pendiente para próxima sesión

### 🟡 Probar el flujo completo en PIE
- Pisar EPPs en orden (Gorro→Bata→Mascarilla→Guantes→Gafas)
- Verificar que aparece la flecha apuntando a `(2147,-973,304)` tras el 5º EPP
- Caminar hasta el cilindro
- Verificar que dispara: mensaje "Vamos a mover la muestra" + flecha destruida + CilindroMeta destruido + BP_CilindroDestructible_Meta destruido

### 🟡 Verificar puerta interior con EPPs
- Probar que la puerta `BP_PuertaInteriorAuto` con `RequiereEPPs=True` (instancia `BP_PuertaInteriorAuto` en (1345,-1342)) **nunca** abre sin EPPs
- Probar que el prompt `PuertaWidgetBlueprint` aparece al acercarse
- Probar que la alerta `WB_AlertaEPP` aparece al presionar E sin EPPs
- Probar que abre normal con EPPs colocados

### 🟡 Si el mensaje "Vamos a mover la muestra" no es lo bastante visible
- Considerar reemplazar el `PrintString` en `BP_CilindroDestructible` con un widget UMG dedicado.
- Si se duplica `WB_AlertaEPP`: alternativa que funcionó parcialmente fue acceder vía `unreal.find_object` por path, pero los subobjetos del WidgetTree quedaron inaccesibles tras `duplicate_asset`. Se recomienda crear el widget desde cero o duplicar manualmente desde el editor de UE.

### 🟡 Posicionamiento de la flecha guía
- `BP_TourArrow_Muestra` está en `(1300,-1850,350)` (zona EPP). Como su Tick hace que siga al jugador (ver lógica en `BP_TourArrow.EventGraph`), la posición inicial no es crítica. Si se nota que no se ve bien al jugador, mover a una posición más cercana al área de salida.

---

## Problemas conocidos (pendientes de fix)

1. **🔴 `BP_TourArrow` visible al inicio** — La instancia `BP_TourArrow` (flecha 2, en 1266,-1878) tiene `Hidden In Game = false`. El `ReceiveBeginPlay` está deshabilitado, así que no hay lógica de ocultamiento. Debe marcarse manualmente como `Hidden In Game = true` en el panel de detalles del actor en el nivel, y solo mostrarse cuando `BP_MetaZone` llame a `SetActorHiddenInGame(false)` via `ProximaFlecha`.

2. **🔴 `BP_Centrifuge` inerte** — Todos los eventos deshabilitados. La lógica de rotación de tapa y colocación de tubos no se ejecuta. Si debe animar, habilitar `ReceiveBeginPlay`.

3. **🟡 `BP_GuiaNavegacion` no está en la escena** — Asset creado pero sin instancia. Tiene `ReceiveTick` activo pero `ReceiveBeginPlay` deshabilitado; si se coloca, revisar esa inconsistencia.

5. **🟡 `PrintString` en `BP_PuertaPrincipal`** — Nodo de debug que imprime en pantalla en runtime. Eliminar antes de la versión final.

6. **🟡 NPCs idénticos** — `BP_NPC_Lab` y `BP_NPC_Lab2` tienen exactamente la misma lógica. Considerar unificar en un solo BP parametrizable.

---

## Rutas de assets frecuentes

| Asset | Ruta |
|-------|------|
| Tour arrows | `/Game/Tour/BP_TourArrow`, `/Game/Tour/BP_MetaZone` |
| EPP system | `/Game/EPP/BP_ItemEPP` |
| Personaje | `/Game/FirstPerson/Blueprints/BP_FirstPersonCharacter` |
| Puertas | `/Game/Fab/Puertas/puerta/Blueprints/` |
| NPCs | `/Game/Lab/Blueprints/BP_NPC_Lab`, `BP_NPC_Lab2` |
| Lab misc | `/Game/Lab/Blueprints/` (GuiaNavegacion, CilindroDestructible, Centrifuge) |
| Props lab | `/Game/Fab/LabsAssets/Lab1/LabPr1` |
| Audio bienvenida | `/Game/Fab/Audios/BP_Bienvenida` |

---

## Notas técnicas

- Los T3D export de los BPs se guardan en `D:/BP_Audit_Export/` (archivos UTF-16).
- `LabPr1` es un contenedor de 70 meshes estáticos (círculos, esferas, hélice) — sin lógica.
- El sistema de EPPs usa `TieneEPPs` (bool en `BP_FirstPersonCharacter`) para la puerta con `RequiereEPPs=True`. El antiguo `GetAllActorsWithTag("LlaveEPP")` fue eliminado.
- Las puertas usan `Lerp` de rotación (no timeline) — `PuertaAbierta`/`PuertaCerrada` son rotaciones target.
- XR Framework disponible en `/Game/XRFramework/` pero no activo en `Lab_Despues`.
