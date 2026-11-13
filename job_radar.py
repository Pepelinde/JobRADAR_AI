"""Job Radar: importación JSON, reglas, TF-IDF/coseno y regresión opcional.

Código creado con asistencia de OpenAI Codex. Solo biblioteca estándar.
No conecta cuentas, no programa tareas y no envía mensajes.
"""
import argparse
import json
import math
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

FEATURES = ["cosine", "skill_coverage", "location_match", "experience_match"]


def normalized(text):
    """Unifica acentos y mayúsculas; no inventa equivalencias profesionales."""
    return "".join(c for c in unicodedata.normalize("NFKD", text.lower())
                   if not unicodedata.combining(c))


def tokens(text):
    # Conserva términos como C++ o .NET; elimina palabras funcionales comunes.
    stop = {"de", "la", "el", "en", "y", "a", "con", "para", "the", "and", "of", "in", "to"}
    return [t for t in re.findall(r"[\w]+(?:\+\+|#)?|\.net", normalized(text))
            if t not in stop]


def text_list(value, name):
    if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
        raise ValueError(f"{name}: se requiere una lista de textos no vacíos")
    return list(dict.fromkeys(x.strip() for x in value))


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def validate_profile(p):
    """Valida el perfil. None representa experiencia desconocida, nunca cero."""
    if not isinstance(p, dict):
        raise ValueError("El perfil debe ser un objeto")
    for field in ["locations", "positions", "skills"]:
        p[field] = text_list(p.get(field), field)
    if not p["locations"] or not p["positions"]:
        raise ValueError("Elige al menos una ubicación y posición")
    if not isinstance(p.get("summary", ""), str):
        raise ValueError("summary debe ser texto")
    years = p.get("years_experience")
    if years is not None and (type(years) not in (int, float) or not math.isfinite(years) or years < 0):
        raise ValueError("years_experience debe ser un número no negativo o null")
    return p


def validate_offers(data, source):
    """Acepta una lista de ofertas o un objeto con items; exige evidencia de origen."""
    items = data.get("items") if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ValueError("Se esperaba una lista o un objeto con items")
    result = []
    for original in items:
        if not isinstance(original, dict):
            raise ValueError("Cada oferta debe ser un objeto")
        offer = dict(original)
        for field in ["id", "title", "company", "location", "description", "url"]:
            if not isinstance(offer.get(field), str) or not offer[field].strip():
                raise ValueError(f"Oferta: falta {field}")
        if not re.match(r"^https?://[^\s]+$", offer["url"]):
            raise ValueError("URL de oferta no válida")
        offer["required_skills"] = text_list(offer.get("required_skills", []), "required_skills")
        years = offer.get("min_years")
        if years is not None and (type(years) not in (int, float) or not math.isfinite(years) or years < 0):
            raise ValueError("min_years debe ser un número no negativo o null")
        if offer.get("status", "unverified") not in ("open", "unverified", "closed", "expired"):
            raise ValueError("status no válido")
        for field in ["published_at", "expires_at", "verified_at"]:
            if offer.get(field) is not None:
                datetime.fromisoformat(offer[field].replace("Z", "+00:00"))
        offer["source"] = source
        result.append(offer)
    return result


def collect(sources):
    """Importa archivos o feeds JSON HTTPS autorizados; registra fallos parciales.

    No es un scraper de LinkedIn/InfoJobs. Un feed requiere el esquema documentado.
    """
    offers, coverage = [], []
    for source in sources:
        try:
            if source.startswith("https://"):
                request = Request(source, headers={"User-Agent": "JobRadar/1.0", "Accept": "application/json"})
                with urlopen(request, timeout=20) as response:
                    raw = response.read(2_000_001)
                if len(raw) > 2_000_000:
                    raise ValueError("Feed demasiado grande (máximo 2 MB)")
                data = json.loads(raw.decode("utf-8-sig"))
            elif "://" in source:
                raise ValueError("Los feeds remotos deben utilizar HTTPS")
            else:
                data = read_json(source)
            batch = validate_offers(data, source)
            offers.extend(batch)
            coverage.append({"source": source, "ok": True, "count": len(batch)})
        except (OSError, ValueError) as error:
            coverage.append({"source": source, "ok": False, "error": str(error)})
    # Deduplica por URL exacta o título/empresa/localidad normalizados.
    # No fusiona campos contradictorios: conserva la primera fuente aportada.
    unique, seen = [], set()
    for offer in offers:
        keys = {("url", offer["url"]), ("job", *(normalized(offer[k]).strip() for k in ("title", "company", "location")))}
        if keys & seen:
            continue
        seen.update(keys)
        unique.append(offer)
    return unique, coverage


