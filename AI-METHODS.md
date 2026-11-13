# Métodos implementados en Job Radar

## Generador de instrucciones

`configure_search.py` **no implementa ningún algoritmo de aprendizaje automático** ni llama a una API de IA. Lee JSON, valida listas, elimina textos duplicados exactos y rellena una plantilla de instrucciones. La misma entrada produce la misma salida.

| Método preguntado | ¿Se implementa en configure_search.py? |
| --- | --- |
| Regla de Bayes / clasificador bayesiano | No |
| Simulación Monte Carlo | No |
| Regresión | No |
| Vecinos más cercanos (k-NN) | No |
| Entrenamiento o inferencia de un modelo propio | No |

La eliminación de textos repetidos con `dict.fromkeys()` es una operación de programación convencional, no un modelo de IA. Tampoco comprueba si dos anuncios son la misma vacante: solo limpia listas de configuración.

## Nuevo comparador: job_radar.py

El comparador sí implementa **TF-IDF y similitud del coseno**, reglas explícitas y **regresión logística opcional** con descenso de gradiente y regularización L2. Se entrena únicamente cuando se aportan valoraciones humanas de relevancia. No se distribuye un modelo entrenado con datos reales ni evaluado. Las puntuaciones no son probabilidades de contratación.

La similitud usa palabras compartidas, no embeddings ni comprensión semántica profunda. No se implementan Bayes, Monte Carlo ni k-NN. [MATCHING.md](MATCHING.md) documenta fórmulas, datos, límites, entrenamiento y pruebas.

## Dónde interviene el asistente de lenguaje

La IA ha asistido en la creación del código y la documentación. Además, el texto generado puede utilizarse posteriormente con un asistente de IA con búsqueda para interpretar y resumir ofertas. Ese asistente es externo al programa: el repositorio no lo ejecuta ni incorpora su modelo.

Ninguno de los módulos llama a un modelo de lenguaje. El comparador puntúa ofertas respecto al perfil, no candidatos para una empresa. No se han medido precisión o exhaustividad en ofertas reales.

## Posible evolución

El siguiente paso sería evaluar con datos representativos, estabilizar el vocabulario/IDF entre lotes y contrastar si la regresión mejora las recomendaciones frente al índice manual. No se debe atribuir al modelo precisión real sin esa evaluación.

---

## English summary

The instruction generator remains a deterministic template without ML. The new matcher implements explicit rules, TF-IDF cosine similarity and optional logistic regression trained on human relevance labels. Neither module calls an LLM or implements Bayes, Monte Carlo or k-NN. No model trained on real data or validated hiring predictions are provided.
