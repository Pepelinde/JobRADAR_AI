<!-- This is the markdown template for the final project of the Building AI course,
created by Reaktor Innovations and University of Helsinki.
Copy the template, paste it to your GitHub README and edit! -->

# Job Radar

Final project for the Building AI course

**Español** | [English](README.md)

## Summary

Job Radar compara ofertas de empleo con un perfil configurable mediante reglas y similitud de texto. Explica coincidencias y requisitos pendientes, y permite entrenar una regresión logística con valoraciones humanas para ordenar las oportunidades.

## Background

Las ofertas se distribuyen entre distintas fuentes, pueden estar duplicadas y a menudo no permiten confirmar si una persona cumple sus requisitos. Compararlas manualmente con un perfil consume tiempo durante una búsqueda activa.

El proyecto busca facilitar esa revisión sin inventar competencias ni confundir información desconocida con requisitos cumplidos. Es una necesidad recurrente en la búsqueda de empleo; no se ha medido su frecuencia en la población.

Los problemas abordados son:

- Reunir y normalizar ofertas procedentes de varias fuentes estructuradas.
- Comparar formación, competencias y experiencia con los requisitos publicados.
- Evitar duplicados y señalar ofertas cerradas o fuera de las ubicaciones elegidas.
- Explicar por qué una oferta puede interesar y qué falta por confirmar.

## How is it used?

Está pensado para personas que buscan empleo y quieren revisar oportunidades según sus ubicaciones, puestos y competencias. Se ejecuta localmente cuando la persona dispone de nuevos datos; no programa tareas ni envía correos. Requiere **Python 3.10 o posterior**, sin paquetes adicionales.

### 1. Probar con datos ficticios

```sh
python job_radar.py rank --profile profile.example.json --source offers.example.json
```

Los perfiles, empresas, ubicaciones y ofertas del ejemplo son inventados. Los enlaces `example.invalid` no corresponden a candidaturas reales.

### 2. Configurar una comparación propia

Copia `profile.example.json` a `profile.local.json` y modifica `locations`, `positions`, `skills`, `summary` y `years_experience`. Usa `null` cuando no se conozca la experiencia. Prepara ofertas con el esquema descrito en [MATCHING.md](MATCHING.md).

```sh
python job_radar.py rank --profile profile.local.json --source offers-a.local.json --source offers-b.local.json
```

`--source` puede repetirse y acepta archivos o feeds JSON HTTPS autorizados. No admite directamente páginas HTML de portales. Los archivos `*.local.json` están excluidos de Git.

El informe JSON incluye:

- Fuentes consultadas, errores y cobertura parcial.
- Ofertas ordenadas con `score`, similitud, coincidencias y requisitos pendientes.
- Ubicación, enlace y condiciones aportadas por la fuente; los datos ausentes figuran como desconocidos.
- Exclusiones con sus motivos. Las ofertas con `eligible: false` quedan al final y no deben tratarse como recomendaciones.

### 3. Aprender de valoraciones humanas, opcionalmente

`feedback.local.json` debe ser una lista de valoraciones. Cada entrada contiene las cuatro `features` copiadas del informe y `relevant`: 1 para relevante o 0 para no relevante.

```json
{"features": [0.45, 0.5, 1, 0], "relevant": 1}
```

Se necesitan al menos 20 valoraciones y ambas clases. Ese mínimo técnico no garantiza datos suficientes ni calidad estadística. No deben generarse etiquetas a partir de las puntuaciones del propio programa.

```sh
python job_radar.py train --feedback feedback.local.json > model.local.json
python job_radar.py rank --profile profile.local.json --source offers.local.json --model model.local.json
```

Con modelo, las ofertas elegibles se ordenan por `estimated_relevance`. El modelo se guarda con `evaluated: false`: no ha sido evaluado en datos independientes.

### 4. Generar instrucciones para un asistente externo

El módulo separado `configure_search.py` permite elegir ubicaciones, puestos y palabras clave para generar un texto de instrucciones. No ejecuta búsquedas ni llama a una IA.

```sh
python configure_search.py --config search.example.json
python configure_search.py --config search.example.json --location "Ciudad Inventada" --position "Técnico/a de sensores"
```

Para uso propio, copia la configuración a `search.local.json`. Las opciones repetidas sustituyen la lista correspondiente del archivo. Más detalles en [EXAMPLE.md](EXAMPLE.md).

### 5. Comprobar el funcionamiento

```sh
python -m unittest -v test_job_radar.py
```

**10 pruebas sintéticas superadas:** coseno, reglas de ubicación/cierre/caducidad, experiencia desconocida, datos inválidos, duplicados, fallos parciales/totales, importación HTTPS simulada, aprendizaje logístico y conservación de exclusiones con modelo. No miden precisión en ofertas reales.

## Data sources and AI methods

### Datos y recogida

El sistema recibe datos aportados por la persona usuaria y ofertas estructuradas de fuentes cuyo acceso esté autorizado. Incluye un importador de JSON local y feeds HTTPS; **no hay conectores específicos de LinkedIn o InfoJobs** ni extracción automática de requisitos desde HTML.

