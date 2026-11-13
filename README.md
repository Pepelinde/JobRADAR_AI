# Job Radar

**Español** | [English](README.en.md)

Proyecto configurable de búsqueda asistida de empleo: elige ubicaciones, puestos y palabras clave.

**Nuevo: comparador local.** Importa ofertas JSON, aplica reglas y TF-IDF/coseno, y admite regresión logística opcional con valoraciones humanas. [Guía, demostración y límites](MATCHING.md).

```sh
python job_radar.py rank --profile profile.example.json --source offers.example.json
```

Ejemplos ficticios. No hay conectores específicos de plataformas ni envío automático.

### Funciones implementadas

| Función | Comportamiento actual |
| --- | --- |
| Configuración de búsquedas | Ubicaciones, puestos, palabras clave y competencias confirmadas; opciones de archivo o línea de comandos |
| Importación de ofertas | Archivos JSON o varios feeds JSON HTTPS autorizados mediante `--source` repetido |
| Cobertura de fuentes | Registra éxitos y errores; conserva otras fuentes ante fallos y termina con código 2 si fallan todas |
| Validación | Comprueba campos obligatorios, URL, fechas, listas y experiencia numérica no negativa |
| Deduplicación | URL exacta o combinación normalizada de título, empresa y ubicación; conserva la primera fuente |
| Reglas de exclusión | Ubicación no elegida, estado cerrado/vencido o fecha límite pasada |
| Comparación del perfil | Competencias declaradas y antigüedad; los datos desconocidos se muestran como pendientes |
| TF-IDF y coseno | Compara palabras del perfil y de cada oferta mediante vectores de texto |
| Índice explicable | Combina coseno, competencias, ubicación y experiencia con pesos manuales |
| Regresión logística opcional | Aprende de valoraciones humanas de relevancia y permite ordenar usando el modelo guardado |
| Informe JSON | Incluye puntuaciones, coincidencias, requisitos pendientes, exclusiones, fuentes y condiciones publicadas |
| Ejemplos y pruebas | Perfil y ofertas ficticios; 10 pruebas sintéticas superadas, sin medir precisión real |

Las ofertas excluidas permanecen al final del informe con `eligible: false`; no deben tratarse como recomendaciones. El programa no visita los anuncios para verificar su vigencia: identifica lo declarado por la fuente.

### Archivos principales

- [`configure_search.py`](configure_search.py): generador comentado de instrucciones de búsqueda.
- [`job_radar.py`](job_radar.py): importación, reglas, TF-IDF/coseno, clasificación y entrenamiento.
- [`search.example.json`](search.example.json): configuración ficticia del generador.
- [`profile.example.json`](profile.example.json) y [`offers.example.json`](offers.example.json): datos ficticios del comparador.
- [`test_job_radar.py`](test_job_radar.py): pruebas de reglas, similitud, aprendizaje y fallos de fuentes.
- [`MATCHING.md`](MATCHING.md): esquema de datos y guía técnica; [`AI-METHODS.md`](AI-METHODS.md): alcance de los métodos de IA.

## 1. Your idea in a nutshell — La idea en pocas palabras

**Job Radar** ayuda a encontrar oportunidades de trabajo relacionadas con un perfil profesional y contrastar sus requisitos. Cada persona puede elegir sus ubicaciones, puestos y palabras clave.

El proyecto combina búsqueda en fuentes públicas, asistencia de IA y revisión de la evidencia. Cada recomendación explica su encaje, los requisitos pendientes de confirmar y las limitaciones de acceso a la oferta.

## 2. Background — Contexto y motivación

Las ofertas están repartidas entre portales y páginas de empresas. Una misma vacante puede aparecer repetida, republicada o seguir indexada después de cerrarse. Revisar estas fuentes y compararlas con un perfil consume tiempo cada día.

La motivación del proyecto es facilitar una búsqueda configurable en varias zonas geográficas, sin dar por supuesta una experiencia específica que la persona no haya acreditado.

Es un problema recurrente durante una búsqueda activa. Este proyecto no aporta una medición estadística de su frecuencia en la población; aborda una necesidad observada en el uso diario. Resulta interesante porque la utilidad de la IA depende tanto de encontrar resultados como de reconocer qué información falta o no puede comprobarse.

