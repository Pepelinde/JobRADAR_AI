"""Generate search instructions offline; no network, scheduling or email actions.

Created for Job Radar with OpenAI Codex assistance.
Uses only the Python standard library; no copied snippets.
"""

import argparse
import json
from pathlib import Path


def text_list(config, key, required=False):
    value = config.get(key, [])
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ValueError(f"{key}: usa una lista de textos no vacíos")
    result = list(dict.fromkeys(item.strip() for item in value))
    if required and not result:
        raise ValueError(f"{key}: elige al menos una opción")
    return result


def build_instructions(config):
    if not isinstance(config, dict):
        raise ValueError("La configuración debe ser un objeto JSON")
    label = config.get("profile_label", "Perfil sin nombre")
    if not isinstance(label, str) or not label.strip():
        raise ValueError("profile_label: indica un texto no vacío")
    locations = text_list(config, "locations", required=True)
    positions = text_list(config, "positions", required=True)
    keywords = text_list(config, "keywords")
    skills = text_list(config, "confirmed_skills")
    sources = text_list(config, "sources", required=True)
    sections = [
        "INSTRUCCIONES DE BÚSQUEDA — configuración independiente",
        f"Perfil: {label.strip()}",
        "Ubicaciones (cualquiera de ellas, respetando su alcance):\n- "
        + "\n- ".join(locations),
        "Posiciones (cualquiera de ellas; buscar en cada ubicación):\n- "
        + "\n- ".join(positions),
        "Palabras clave opcionales, no competencias acreditadas: "
        + (", ".join(keywords) or "ninguna"),
        "Competencias confirmadas en esta configuración: "
        + ("; ".join(skills) or "ninguna; no inferir competencias"),
        "Fuentes a consultar, si son accesibles:\n- " + "\n- ".join(sources),
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
    return "\n\n".join(sections)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--location", action="append", help="Repetible; sustituye locations")
    parser.add_argument("--position", action="append", help="Repetible; sustituye positions")
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text(encoding="utf-8-sig"))
        if not isinstance(config, dict):
            raise ValueError("La configuración debe ser un objeto JSON")
        if args.location is not None:
            config["locations"] = args.location
        if args.position is not None:
            config["positions"] = args.position
        print(build_instructions(config))
    except (OSError, ValueError) as error:
        parser.exit(2, f"Error de configuración: {error}\n")


if __name__ == "__main__":
    main()
