# Repository guide

**The canonical release is on `main`.** This branch contains the source and models needed to run and deploy the application.
The live website is hosted on **Streamlit Community Cloud**: **[https://mizanak.streamlit.app/](https://mizanak.streamlit.app/)**.
Ready packages are available in [GitHub Releases](https://github.com/abdulazizalhwaiml-dot/Disease-prediction-model/releases/latest). Historical branches remain available for reference and are not needed to run the current version.

| Task | Guide |
|---|---|
| Windows setup | [WINDOWS.md](WINDOWS.md) |
| Streamlit hosting and alternatives | [STREAMLIT_CLOUD.md](STREAMLIT_CLOUD.md) |
| Docker and retraining | [DEPLOYMENT.md](DEPLOYMENT.md) |
| Development and interface checks | [DEVELOPMENT.md](DEVELOPMENT.md) |
| Data and condition definitions | [DATA_DICTIONARY.md](DATA_DICTIONARY.md) |
| Methodology and limitations | [METHODOLOGY.md](METHODOLOGY.md) |
| Completed validation | [VALIDATION.md](../reports/VALIDATION.md) |
| Current model performance | [MODEL_CARD.md](../reports/MODEL_CARD.md) |

`app/` contains the interface, `src/nhanes_ai/` contains data and model code, and `scripts/` contains setup and launch commands. Original NHANES files and training reports remain separate from the interface so results can be verified.