def cosine_scores(profile_text, offer_texts):
    """TF-IDF aprendido del conjunto importado y coseno con el perfil.

    TF = frecuencia relativa; IDF suavizado = log((1+n)/(1+df))+1.
    Las puntuaciones pueden cambiar al cambiar el conjunto de ofertas.
    """
    documents = [tokens(profile_text)] + [tokens(t) for t in offer_texts]
    df = Counter(t for doc in documents for t in set(doc))
    n = len(documents)
    vectors = []
    for doc in documents:
        counts = Counter(doc)
        v = {t: count / max(1, len(doc)) * (math.log((1 + n) / (1 + df[t])) + 1)
             for t, count in counts.items()}
        norm = math.sqrt(sum(x*x for x in v.values()))
        vectors.append({t: x / norm for t, x in v.items()} if norm else {})
    # Acota pequeños errores de redondeo de coma flotante.
    return [max(0., min(1., sum(x * v.get(t, 0) for t, x in vectors[0].items()))) for v in vectors[1:]]


def rank(profile, offers, model=None):
    """Aplica reglas y genera explicaciones; requisitos desconocidos quedan visibles."""
    profile = validate_profile(dict(profile))
    ptext = " ".join(profile["positions"] + profile["skills"]) + " " + profile.get("summary", "")
    similarities = cosine_scores(ptext, [" ".join([o["title"], o["description"]] + o["required_skills"]) for o in offers])
    results = []
    today = datetime.now(timezone.utc).date()
    known = {normalized(s) for s in profile["skills"]}
    for offer, similarity in zip(offers, similarities):
        reasons, pending, excluded = [], [], []
        # Coincidencia literal normalizada: no se presupone geocodificación.
        location = normalized(offer["location"]) in {normalized(x) for x in profile["locations"]}
        if not location:
            excluded.append("Ubicación fuera de las opciones exactas elegidas")
        else:
            reasons.append("Ubicación coincidente")
        if offer.get("status") in ("closed", "expired"):
            excluded.append("Oferta cerrada o vencida según la fuente")
        if offer.get("expires_at") and datetime.fromisoformat(offer["expires_at"].replace("Z", "+00:00")).date() < today:
            excluded.append("Fecha límite vencida")
        matched = [s for s in offer["required_skills"] if normalized(s) in known]
        missing = [s for s in offer["required_skills"] if normalized(s) not in known]
        if matched:
            reasons.append("Competencias coincidentes: " + ", ".join(matched))
        if missing:
            pending.append("Competencias no acreditadas: " + ", ".join(missing))
        coverage = len(matched) / len(offer["required_skills"]) if offer["required_skills"] else 0
        years, minimum = profile.get("years_experience"), offer.get("min_years")
        experience = 0
        if years is None or minimum is None:
            pending.append("Experiencia: información insuficiente para comparar")
        elif years < minimum:
            pending.append(f"Experiencia declarada {years}; solicitada {minimum}")
        else:
            experience = 1
            reasons.append("Antigüedad declarada suficiente; verificar que corresponda al área requerida")
        if offer.get("status") != "open" or not offer.get("verified_at"):
            pending.append("Vigencia pendiente de verificación")
        else:
            pending.append("Estado abierto declarado por la fuente; no comprobado por el programa")
        features = [similarity, coverage, float(location), float(experience)]
        # Heurística transparente, NO probabilidad de contratación ni relevancia calibrada.
        score = 100 * (.55 * similarity + .30 * coverage + .10 * location + .05 * experience)
        result = {**offer, "eligible": not excluded, "score": round(score, 2),
                  "cosine": round(similarity, 4), "features": features,
                  "matches": reasons, "pending": pending, "excluded_reasons": excluded,
                  "contract": offer.get("contract") or "No consta",
                  "salary": offer.get("salary") or "No consta",
                  "work_mode": offer.get("work_mode") or "No consta"}
        if model:
            result["estimated_relevance"] = round(predict(features, model), 4)
        results.append(result)
    return sorted(results, key=lambda r: (r["eligible"], r.get("estimated_relevance", r["score"])), reverse=True)


