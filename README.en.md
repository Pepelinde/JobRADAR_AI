<!-- This is the markdown template for the final project of the Building AI course,
created by Reaktor Innovations and University of Helsinki.
Copy the template, paste it to your GitHub README and edit! -->

# Job Radar

Final project for the Building AI course

[Español](README.md) | **English**

## Summary

Job Radar compares job listings with a configurable profile using rules and text similarity. It explains matches and unconfirmed requirements, and supports logistic regression trained on human relevance ratings to rank opportunities.

## Background

Job listings are spread across sources, may be duplicated and often leave uncertainty about whether a person meets their requirements. Manually comparing them with a profile takes time during an active search.

The project aims to simplify that review without inventing skills or treating unknown information as a satisfied requirement. This is a recurring job-search need; its frequency in the population has not been measured.

Problems addressed include:

- Combining and normalizing listings from multiple structured sources.
- Comparing education, skills and experience with published requirements.
- Detecting duplicates and identifying closed listings or unselected locations.
- Explaining why a listing may be relevant and what still needs confirmation.

## How is it used?

The intended users are job seekers who want to review opportunities against their locations, positions and skills. It runs locally when new data is available; it does not schedule tasks or send emails. Requires **Python 3.10 or later**, with no additional packages.

### 1. Try fictional data

```sh
python job_radar.py rank --profile profile.example.json --source offers.example.json
```

Example profiles, companies, locations and vacancies are invented. The `example.invalid` links are not real application pages.

### 2. Configure a comparison

Copy `profile.example.json` to `profile.local.json` and edit `locations`, `positions`, `skills`, `summary` and `years_experience`. Use `null` for unknown experience. Prepare listings using the schema in [MATCHING.md](MATCHING.md).

```sh
python job_radar.py rank --profile profile.local.json --source offers-a.local.json --source offers-b.local.json
```

Repeat `--source` to import files or authorized HTTPS JSON feeds. Ordinary HTML job-board pages are not supported directly. Files named `*.local.json` are excluded from Git.

The JSON report includes:

- Source results, errors and partial coverage.
- Ranked listings with `score`, similarity, matches and pending requirements.
- Location, link and source-provided conditions; absent information remains unknown.
- Exclusions and reasons. Listings with `eligible: false` remain at the end and must not be presented as recommendations.

### 3. Optionally learn from human ratings

`feedback.local.json` must contain a list of ratings. Each entry has the four `features` copied from a result and `relevant`: 1 for relevant or 0 for irrelevant.

```json
{"features": [0.45, 0.5, 1, 0], "relevant": 1}
```

At least 20 ratings and both classes are required. This technical minimum does not guarantee sufficient or statistically adequate data. Do not generate labels from the program's own scores.

```sh
python job_radar.py train --feedback feedback.local.json > model.local.json
python job_radar.py rank --profile profile.local.json --source offers.local.json --model model.local.json
```

With a model, eligible listings are ranked by `estimated_relevance`. Models are saved with `evaluated: false`: they have not been independently evaluated.

### 4. Generate instructions for an external assistant

The separate `configure_search.py` module generates search instructions from chosen locations, positions and keywords. It does not search or call an AI service.

```sh
python configure_search.py --config search.example.json
python configure_search.py --config search.example.json --location "Invented City" --position "Sensor technician"
```

For personal use, copy the configuration to `search.local.json`. Repeated command-line options replace the corresponding list from the file. See [EXAMPLE.md](EXAMPLE.md).

The code comments, example configuration, output and detailed guides are currently in Spanish; this README provides English usage instructions. English configuration values do not translate the program's output template.

### 5. Check the implementation

```sh
python -m unittest -v test_job_radar.py
```

**10 passing synthetic tests:** cosine, location/closure/expiry rules, unknown experience, invalid data, duplicates, partial/total source failures, mocked HTTPS import, logistic learning and preservation of exclusions with a model. They do not measure accuracy on real vacancies.

## Data sources and AI methods

### Data and collection

The system accepts user-provided profile information and structured listings from sources authorized for use. It imports local JSON and HTTPS feeds; **there are no LinkedIn or InfoJobs-specific connectors**, or automatic HTML requirement extraction.

