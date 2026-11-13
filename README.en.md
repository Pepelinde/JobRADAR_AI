# Job Radar

[Español](README.md) | **English**

A configurable project for assisted job searching: choose locations, positions and keywords.

**New: local matcher.** Import JSON listings, apply rules and TF-IDF cosine similarity, and optionally train logistic regression from human relevance labels. See [MATCHING.md](MATCHING.md), including an English summary, for the demo and limitations.

```sh
python job_radar.py rank --profile profile.example.json --source offers.example.json
```

All examples are fictional. No platform-specific connectors or automatic email delivery are included.

### Implemented features

| Feature | Current behavior |
| --- | --- |
| Search configuration | Locations, positions, keywords and confirmed skills through files or command-line options |
| Listing import | JSON files or multiple authorized HTTPS JSON feeds through repeated `--source` options |
| Source coverage | Records successes and failures, preserves other sources and exits with code 2 if all sources fail |
| Validation | Checks required fields, URLs, dates, lists and nonnegative numeric experience |
| Deduplication | Exact URL or normalized title/company/location combination; keeps the first source |
| Exclusion rules | Unselected location, closed/expired status or past application deadline |
| Profile comparison | Declared skills and experience; unknown information remains unconfirmed |
| TF-IDF and cosine | Compares profile and listing words using text vectors |
| Explainable index | Combines cosine, skills, location and experience using manual weights |
| Optional logistic regression | Learns from human relevance labels and ranks with a saved model |
| JSON report | Scores, matches, pending requirements, exclusions, sources and published conditions |
| Examples and tests | Fictional profile/listings and 10 passing synthetic tests, without real-world accuracy claims |

Excluded listings remain at the end of the report with `eligible: false`; they must not be presented as recommendations. The program does not visit advertisements to verify their status: it reports source-provided information.

### Main files

- [`configure_search.py`](configure_search.py): commented search-instruction generator.
- [`job_radar.py`](job_radar.py): import, rules, TF-IDF/cosine, classification and training.
- [`search.example.json`](search.example.json): fictional generator configuration.
- [`profile.example.json`](profile.example.json) and [`offers.example.json`](offers.example.json): fictional matcher data.
- [`test_job_radar.py`](test_job_radar.py): rule, similarity, learning and source-failure tests.
- [`MATCHING.md`](MATCHING.md): data schema and technical guide; [`AI-METHODS.md`](AI-METHODS.md): scope of AI methods.

## 1. Your idea in a nutshell

**Job Radar** helps identify job opportunities related to a professional profile and assess their requirements. Each user can choose their locations, positions and keywords.

The project combines public-source searching, AI assistance and evidence review. Each recommendation explains its relevance, requirements that still need confirmation and limitations in accessing the listing.

## 2. Background

Job listings are spread across job boards and company websites. The same vacancy may appear multiple times, be reposted or remain indexed after closing. Reviewing these sources and comparing them against a profile takes time every day.

The project's motivation is to make searches configurable across several geographical areas, without assuming experience that the user has not confirmed.

This is a recurring problem during an active job search. The project does not provide population-level statistics about its frequency; it addresses a need observed in everyday use. AI's usefulness depends both on finding results and on recognizing missing or unverifiable information.

## 3. Data and AI techniques

### Data sources

- A professional profile voluntarily provided by the user: education, experience and confirmed skills.
- Public listings from LinkedIn Jobs and InfoJobs.
- Company and recruitment consultancy career pages, preferred when they allow verification of the original listing.
- A history of listings and deliveries to avoid duplicates.

Public pages and indexed content may be consulted when direct access fails. This does not imply authenticated access to job boards or their complete databases. An indexed result alone does not establish that a vacancy is still open.

### Techniques used in the assisted workflow

This section describes use with an external assistant. The local code implements the rules and numerical methods below without calling a language model.

- Query expansion using technical synonyms: PLC, programmable logic controllers, automation, HMI, SCADA, Siemens/TIA Portal, STEP 7, Rockwell, Schneider or Omron.
- Semantic interpretation using a language model to relate job requirements to confirmed profile information.
- Extraction and summarization of title, company, location, date, contract, salary, working arrangement and requirements.
- Comparison of titles, companies, locations, links and duties to identify duplicates and reposts.
- Explanations of relevance and information gaps, with links to sources.

Brands and tools used as search terms do not automatically become user skills. No model trained on real data is distributed, and precision or recall has not been measured. The matcher implements heuristic deduplication and optional logistic classification, but no persistent database.

