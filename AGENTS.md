# VR — Prevención de Riesgos Laborales UPEC

Tesis Unreal Engine 5.7 — laboratorio de microbiología/biotecnología UPEC. Mide aceptación/usabilidad (TAM/SUS).

## MCP & Herramientas

- **VibeUE** en `http://127.0.0.1:8088/mcp` (token en `.mcp.json`). Verificar conexión antes de toda tarea.
- **EditorPerformanceSettings → bThrottleCPUWhenNotForeground = False** (no estrangular CPU al perder foco; no reactivar "Use Less CPU when in Background"). Mantener ventana del editor visible durante ops largas.
- **Regla crítica**: Editar Blueprints SOLO con `unreal.BlueprintService` vía `mcp__VibeUE__execute_python_code`. NUNCA T3D para escribir (solo lectura/diagnóstico, export utf-16 a `D:/BP_Audit_Export/`).
- **Actions**: `unreal.AssetToolsHelpers`, `unreal.EditorAssetLibrary`, `unreal.BlueprintService`, `unreal.WidgetService`. `WidgetService` para UMG.
- **Compilar y guardar**: `bs.compile_blueprint(path)` → `EditorAssetLibrary.save_asset(path)`. Guardar nivel (`LevelEditorSubsystem.save_current_level()`) tras compilar BPs con vars nuevas **puede crash** (assertion `KismetReinstanceUtilities.cpp:2478`); guardar dos veces si falla.

## Mapas activos

| Mapa | Propósito |
|------|-----------|
| `/Game/Maps/Lab_Despues` | **Mapa activo** — laboratorio CON medidas de seguridad |
| `Lab/Maps/Scene` | Escena base |
| `Maps/Lab_Principal` | Laboratorio SIN medidas |

EditorStartupMap = `/Game/FirstPerson/Menus/MenuPrincipal` (menú). GameInstance = `BP_Instancia_C` (no `BP_GameInstance`).

## Flujo Lab_Despues

```
PlayerStart (1110,-1531,420)
  → BP_Bienvenida (773,-1045,538): trigger → audio + subtítulos → RemoveWidget
  → BP_TourArrow_Guia (830,-525,262): flecha 1, visible inicio
  → BP_PuertaPrincipal (1110,-1531,420): abre con Lerp al entrar, muestra texto
  → BP_MetaZone (1266,-1888,305): overlap → activa ProximaFlecha → se destruye
  → BP_TourArrow (1266,-1878,350): flecha 2 (debe iniciar OCULTA)
  → 5× BP_ItemEPP (~1257,-1942): orden Gorro(0)→Bata(1)→Mascarilla(2)→Guantes(3)→Gafas(4)
  → 9× BP_PuertaInteriorAuto: RequiereEPPs bloquea si no hay EPPs
  → BP_MetaZone_Destino (1010,-1531,303)
```

NPCs: `NPC_Lab` y `BP_NPC_Lab2` — patrullan PuntoA↔PuntoB (Tick). Lógica idéntica; considerar unificar.

## Blueprints clave

| BP | Ruta | Variables clave |
|----|------|-----------------|
| `BP_FirstPersonCharacter` | `/Game/FirstPerson/Blueprints/` | `TieneEPPs`, `EPP_Contador`, `ActorMiradoActual`, `ActorInteractuable`, `FragmentoMiradoActual`, `FragmentosRecogidos`/`FragmentosTotal`, `WidgetInteractPrompt`, `bPinzaTomada` |
| `BP_ItemEPP` | `/Game/EPP/` | `NombreItem`, `bEsEPP`, `IndiceOrden` (0-4), `PrevioEPP` |
| `BP_TourArrow` | `/Game/Tour/` | `bArrived`, `TargetLocation`, `HeightOffset`, `ArrivalRadius`, `bAutoShow` |
| `BP_MetaZone` | `/Game/Tour/` | `ProximaFlecha` (ref a BP_TourArrow) |
| `BP_PuertaInteriorAuto` | `/Game/Fab/Puertas/puerta/Blueprints/` | `PuertaAbierta`/`PuertaCerrada` (rotaciones Lerp), `RequiereEPPs`, `ClaseAlerta`=WB_AlertaEPP_C, `ClasePrompt`=PuertaWidgetBlueprint_C |
| `BP_PuertaPrincipal` | mismas puertas | idem + `CylinderActor`, `GuiaInicial` |
| `BP_CilindroDestructible` | `/Game/Lab/Blueprints/` | `FlechaGuia` (BP_TourArrow_C), `CilindroVisual` (Actor) |

