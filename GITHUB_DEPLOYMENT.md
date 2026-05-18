# GitHub and GitHub Pages Deployment

This project has two deployable parts:

1. **Static GitHub Pages UI**: `docs/index.html`
2. **Python FastAPI backend**: `web_api/app.py`

GitHub Pages cannot execute Python. The GitHub Pages site must call a separately running API backend.

## 1. Prepare the Repository

If this folder is not already a Git repository:

```bash
git init
git add .
git commit -m "Prepare EARR-TOPSIS public API and demo site"
```

Then create a GitHub repository and push:

```bash
git branch -M main
git remote add origin https://github.com/<username>/<repo>.git
git push -u origin main
```

## 2. Enable GitHub Pages

1. Open the GitHub repository.
2. Go to **Settings > Pages**.
3. Under **Build and deployment**, choose:
   - Source: `Deploy from a branch`
   - Branch: `main`
   - Folder: `/docs`
4. Save.
5. GitHub will publish the frontend at:

```text
https://<username>.github.io/<repo>/
```

## 3. Deploy the API Backend

Recommended no-cost CPU option: **Hugging Face Spaces**.

This project includes a repository-level `Dockerfile` that runs FastAPI on port `7860`, which is the standard Docker Space port.

1. Create a Hugging Face Space.
2. Select:
   - SDK: `Docker`
   - Hardware: `CPU Basic`
3. Push this repository's deployable files to the Space.
4. The hosted app will be available at:

```text
https://<username>-<space-name>.hf.space
```

That one URL serves both:

- frontend: `/`
- backend: `/api/run`

See `HUGGINGFACE_SPACES_DEPLOYMENT.md` for the full guide.

Alternative beginner-friendly option: Render.

1. Push this repository to GitHub.
2. Open Render and create a new **Web Service** from the GitHub repo.
3. Render can use `render.yaml`, or configure manually:
   - Root directory: `web_api`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. After deployment, copy the Render service URL.
5. Paste that URL into the GitHub Pages UI's **API endpoint** field.

## 4. Local Test Before Publishing

```bash
source .venv/bin/activate
python -m uvicorn web_api.app:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

Run an API test:

```bash
curl -X POST http://127.0.0.1:8000/api/run \
  -F "file=@web_api/examples/example_native.json" \
  -F "methods=M4,M6,M7" \
  -F "num_bags=20" \
  -F "seed=42" \
  -F "top_k=10"
```

## 5. Public Safety Checklist

Before making the repository public, check:

- Remove private datasets if they should not be redistributed.
- Remove unofficial PDF drafts if they contain personal/admin information.
- Keep `outputs/final_evidence/` if you want reproducible thesis tables visible.
- Keep `web_api/examples/` because users need upload examples.
- Do not claim the API is a production decision authority.

The platform is a research demo and reproducibility interface.