## 3. Data and AI techniques — Datos y técnicas de IA

### Fuentes de datos

- Perfil profesional aportado voluntariamente por la persona usuaria: formación, experiencia y competencias confirmadas.
- Anuncios públicos de LinkedIn Empleos e InfoJobs.
- Páginas de empleo de empresas y consultoras, preferidas cuando permiten contrastar el anuncio original.
- Historial de ofertas y envíos para evitar duplicados.

Se pueden consultar páginas públicas y contenido indexado cuando el acceso directo falla. Esto no implica disponer de acceso autenticado a los portales ni a sus bases de datos completas. Un resultado indexado no acredita por sí solo que una vacante siga abierta.

### Técnicas utilizadas en el flujo asistido

Las técnicas de este apartado describen el uso con un asistente externo. El código local implementa las reglas y métodos numéricos detallados a continuación, sin llamadas a un modelo de lenguaje.

- Expansión de consultas con sinónimos técnicos: PLC, autómatas programables, automatización, HMI, SCADA, Siemens/TIA Portal, STEP 7, Rockwell, Schneider u Omron.
- Interpretación semántica mediante un modelo de lenguaje para relacionar requisitos de las ofertas y datos confirmados del perfil.
- Extracción y resumen de título, empresa, ubicación, fecha, contrato, salario, modalidad y requisitos.
- Comparación de título, empresa, ubicación, enlaces y funciones para identificar duplicados y republicaciones.
- Redacción de motivos de encaje y carencias de información con enlaces a las fuentes.

Las marcas y herramientas usadas para buscar no se convierten automáticamente en competencias de la persona. No se distribuye un modelo entrenado con datos reales ni se han medido precisión o exhaustividad. El comparador implementa deduplicación heurística y clasificación logística opcional; no incluye una base de datos persistente.

### Métodos numéricos del comparador

El texto se normaliza y tokeniza. TF-IDF usa frecuencia relativa e IDF suavizado `log((1+n)/(1+df))+1`; el coseno mide la coincidencia entre los vectores del perfil y cada oferta. No usa embeddings ni reconoce sinónimos automáticamente.

El índice inicial es `100 × (0.55 × coseno + 0.30 × cobertura_competencias + 0.10 × ubicación + 0.05 × experiencia)`. Los pesos son decisiones iniciales, no valores aprendidos ni validados. La regresión logística opcional usa esas cuatro características y aprende mediante descenso de gradiente con regularización L2. No se implementan Bayes, Monte Carlo ni k-NN.

### Estado real del proyecto

El código está comentado por funciones y pasos. El generador y el comparador son módulos distintos; este último implementa coseno y regresión logística opcional. Véase [AI-METHODS.md](AI-METHODS.md).

Este repositorio incluye un **generador local de instrucciones de búsqueda** y un comparador local. El comparador importa archivos o feeds JSON autorizados; no recoge páginas HTML de portales ni envía correos. No es una aplicación autónoma de alertas. Clonarlo o cambiar su configuración no modifica ninguna alerta externa.

No se incluyen credenciales, datos de destinatarios, historial personal ni copias completas de anuncios.

## 4. How is it used — Uso y personas afectadas

### Comparar ofertas con el perfil

Requiere Python 3.10+, sin instalar paquetes adicionales. Copia el perfil a `profile.local.json` e introduce ubicaciones, puestos, competencias, resumen y años de experiencia (`null` si no constan). Importa ofertas con el esquema de [MATCHING.md](MATCHING.md):

```sh
python job_radar.py rank --profile profile.local.json --source offers.local.json
```

Para combinar fuentes locales, repite la opción:

```sh
python job_radar.py rank --profile profile.local.json --source offers-a.local.json --source offers-b.local.json
```

También admite una URL HTTPS que devuelva JSON con el esquema esperado. Los portales HTML habituales no se pueden pasar directamente como feeds.

### Entrenar y aplicar la regresión logística

