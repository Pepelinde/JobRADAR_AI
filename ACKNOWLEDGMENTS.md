# Autoría, fuentes y código de terceros

## Registro de esta entrega — 13/11/2026

| Elemento | Procedencia / contribución | Condiciones |
| --- | --- | --- |
| Idea y requisitos | Persona promotora, sin identificación personal en los archivos | Definición del alcance |
| Documentación y ejemplos | Redacción asistida por OpenAI Codex | Sin material externo copiado |
| Datos de empleo del flujo descrito | Empresas anunciantes, LinkedIn e InfoJobs | Sus autores conservan los derechos; no se distribuyen anuncios completos |
| Codex y Gmail | Servicios externos utilizados en el flujo | No son dependencias de código incluidas en esta entrega |

## Código incluido

`job_radar.py`, `test_job_radar.py` y los ejemplos ficticios de perfil/ofertas se han creado para este proyecto con asistencia de OpenAI Codex. Implementan fórmulas convencionales de TF-IDF, coseno y regresión logística, sin copiar código de terceros. Los módulos adicionales (`math`, `re`, `unicodedata`, `collections`, `datetime`, `urllib.request` y `unittest`) son de la biblioteca estándar de Python. No se redistribuyen modelos externos ni pesos preentrenados.

`configure_search.py` es código nuevo preparado para este proyecto con asistencia de OpenAI Codex. Los ejemplos JSON y las instrucciones también se han creado para esta entrega. No se han copiado fragmentos externos.

Utiliza `argparse`, `json` y `pathlib` de la biblioteca estándar de Python, mantenida por la comunidad de Python y distribuida por la Python Software Foundation. Python se instala por separado; su código no se redistribuye aquí. Referencias: [Python](https://www.python.org/), [licencia e historia](https://docs.python.org/3/license.html).

El generador no incluye conexiones a cuentas privadas ni modifica automatizaciones externas.

No se ha elegido una licencia de redistribución para el código propio ni se afirma que el repositorio sea software de código abierto. Antes de incorporar material ajeno hay que verificar su licencia: una cita no sustituye al permiso de reutilización.

## Registro obligatorio para futuras incorporaciones

Para cada biblioteca o fragmento de terceros, anotar:

- Nombre del componente y archivos afectados.
- Autor o titular indicado en el origen; no inferirlo a partir de quién subió una copia.
- URL original, versión o identificador de commit y fecha de consulta.
- Licencia y avisos de copyright, conservando el texto que exija esa licencia.
- Uso realizado y modificaciones propias.

Si el origen o el permiso son desconocidos, no presentarlo como código propio ni publicarlo hasta aclararlo. Identificar también el código nuevo generado con asistencia de IA, sin inventar autores o atribuirlo a los servicios que únicamente aportaron datos.
