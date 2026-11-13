# Ejemplo completamente ficticio

Una persona inventada quiere buscar dos posiciones: técnico/a de sensores o programador/a PLC junior. Elige Ciudad Inventada y todos los municipios de la provincia imaginaria Sierra Imaginaria. Tanto el perfil como las ubicaciones son ficticios.

El archivo [search.example.json](search.example.json) contiene estas elecciones. Al ejecutar:

```sh
python configure_search.py --config search.example.json
```

se generan instrucciones con ambas ubicaciones y ambas posiciones. Cada puesto se busca en cada ubicación; no se exige que un anuncio tenga simultáneamente los dos títulos. Las palabras PLC y HMI amplían la consulta, sin atribuir esas competencias a la persona.

Para una búsqueda propia, copia el archivo a `search.local.json`, sustituye los lugares inventados por ubicaciones reales e indica ciudad, provincia o región. Introduce los puestos que te interesen y solo las competencias que puedas acreditar. El archivo local queda excluido de Git.

**No hay ofertas reales en este ejemplo.** El generador funciona sin Internet y no consulta portales, no crea una alerta ni envía mensajes. Su salida debe revisarse antes de usarla como instrucciones en un asistente con búsqueda. Las automatizaciones externas no consumen estos archivos.