[LinkedIn Empleos](https://www.linkedin.com/jobs/), [InfoJobs](https://www.infojobs.net/) y las páginas de empresas son posibles fuentes para una futura integración autorizada. El prototipo distribuido utiliza únicamente ejemplos ficticios.

Cada oferta necesita `id`, `title`, `company`, `location`, `description` y `url`. Admite competencias, experiencia mínima, contrato, salario, modalidad y fechas. Los detalles se describen en [MATCHING.md](MATCHING.md). El estado abierto es una afirmación de la fuente; el programa no visita el enlace para verificarlo.

### Métodos implementados

| Componente | Método y resultado |
| --- | --- |
| Validación | Comprueba campos, listas, URL, fechas y experiencia no negativa |
| Deduplicación | URL exacta o título/empresa/ubicación normalizados; conserva la primera fuente |
| Reglas | Excluye ubicación no elegida y ofertas cerradas o vencidas; compara requisitos sin inventar datos |
| Representación textual | Tokenización y TF-IDF con frecuencia relativa e IDF suavizado |
| Comparación | Similitud del coseno entre los vectores del perfil y la oferta |
| Índice inicial | Pesos manuales para coseno, competencias, ubicación y experiencia |
| Aprendizaje opcional | Regresión logística binaria, descenso de gradiente y regularización L2 |
| Explicación | Coincidencias, carencias de información, exclusiones y procedencia |

El IDF utilizado es `log((1+n)/(1+df))+1`. El índice es:

```text
100 × (0.55 × coseno + 0.30 × cobertura_competencias
       + 0.10 × ubicación + 0.05 × experiencia)
```

Los pesos son decisiones iniciales sin validación empírica. La regresión usa esas cuatro características y etiquetas humanas de relevancia. **Ni el índice ni la salida logística son probabilidades de contratación.**

La similitud compara palabras: no utiliza embeddings ni reconoce sinónimos automáticamente. No se implementan Bayes, Monte Carlo, k-NN ni llamadas a modelos de lenguaje. La asistencia de IA en la creación del proyecto se reconoce por separado.

### Archivos

- [`job_radar.py`](job_radar.py): importación, comparación y entrenamiento, con comentarios explicativos.
- [`configure_search.py`](configure_search.py): generador de instrucciones comentado.
- [`profile.example.json`](profile.example.json), [`offers.example.json`](offers.example.json) y [`search.example.json`](search.example.json): ejemplos ficticios.
- [`test_job_radar.py`](test_job_radar.py): pruebas automatizadas.
- [`MATCHING.md`](MATCHING.md) y [`AI-METHODS.md`](AI-METHODS.md): documentación técnica.

## Challenges

- No garantiza cobertura de todas las plataformas ni vigencia de las ofertas. Un fallo de fuente se registra; si fallan todas, devuelve código 2 sin afirmar que no haya vacantes.
- La importación requiere datos estructurados. No hay conectores específicos, base de datos persistente, correo automático ni aplicación autónoma de alertas.
- Ubicaciones y competencias usan coincidencia textual normalizada. No hay geocodificación: una ciudad no se reconoce automáticamente dentro de una provincia.
- La antigüedad global no acredita experiencia en una tecnología concreta. La información desconocida exige revisión humana.
- La deduplicación puede fusionar plazas distintas o dejar pasar variantes.
- TF-IDF depende del lote de ofertas; cambiarlo modifica las características. Un modelo productivo requeriría estabilizar el vocabulario/IDF y evaluar con datos independientes.
- No se proporciona un modelo entrenado con datos reales ni métricas de precisión, exhaustividad o calibración.
- Deben protegerse los perfiles y valoraciones, respetar las condiciones de las fuentes y evitar inferencias sobre atributos sensibles o decisiones discriminatorias.
- No decide contrataciones, presenta candidaturas, evita controles de acceso ni soluciona la falta de vacantes o la discriminación laboral.

Los candidatos mantienen el control de sus datos y decisiones; las empresas deben ver sus requisitos representados con fidelidad. Los cambios en este repositorio no modifican ninguna alerta externa.

## What next?

1. Incorporar conectores a APIs o feeds oficiales concretos cuando su uso esté autorizado.
2. Guardar ofertas, procedencia y comprobaciones de estado en un registro persistente.
3. Estabilizar vocabulario/IDF y comparar el índice manual y la regresión con conjuntos separados de entrenamiento y evaluación.
4. Medir relevancia, duplicados, cierres, precisión, exhaustividad y calibración; no atribuir mejoras sin evidencia.
5. Añadir un panel accesible para configurar búsquedas, corregir perfiles y aportar valoraciones humanas.
6. Considerar normalización geográfica y equivalencias técnicas revisadas.
7. Añadir una capa independiente de entrega y controles de privacidad.

Para avanzar se necesitan conocimientos de integración de datos, estadística y evaluación de aprendizaje automático, además de personas que revisen ejemplos representativos y ayuden a evaluar accesibilidad y sesgos.

## Acknowledgments

- **Plantilla del proyecto Building AI:** creada por **Reaktor Innovations y la University of Helsinki**, según la plantilla facilitada. Se conserva su atribución en el comentario inicial. Esta referencia no implica afiliación o evaluación del proyecto por esas entidades.
- **Idea y requisitos:** persona promotora del proyecto, sin identificación personal en los archivos.
- **Código y documentación:** preparados con asistencia de **OpenAI Codex**, sin copiar implementaciones de otros repositorios.
- **Python y biblioteca estándar:** comunidad de Python y **Python Software Foundation**. Python se instala por separado y mantiene su [licencia e historial de derechos](https://docs.python.org/3/license.html); no se redistribuye su código aquí.
- **Métodos matemáticos:** TF-IDF, coseno y regresión logística son técnicas conocidas; su uso no implica haber incorporado una biblioteca externa o un modelo preentrenado.
- **Datos y recursos gráficos:** ejemplos sintéticos creados para el proyecto; no se han incorporado imágenes ni anuncios de terceros.

Los avisos de dependencias y autoría figuran en [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md). El código y la documentación propios se distribuyen bajo [MIT](LICENSE), con atribución «Job Radar contributors»: permite uso, modificación y redistribución, incluido uso comercial, conservando los avisos y sin garantías. No concede derechos sobre datos, servicios o materiales de terceros ni cambia la visibilidad del repositorio.
