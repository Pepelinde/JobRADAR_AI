# Job Radar

[Español](README.md) | **English**

A configurable project for assisted job searching: choose locations, positions and keywords.

**New: local matcher.** Import JSON listings, apply rules and TF-IDF cosine similarity, and optionally train logistic regression from human relevance labels. See [MATCHING.md](MATCHING.md), including an English summary, for the demo and limitations.

```sh
python job_radar.py rank --profile profile.example.json --source offers.example.json
```

All examples are fictional. No platform-specific connectors or automatic email delivery are included.

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

- Query expansion using technical synonyms: PLC, programmable logic controllers, automation, HMI, SCADA, Siemens/TIA Portal, STEP 7, Rockwell, Schneider or Omron.
- Semantic interpretation using a language model to relate job requirements to confirmed profile information.
- Extraction and summarization of title, company, location, date, contract, salary, working arrangement and requirements.
- Comparison of titles, companies, locations, links and duties to identify duplicates and reposts.
- Explanations of relevance and information gaps, with links to sources.

Brands and tools used as search terms do not automatically become user skills. No model trained on real data is distributed, and precision or recall has not been measured. The matcher implements heuristic deduplication and optional logistic classification, but no persistent database.

### Current project status

The code includes function docstrings and comments in Spanish. See [AI-METHODS.md](AI-METHODS.md): the generator and matcher are separate modules. The matcher implements cosine similarity and optional logistic regression.

This repository includes a configurable **local search-instruction generator** and a local matcher. The matcher imports files or authorized JSON feeds; it does not scrape job-board HTML or send emails. It is not a standalone alert application. Cloning it or changing its configuration does not modify any external alert.

No credentials, recipient details, personal history or complete copies of job advertisements are included.

## 4. How is it used

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
2. Separate data acquisition, relevance assessment, review and delivery so that each stage can be checked.
3. Add official APIs or feeds when available and authorized for use.
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

**Code used in this repository:** `configure_search.py`, generated for this project with OpenAI Codex assistance. It uses only the Python standard library and incorporates no external snippets. Attribution and dependencies are documented in [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md), currently in Spanish. The Python community and Python Software Foundation are credited there for Python and its standard library.

### Sources and references

- [LinkedIn Jobs](https://www.linkedin.com/jobs/).
- [InfoJobs](https://www.infojobs.net/).
- [OpenAI Codex](https://openai.com/codex/).
- [Gmail](https://mail.google.com/).

References identify sources and tools; they do not imply sponsorship, affiliation, a reuse license or guaranteed access.