### Numerical methods in the matcher

Text is normalized and tokenized. TF-IDF uses relative term frequency and smoothed IDF `log((1+n)/(1+df))+1`; cosine measures overlap between the profile and listing vectors. This is not embedding-based semantic matching and does not automatically recognize synonyms.

The initial index is `100 × (0.55 × cosine + 0.30 × skill_coverage + 0.10 × location + 0.05 × experience)`. Weights are initial design choices, not learned or validated values. Optional logistic regression uses those four features and learns through gradient descent with L2 regularization. Bayes, Monte Carlo and k-NN are not implemented.

### Current project status

The code includes function docstrings and comments in Spanish. See [AI-METHODS.md](AI-METHODS.md): the generator and matcher are separate modules. The matcher implements cosine similarity and optional logistic regression.

This repository includes a configurable **local search-instruction generator** and a local matcher. The matcher imports files or authorized JSON feeds; it does not scrape job-board HTML or send emails. It is not a standalone alert application. Cloning it or changing its configuration does not modify any external alert.

No credentials, recipient details, personal history or complete copies of job advertisements are included.

## 4. How is it used

### Match listings against a profile

Requires Python 3.10+, with no extra packages. Copy the profile to `profile.local.json` and enter locations, positions, skills, a summary and years of experience (`null` when unknown). Import listings using the schema in [MATCHING.md](MATCHING.md):

```sh
python job_radar.py rank --profile profile.local.json --source offers.local.json
```

Repeat the option to combine local sources:

```sh
python job_radar.py rank --profile profile.local.json --source offers-a.local.json --source offers-b.local.json
```

An HTTPS URL returning JSON in the expected schema is also supported. Ordinary HTML job-board pages cannot be used directly as feeds.

### Train and apply logistic regression

Prepare `feedback.local.json` with at least 20 human ratings, including both relevant and irrelevant examples. Each entry contains `features` copied from a result and a human `relevant` label of 0 or 1. This is a technical minimum, not a guarantee of adequate training data. Do not generate labels from the program's own scores.

```json
{"features": [0.45, 0.5, 1, 0], "relevant": 1}
```

```sh
python job_radar.py train --feedback feedback.local.json > model.local.json
python job_radar.py rank --profile profile.local.json --source offers.local.json --model model.local.json
```

With a model, the report adds `estimated_relevance` and uses it to rank eligible listings. Models are marked `evaluated: false`. Neither this estimate nor the manual index is a hiring probability. Files named `*.local.json` are excluded from Git.

### Run tests

```sh
python -m unittest -v test_job_radar.py
```

The 10 tests cover cosine, location/closure/expiry rules, unknown experience, invalid data, duplicates, partial/total source failures, mocked HTTPS import, logistic learning and preservation of exclusions when using a model. These are synthetic checks, not an evaluation of real recommendations.

### Generate instructions for an external assistant

The user chooses locations and positions in a local file and generates instructions. After reviewing the output, they use it with an assistant that has search access. Frequency and delivery channels would be configured separately in the environment running the search; the generator does not schedule tasks or connect accounts.

### Choosing locations and positions

Requires Python 3.10 or later, with no additional packages.

1. Copy `search.example.json` to `search.local.json` (the latter is excluded from Git).
2. Edit `locations` and `positions`: each list accepts multiple entries, treated as alternatives. Locations explicitly state their scope; nearby places are not added automatically.
3. Use `keywords` for optional search terms and `confirmed_skills` only for confirmed skills. A keyword is not proof of a skill.
4. Run:

```sh
python configure_search.py --config search.local.json
```

The output is displayed on screen. To try it without personal data:

```sh
python configure_search.py --config search.example.json
```

You can also choose the lists when running the command. Repeating an option adds another alternative; supplied options replace the corresponding list from the file:

```sh
python configure_search.py --config search.example.json --location "Invented City (fictional city)" --position "Sensor technician (example position)"
```

The example file uses **invented locations and a fictional profile**; it does not describe real people or vacancies. See [EXAMPLE.md](EXAMPLE.md), currently in Spanish. The program checks that required lists are not empty. It does not validate whether a location exists: this permits fictional examples and requires review for real searches.

**Language note:** this document is in English, but the current generator's instructions, validation messages and example configuration are in Spanish. Configuration values may be written in English; this does not translate the generated instruction template.

