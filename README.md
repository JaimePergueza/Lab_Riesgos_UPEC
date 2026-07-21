# Lab_Riesgos_UPEC

Simulador en **Realidad Virtual (RV)** desarrollado con **Unreal Engine 5.7** para la **prevención de riesgos laborales** en laboratorios de microbiología/biotecnología.

Proyecto de tesis — Universidad Politécnica Estatal del Carchi (UPEC).  
Se evaluó la **aceptación tecnológica (TAM)** y la **usabilidad (SUS)** del simulador como herramienta de capacitación en seguridad laboral mediante RV.

## Requisitos

- Unreal Engine 5.7
- Git + Git LFS
- Plugin **VibeUE** (instalar manualmente)
- Casco de RV compatible con OpenXR (opcional para edición)

## Clonar

```powershell
git lfs clone https://github.com/JaimePergueza/Lab_Riesgos_UPEC.git
```

Abrir `Lab_Riesgos_UPEC.uproject` — el motor regenerará `Binaries/` e `Intermediate/`.

## Plugins habilitados

- UnrealMCP
- ModelingToolsEditorMode
- GameplayStateTree
- WMFCodecs
- OpenXR + HandTracking
- Meshy

## Mapas activos

| Mapa | Ruta |
|------|------|
| Menú principal | `/Game/FirstPerson/Menus/MenuPrincipal` |
| Laboratorio (con medidas) | `/Game/Maps/Lab_Despues` |

## Controles

- **E** — Interactuar (puertas, EPPs)
- **R** — Recoger pinza / fragmentos de vidrio
- Movimiento WASD + ratón (estándar FirstPerson)
- OpenXR + HandTracking para interacción en RV

## Configuración inicial

1. Clonar con `git lfs clone`
2. Instalar **VibeUE** plugin en la PC de destino
3. Copiar `.mcp.json` local si se trabaja con MCP
4. Abrir `.uproject` y esperar a que compile
