# Comparador de ofertas

Python 3.10+, sin paquetes adicionales. No conecta cuentas, no envía mensajes ni modifica alertas externas. Los ejemplos son inventados; `example.invalid` no es un portal de candidaturas.

## Demostración

```sh
python job_radar.py rank --profile profile.example.json --source offers.example.json
```

Devuelve JSON con cobertura y ofertas ordenadas. Las excluidas quedan al final con `eligible: false` y motivos: no deben mostrarse como recomendaciones. `score` es un índice heurístico de 0 a 100, no una probabilidad de contratación ni un porcentaje validado de compatibilidad.

Repite `--source` para importar varios archivos o feeds JSON HTTPS autorizados. Los fallos quedan registrados y se conserva lo importado de otras fuentes. Si fallan todas, termina con código 2 y no declara «sin ofertas». **No hay conectores específicos de LinkedIn o InfoJobs**: sus páginas HTML no son feeds JSON. La incorporación de esas plataformas requiere conectores con acceso autorizado.

## Datos

Copia el perfil a `profile.local.json`, excluido de Git. Usa listas en `locations`, `positions`, `skills`; las dos primeras son obligatorias. `summary` es texto opcional y `years_experience` un número no negativo o `null` si no consta.

Las posiciones guían la similitud; no son filtros literales excluyentes. Las ubicaciones se comparan por nombre exacto normalizado, sin acentos ni distinción de mayúsculas. No hay geocodificación: una ciudad no se reconoce automáticamente dentro de una provincia. Usa nombres consistentes entre perfil y ofertas. La antigüedad global no acredita experiencia en una herramienta concreta.

Una fuente contiene una lista JSON o `{"items": [...]}`. Cada oferta necesita `id`, `title`, `company`, `location`, `description`, `url`. Admite `required_skills`, `min_years`, `contract`, `salary`, `work_mode`, `published_at`, `expires_at`, `verified_at` y `status` (`open`, `unverified`, `closed`, `expired`). Fechas ISO 8601. `null` representa información desconocida. Los campos se aportan explícitamente: no se extraen automáticamente de HTML.

El estado abierto y la fecha de verificación son afirmaciones de la fuente: el programa no visita el anuncio para comprobarlos. Se excluyen ofertas cerradas o vencidas. Se deduplica por URL exacta o título/empresa/ubicación normalizados, conservando la primera fuente. Esta heurística puede fusionar plazas distintas o dejar pasar variantes.

## Método

1. Tokenización y normalización del perfil y los anuncios.
2. TF-IDF con frecuencia relativa e IDF suavizado `log((1+n)/(1+df))+1`.
3. Similitud del coseno entre perfil y oferta.
4. Comparación de competencias declaradas y experiencia. La información ausente queda pendiente, sin inventar coincidencias.
5. Índice `100 × (0.55 × coseno + 0.30 × cobertura_competencias + 0.10 × ubicación + 0.05 × experiencia)`.

Los pesos son decisiones iniciales sin validación empírica. Se comparan palabras, no embeddings: no se reconocen sinónimos automáticamente. El IDF depende del lote de ofertas y sus cambios pueden alterar las puntuaciones.

## Regresión logística opcional

Implementada con descenso de gradiente y regularización L2. Requiere al menos 20 valoraciones y ambas clases; es un mínimo técnico, no garantía de suficiencia estadística. No se distribuye un modelo preentrenado ni datos personales.

Cada entrada de `feedback.local.json` contiene:

```json
{"features": [0.45, 0.5, 1, 0], "relevant": 1}
```

Copia `features` del resultado valorado: coseno, cobertura de competencias, ubicación, experiencia. `relevant` es una valoración humana, 1 relevante o 0 no relevante. No fabriques etiquetas usando el propio índice: sería aprendizaje circular.

```sh
python job_radar.py train --feedback feedback.local.json > model.local.json
python job_radar.py rank --profile profile.local.json --source offers.local.json --model model.local.json
```

Con modelo se ordenan las ofertas elegibles por `estimated_relevance`. Es una salida probabilística **sin calibración ni evaluación independiente**, no una probabilidad de contratación. El modelo queda marcado `evaluated: false`. Antes de uso productivo deben separarse entrenamiento y evaluación, evitar duplicados entre conjuntos y medir precisión, exhaustividad y calibración con ejemplos representativos. También debe estabilizarse la generación de características: el TF-IDF actual depende del lote; se recomienda persistir vocabulario/IDF antes de entrenar un modelo de producción.

No se implementan Bayes, k-NN ni Monte Carlo. No se presentan candidaturas.

## Pruebas

```sh
python -m unittest -v test_job_radar.py
```

Los casos sintéticos comprueban cálculo, reglas, datos ausentes, duplicados y fallos de fuentes. No miden rendimiento en vacantes reales.

## Autoría

Código y ejemplos creados para el proyecto con asistencia de OpenAI Codex, sin copiar implementaciones externas. Solo biblioteca estándar de Python, acreditada en `ACKNOWLEDGMENTS.md`.

## English summary

The local prototype imports JSON files or authorized HTTPS JSON feeds, applies explicit rules and TF-IDF cosine similarity, and optionally trains binary logistic regression from human relevance labels. It does not scrape platforms, call an LLM, send email or modify external alerts. All examples are fictional. Location matching is exact after normalization. Unknown qualifications remain unconfirmed. Scores and unevaluated logistic outputs are not hiring probabilities. Synthetic tests do not establish real-world accuracy.
