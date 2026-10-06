# Benchmark Architect: The Performance Truth Engine — MVP

A beginner-friendly Streamlit prototype for comparing a PMS portfolio with a custom benchmark.

## What this version does

- Presents a simple Level 1 benchmark mission
- Uses deterministic synthetic Indian market-style returns
- Lets the player build a three-component custom benchmark
- Calculates R², tracking error, information ratio, beta and simplified alpha
- Shows portfolio vs benchmark growth visually
- Produces a 1,000-point architect score and XP
- Explains the statistics in plain English

## Important

This prototype uses synthetic data only. It is an educational demonstration, not investment advice, and should not be represented as live market analytics.

## Recommended setup

Use Python 3.13 for this first version. Create a virtual environment, install the packages, then run Streamlit.

### Mac / Linux

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

The browser should open to the app. If it does not, open the local URL shown in the terminal.

### Browser-only alternative

Streamlit Community Cloud can be connected to a GitHub repository, and GitHub Codespaces can provide a browser-based development environment. See the official Streamlit documentation.

## Project structure

```text
benchmark_architect_mvp/
├── app.py
├── benchmark_engine.py
├── requirements.txt
├── README.md
└── tests/
    └── test_engine.py
```

## Next development stages

1. Holdings-based style analysis
2. Portfolio characteristics and sector weights
3. Benchmark appropriateness score
4. Benchmark gaming investigations
5. Brinson attribution
6. Campaign progression and achievements
7. Real/licensed historical data
8. Multi-market support
9. Sandbox and Arena modes
10. Production-grade deployment and user accounts
