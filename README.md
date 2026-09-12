![Logo](Logo.png)

# Lab_Riesgos_UPEC

Simulador en **Realidad Virtual (RV)** desarrollado con **Unreal Engine 5.7** para la **prevención de riesgos laborales** en laboratorios de microbiología/biotecnología.

Proyecto de tesis — Universidad Politécnica Estatal del Carchi (UPEC).  
Se evaluó la **aceptación tecnológica (TAM)** y la **usabilidad (SUS)** del simulador como herramienta de capacitación en seguridad laboral mediante RV.

## Requisitos

- Unreal Engine 5.7
- Git + Git LFS
- Casco de RV compatible con OpenXR (opcional para edición)

## Clonar

```powershell
git clone --branch codex/optimizacion-empaquetado https://github.com/JaimePergueza/Lab_Riesgos_UPEC.git
cd Lab_Riesgos_UPEC
git lfs pull
```

Abrir `Lab_Riesgos_UPEC.uproject` — el motor regenerará los archivos necesarios automáticamente.

Para instalar las dependencias, reconstruir VibeUE y conectar Codex/MCP en otra PC, sigue [MIGRACION.md](MIGRACION.md).

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
