# Migrar Lab_Riesgos_UPEC a otra computadora

Este repositorio contiene el proyecto Unreal Engine 5.7. La rama de trabajo es
`codex/optimizacion-empaquetado`. Para recuperar también la conexión de Codex
con el editor se instala VibeUE por separado, en un commit fijo, y se aplica
la corrección local incluida en `Patches/`.

## Requisitos en la PC nueva

- Windows, Unreal Engine **5.7**, Git y Git LFS. Ejecutar `git lfs install` una
  vez por usuario. El proyecto tiene C++; instalar Visual Studio 2022 con las
  herramientas C++, Unreal y Windows SDK indicadas en `.vsconfig` (Visual
  Studio Installer permite importar ese archivo).
- Conexión para descargar los objetos de Git LFS y el repositorio VibeUE.
  VibeUE requiere una clave de API propia, configurada en su interfaz; el token
  HTTP local del servidor MCP se configura aparte. No hay credenciales en Git.
- Para usar RV: runtime/controladores OpenXR y hardware compatible. Para
  empaquetar Android: SDK, NDK y JDK compatibles con UE 5.7 en la instalación
  local del motor. No se necesitan para abrir el proyecto en Windows.

## Clonar y abrir

```powershell
git lfs install
git clone --branch codex/optimizacion-empaquetado https://github.com/JaimePergueza/Lab_Riesgos_UPEC.git
cd Lab_Riesgos_UPEC
git lfs pull
git lfs fsck
```

Abrir `Lab_Riesgos_UPEC.uproject`. Aceptar la generación de archivos de
Visual Studio y la compilación de módulos C++ y plugins cuando Unreal la
solicite. El mapa de inicio configurado es
`/Game/FirstPerson/Menus/MenuPrincipal`; el laboratorio con medidas está en
`/Game/Maps/Lab_Despues`. `Content/Movies` contiene los videos usados por el
proyecto. Las configuraciones portables están en `Config/`; las clases C++ en
`Source/`; `Plugins/UnrealMCP`, `Plugins/meshy` y
`Plugins/BlueprintCommentTools` incluyen descriptor y código fuente.

`Content/__ExternalActors__` y `Content/__ExternalObjects__` son parte de los
mapas World Partition/One File Per Actor: conservarlos junto a los `.umap`.
Los `.uasset`, `.umap`, `.mp4` y demás binarios definidos en `.gitattributes`
se descargan con Git LFS. Si Unreal muestra archivos puntero pequeños en vez
de assets, ejecutar de nuevo `git lfs pull` antes de abrir el editor.

Los iconos y clases Java de `Build/Android/res` y `Build/Android/src` se
conservan por su personalización de Android. `Binaries`, `Intermediate`,
`Saved`, `DerivedDataCache`, empaquetados y el resto de `Build` se regeneran.

## Restablecer VibeUE y Codex/MCP

El VibeUE local usado para este proyecto proviene de
`https://github.com/kevinpbuckley/VibeUE.git`, commit
`c187526263c0fa5b2de41e83ac02a4538dc248e4`. Hay un cambio local para
evitar un `ensure` de UE 5.7 al cambiar padres de componentes Blueprint. El
parche está en `Patches/VibeUE-UE57-SCS-parentage.patch`; no depende de rutas
de esta PC. En una copia nueva, desde la raíz del proyecto:

```powershell
./scripts/install_vibeue.ps1
```

El script se detiene si `Plugins/VibeUE` ya existe para evitar sobrescribir
trabajo local. Si se instaló VibeUE por Fab, comprobar que su versión tenga la
misma API y aplicar/verificar la corrección equivalente manualmente; el flujo
reproducible es el script anterior. En Unreal, activar VibeUE en **Edit >
Plugins** y reiniciar el editor. Instalar/activar su dependencia
`PythonScriptPlugin` cuando Unreal lo pida. En **Tools > VibeUE > AI Chat**
introducir una clave de API válida. En **Project Settings > Plugins > VibeUE**,
habilitar el servidor MCP, usar puerto `8088` y elegir un **Bearer Token** local.
VibeUE puede requerir validar la clave de API en red al iniciar.

Crear la configuración local de Codex copiando
`migration/examples/codex-config.toml` a `.codex/config.toml`; sustituir
`REEMPLAZAR_TOKEN_LOCAL` por el Bearer Token configurado en VibeUE. Para
clientes que usan JSON, copiar `migration/examples/mcp.json` a `.mcp.json` o
`.cursor/mcp.json` y sustituir el mismo marcador. Estos archivos de destino
están ignorados por Git porque contienen el token; los ejemplos sí están
versionados. Codex se conecta a `http://127.0.0.1:8088/mcp`. Reiniciar Codex
después de cambiar la configuración y comprobar con una herramienta de lectura
de VibeUE (por ejemplo, descubrir una clase Python). El editor debe estar
abierto para que el servidor del puerto `8088` responda.

El plugin `Plugins/UnrealMCP` y `unreal_mcp_bridge.py` implementan un puente
TCP **heredado y separado** en `127.0.0.1:55557`. No es necesario para el
servidor VibeUE de `8088`. Si se necesita ese puente alternativo, instalar
Python 3 y `pip install -r requirements-mcp.txt`, y configurar el cliente MCP
para lanzar `unreal_mcp_bridge.py` como proceso stdio. No apuntar el cliente
HTTP de VibeUE al puerto TCP heredado.

## Archivos de importación y rutas locales

`MobileAssets/TouchButtons/Import_Mobile_Touch_Icons.json` y
`SourceAssets/PauseUI/import_pause_ui.json` guardan rutas relativas a la raíz
del repositorio. Sus `.png` de origen también están versionados. Si es
necesario repetir la importación en Unreal, ejecutar:

```powershell
./scripts/prepare_import_manifests.ps1
```

El script valida los archivos y genera manifiestos con rutas absolutas de la
PC nueva en `Saved/ImportManifests/`, carpeta local ignorada. Usar esos
manifiestos generados con la herramienta de importación de Unreal.

`next/.mcp-config.json` era una configuración local para el plugin **Aura**
del motor, con rutas `D:/UE/...`; Aura está deshabilitado en `.uproject` y ese
archivo no forma parte del proyecto migrable. Si se usa Aura en la PC nueva,
instalarlo y configurar sus rutas allí. Las rutas `/Game/...` de los `.ini` son
rutas virtuales de Unreal y no dependen de la unidad de disco.

## Comprobaciones después de clonar

```powershell
git status --short --branch
git lfs ls-files
git lfs fsck
```

El repositorio debería estar limpio antes de abrir Unreal. Tras abrirlo, las
carpetas regenerables ignoradas aparecerán localmente sin entrar en Git. No
se ha ejecutado una compilación ni una apertura de Unreal en una PC nueva como
parte de esta preparación; verificar en la nueva instalación que todos los
plugins compilen y que los mapas/medios se carguen correctamente.