The intended assisted workflow searches sources, checks for closures, removes duplicates and prepares a summary. Before any delivery, it checks whether an email for that day already exists. Messages include new listings or relevant changes; incomplete coverage is disclosed without claiming that no vacancies exist. The user reviews the links and decides whether to apply. Applications are not submitted automatically. These search and delivery steps are not implemented by the local generator.

Example output format with fictional data:

> FICTIONAL DEMONSTRATION: Sensor technician — Invented Company — Invented City. Contract: not stated. Salary: not stated. Relevance and requirements: pending a real review. No advertisement or application link exists.

People affected:

- **Candidates:** receive search support, retain control over their data and decisions, and need to understand uncertainty in recommendations.
- **Employers and recruiters:** their requirements must be summarized accurately, without attributing unpublished conditions to them.
- **Job boards and sources:** retain their rights and access conditions; the project links to advertisements and does not bypass access restrictions.
- **Other stakeholders:** future expansion should account for accessibility, different career paths and selection bias.

## 5. Challenges

- There are no LinkedIn or InfoJobs-specific connectors, HTML requirement extraction or email delivery; input must be structured data.
- Locations and skills use normalized text matching. There is no geocoding or semantic equivalence; cities are not automatically mapped to provinces.
- TF-IDF depends on the imported batch: changing listings may change scores and regression features. Production use requires a stable vocabulary/IDF and independent evaluation on representative data.
- Experience is compared globally, not per technology. Open status is a source assertion rather than an automatic verification.

- The project cannot guarantee finding every vacancy or verifying the status of every indexed listing.
- Blocked pages, login requirements and outdated search indexes limit coverage.
- AI may omit or misinterpret requirements; verifiable sources and human review remain necessary.
- Listings may change URL, recruitment intermediary or title, making deduplication harder.
- Profiles may be incomplete: years of experience, duties or tool proficiency must not be invented.
- Thematic relevance does not prove that a user meets every requirement or guarantee employment.
- Email delivery depends on permissions, quotas and the availability of Gmail and the platform running the task.
- The project does not solve a shortage of vacancies, hiring discrimination or salary negotiation.
- It does not publish full advertisements, bypass access controls or submit job applications.

## 6. What next

1. Implement a structured record of listings, sources, status checks and deliveries with stable identifiers.
2. Extend the existing import, comparison and review stages with a separate delivery layer.
3. Add connectors for specific official APIs or feeds when available and authorized; generic JSON import already exists.
4. Evaluate human-reviewed examples for relevance, duplicates, closed listings and accuracy of contract and salary information.
5. Let users correct their skills and mark useful or irrelevant listings without inferring sensitive attributes.
6. Add an accessible dashboard showing source availability and notification controls.
7. Expand configuration options according to user needs.

## 7. Acknowledgments

- **Idea and requirements:** provided by the project's initiator, whose identity is not published in these files.
- **Documentation and local generator:** prepared with OpenAI Codex assistance. Generated work is not presented as independent research or development by the project's initiator.
- **Job sources:** advertising companies, LinkedIn and InfoJobs. Each advertisement belongs to its creator; using a data source does not mean using its code.
- **Workflow tools:** Codex and the Gmail connection. These are external services, not code incorporated into the repository.
- **Inspiration:** making job searches easier and the seven-part AI project proposal format. The questionnaire is not attributed to a specific institution without verifying its origin.

**Code used in this repository:** `configure_search.py`, `job_radar.py` and `test_job_radar.py`, generated for this project with OpenAI Codex assistance. They use only the Python standard library, maintained by its community and distributed by the Python Software Foundation. No external snippets or pretrained models are incorporated. Attribution and dependencies are documented in [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md), currently in Spanish.

### Sources and references

- [LinkedIn Jobs](https://www.linkedin.com/jobs/).
- [InfoJobs](https://www.infojobs.net/).
- [OpenAI Codex](https://openai.com/codex/).
- [Gmail](https://mail.google.com/).

References identify sources and tools; they do not imply sponsorship, affiliation, a reuse license or guaranteed access.

## License

The project's own code and documentation are distributed under the [MIT License](LICENSE). It permits use, modification and redistribution, including commercial use, provided the copyright and permission notices are retained. The software is provided without warranty. The notice uses “Job Radar contributors” without publishing personal information.

Python and external components retain their own licenses. This license does not grant rights to third-party advertisements, data or external services, and does not change the repository's private visibility. Reference text: [MIT — Open Source Initiative](https://opensource.org/license/mit).
