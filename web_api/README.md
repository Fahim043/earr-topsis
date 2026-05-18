# EARR-TOPSIS FastAPI Backend

This folder exposes the three proposed thesis methods through a public API:

- **M4**: reliability-weighted bootstrap bagging
- **M6**: reliability-weighted fuzzy aggregation
- **M7 / EARR-TOPSIS**: entropy-aware reliability-weighted robust fuzzy TOPSIS

The animated browser dashboard is served from `web_api/static/index.html`. A GitHub Pages copy is available at `../docs/index.html`.

## Local Start

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r web_api/requirements.txt
python -m uvicorn web_api.app:app --host 127.0.0.1 --port 8000 --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Web dashboard |
| `/health` | GET | Service health |
| `/api/methods` | GET | Method names and purpose |
| `/api/schema` | GET | Accepted upload schemas |
| `/api/example` | GET | Native fuzzy JSON example |
| `/api/validate` | POST | Validate and summarize an upload |
| `/api/run` | POST | Run selected methods |

## `/api/run` Form Fields

| Field | Required | Default | Meaning |
|---|---:|---:|---|
| `file` | yes | none | JSON, CSV, TSV, XLS, XLSX, or XLSM dataset |
| `methods` | no | `M4,M6,M7` | Comma-separated methods |
| `num_bags` | no | `100` | Bootstrap bag count |
| `seed` | no | `42` | Deterministic random seed |
| `pseudo_dms` | no | `15` | Pseudo decision makers for crisp uploads |
| `cost_criteria` | no | empty | Comma-separated cost criteria for crisp uploads |
| `top_k` | no | `50` | Ranking rows returned per method |
| `max_alternatives` | no | `300` | Limit alternatives for large workbooks; `0` means no limit |

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/run \
  -F "file=@web_api/examples/example_native.json" \
  -F "methods=M4,M6,M7" \
  -F "num_bags=20" \
  -F "seed=42" \
  -F "top_k=10"
```

Crisp matrix example:

```bash
curl -X POST http://127.0.0.1:8000/api/run \
  -F "file=@web_api/examples/example_crisp.csv" \
  -F "methods=M7" \
  -F "num_bags=20" \
  -F "seed=42" \
  -F "pseudo_dms=15" \
  -F "cost_criteria=cost" \
  -F "top_k=10"
```

## Supported Dataset Formats

### Native JSON

Required:

- `alternatives`
- `criteria`
- `decision_makers`
- `ratings`

Optional:

- `criteria_weights`
- `criteria_types`

### Flat fuzzy table

Required columns:

- `decision_maker`
- `alternative`
- `criterion`
- `l`
- `m`
- `u`

Optional columns:

- `weight_l`
- `weight_m`
- `weight_u`
- `criteria_type`

### Crisp matrix

The first text column is interpreted as the alternative identifier. Numeric columns are converted to criteria. The backend creates deterministic pseudo decision makers for demonstration, and listed cost criteria are scaled in the reverse direction before conversion to fuzzy ratings.

For healthcare allocation style files with `city` and `year` columns, the backend creates alternatives such as `北京市_2008` so repeated city names do not collide. Missing numeric cells are treated as neutral mid-scale values during demo conversion.

### Supplier hesitant-fuzzy workbook

The API recognizes the supplier-selection workbooks used in the thesis when an Excel file contains the `Julgamentos DMs` sheet. It extracts decision-maker blocks and parses hesitant linguistic values such as `[s4]` or `[s3,s4]` into triangular fuzzy numbers.

Files that contain only labels or lookup information, such as `country_names.xlsx`, are rejected because TOPSIS needs numeric criteria or fuzzy ratings.

## Deployment

GitHub Pages can host only the static frontend. Deploy this backend separately to a Python host, or use Hugging Face Spaces to host the frontend and backend together.

Recommended free CPU-only route:

```text
Hugging Face Spaces -> Docker -> CPU Basic
```

Use the repository-level `Dockerfile`. It starts:

```bash
uvicorn web_api.app:app --host 0.0.0.0 --port 7860
```

See `../HUGGINGFACE_SPACES_DEPLOYMENT.md` for the full step-by-step guide.

Typical Render setup:

```text
Root directory: web_api
Build command: pip install -r requirements.txt
Start command: uvicorn app:app --host 0.0.0.0 --port $PORT
```

After deployment, open the GitHub Pages UI and paste the backend URL into the **API endpoint** field.

## Safety

This backend is a research prototype. Before public production use, add authentication, upload-size limits, rate limits, malware/file-type scanning, persistent job records, and secure cleanup of uploaded files.
