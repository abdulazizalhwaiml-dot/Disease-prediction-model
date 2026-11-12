# Host Mizanak on Streamlit Community Cloud

**The website is hosted on Streamlit Community Cloud at [https://mizanak.streamlit.app/](https://mizanak.streamlit.app/).**

GitHub stores the source and model files. Streamlit Community Cloud runs Python and serves the application. GitHub Pages serves static sites and cannot run this Streamlit application.

## Deployment configuration

- Repository: `abdulazizalhwaiml-dot/Disease-prediction-model`.
- Canonical branch: `main`, containing both the application and active models.
- Entrypoint: `streamlit_app.py`, which configures local imports from `src/`.
- Trusted model release: `models/current.json`, eight joblib files, and a manifest.
- `requirements.txt` pins the Python packages used by the models.
- `packages.txt` installs `libgomp1`, required by LightGBM on Linux.
- No per-session training or AI-service API key is required.

## Recreate the deployment

1. Open https://share.streamlit.io and sign in with the repository owner's GitHub account.
2. Connect GitHub. The repository is currently public; grant Streamlit access if it becomes private.
3. Select **Create app**, then deployment from GitHub.
4. Use the following settings:

| Setting | Value |
|---|---|
| Repository | `abdulazizalhwaiml-dot/Disease-prediction-model` |
| Branch | `main` |
| Main file path | `streamlit_app.py` |
| Python version — Advanced settings | **3.12** |

5. Choose an available subdomain and select **Deploy**. The existing deployment uses `mizanak.streamlit.app`.
6. Open the deployed URL, answer both family-history questions, and check the estimates and common wellness message.
7. Review sharing settings; repository privacy and application privacy are separate settings.

Use `main` for development, runtime, and deployment. Do not deploy from `downloads/*` branches, which contain ZIP packages rather than extracted application files. Use [Releases](https://github.com/abdulazizalhwaiml-dot/Disease-prediction-model/releases/latest) for ready packages. Earlier branches remain as historical records.

## Free and low-cost options

The original service comparison was checked against official pages on **November 3, 2026**; prices and limits may change.

| Service | Cost | Suitability |
|---|---|---|
| Streamlit Community Cloud | Free | Current host; deploys directly from `main` with HTTPS and a `streamlit.app` URL |
| Render Web Service | Limited free resources, or paid compute from $7/month | Python alternative; the $7 plan has 512 MB RAM and a larger plan may be needed |

Inactive Streamlit applications sleep after 12 hours and wake when visited. Continuous uptime and unlimited resources are not guaranteed. This application needs no database, GPU, or API subscription. Review service logs before choosing a paid plan if resources become an issue.

GitHub Pages cannot run Python/Streamlit. The original comparison did not assume free Hugging Face Docker Spaces: its documentation required a paid plan to create Docker Spaces, even when CPU Basic had no hourly charge.

### Optional Render configuration

Create a **Web Service** from the repository's `main` branch, select **Python**, and use:

```text
Build Command: pip install -r requirements.txt
Start Command: python -m streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=$PORT
Health Check Path: /_stcore/health
Environment Variable: PYTHON_VERSION=3.12.12
```

Render deployment has not been tested. If build logs report missing `libgomp1`, use the included Dockerfile instead of the Python environment, with port `8501` in the container start command. A paid disk or database is unnecessary for this application.

## Troubleshooting

- **Python version mismatch:** select 3.12 when creating the app; do not bypass model checks by changing the manifest.
- **Repository not listed:** complete Streamlit/GitHub access authorization for private repositories.
- **No valid models:** select `main` and verify `models/current.json` and its referenced directory exist.
- **libgomp error:** verify the repository-root `packages.txt` contains `libgomp1`.
- **Package installation failure:** inspect build logs. Avoid arbitrary package upgrades because model compatibility checks use package versions.

The project remains experimental and is not clinically validated. Performance on home scales and local populations requires external validation.

References: [Official deployment steps](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), [Application dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies), [Streamlit resources and sleep](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app#app-resources-and-limits), [Render pricing](https://render.com/pricing), [Hugging Face Spaces](https://huggingface.co/docs/hub/spaces-overview), [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).