def sigmoid(z):
    return 1 / (1 + math.exp(-max(-40, min(40, z))))


def predict(features, model):
    """Regresión logística: sigmoide del sesgo más la suma ponderada."""
    return sigmoid(model["bias"] + sum(w*x for w, x in zip(model["weights"], features)))


def train(rows):
    """Aprende pesos con descenso de gradiente y regularización L2.

    Las etiquetas son valoraciones humanas de relevancia, no contrataciones.
    No se publica una métrica de generalización sin evaluación independiente.
    """
    if not isinstance(rows, list) or len(rows) < 20:
        raise ValueError("Se requieren al menos 20 valoraciones; más datos no garantizan calidad")
    for row in rows:
        xs = row.get("features") if isinstance(row, dict) else None
        if not isinstance(xs, list) or len(xs) != len(FEATURES) or any(type(x) not in (int, float) or not math.isfinite(x) or not 0 <= x <= 1 for x in xs):
            raise ValueError("Cada valoración necesita 4 features numéricas entre 0 y 1")
        if type(row.get("relevant")) is not int or row["relevant"] not in (0, 1):
            raise ValueError("relevant debe ser 0 o 1")
    if {r["relevant"] for r in rows} != {0, 1}:
        raise ValueError("Se necesitan ejemplos relevantes y no relevantes")
    model = {"version": 1, "feature_names": FEATURES, "weights": [0.] * 4, "bias": 0.,
             "training_count": len(rows), "evaluated": False}
    for _ in range(1500):
        errors = [predict(r["features"], model) - r["relevant"] for r in rows]
        model["bias"] -= .2 * sum(errors) / len(rows)
        for j in range(4):
            grad = sum(e*r["features"][j] for e, r in zip(errors, rows)) / len(rows)
            model["weights"][j] -= .2 * (grad + .01 * model["weights"][j])
    return model


def load_model(path):
    model = read_json(path)
    if not isinstance(model, dict) or model.get("version") != 1 or model.get("feature_names") != FEATURES:
        raise ValueError("Modelo incompatible")
    weights = model.get("weights")
    if not isinstance(weights, list) or len(weights) != 4 or any(type(x) not in (int, float) or not math.isfinite(x) for x in weights):
        raise ValueError("Pesos de modelo no válidos")
    if type(model.get("bias")) not in (int, float) or not math.isfinite(model["bias"]):
        raise ValueError("Sesgo de modelo no válido")
    return model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    search = sub.add_parser("rank", help="Importar y comparar ofertas")
    search.add_argument("--profile", required=True)
    search.add_argument("--source", action="append", required=True)
    search.add_argument("--model")
    learning = sub.add_parser("train", help="Aprender de valoraciones humanas")
    learning.add_argument("--feedback", required=True)
    args = parser.parse_args()
    try:
        if args.command == "train":
            report = train(read_json(args.feedback))
        else:
            offers, coverage = collect(args.source)
            report = {"coverage": coverage, "partial_coverage": any(not c["ok"] for c in coverage),
                      "results": rank(read_json(args.profile), offers, load_model(args.model) if args.model else None),
                      "notice": "Puntuación orientativa; no probabilidad de contratación. Revisar fuentes y requisitos."}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if args.command == "rank" and all(not c["ok"] for c in coverage):
            return 2
        return 0
    except (OSError, ValueError) as error:
        parser.exit(2, f"Error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