Prepara `feedback.local.json` con al menos 20 valoraciones, incluyendo relevantes y no relevantes. Cada entrada contiene `features` copiado del resultado y una etiqueta humana `relevant` de 0 o 1. Ese mínimo permite ejecutar el programa, pero no garantiza un entrenamiento de calidad. No deben fabricarse etiquetas a partir de la puntuación del propio programa.

```json
{"features": [0.45, 0.5, 1, 0], "relevant": 1}
```

```sh
python job_radar.py train --feedback feedback.local.json > model.local.json
python job_radar.py rank --profile profile.local.json --source offers.local.json --model model.local.json
```

Con modelo, el informe añade `estimated_relevance` y lo usa para ordenar las ofertas elegibles. El modelo queda marcado `evaluated: false`. Ni esta estimación ni el índice manual representan una probabilidad de contratación. Los archivos `*.local.json` están excluidos de Git.

### Ejecutar las pruebas

```sh
python -m unittest -v test_job_radar.py
```

Las 10 pruebas cubren coseno, reglas de ubicación/cierre/caducidad, experiencia desconocida, datos inválidos, duplicados, fallos parciales/totales, importación HTTPS simulada, aprendizaje logístico y conservación de exclusiones al usar un modelo. Son verificaciones con datos sintéticos; no una evaluación de recomendaciones reales.

### Generar instrucciones para un asistente externo

La persona elige las ubicaciones y posiciones en un archivo local y genera las instrucciones. Las usa con un asistente con acceso a búsqueda, revisando antes el contenido. La frecuencia y los canales de entrega se configurarían por separado en el entorno que ejecute la búsqueda; el generador no crea tareas programadas ni conecta cuentas.

### Elegir ubicaciones y posiciones

Requiere Python 3.10 o posterior, sin paquetes adicionales.

1. Copia `search.example.json` a `search.local.json` (este último no se sube a Git).
2. Cambia `locations` y `positions`: cada lista admite varias entradas, combinadas como alternativas. Las ubicaciones indican explícitamente su alcance; no se añaden localidades próximas de forma automática.
3. Usa `keywords` para términos opcionales de búsqueda y `confirmed_skills` únicamente para competencias confirmadas. Una palabra clave no acredita una competencia.
4. Ejecuta:

```sh
python configure_search.py --config search.local.json
```

El resultado se muestra en pantalla. Para probar sin datos personales:

```sh
python configure_search.py --config search.example.json
```

También puedes elegir las listas directamente al ejecutar (cada opción repetida añade otra alternativa y sustituye la lista del archivo):

```sh
python configure_search.py --config search.example.json --location "Ciudad Inventada (ciudad ficticia)" --position "Técnico/a de sensores (puesto de ejemplo)"
```

El archivo de ejemplo utiliza **lugares y perfil inventados**; no describe personas ni ofertas reales. Véase [EXAMPLE.md](EXAMPLE.md). El programa comprueba que las listas obligatorias no estén vacías. No valida que una localidad exista: eso permite ejemplos ficticios y requiere revisión para búsquedas reales.

Un flujo externo puede consultar fuentes y organizar la entrega de resúmenes, comprobando duplicados de envío. Esas conexiones y envíos no están implementados en estos programas. El comparador local informa de coincidencias y requisitos pendientes; la persona revisa los enlaces y decide si quiere solicitar el puesto. No se presentan candidaturas automáticamente.

Ejemplo de formato, con datos ficticios:

> DEMOSTRACIÓN FICTICIA: Técnico/a de sensores — Empresa Inventada — Ciudad Inventada. Contrato: no consta. Salario: no consta. Encaje y requisitos: pendientes de una revisión real. No existe anuncio ni enlace de candidatura.

Personas afectadas:

- **Candidatos:** reciben apoyo para buscar, mantienen el control sobre sus datos y decisiones y necesitan entender la incertidumbre de las recomendaciones.
- **Empresas y selección:** sus requisitos deben resumirse con fidelidad, sin atribuirles condiciones que no publicaron.
- **Portales y fuentes:** conservan sus derechos y condiciones de acceso; el proyecto enlaza los anuncios y no evita restricciones de acceso.
- **Otras personas interesadas:** una futura generalización debería contemplar accesibilidad, diferencias de trayectoria y sesgos de selección.

