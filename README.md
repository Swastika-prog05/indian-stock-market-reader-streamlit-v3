# Indian Stock Market Reader Streamlit V3

Repository name:

indian-stock-market-reader-streamlit-v3

This V3 version fixes the preset issue where IT Portfolio, Consumer Portfolio, and Growth Portfolio could show:

"Could not fetch enough valid data."

What changed:

- Replaced weak/problematic preset tickers with more stable NSE tickers.
- Reduced strict data requirement from 60 rows to 40 rows.
- Fetches stocks one by one instead of one large Yahoo Finance batch.
- Skips unavailable tickers instead of failing the whole app.
- Uses more reliable Growth Portfolio stocks.
- Uses more reliable Consumer and IT Portfolio stocks.
- Shows skipped tickers as a warning.
- Keeps the analysis running when at least 2 valid stocks are available.

Upload these files to the root of your GitHub repository:

indian-stock-market-reader-streamlit-v3/
├── streamlit_app.py
├── requirements.txt
└── README.md

Streamlit Cloud settings:

Main file path:
streamlit_app.py

After uploading:

1. Open Streamlit Cloud.
2. Select repo: indian-stock-market-reader-streamlit-v3
3. Set main file path: streamlit_app.py
4. Deploy.

If updating an existing app:

1. Open Manage app.
2. Click Clear cache and reboot.

Important:

The dependency file must be named exactly:

requirements.txt
