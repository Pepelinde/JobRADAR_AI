"""Generate search instructions offline; no network, scheduling or email actions.

Created for Job Radar with OpenAI Codex assistance.
Uses only the Python standard library; no copied snippets.
"""

import argparse  # Interpreta las opciones escritas al ejecutar el programa.
import json  # Convierte el contenido JSON en estructuras de Python.
from pathlib import Path  # Representa rutas y permite leer el archivo elegido.


def text_list(config, key, required=False):
    """Valida y limpia una lista de textos, conservando su orden.

    config es el diccionario de configuración; key identifica el campo.
    required=True exige al menos una entrada. Devuelve una lista nueva;
    no modifica el diccionario recibido. Lanza ValueError si el dato no sirve.
    """
    # Si el campo no existe, se considera una lista vacía.
    value = config.get(key, [])
    # Rechaza valores que no sean listas o contengan textos vacíos/no textuales.
    # any() detecta si al menos un elemento incumple la condición.
    # El «or» evita recorrer value cuando ni siquiera es una lista.
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ValueError(f"{key}: usa una lista de textos no vacíos")
    # strip() elimina espacios de los extremos. Las claves de un diccionario
    # no se repiten y conservan el orden: así se eliminan duplicados exactos.
    # No se comparan significados ni variantes en mayúsculas/minúsculas.
    result = list(dict.fromkeys(item.strip() for item in value))
    # Una lista vacía solo es un error cuando el campo es obligatorio.
    if required and not result:
        raise ValueError(f"{key}: elige al menos una opción")
    return result


def build_instructions(config):
    """Construye un texto de instrucciones a partir de una configuración.

    Es una plantilla determinista: la misma entrada genera el mismo texto.
    No consulta fuentes, no puntúa ofertas ni llama a un modelo de IA.
    """
    # Un objeto JSON se representa como dict; otros tipos no son válidos aquí.
    if not isinstance(config, dict):
        raise ValueError("La configuración debe ser un objeto JSON")
    label = config.get("profile_label", "Perfil sin nombre")  # Nombre opcional.
    if not isinstance(label, str) or not label.strip():
        raise ValueError("profile_label: indica un texto no vacío")
    # Estos tres campos necesitan entradas; palabras clave y competencias
    # pueden quedar vacías. La validación se comparte mediante text_list().
    locations = text_list(config, "locations", required=True)
    positions = text_list(config, "positions", required=True)
    keywords = text_list(config, "keywords")
    skills = text_list(config, "confirmed_skills")
    sources = text_list(config, "sources", required=True)
    # Cada elemento será un párrafo. Las cadenas contiguas se concatenan;
    # join() une las entradas con separadores, sin interpretar su contenido.
    sections = [
        "INSTRUCCIONES DE BÚSQUEDA — configuración independiente",
        f"Perfil: {label.strip()}",  # La f-string inserta el nombre validado.
        "Ubicaciones (cualquiera de ellas, respetando su alcance):\n- "
        + "\n- ".join(locations),
        "Posiciones (cualquiera de ellas; buscar en cada ubicación):\n- "
        + "\n- ".join(positions),
        # «or» elige el texto alternativo cuando la lista unida queda vacía.
        "Palabras clave opcionales, no competencias acreditadas: "
        + (", ".join(keywords) or "ninguna"),
        "Competencias confirmadas en esta configuración: "
        + ("; ".join(skills) or "ninguna; no inferir competencias"),
        "Fuentes a consultar, si son accesibles:\n- " + "\n- ".join(sources),
        # Son instrucciones para una revisión posterior: escribirlas aquí
        # no implementa búsquedas, deduplicación de ofertas ni comprobaciones.
        "No añadir ubicaciones próximas ni filtros salariales o contractuales "
        "sin indicación. Distinguir encaje temático de requisitos acreditados. "
        "Excluir anuncios explícitamente cerrados y deduplicar republicaciones. "
        "Indicar cobertura parcial cuando fallen fuentes. Por oferta: título, "
        "empresa, ubicación, fecha, enlace, contrato, salario y modalidad si "
        "constan; motivo de encaje y requisitos por confirmar. No inventar "
        "condiciones ni presentar candidaturas. Diferenciar vigencia verificada "
        "de contenido indexado. Si la configuración es ficticia, tratarla "
        "únicamente como demostración; no inventar resultados reales.",
        "Este texto no programa tareas, no envía correo y no cambia ninguna "
        "alerta existente. Revisarlo antes de usarlo.",
    ]
    return "\n\n".join(sections)  # Separa los párrafos mediante una línea vacía.


def main():
    """Lee opciones y archivo, aplica cambios temporales e imprime el texto.

    No escribe sobre el archivo de configuración. Los errores de lectura o
    validación terminan con código 2, que permite detectar el fallo al ejecutar.
    """
    # __doc__ es la descripción inicial del archivo, usada en --help.
    parser = argparse.ArgumentParser(description=__doc__)
    # --config es obligatorio; type=Path convierte su valor en una ruta.
    parser.add_argument("--config", type=Path, required=True)
    # append acumula opciones repetidas. Si no aparecen, su valor será None.
    parser.add_argument("--location", action="append", help="Repetible; sustituye locations")
    parser.add_argument("--position", action="append", help="Repetible; sustituye positions")
    args = parser.parse_args()  # Lee y valida los argumentos de la ejecución.
    try:
        # Lee UTF-8 aceptando también una marca BOM y analiza el JSON.
        # read_text puede fallar por permisos/ruta; loads por JSON incorrecto.
        config = json.loads(args.config.read_text(encoding="utf-8-sig"))
        if not isinstance(config, dict):
            raise ValueError("La configuración debe ser un objeto JSON")
        # Las opciones de ejecución sustituyen las listas solo en memoria.
        if args.location is not None:
            config["locations"] = args.location
        if args.position is not None:
            config["positions"] = args.position
        print(build_instructions(config))  # Muestra el resultado; no lo envía.
    except (OSError, ValueError) as error:
        # Incluye errores del archivo, de JSON y de las validaciones propias.
        parser.exit(2, f"Error de configuración: {error}\n")


# Ejecuta main() al abrir el archivo como programa. Al importarlo desde otro
# módulo solo se definen las funciones, sin leer archivos ni imprimir nada.
if __name__ == "__main__":
    main()