### EPPs → guía cilindro
Tras 5º EPP: `BP_FirstPersonCharacter.AgregarEPP` hace `GetAllActorsWithTag("ArrowMuestra")[0] → SetActorHiddenInGame(false) + SetActorTickEnabled(true)`. La flecha `BP_TourArrow_Muestra` (tag `ArrowMuestra`, TargetLocation=(2147,-973,304), oculta inicio) guía a `BP_CilindroDestructible_Meta` (tag `CilindroMetaTrigger`). Al pisarlo: PrintString("Vamos a mover la muestra", 3s) + destruye flecha, cilindro visual, y self.

### Puerta EPP flow
`BeginOverlap → EnableInput → CreateWidget(ClasePrompt)`. `E_Key → IF(RequiereEPPs) → true → GetTieneEPPs → IF(true) abre, IF(false) CreateWidget(ClaseAlerta)`. Puertas usan Lerp de rotación, no Timeline.

## Sistema de limpieza (Fase B)
En `BP_FirstPersonCharacter.EventTick`: line-trace → cast a BP_MatrazRota_C (path en `/Game/Fab/EscenaLimpieza/EstacionDerrames/MatrasRotaaglb/`). Componentes internos Pieza1–Pieza6 son StaticMeshComponent; se detectan por `GetObjectName(HitComponent)` contiene "Pieza". Con `bPinzaTomada=true` y mirando pieza → muestra prompt "Recoger fragmento de vidrio [R]". Presionar R (`IA_Recoger`) → `SetVisibility(false)+SetCollisionEnabled(NoCollision)` sobre el componente, `FragmentosRecogidos++`, comparar con `FragmentosTotal=6`.

### Assets limpieza
- BP_MatrazRota: `/Game/Fab/EscenaLimpieza/EstacionDerrames/MatrasRotaaglb/StaticMeshes/BP_MatrazRota`
- BP_Pinza: `/Game/Fab/EscenaLimpieza/EstacionDerrames/PinzaRecoger/StaticMeshes/BP_Pinza`
- BP_TachoCort: `/Game/Fab/EscenaLimpieza/EstacionDerrames/TachoCortopun/StaticMeshes/BP_TachoCort`
- Manager: `/Game/Lab/Blueprints/BP_EscenaLimpiezaManager`
- Interfaz: `/Game/Lab/Blueprints/BPI_LimpiezaCallbacks` (solo `OnTachoColocado`)

## Issues conocidos

1. **🔴 Flecha 2 visible al inicio**: instancia `BP_TourArrow` (1266,-1878) tiene `Hidden In Game=false`. Marcar `true` manualmente en nivel. Debe activarse via `BP_MetaZone → SetActorHiddenInGame(false)`.
2. **🔴 `BP_Centrifuge` inerte**: todos eventos deshabilitados.
3. **🟡 `BP_GuiaNavegacion`** no instanciado en nivel; Tick activo pero BeginPlay deshabilitado.
4. **🟡 PrintString debug** en `BP_PuertaPrincipal` — eliminar para release.
5. **🟡 Mensaje "Vamos a mover la muestra"** es PrintString; si no visible, reemplazar con widget UMG. No duplicar WB_AlertaEPP vía Python (WidgetTree inaccesible tras duplicate_asset).

## Configuración

- **UE 5.7**, DX12 SM6, OpenXR+HandTracking habilitado pero XR Framework inactivo en Lab_Despues.
- **Plugins**: UnrealMCP, Meshy, GameplayStateTree, WMFCodecs, ModelingTools.
- **LFS**: todo .uasset/.umap/.ubulk/.uexp rastreado vía Git LFS.
- **Input**: `E` = AbrirPuerta (interactuar con puertas). `R` = IA_Recoger (tomar pinza, recoger fragmentos). Enhanced Input con IMC_Default.
- **Rendering**: RayTracing=on, Nanite=off, Lumen HW=off, Substrate=on, Reflexión=Lumen (r.ReflectionMethod=2).
- **C++ source**: `/Script/Lab_Riesgos_UPEC` (heredado de TP_FirstPersonBP).