[LinkedIn Jobs](https://www.linkedin.com/jobs/), [InfoJobs](https://www.infojobs.net/) and company career pages are potential sources for future authorized integrations. The distributed prototype uses fictional examples only.

Each listing requires `id`, `title`, `company`, `location`, `description` and `url`. Optional fields include skills, minimum experience, contract, salary, working arrangement and dates. See [MATCHING.md](MATCHING.md). Open status is a source assertion; the program does not visit the link to verify it.

### Implemented methods

| Component | Method and result |
| --- | --- |
| Validation | Checks fields, lists, URLs, dates and nonnegative experience |
| Deduplication | Exact URL or normalized title/company/location; keeps the first source |
| Rules | Excludes unselected locations and closed/expired listings; compares requirements without inventing data |
| Text representation | Tokenization and TF-IDF with relative frequency and smoothed IDF |
| Comparison | Cosine similarity between profile and listing vectors |
| Initial index | Manual weights for cosine, skills, location and experience |
| Optional learning | Binary logistic regression, gradient descent and L2 regularization |
| Explanation | Matches, information gaps, exclusions and provenance |

IDF is `log((1+n)/(1+df))+1`. The initial index is:

```text
100 × (0.55 × cosine + 0.30 × skill_coverage
       + 0.10 × location + 0.05 × experience)
```

Weights are initial design choices without empirical validation. Regression uses those four features and human relevance labels. **Neither the index nor the logistic output is a hiring probability.**

Similarity compares words: it does not use embeddings or automatically recognize synonyms. Bayes, Monte Carlo, k-NN and language-model calls are not implemented. AI assistance in creating the project is acknowledged separately.

### Files

- [`job_radar.py`](job_radar.py): import, matching and training with explanatory comments.
- [`configure_search.py`](configure_search.py): commented instruction generator.
- [`profile.example.json`](profile.example.json), [`offers.example.json`](offers.example.json) and [`search.example.json`](search.example.json): fictional examples.
- [`test_job_radar.py`](test_job_radar.py): automated tests.
- [`MATCHING.md`](MATCHING.md) and [`AI-METHODS.md`](AI-METHODS.md): technical documentation.

## Challenges

- Coverage and listing status cannot be guaranteed. Source failures are recorded; if all fail, the program returns code 2 without claiming there are no vacancies.
- Input must be structured. There are no platform-specific connectors, persistent database, automatic emails or standalone alert application.
- Locations and skills use normalized text matching. There is no geocoding: cities are not automatically mapped to provinces.
- Overall experience does not establish experience in a particular technology. Unknown information requires human review.
- Deduplication may merge separate vacancies or miss variants.
- TF-IDF depends on the listing batch; changing it changes features. Production models require a stable vocabulary/IDF and independent evaluation.
- No model trained on real data, precision, recall or calibration results are provided.
- Profiles and ratings need protection, source conditions must be respected, and sensitive-attribute inference or discriminatory decisions must be avoided.
- The system does not make hiring decisions, submit applications, bypass access controls or solve vacancy shortages or employment discrimination.

Candidates retain control over their data and decisions; employer requirements must be represented accurately. Repository changes do not modify external alerts.

## What next?

1. Add connectors for specific official APIs or feeds when authorized.
2. Persist listings, provenance and status checks.
3. Stabilize vocabulary/IDF and compare the manual index and regression on separate training and evaluation sets.
4. Measure relevance, duplicates, closures, precision, recall and calibration; claim improvements only with evidence.
5. Add an accessible dashboard for configuration, profile corrections and human ratings.
6. Consider geographical normalization and reviewed technical equivalences.
7. Add a separate delivery layer and privacy controls.

Further progress needs data-integration, statistics and machine-learning evaluation skills, plus people to review representative examples and assess accessibility and bias.

## Acknowledgments

- **Building AI project template:** created by **Reaktor Innovations and the University of Helsinki**, as credited in the supplied template. Its attribution is retained in the opening comment. This does not imply affiliation or assessment by those organizations.
- **Idea and requirements:** the project's initiator, without personal identification in the files.
- **Code and documentation:** prepared with **OpenAI Codex** assistance, without copying implementations from other repositories.
- **Python and its standard library:** the Python community and **Python Software Foundation**. Python is installed separately and retains its [license and copyright history](https://docs.python.org/3/license.html); its code is not redistributed here.
- **Mathematical methods:** TF-IDF, cosine and logistic regression are established techniques; using them does not mean incorporating an external library or pretrained model.
- **Data and images:** synthetic examples created for the project; no third-party images or advertisements are included.

Dependency and authorship notices are in [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md). The project's own code and documentation are distributed under [MIT](LICENSE), attributed to “Job Radar contributors”: use, modification and redistribution, including commercial use, are permitted with retained notices and without warranty. This does not grant rights to third-party data, services or materials, or change repository visibility.
