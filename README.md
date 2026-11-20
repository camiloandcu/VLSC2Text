# LatAm IA Challenge · LSC5

Proyecto de reconocimiento de cinco señas aisladas de Lengua de Señas Colombiana a partir de video y landmarks. El objetivo de competición es generalizar a una persona ausente del entrenamiento, evaluado mediante accuracy top-1.

Clases: **Café, Aromática, Hola, Qué necesitas y Con gusto**. La entrega prevista incluye pesos, código de entrenamiento/inferencia, predicciones CSV y reporte técnico. Cierre comunicado por el equipo: **25 de noviembre de 2026, hora de Bogotá**; hora exacta pendiente.

## Estado

El proyecto cuenta con una auditoría de entrenamiento, una revisión de 87 recursos disponibles y un protocolo experimental. El código implementa estadísticas de landmarks opacos, MLP y TCN de secuencias opacas en CPU, con evaluación LOSO de recetas fijas de80 épocas, con restauración desde originales y agregación OOF verificable. El piloto visual congelado en GPU local completó30 clips y verificó el replay de un clip en otro proceso; la extracción completa y tres cabezas RGB LOSO terminaron, pero la restauración desde originales falló; ese resultado visual permanece provisional. El estado y las decisiones de cada etapa están en el [índice del proyecto](docs/00_INDEX.md).

## Documentación

- [Problema y reglas](docs/01_problem_definition.md).
- [Evidencia de datos](docs/02_data_audit.json).
- [Estado del arte](docs/03_state_of_art.md) e [índice de fuentes](literature/README.md).
- [Alternativas y protocolo experimental](docs/04_solution_and_experiment_design.md).
- [Arquitectura técnica](docs/05_technical_architecture.md).
- [Implementación, verificación e iteración](docs/06_delivery_and_iteration_plan.md).
- [Resultados, reporte y posible artículo](docs/07_results_and_publication_protocol.md).
- [Recursos comprobados y operación de Cronos](docs/08_compute_operations.md).

## Datos y reproducción

LSC5 fue suministrado para el reto por sus organizadores. Los videos y landmarks originales se mantienen fuera del repositorio público; sus condiciones de uso y redistribución requieren confirmación. El test está reservado a inferencia de un modelo fijado.

El paquete inicial usa Python 3.10 y PyTorch CPU. Preparación con `uv`:

```bash
uv venv --python 3.10 .venv
uv pip install --python .venv/bin/python -r requirements/dev.txt
uv pip install --python .venv/bin/python --no-deps -e .
.venv/bin/python -m pytest -q
```

Los comandos disponibles y el recorrido CPU están en la [arquitectura](docs/05_technical_architecture.md). La CLI trabaja exclusivamente con train e incluye el piloto RGB con entorno CUDA separado; añade extracción visual completa y una cabeza RGB con gates de costo/restauración; la inferencia del test sigue fuera de este incremento. La línea base MLP obtuvo60,98% de accuracy LOSO en desarrollo; la TCN opaca obtuvo48,89% y no la superó. RGB suma41,24% provisional; falta restauración completa, por lo que no constituye una candidata aceptada. Resultados por persona y límites en el [registro de resultados](docs/07_results_and_publication_protocol.md). El piloto de dos épocas conserva su carácter diagnóstico; todavía no hay puntuación oficial.

## Alcance y atribución

Este proyecto clasifica clips delimitados dentro de un vocabulario de cinco clases. Sus resultados futuros no acreditarán por sí solos traducción continua ni cobertura de toda la LSC.

Las referencias bibliográficas y condiciones conocidas de recursos externos están en el índice de investigación. La licencia del código propio está pendiente de elección; los datos, pesos y componentes de terceros mantienen sus términos particulares.