## 5. Challenges — Limitaciones

- No hay conectores específicos de LinkedIn o InfoJobs, extracción de requisitos desde HTML ni envío de correo; se importan datos estructurados.
- Las ubicaciones y competencias se comparan por texto normalizado. No hay geocodificación ni equivalencias semánticas; una ciudad no se reconoce automáticamente dentro de una provincia.
- TF-IDF depende del lote importado: cambiar las ofertas puede cambiar el índice y las características de la regresión. Antes de uso productivo debe estabilizarse el vocabulario/IDF y evaluarse el modelo con datos independientes y representativos.
- La antigüedad se compara de forma global; no acredita experiencia en una tecnología concreta. El estado abierto es una afirmación de la fuente, no una comprobación automática.

- No garantiza encontrar todas las vacantes ni comprobar la vigencia de todas las ofertas indexadas.
- Los bloqueos, páginas que requieren sesión e índices desactualizados limitan la cobertura.
- La IA puede omitir o interpretar mal requisitos; deben mantenerse fuentes verificables y revisión humana.
- Un anuncio puede cambiar de URL, empresa intermediaria o título, dificultando la deduplicación.
- El perfil puede estar incompleto: no deben inventarse años de experiencia, funciones o dominio de herramientas.
- La afinidad temática no demuestra que la persona cumpla todos los requisitos ni garantiza contratación.
- El correo depende de permisos, cuotas y disponibilidad de Gmail y de la plataforma que ejecuta la tarea.
- No soluciona la falta de vacantes, la discriminación en contratación ni la negociación salarial.
- No publica anuncios completos, no evita controles de acceso ni envía solicitudes de empleo.

## 6. What next — Próximos pasos

1. Implementar un registro estructurado de ofertas, fuentes, comprobaciones de vigencia y envíos, con identificadores estables.
2. Ampliar la importación, comparación y revisión existentes con una capa de entrega independiente.
3. Incorporar conectores a APIs o feeds oficiales concretos cuando estén disponibles y su uso esté autorizado; la importación JSON genérica ya existe.
4. Añadir evaluación con ejemplos revisados por humanos: relevancia, duplicados, ofertas cerradas y exactitud de contratos y salarios.
5. Permitir que la persona corrija competencias y marque ofertas útiles o irrelevantes, sin inferir atributos sensibles.
6. Añadir un panel accesible con estado de cada fuente y control de notificaciones.
7. Ampliar las opciones de configuración según las necesidades de uso.

## 7. Acknowledgments — Reconocimientos y autoría

- **Idea y requisitos:** aportados por la persona promotora del proyecto, cuya identidad no se publica en estos archivos.
- **Documentación y generador local:** preparados con asistencia de OpenAI Codex. No se presenta el trabajo generado como investigación o desarrollo independiente de la persona promotora.
- **Fuentes de ofertas:** empresas anunciantes, LinkedIn e InfoJobs. La autoría de cada anuncio pertenece a su creador; usar una fuente de datos no equivale a utilizar su código.
- **Herramientas del flujo:** Codex y la conexión Gmail. Son servicios externos, no código incorporado al repositorio.
- **Inspiración:** facilitar la búsqueda de empleo y el formato de propuesta de proyecto de IA en siete apartados. No se atribuye ese cuestionario a una institución concreta sin verificar su procedencia.

**Código empleado en este repositorio:** `configure_search.py`, `job_radar.py` y `test_job_radar.py`, generados para este proyecto con asistencia de OpenAI Codex. Utilizan únicamente la biblioteca estándar de Python, mantenida por su comunidad y distribuida por la Python Software Foundation; no incorporan fragmentos externos ni modelos preentrenados. La atribución y las dependencias se documentan en [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md).

### Fuentes y referencias

- [LinkedIn Empleos](https://www.linkedin.com/jobs/).
- [InfoJobs](https://www.infojobs.net/).
- [OpenAI Codex](https://openai.com/codex/).
- [Gmail](https://mail.google.com/).

Las referencias identifican las fuentes y herramientas; no implican patrocinio, afiliación, licencia de reutilización ni acceso garantizado.
