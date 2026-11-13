# ¿Qué métodos de IA utiliza este proyecto?

## Código actual

`configure_search.py` **no implementa ningún algoritmo de aprendizaje automático** ni llama a una API de IA. Lee JSON, valida listas, elimina textos duplicados exactos y rellena una plantilla de instrucciones. La misma entrada produce la misma salida.

| Método preguntado | ¿Se implementa en el código actual? |
| --- | --- |
| Regla de Bayes / clasificador bayesiano | No |
| Simulación Monte Carlo | No |
| Regresión | No |
| Vecinos más cercanos (k-NN) | No |
| Entrenamiento o inferencia de un modelo propio | No |

La eliminación de textos repetidos con `dict.fromkeys()` es una operación de programación convencional, no un modelo de IA. Tampoco comprueba si dos anuncios son la misma vacante: solo limpia listas de configuración.

## Dónde interviene la IA

La IA ha asistido en la creación del código y la documentación. Además, el texto generado puede utilizarse posteriormente con un asistente de IA con búsqueda para interpretar y resumir ofertas. Ese asistente es externo al programa: el repositorio no lo ejecuta ni incorpora su modelo.

Las técnicas descritas en el README para el flujo asistido no deben confundirse con funciones ya implementadas aquí. No hay entrenamiento, puntuación automática de candidatos ni métricas de precisión o exhaustividad.

## Posible evolución

Un futuro módulo podría comparar textos mediante representaciones vectoriales y similitud, o aprender a ordenar ofertas a partir de ejemplos evaluados por personas. Eso requeriría datos apropiados, una implementación adicional y evaluación. No se debe afirmar que existe ni atribuirle resultados mientras no se haya desarrollado y comprobado.

---

## English summary

The current Python script is a deterministic instruction-template generator. It does not implement Bayes, Monte Carlo, regression, k-NN, model training or AI API calls. Exact duplicate removal is ordinary list processing, not machine learning or job-listing deduplication. AI assisted in creating the project, and an external AI assistant may later use the generated instructions; that assistant is not executed by this repository.
