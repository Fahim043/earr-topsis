# Free Backend Deployment With Hugging Face Spaces

GitHub hosts the source repository, README, diagrams, and frozen evidence tables. Hugging Face Spaces hosts the live Python system. For this project, the clean free option is a **Hugging Face Docker Space** because the algorithm is CPU-only.

## Why This Fits

- No GPU is required.
- Hugging Face CPU Basic Spaces are free.
- CPU Basic currently provides 2 vCPU, 16 GB RAM, and 50 GB non-persistent disk.
- A free CPU Space may sleep after long inactivity; a visitor wakes it again.
- The backend does not need persistent storage because uploads are processed temporarily.

## What Is Included

This repository now includes:

- `Dockerfile`: runs the FastAPI app on port `7860`, the standard Hugging Face Space port.
- `.dockerignore`: keeps heavy thesis outputs, local virtual environments, PDFs, and raw datasets out of the Docker image.
- `web_api/app.py`: serves both the UI and the API from the same backend.

## Deployment Steps

1. Create a free Hugging Face account.
2. Go to **Spaces > Create new Space**.
3. Choose:
   - Space SDK: `Docker`
   - Hardware: `CPU Basic`
   - Visibility: `Public` for professor/demo sharing, or `Private` while testing
4. Clone the Space repository:

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
```

5. Copy this project into that Space repository, including:
   - `Dockerfile`
   - `.dockerignore`
   - `web_api/`
   - `m1_normal_topsis.py`
   - `m4_weighted_bagging.py`
   - `m6_reliability_weighted.py`
   - `m7_entropy_reliability.py`
   - `reliability.py`

6. Make sure the Space `README.md` starts with this YAML block:

```yaml
---
title: EARR-TOPSIS
colorFrom: purple
colorTo: pink
sdk: docker
app_port: 7860
---
```

7. Commit and push:

```bash
git add .
git commit -m "Deploy EARR-TOPSIS FastAPI demo"
git push
```

8. Open:

```text
https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space
```

The same URL is both the website and the API backend. For example:

```text
https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/health
https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/api/run
```

## Limits To Mention Honestly

- It is a research prototype, not a production SaaS.
- Free CPU hosting may sleep after inactivity.
- Large workbooks with thousands of alternatives and hundreds of bags can be slow.
- Uploaded files are processed as temporary files; no result database is stored.
- Public deployments should avoid confidential datasets unless private hosting is enabled.
