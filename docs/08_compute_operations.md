# 08 · Operación del servidor Cronos

Verificación del 19 de noviembre de 2026 mediante SSH, autorizada por el usuario. Este documento posee el inventario y las condiciones operativas del servidor. El diseño experimental permanece en [04](04_solution_and_experiment_design.md) y la decisión de implementación en el [índice](00_INDEX.md).

## 1. Resultado sobre la GPU

Cronos tiene una **NVIDIA RTX A6000**, confirmada por PCI y `/proc/driver/nvidia`. El manual declara **48 GB de VRAM**; esa capacidad no pudo medirse mediante NVML con esta cuenta.

La cuenta de estudiantes **no tiene acceso GPU** en la configuración inspeccionada. Hay cuatro evidencias concordantes:

- `nvidia-smi` devuelve `Failed to initialize NVML: Insufficient Permissions`.
- Las ACL de `/dev/nvidia0` y `/dev/nvidiactl` incluyen `group:estudiantes:---`.
- Slurm tiene activo `JobSubmitPlugins=lua`. El archivo legible `/etc/slurm/job_submit.lua` aplica a la cuenta inspeccionada y rechaza solicitudes que incluyan GPU.
- El entorno provisto instala `torch==2.4.1+cpu` y `torchvision==0.19.1+cpu`.

`sinfo` anuncia `gpu:rtx_a6000:1` porque describe el nodo; ese anuncio no concede acceso al usuario. La presencia de `nvcc` tampoco lo concede. No se intentó sortear las restricciones ni enviar un trabajo GPU. La afirmación de disponibilidad GPU comunicada verbalmente requiere una habilitación administrativa antes de incorporarse al presupuesto.

## 2. Hardware y límites efectivos

| Ámbito | Estado verificado | Evidencia o límite |
|---|---|---|
| Sistema | Ubuntu 22.04 LTS, kernel 6.8.0-138-generic, x86_64 | Consulta remota. |
| Procesador | 2 × Intel Xeon Gold 6138 a 2,00 GHz | `lscpu`: 20 núcleos por socket, 2 hilos por núcleo, 80 CPU lógicas. |
| RAM física | Aproximadamente 1 TiB compartido | `free -h`; no corresponde a la asignación de un grupo. |
| Almacenamiento | ext4, volumen compartido de aproximadamente 1,8 T | Cerca de 1,2 T disponibles en la inspección; cambia con el uso de todos los grupos. |
| Partición | `estudiantes`, activa | Slurm 21.08.5; un nodo. |
| CPU para estudiantes | Hasta 64 CPU por nodo en esa partición | `MaxCPUsPerNode=64`; compartidas entre grupos. |
| CPU por trabajo | Máximo 4 | Regla activa en `job_submit.lua`. |
| Memoria por trabajo | 4.096 MiB por CPU por defecto; máximo 32.768 MiB | Configuración de partición; con 4 CPU, valor predeterminado de 16 GiB. |
| Duración por trabajo | Máximo 24 horas | `MaxTime=1-00:00:00`. |
| Concurrencia de la cuenta | 2 trabajos en ejecución, hasta 10 enviados | Asociación de Slurm: `MaxJobs=2`, `MaxSubmitJobs=10`. |
| Recursos agregados de la cuenta | 8 CPU y 64 G de memoria configurados | Asociación `GrpTRES=cpu=8,mem=64G`; no son recursos reservados. |
| Sesión SSH | Cuota de CPU equivalente a 2 CPU; memoria máxima de 32 GiB | Cgroup del usuario: `cpu.max=200000 100000`, `memory.max=34359738368`. |
| GPU | Existente y bloqueada para la cuenta | Evidencias de la sección 1. |

La máscara de afinidad de la sesión muestra las 80 CPU, pero su cuota sigue siendo 2 CPU. El trabajo pesado se envía con Slurm. Los límites de asociación y de partición son configuración observada; no se sometieron a una prueba de carga o de memoria.

Una solicitud CPU de 4 CPU, 32 G y un minuto pasó `sbatch --test-only`. Esto valida la solicitud sin enviar ni ejecutar un trabajo. La cola estaba vacía en la inspección; no acredita disponibilidad futura.

## 3. Conexión y directorios

La conexión SSH desde la terminal local funcionó. Dirección, puerto, usuario y contraseña se conservan fuera del proyecto, en un archivo de configuración privado de la máquina local con permisos `600` y directorio `700`. No deben copiarse a documentación pública, comandos registrados, argumentos de contraseña o Git. El archivo contiene valores literales y no se ejecuta con `source`.

El reloj del servidor reportó desfase UTC−03:00, dos horas por delante de Bogotá. Se debe conservar el desfase en la evidencia de corridas y distinguirlo de la zona del cierre del reto.

Se registró la clave ED25519 presentada en la primera conexión en un archivo local de hosts conocidos. Las conexiones posteriores exigieron esa misma clave. No se ha contrastado su huella por un canal independiente del administrador.

Conexión manual con los valores privados:

```bash
ssh -p <puerto> <usuario>@<host>
```

| Ruta remota | Uso y estado observado |
|---|---|
| `$HOME` / `~` | Carpeta inicial de la cuenta, permisos `700`. |
| `~/Dataset/Train.zip` | Archivo de 7.027.722.880 bytes, no modificable por la cuenta. |
| `~/Dataset/Test.zip` | Archivo de 1.900.849.176 bytes, no modificable por la cuenta. Se comprobó existencia y permiso, sin abrir su contenido. |
| `~/ejemplo/` | Scripts y lanzadores `.sbatch` provistos por los organizadores, además de una muestra. No se ejecutaron. |
| `~/resultados/` | Directorio provisto para métricas y modelos; sin resultados en la inspección. |
| `~/venv_entrenamiento/` | Entorno virtual Python provisto; ocupa aproximadamente 4 G. |
| `/opt/wheels_estudiantes/` | Catálogo local para instalar dependencias sin internet; 150 archivos observados. |

