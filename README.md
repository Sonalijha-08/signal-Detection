# Signal Detection System
Detect when a company is entering a large hiring phase by scanning public news, press releases, and career pages.
## Setup and Run
1. **Clone / open the project** (already located at `C:/Users/Sonali Jha/.gemini/antigravity/scratch/signal_detection`).
2. **Create a virtual environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```
3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   # required packages (if no requirements.txt):
   pip install colorama feedparser beautifulsoup4 requests
   ```
4. **Prepare the companies list** – edit `companies.json` to contain the desired company names (one JSON array of strings).
5. **Run the handler**
   ```powershell
   python handler.py companies.json --json signals_output.json --sqlite signals.db --verbose --min-score 0
   ```
   The command will fetch RSS feeds and career pages, score hiring signals, deduplicate to one record per company, and output JSON and SQLite files.
## Features
- Accept a list of target companies (JSON array).
- Fetch recent Google News RSS results for each company.
- Optionally fetch the company's `/careers` page (simple heuristic).
- Extract hiring‑related keywords and numeric hiring signals (e.g., "500+ hires").
- Score each signal with a heuristic confidence score (0‑100).
- Output structured records in JSON (required) and optionally SQLite.
- Modular design: `signals/` package, `utils/` helpers, and a lightweight CLI.
## Data Ingestion Approach
- **RSS feeds** – `signals/fetcher.py` calls `fetch_rss(company)`, which builds a Google News RSS URL for the company name (e.g., `https://news.google.com/rss/search?q=Apple+hiring`). This gives fresh news articles about hiring.
- **Career pages** – a simple heuristic derives a domain `company.com` and fetches `https://{domain}/careers`. The HTML is parsed for numeric hiring signals.
- **Why** – RSS provides timely, structured news without needing API keys; career pages contain explicit hiring counts when companies publish them.
- **Work‑arounds** – many companies don’t expose a `/careers` page or block bots, so the fetcher falls back gracefully and the system continues with whatever sources succeeded.
## Project Structure
##AI used: Claude code , Copilot , git copilot
```
signal_detection/
├─ signals/                # Core signal detection logic
│   ├─ __init__.py
│   ├─ fetcher.py          # RSS, generic URL, career page fetch
│   ├─ parser.py           # HTML → text, keyword & numeric extraction
│   ├─ scorer.py           # Heuristic scoring
│   └─ output.py           # JSON / SQLite writers
├─ utils/                  # Helper utilities
│   ├─ __init__.py
│   ├─ http.py             # requests session with retries
│   └─ logging.py          # simple logger
├─ cli.py                  # Command‑line interface
├─ requirements.txt        # Python dependencies
└─ README.md               # You are reading it!
```
## Scoring Logic
|
 Score 
|
 Meaning 
|
|
------
|
----------
|
|
 95   
|
**
High‑confidence
**
 – presence of any 
`HIGH_KEYWORDS`
 (e.g., “mass hiring”, “massive expansion”) 
**
or
**
 a numeric count ≥ 1000.
|
 85   
|
**
Mid‑score
**
 – presence of any 
`MID_SCORE_KEYWORDS`
 (e.g., “high hiring”, “500+ hires”) 
**
or
**
 a numeric count between 500‑999.
|
 70   
|
**
Multiple keywords
**
 – two or more distinct hiring‑related keywords but no strong numeric signal.
|
 55   
|
**
Single keyword
**
 – at least one hiring keyword from 
`HIRING_KEYWORDS`
.
|
 35   
|
**
Weak/No signal
**
 – no keywords and no numbers; reason text is “wenwill hire soon”.
## Installation
```bash
# From the project root
python -m venv venv       # optional but recommended
source venv/Scripts/activate   # Windows PowerShell
pip install -r requirements.txt
```
**What the score cannot capture** – sentiment, context (e.g., a rumor vs. an official announcement), or future hiring plans announced without numbers.
The `requirements.txt` currently contains:
```
requests
beautifulsoup4
feedparser
pydantic
```
Feel free to add more packages if you extend the system.
## Assumptions and Limitations
- **Assumptions**
  - Companies expose a public RSS feed via Google News.
  - The career page is reachable at `https://{company}.com/careers`.
  - Keywords listed cover most real‑world hiring mentions.
- **Limitations**
  - Misses signals on sub‑domains or non‑standard career URLs.
  - Numbers extracted are naïve (e.g., “500‑600” becomes `500`).
  - Deduplication keeps only the highest‑scoring record; other useful signals are discarded.
- **First‑fix priority** – improve career‑page discovery (search for a “careers” link) and add sentiment analysis to filter out speculative articles.
## Usage
1. **Prepare a list of companies** – a JSON file containing an array of company names:
```json
["Acme Corp", "Globex Inc", "Initech"]
```
Save it as, for example, `companies.json`.
## AI‑Tool‑Usage‑Log
All AI‑assisted actions performed during development are saved in the `ai-tool-usage-log/` folder. See `session_log.md` for a complete transcript of tool calls (file reads, edits, and reasoning).
2. **Run the CLI**:
```bash
python cli.py companies.json --output-json signals_output.json [--output-sqlite signals.db]
```
   - `--output-json` (required) – path where the JSON results will be written.
   - `--output-sqlite` (optional) – path to a SQLite database file to store the same records.
   - `--min-score` (optional) – set a minimum confidence score to filter weak signals.
**Generated code verification** – All modifications (fallback reason change, deduplication logic) were written, reviewed with the file‑view tools, and executed locally to confirm they run without errors. Any AI‑suggested snippets were inspected and adjusted to fit the project’s style and requirements.
3. **Inspect the results**:
   - Open `signals_output.json` – it contains an array of objects with the shape:
```json
{
  "company": "Acme Corp",
  "signal_type": "mass_hiring_signal",
  "source_url": "https://...",
  "matched_keywords": ["hiring", "expansion"],
  "signal_score": 85,
  "detected_at": "2026-05-26T16:00:00Z",
  "reason": "found keywords: hiring, expansion; numeric hiring signal(s): 500"
}
```
   - If you supplied `--output-sqlite`, you can explore the DB with any SQLite client:
```sql
SELECT * FROM signals;
```
## Extending / Customising
- **Add more keywords** – edit `signals/parser.py` → `HIRING_KEYWORDS`.
- **Tune the scoring** – modify `signals/scorer.py` → `score_signal`.
- **Improve career‑page discovery** – enhance `signals/fetcher.py` → `fetch_company_careers`.
