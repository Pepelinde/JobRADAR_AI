# Job Radar

**Español** | [English](README.en.md)

Proyecto configurable de búsqueda asistida de empleo: elige ubicaciones, puestos y palabras clave.

**Nuevo: comparador local.** Importa ofertas JSON, aplica reglas y TF-IDF/coseno, y admite regresión logística opcional con valoraciones humanas. [Guía, demostración y límites](MATCHING.md).

```sh
python job_radar.py rank --profile profile.example.json --source offers.example.json
```

Ejemplos ficticios. No hay conectores específicos de plataformas ni envío automático.

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

- Expansión de consultas con sinónimos técnicos: PLC, autómatas programables, automatización, HMI, SCADA, Siemens/TIA Portal, STEP 7, Rockwell, Schneider u Omron.
- Interpretación semántica mediante un modelo de lenguaje para relacionar requisitos de las ofertas y datos confirmados del perfil.
- Extracción y resumen de título, empresa, ubicación, fecha, contrato, salario, modalidad y requisitos.
- Comparación de título, empresa, ubicación, enlaces y funciones para identificar duplicados y republicaciones.
- Redacción de motivos de encaje y carencias de información con enlaces a las fuentes.

Las marcas y herramientas usadas para buscar no se convierten automáticamente en competencias de la persona. No se distribuye un modelo entrenado con datos reales ni se han medido precisión o exhaustividad. El comparador implementa deduplicación heurística y clasificación logística opcional; no incluye una base de datos persistente.

### Estado real del proyecto

El código está comentado por funciones y pasos. El generador y el comparador son módulos distintos; este último implementa coseno y regresión logística opcional. Véase [AI-METHODS.md](AI-METHODS.md).

Este repositorio incluye un **generador local de instrucciones de búsqueda** y un comparador local. El comparador importa archivos o feeds JSON autorizados; no recoge páginas HTML de portales ni envía correos. No es una aplicación autónoma de alertas. Clonarlo o cambiar su configuración no modifica ninguna alerta externa.

No se incluyen credenciales, datos de destinatarios, historial personal ni copias completas de anuncios.

## 4. How is it used — Uso y personas afectadas

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

El flujo consulta fuentes, contrasta posibles cierres, elimina duplicados y prepara un resumen. Antes del envío comprueba si ya existe un correo de ese día. El mensaje incluye novedades o cambios relevantes; si la cobertura es incompleta, lo indica sin afirmar que no hay ofertas. La persona revisa los enlaces y decide si quiere solicitar el puesto. No se presentan candidaturas automáticamente.

Ejemplo de formato, con datos ficticios:

> DEMOSTRACIÓN FICTICIA: Técnico/a de sensores — Empresa Inventada — Ciudad Inventada. Contrato: no consta. Salario: no consta. Encaje y requisitos: pendientes de una revisión real. No existe anuncio ni enlace de candidatura.

Personas afectadas:

- **Candidatos:** reciben apoyo para buscar, mantienen el control sobre sus datos y decisiones y necesitan entender la incertidumbre de las recomendaciones.
- **Empresas y selección:** sus requisitos deben resumirse con fidelidad, sin atribuirles condiciones que no publicaron.
- **Portales y fuentes:** conservan sus derechos y condiciones de acceso; el proyecto enlaza los anuncios y no evita restricciones de acceso.
- **Otras personas interesadas:** una futura generalización debería contemplar accesibilidad, diferencias de trayectoria y sesgos de selección.

## 5. Challenges — Limitaciones

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
2. Separar adquisición de datos, valoración de encaje, revisión y entrega para poder comprobar cada etapa.
3. Incorporar APIs o feeds oficiales cuando estén disponibles y su uso esté autorizado.
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

**Código empleado en este repositorio:** `configure_search.py`, generado para este proyecto con asistencia de OpenAI Codex; utiliza únicamente la biblioteca estándar de Python. No incorpora fragmentos externos. La atribución y las dependencias se documentan en [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md).

### Fuentes y referencias

- [LinkedIn Empleos](https://www.linkedin.com/jobs/).
- [InfoJobs](https://www.infojobs.net/).
- [OpenAI Codex](https://openai.com/codex/).
- [Gmail](https://mail.google.com/).

Las referencias identifican las fuentes y herramientas; no implican patrocinio, afiliación, licencia de reutilización ni acceso garantizado.