El manual permite descomprimir los datos necesarios dentro de `~/Dataset`. Esta inspección no extrajo archivos ni accedió a los payloads del test. La equivalencia entre el archivo train del servidor y el dataset local todavía no se ha comprobado.

Para una futura implementación, se propone `~/LatamIAChallenge/` para el código y `~/resultados/<run_id>/` para artefactos, manteniendo los datos en `~/Dataset`. Estas rutas de proyecto aún no se han creado. No se inspeccionaron carpetas personales de otros grupos.

## 4. Entorno disponible

La sesión SSH no interactiva no activó automáticamente el entorno. Debe activarse explícitamente en cada lanzador:

```bash
source ~/venv_entrenamiento/bin/activate
python --version
```

| Dependencia | Versión observada |
|---|---|
| Python | 3.10.12 |
| PyTorch / torchvision | 2.4.1+cpu / 0.19.1+cpu |
| NumPy / SciPy | 1.26.4 / 1.15.3 |
| scikit-learn / pandas | 1.5.2 / 2.2.3 |
| OpenCV contrib / MediaPipe | 4.10.0.84 / 0.10.14 |
| JupyterLab / ipykernel | 4.6.6 / 7.3.0 |
| tqdm | 4.70.1 |

Hay `git`, `rsync`, `unzip`, `zip`, `tmux`, `sbatch`, `srun` y `nvcc`. `ffmpeg` y `ffprobe` no aparecieron en el `PATH` inspeccionado. No se localizaron distribuciones instaladas de `timm`, `transformers`, `einops` o Lightning en el entorno consultado. No se instalaron paquetes ni se comprobó la conectividad saliente para descargar pesos.

El manual permite dependencias en entornos del usuario y describe recuperación mediante el catálogo offline. Prohíbe `sudo`, `apt` y Docker. No se probaron privilegios elevados.

## 5. Uso posterior y conservación

Para trabajos autorizados, los lanzadores deben declarar partición, CPU, memoria y tiempo; activar el entorno y limitar los hilos de las bibliotecas al recurso solicitado. Consultas operativas de solo lectura:

```bash
sinfo -o '%P %a %l %D %c %m %G'
squeue -u "$USER"
scontrol show partition estudiantes
sacct -u "$USER" --format=JobID,JobName,State,Elapsed,AllocCPUS,MaxRSS
df -h "$HOME"
```

El inventario confirma utilidad para el primer perfil compacto medido y potencial para preparación de datos; otros perfiles requieren sus propios pilotos. GPU local y Colab conservan sus condiciones documentadas en [01](01_problem_definition.md); Cronos no aporta GPU utilizable bajo los permisos actuales.

El primer piloto CPU autorizado ya se ejecutó mediante Slurm; su [evidencia por criterio](../openspec/changes/archive/2026-11-19-cpu-pilot-walking-path/tasks.md) posee duración, recursos, restauración y límites, sin generalizarlos a otros modelos. Se observó `KillWait=30s` al preparar esa ejecución. El ledger activo del proyecto está en `~/resultados/lsc5/budget.json`; copias recuperadas locales son snapshots privados, no saldos adicionales. Los trabajos se presentaron retenidos, se vincularon con su reserva y se liberó únicamente el job propio.

El incremento posterior [R2-E01](../openspec/changes/archive/2026-11-19-cpu-baseline-loso/tasks.md) ejecutó tres folds completos con el mismo procedimiento, verificó nuevamente KillWait y recuperó código/resultados localmente. Su límite específico se agregó al ledger sin reiniciar el historial.

El acceso funcionó el 19 y20 de noviembre, después de la ventana pública originalmente anunciada. **No hay fecha confirmada de retiro**, garantía de respaldo ni política de borrado acreditada. El manual describe disco compartido sin cuota automática; no se comprobó ausencia de otras restricciones. Se deben conservar copias autorizadas de código y artefactos antes de depender de esta infraestructura.

## 6. Procedencia y límites

Fuentes primarias: *Manual de usuario · Servidor EMC2 (cronos) · Grupos de estudiantes*, versión 1.1 del 16 de noviembre de 2026, secciones 3–7; `LEEME.txt` de la cuenta; configuración y respuestas del sistema consultadas el 19 de noviembre. La evidencia bruta de la inspección y del seguimiento se conserva en privado, fuera del repositorio.

La inspección inicial creó únicamente archivos locales de autenticación, clave de host y evidencia; no modificó configuraciones remotas ni inició entrenamiento. Los incrementos posteriores autorizados sí transfieren código/cachés privados y ejecutan trabajos CPU, con evidencia en sus ítems. El estado operativo y los permisos pueden cambiar; antes de aprovechar una habilitación GPU futura se deben volver a comprobar la política, el acceso al dispositivo y el entorno.


El incremento R2.2 usa una carpeta nueva de código/caché opaca y el mismo ledger activo. La preparación de secuencias se incluye dentro del piloto Slurm, a partir del archivo train ya presente; se verifican hashes individuales contra el manifiesto local. No se transfiere el dataset completo ni se extraen videos. Los lanzadores temporales separan5/15min de TimeLimit y360/960s de reserva; KillWait30s se vuelve a verificar al presentar trabajos. Se mantiene máximo dos jobs activos y no se entrena en login. Snapshots locales preservan productor y artefactos para reproducibilidad; el plazo de retiro sigue sin confirmarse.
