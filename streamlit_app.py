import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from datetime import date, timedelta

st.set_page_config(
    page_title="Indian Stock Market Reader",
    page_icon="📈",
    layout="wide"
)

# ---------------------------------------------------
# Stable Indian stock universe
# Yahoo Finance NSE tickers use .NS
# This V3 version avoids weak/problematic preset tickers.
# ---------------------------------------------------

INDIAN_STOCKS = {
    "Large Cap": {
        "Reliance Industries": "RELIANCE.NS",
        "TCS": "TCS.NS",
        "HDFC Bank": "HDFCBANK.NS",
        "ICICI Bank": "ICICIBANK.NS",
        "Infosys": "INFY.NS",
        "Bharti Airtel": "BHARTIARTL.NS",
        "State Bank of India": "SBIN.NS",
        "Larsen & Toubro": "LT.NS",
        "ITC": "ITC.NS",
        "Hindustan Unilever": "HINDUNILVR.NS",
        "Axis Bank": "AXISBANK.NS",
        "Kotak Mahindra Bank": "KOTAKBANK.NS",
        "Bajaj Finance": "BAJFINANCE.NS",
        "HCL Technologies": "HCLTECH.NS",
        "Sun Pharma": "SUNPHARMA.NS",
        "Maruti Suzuki": "MARUTI.NS",
        "Asian Paints": "ASIANPAINT.NS",
        "Titan Company": "TITAN.NS",
        "UltraTech Cement": "ULTRACEMCO.NS",
        "NTPC": "NTPC.NS"
    },
    "Banking & Finance": {
        "HDFC Bank": "HDFCBANK.NS",
        "ICICI Bank": "ICICIBANK.NS",
        "State Bank of India": "SBIN.NS",
        "Axis Bank": "AXISBANK.NS",
        "Kotak Mahindra Bank": "KOTAKBANK.NS",
        "IndusInd Bank": "INDUSINDBK.NS",
        "Bank of Baroda": "BANKBARODA.NS",
        "Canara Bank": "CANBK.NS",
        "Federal Bank": "FEDERALBNK.NS",
        "Bajaj Finance": "BAJFINANCE.NS",
        "Bajaj Finserv": "BAJAJFINSV.NS"
    },
    "IT & Technology": {
        "TCS": "TCS.NS",
        "Infosys": "INFY.NS",
        "HCL Technologies": "HCLTECH.NS",
        "Wipro": "WIPRO.NS",
        "Tech Mahindra": "TECHM.NS",
        "LTIMindtree": "LTIM.NS",
        "Persistent Systems": "PERSISTENT.NS",
        "Mphasis": "MPHASIS.NS",
        "Coforge": "COFORGE.NS",
        "Oracle Financial Services": "OFSS.NS"
    },
    "FMCG & Consumer": {
        "ITC": "ITC.NS",
        "Hindustan Unilever": "HINDUNILVR.NS",
        "Nestle India": "NESTLEIND.NS",
        "Britannia": "BRITANNIA.NS",
        "Dabur India": "DABUR.NS",
        "Godrej Consumer Products": "GODREJCP.NS",
        "Marico": "MARICO.NS",
        "Tata Consumer Products": "TATACONSUM.NS",
        "Colgate Palmolive India": "COLPAL.NS",
        "Varun Beverages": "VBL.NS"
    },
    "Auto": {
        "Maruti Suzuki": "MARUTI.NS",
        "Mahindra & Mahindra": "M&M.NS",
        "Tata Motors": "TATAMOTORS.NS",
        "Bajaj Auto": "BAJAJ-AUTO.NS",
        "Hero MotoCorp": "HEROMOTOCO.NS",
        "Eicher Motors": "EICHERMOT.NS",
        "TVS Motor": "TVSMOTOR.NS",
        "Ashok Leyland": "ASHOKLEY.NS",
        "Bosch": "BOSCHLTD.NS",
        "MRF": "MRF.NS"
    },
    "Pharma & Healthcare": {
        "Sun Pharma": "SUNPHARMA.NS",
        "Dr Reddy's Laboratories": "DRREDDY.NS",
        "Cipla": "CIPLA.NS",
        "Divi's Laboratories": "DIVISLAB.NS",
        "Apollo Hospitals": "APOLLOHOSP.NS",
        "Lupin": "LUPIN.NS",
        "Aurobindo Pharma": "AUROPHARMA.NS",
        "Biocon": "BIOCON.NS",
        "Torrent Pharma": "TORNTPHARM.NS",
        "Max Healthcare": "MAXHEALTH.NS"
    },
    "Growth & Momentum": {
        "Trent": "TRENT.NS",
        "Dixon Technologies": "DIXON.NS",
        "Persistent Systems": "PERSISTENT.NS",
        "Tata Elxsi": "TATAELXSI.NS",
        "Polycab India": "POLYCAB.NS",
        "ABB India": "ABB.NS",
        "Bharat Electronics": "BEL.NS",
        "Cummins India": "CUMMINSIND.NS",
        "Varun Beverages": "VBL.NS",
        "Tata Motors": "TATAMOTORS.NS"
    },
    "Infrastructure & Cement": {
        "Larsen & Toubro": "LT.NS",
        "UltraTech Cement": "ULTRACEMCO.NS",
        "Shree Cement": "SHREECEM.NS",
        "Ambuja Cements": "AMBUJACEM.NS",
        "ACC": "ACC.NS",
        "Grasim Industries": "GRASIM.NS",
        "Adani Ports": "ADANIPORTS.NS",
        "Power Grid Corporation": "POWERGRID.NS",
        "NTPC": "NTPC.NS",
        "Coal India": "COALINDIA.NS"
    }
}

INDIAN_INDICES = {
    "Nifty 50": "^NSEI",
    "Sensex": "^BSESN",
    "Bank Nifty": "^NSEBANK",
    "Nifty IT": "^CNXIT"
}

PRESET_PORTFOLIOS = {
    "Balanced India Portfolio": [
        "Reliance Industries", "TCS", "HDFC Bank", "ICICI Bank", "Infosys",
        "Larsen & Toubro", "ITC", "Sun Pharma"
    ],
    "Banking Portfolio": [
        "HDFC Bank", "ICICI Bank", "State Bank of India", "Axis Bank",
        "Kotak Mahindra Bank", "Bank of Baroda", "Canara Bank"
    ],
    "IT Portfolio": [
        "TCS", "Infosys", "HCL Technologies", "Wipro", "Tech Mahindra",
        "Persistent Systems", "Mphasis"
    ],
    "Consumer Portfolio": [
        "ITC", "Hindustan Unilever", "Nestle India", "Britannia",
        "Dabur India", "Marico", "Tata Consumer Products"
    ],
    "Growth Portfolio": [
        "Trent", "Dixon Technologies", "Persistent Systems", "Tata Elxsi",
        "Polycab India", "ABB India", "Bharat Electronics", "Varun Beverages"
    ]
}


def flatten_stock_universe():
    stocks = {}
    sectors = {}
    for sector, stock_map in INDIAN_STOCKS.items():
        for name, ticker in stock_map.items():
            stocks[name] = ticker
            sectors.setdefault(name, set()).add(sector)
    return stocks, {name: ", ".join(sorted(vals)) for name, vals in sectors.items()}


ALL_STOCKS, STOCK_SECTORS = flatten_stock_universe()
TICKER_TO_NAME = {ticker: name for name, ticker in ALL_STOCKS.items()}


# ---------------------------------------------------
# UI styling
# ---------------------------------------------------

st.markdown(
    """
    <style>
    .main-answer {
        padding: 1.1rem;
        border-radius: 14px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    .answer-title {
        font-size: 1.08rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }
    .answer-text {
        font-size: 1rem;
        line-height: 1.55;
    }
    .small-note {
        color: #64748b;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def answer_box(title, text):
    st.markdown(
        f"""
        <div class="main-answer">
            <div class="answer-title">{title}</div>
            <div class="answer-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def pct(x):
    return f"{x:.2%}"


def money(x):
    return f"₹{x:,.0f}"


def risk_label(volatility):
    if volatility < 0.18:
        return "Low to moderate risk"
    if volatility < 0.30:
        return "Moderate to high risk"
    return "High risk"


def clean_custom_ticker(raw):
    value = raw.strip().upper()
    if not value:
        return ""
    if value.startswith("^"):
        return value
    if "." not in value:
        value = value + ".NS"
    return value


# ---------------------------------------------------
# Data functions
# ---------------------------------------------------

@st.cache_data(show_spinner=False, ttl=1800)
def fetch_single_ticker(ticker, start_date, end_date):
    """
    Fetches a single ticker.
    One-by-one fetching is more stable than one large Yahoo batch request.
    """
    try:
        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=True,
            threads=False
        )
    except Exception:
        return pd.Series(dtype=float)

    if data is None or data.empty:
        return pd.Series(dtype=float)

    if "Close" in data.columns:
        series = data["Close"].copy()
    elif "Adj Close" in data.columns:
        series = data["Adj Close"].copy()
    else:
        return pd.Series(dtype=float)

    series = series.dropna()
    series.name = ticker
    return series


@st.cache_data(show_spinner=False, ttl=1800)
def load_stock_data(tickers, start_date, end_date):
    valid_series = []
    failed_tickers = []

    for ticker in tickers:
        series = fetch_single_ticker(ticker, start_date, end_date)
        if series.empty or len(series.dropna()) < 40:
            failed_tickers.append(ticker)
        else:
            valid_series.append(series)

    if not valid_series:
        return pd.DataFrame(), sorted(list(set(failed_tickers)))

    prices = pd.concat(valid_series, axis=1).sort_index()
    prices = prices.ffill().dropna(how="all")

    final_valid = []
    for col in prices.columns:
        if prices[col].dropna().shape[0] >= 40:
            final_valid.append(col)
        else:
            failed_tickers.append(col)

    prices = prices[final_valid].ffill()

    # Do not require every stock to have data on every date.
    # Only drop rows where all selected stocks are missing.
    prices = prices.dropna(how="all")

    # Fill remaining gaps conservatively.
    prices = prices.ffill().bfill()

    return prices, sorted(list(set(failed_tickers)))


def calculate_stock_metrics(prices, risk_free_rate):
    daily_returns = prices.pct_change().replace([np.inf, -np.inf], np.nan).dropna(how="all")
    daily_returns = daily_returns.fillna(0)

    ann_return = daily_returns.mean() * 252
    ann_volatility = daily_returns.std() * np.sqrt(252)
    sharpe = (ann_return - risk_free_rate) / ann_volatility.replace(0, np.nan)
    total_return = (prices.iloc[-1] / prices.iloc[0]) - 1

    max_drawdown = {}
    for ticker in prices.columns:
        cumulative = prices[ticker] / prices[ticker].iloc[0]
        running_max = cumulative.cummax()
        drawdown = cumulative / running_max - 1
        max_drawdown[ticker] = drawdown.min()

    metrics = pd.DataFrame({
        "Total Return": total_return,
        "Annual Return": ann_return,
        "Annual Volatility": ann_volatility,
        "Sharpe Ratio": sharpe,
        "Max Drawdown": pd.Series(max_drawdown)
    })

    return metrics.replace([np.inf, -np.inf], np.nan).dropna(), daily_returns


def simulate_portfolios(daily_returns, simulations, risk_free_rate):
    tickers = list(daily_returns.columns)
    mean_returns = daily_returns.mean() * 252
    cov_matrix = daily_returns.cov() * 252

    rows = []
    for _ in range(simulations):
        weights = np.random.random(len(tickers))
        weights = weights / np.sum(weights)

        port_return = float(np.sum(mean_returns * weights))
        port_volatility = float(np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))))
        sharpe = float((port_return - risk_free_rate) / port_volatility) if port_volatility > 0 else 0

        row = {
            "Return": port_return,
            "Volatility": port_volatility,
            "Sharpe Ratio": sharpe
        }

        for ticker, weight in zip(tickers, weights):
            row[f"{ticker} Weight"] = float(weight)

        rows.append(row)

    sim_df = pd.DataFrame(rows)
    max_sharpe = sim_df.loc[sim_df["Sharpe Ratio"].idxmax()]
    min_risk = sim_df.loc[sim_df["Volatility"].idxmin()]
    return sim_df, max_sharpe, min_risk


def get_weights(best_row, tickers):
    return {ticker: float(best_row.get(f"{ticker} Weight", 0)) for ticker in tickers}


def normalize_prices(prices):
    return prices / prices.iloc[0] * 100


def backtest(prices, weights):
    if len(prices) < 80:
        return pd.Series(dtype=float), pd.Series(dtype=float), None

    split = int(len(prices) * 0.75)
    test_prices = prices.iloc[split:].copy()
    test_returns = test_prices.pct_change().replace([np.inf, -np.inf], np.nan).dropna(how="all").fillna(0)

    aligned_weights = np.array([weights.get(ticker, 0) for ticker in test_returns.columns])
    if aligned_weights.sum() <= 0:
        return pd.Series(dtype=float), pd.Series(dtype=float), None

    aligned_weights = aligned_weights / aligned_weights.sum()

    portfolio_returns = test_returns.dot(aligned_weights)
    portfolio_curve = (1 + portfolio_returns).cumprod() * 100

    equal_weight_returns = test_returns.mean(axis=1)
    benchmark_curve = (1 + equal_weight_returns).cumprod() * 100

    result = {
        "Portfolio Return": portfolio_curve.iloc[-1] / portfolio_curve.iloc[0] - 1,
        "Benchmark Return": benchmark_curve.iloc[-1] / benchmark_curve.iloc[0] - 1
    }

    return portfolio_curve, benchmark_curve, result


def random_forest_prediction(prices, ticker):
    series = prices[ticker].dropna()

    if len(series) < 120:
        return None, None, None

    df = pd.DataFrame({"Close": series})
    df["Lag 1"] = df["Close"].shift(1)
    df["Lag 2"] = df["Close"].shift(2)
    df["Lag 3"] = df["Close"].shift(3)
    df["Lag 5"] = df["Close"].shift(5)
    df["Rolling 7"] = df["Close"].rolling(7).mean()
    df["Rolling 21"] = df["Close"].rolling(21).mean()
    df["Momentum 7"] = df["Close"] / df["Close"].shift(7) - 1
    df = df.dropna()

    features = ["Lag 1", "Lag 2", "Lag 3", "Lag 5", "Rolling 7", "Rolling 21", "Momentum 7"]
    X = df[features]
    y = df["Close"]

    split = int(len(df) * 0.8)
    X_train = X.iloc[:split]
    X_test = X.iloc[split:]
    y_train = y.iloc[:split]
    y_test = y.iloc[split:]

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        min_samples_leaf=2
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))

    pred_df = pd.DataFrame({
        "Actual": y_test,
        "Predicted": predictions
    }, index=y_test.index)

    latest_features = X.iloc[[-1]]
    next_prediction = float(model.predict(latest_features)[0])
    latest_price = float(series.iloc[-1])
    expected_move = (next_prediction / latest_price) - 1

    summary = {
        "Latest Price": latest_price,
        "Predicted Next Price": next_prediction,
        "Expected Move": expected_move,
        "RMSE": rmse
    }

    return pred_df, rmse, summary


# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------

st.sidebar.title("Indian Stock Selection")

selection_mode = st.sidebar.radio(
    "Choose selection mode",
    ["Popular preset", "Sector based", "Manual stock search", "Custom ticker"]
)

selected_names = []
custom_tickers = []

if selection_mode == "Popular preset":
    preset = st.sidebar.selectbox("Select a preset portfolio", list(PRESET_PORTFOLIOS.keys()))
    selected_names = PRESET_PORTFOLIOS[preset]

elif selection_mode == "Sector based":
    selected_sectors = st.sidebar.multiselect(
        "Select sectors",
        list(INDIAN_STOCKS.keys()),
        default=["Large Cap", "Banking & Finance", "IT & Technology"]
    )

    sector_stock_names = []
    for sector in selected_sectors:
        sector_stock_names.extend(list(INDIAN_STOCKS[sector].keys()))

    sector_stock_names = sorted(list(dict.fromkeys(sector_stock_names)))

    default_count = min(8, len(sector_stock_names))
    selected_names = st.sidebar.multiselect(
        "Choose stocks from selected sectors",
        sector_stock_names,
        default=sector_stock_names[:default_count]
    )

elif selection_mode == "Manual stock search":
    selected_names = st.sidebar.multiselect(
        "Search and choose Indian stocks",
        sorted(list(ALL_STOCKS.keys())),
        default=[
            "Reliance Industries", "TCS", "HDFC Bank", "ICICI Bank",
            "Infosys", "Larsen & Toubro", "ITC", "Sun Pharma"
        ]
    )

elif selection_mode == "Custom ticker":
    custom_input = st.sidebar.text_area(
        "Enter NSE tickers",
        value="RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK",
        help="You can type RELIANCE or RELIANCE.NS. The app will auto-add .NS when needed."
    )
    custom_tickers = [clean_custom_ticker(x) for x in custom_input.split(",") if clean_custom_ticker(x)]

include_index = st.sidebar.checkbox("Compare with Indian index", value=True)
selected_index_name = st.sidebar.selectbox("Benchmark index", list(INDIAN_INDICES.keys()), index=0)

today = date.today()
start_date = st.sidebar.date_input("Start date", value=today - timedelta(days=365 * 5))
end_date = st.sidebar.date_input("End date", value=today)

risk_free_rate = st.sidebar.slider(
    "Risk-free rate",
    min_value=0.00,
    max_value=0.15,
    value=0.06,
    step=0.005
)

simulations = st.sidebar.slider(
    "Portfolio simulations",
    min_value=1000,
    max_value=30000,
    value=8000,
    step=1000
)

investment_amount = st.sidebar.number_input(
    "Investment amount",
    min_value=1000,
    value=100000,
    step=1000
)

portfolio_choice = st.sidebar.radio(
    "Portfolio strategy",
    ["Max Sharpe", "Minimum Risk"]
)

run = st.sidebar.button("Analyze now", type="primary")


# ---------------------------------------------------
# Main
# ---------------------------------------------------

st.title("Indian Stock Market Reader")
st.caption("Choose Indian stocks by name, sector, preset, or ticker. V3 uses more reliable presets and skips unavailable Yahoo Finance tickers.")

st.warning("Educational tool only. This is not financial advice.")

if not run:
    st.markdown("### Select Indian stocks from the sidebar and click **Analyze now**.")
    st.stop()

if selection_mode == "Custom ticker":
    tickers = custom_tickers
    selected_label_map = {ticker: ticker for ticker in tickers}
else:
    tickers = [ALL_STOCKS[name] for name in selected_names if name in ALL_STOCKS]
    selected_label_map = {ALL_STOCKS[name]: name for name in selected_names if name in ALL_STOCKS}

if len(tickers) < 2:
    st.error("Please select at least two valid stocks.")
    st.stop()

if len(tickers) > 15:
    st.info("For speed and stability, the app will analyze the first 15 selected stocks.")
    tickers = tickers[:15]

if start_date >= end_date:
    st.error("Start date must be earlier than end date.")
    st.stop()

with st.spinner("Fetching Indian market data and generating analysis..."):
    prices, failed_tickers = load_stock_data(tickers, start_date, end_date)

if failed_tickers:
    readable_failed = [TICKER_TO_NAME.get(t, t.replace(".NS", "")) for t in failed_tickers]
    st.warning(
        "Some selected stocks were skipped because Yahoo Finance returned limited or no data: "
        + ", ".join(readable_failed[:12])
        + ". The analysis below uses the valid stocks only."
    )

if prices.empty or len(prices.columns) < 2:
    st.error(
        "Still could not fetch enough valid data for this selection. "
        "Use Large Cap, Banking Portfolio, IT Portfolio, or choose at least 2 liquid NSE stocks like RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK."
    )
    st.stop()

valid_tickers = list(prices.columns)

display_names = {}
for ticker in valid_tickers:
    display_names[ticker] = selected_label_map.get(ticker, TICKER_TO_NAME.get(ticker, ticker.replace(".NS", "")))

metrics, daily_returns = calculate_stock_metrics(prices, risk_free_rate)

if metrics.empty or daily_returns.empty or len(metrics) < 2:
    st.error("The app could not calculate enough metrics from the selected valid stocks. Try a longer date range.")
    st.stop()

sim_df, max_sharpe, min_risk = simulate_portfolios(daily_returns, simulations, risk_free_rate)

selected_portfolio = max_sharpe if portfolio_choice == "Max Sharpe" else min_risk
weights = get_weights(selected_portfolio, valid_tickers)
portfolio_curve, benchmark_curve, backtest_result = backtest(prices, weights)

st.header("On-Spot Answer")

best_stock = metrics["Sharpe Ratio"].idxmax()
highest_return_stock = metrics["Annual Return"].idxmax()
lowest_risk_stock = metrics["Annual Volatility"].idxmin()
portfolio_risk = risk_label(selected_portfolio["Volatility"])

top_allocations = sorted(weights.items(), key=lambda x: x[1], reverse=True)
top_allocations = [(ticker, weight) for ticker, weight in top_allocations if weight > 0.01]
allocation_text = ", ".join([f"{display_names.get(ticker, ticker)}: {weight:.1%}" for ticker, weight in top_allocations[:6]])

answer_box(
    "Overall reading",
    f"Based on the selected period, <b>{display_names.get(best_stock, best_stock)}</b> has the strongest risk-adjusted performance. "
    f"The highest annual return comes from <b>{display_names.get(highest_return_stock, highest_return_stock)}</b>, while the lowest volatility comes from "
    f"<b>{display_names.get(lowest_risk_stock, lowest_risk_stock)}</b>."
)

answer_box(
    "Best portfolio",
    f"The selected strategy is <b>{portfolio_choice}</b>. The expected annual return is <b>{pct(selected_portfolio['Return'])}</b>, "
    f"expected volatility is <b>{pct(selected_portfolio['Volatility'])}</b>, and Sharpe ratio is <b>{selected_portfolio['Sharpe Ratio']:.3f}</b>. "
    f"Risk level: <b>{portfolio_risk}</b>."
)

answer_box(
    "Suggested allocation",
    f"For an investment amount of <b>{money(investment_amount)}</b>, the largest allocations are: <b>{allocation_text}</b>."
)

if backtest_result:
    outperform = backtest_result["Portfolio Return"] - backtest_result["Benchmark Return"]
    if outperform >= 0:
        text = f"The optimized portfolio outperformed the equal-weight benchmark by <b>{pct(outperform)}</b> during the test window."
    else:
        text = f"The optimized portfolio underperformed the equal-weight benchmark by <b>{pct(abs(outperform))}</b> during the test window."

    answer_box(
        "Backtest result",
        f"The optimized portfolio returned <b>{pct(backtest_result['Portfolio Return'])}</b>. "
        f"The equal-weight benchmark returned <b>{pct(backtest_result['Benchmark Return'])}</b>. {text}"
    )

st.header("Portfolio Metrics")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Expected Return", pct(selected_portfolio["Return"]))
c2.metric("Volatility", pct(selected_portfolio["Volatility"]))
c3.metric("Sharpe Ratio", f"{selected_portfolio['Sharpe Ratio']:.3f}")
c4.metric("Stocks Analyzed", len(valid_tickers))

st.header("Investment Allocation")

allocation_df = pd.DataFrame({
    "Stock": [display_names.get(t, t) for t in valid_tickers],
    "Ticker": valid_tickers,
    "Weight": [weights[t] for t in valid_tickers],
    "Amount": [weights[t] * investment_amount for t in valid_tickers],
    "Sector": [STOCK_SECTORS.get(display_names.get(t, t), "Custom") for t in valid_tickers]
})

allocation_df = allocation_df[allocation_df["Weight"] > 0.001].sort_values("Weight", ascending=False)

allocation_display = allocation_df.copy()
allocation_display["Weight"] = allocation_display["Weight"].map(lambda x: f"{x:.2%}")
allocation_display["Amount"] = allocation_display["Amount"].map(money)

left, right = st.columns([1, 1])

with left:
    st.dataframe(allocation_display, use_container_width=True, hide_index=True)

with right:
    fig_alloc = px.pie(
        allocation_df,
        names="Stock",
        values="Weight",
        title="Portfolio Allocation"
    )
    st.plotly_chart(fig_alloc, use_container_width=True)

st.header("Stock-Level Analysis")

metrics_named = metrics.copy()
metrics_named.insert(0, "Stock", [display_names.get(t, t) for t in metrics_named.index])
metrics_named.insert(1, "Ticker", metrics_named.index)

metrics_display = metrics_named.copy()
for col in ["Total Return", "Annual Return", "Annual Volatility", "Max Drawdown"]:
    metrics_display[col] = metrics_display[col].map(pct)
metrics_display["Sharpe Ratio"] = metrics_display["Sharpe Ratio"].map(lambda x: f"{x:.3f}")

st.dataframe(metrics_display, use_container_width=True, hide_index=True)

st.header("Charts")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Price Performance",
    "Efficient Frontier",
    "Correlation",
    "Backtest",
    "Prediction"
])

with tab1:
    norm = normalize_prices(prices)

    fig = go.Figure()
    for ticker in valid_tickers:
        fig.add_trace(
            go.Scatter(
                x=norm.index,
                y=norm[ticker],
                mode="lines",
                name=display_names.get(ticker, ticker)
            )
        )

    if include_index:
        index_ticker = INDIAN_INDICES[selected_index_name]
        index_data, _ = load_stock_data([index_ticker], start_date, end_date)
        if not index_data.empty:
            index_norm = normalize_prices(index_data)
            index_col = index_norm.columns[0]
            fig.add_trace(
                go.Scatter(
                    x=index_norm.index,
                    y=index_norm[index_col],
                    mode="lines",
                    name=selected_index_name,
                    line=dict(dash="dash")
                )
            )

    fig.update_layout(
        title="Normalized Price Performance",
        xaxis_title="Date",
        yaxis_title="Value, base 100",
        height=550
    )

    st.plotly_chart(fig, use_container_width=True)

with tab2:
    frontier = go.Figure()

    frontier.add_trace(
        go.Scatter(
            x=sim_df["Volatility"],
            y=sim_df["Return"],
            mode="markers",
            marker=dict(
                size=6,
                color=sim_df["Sharpe Ratio"],
                colorscale="Viridis",
                showscale=True,
                colorbar=dict(title="Sharpe")
            ),
            name="Simulated portfolios"
        )
    )

    frontier.add_trace(
        go.Scatter(
            x=[selected_portfolio["Volatility"]],
            y=[selected_portfolio["Return"]],
            mode="markers",
            marker=dict(size=18, symbol="star", color="red"),
            name="Selected portfolio"
        )
    )

    frontier.update_layout(
        title="Efficient Frontier",
        xaxis_title="Volatility",
        yaxis_title="Expected Return",
        height=550
    )

    st.plotly_chart(frontier, use_container_width=True)

with tab3:
    corr = daily_returns.corr()
    corr_display_names = [display_names.get(t, t) for t in corr.columns]

    heatmap = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr_display_names,
            y=corr_display_names,
            colorscale="RdBu",
            zmin=-1,
            zmax=1
        )
    )

    heatmap.update_layout(
        title="Stock Return Correlation",
        height=550
    )

    st.plotly_chart(heatmap, use_container_width=True)

with tab4:
    if backtest_result:
        backtest_fig = go.Figure()

        backtest_fig.add_trace(
            go.Scatter(
                x=portfolio_curve.index,
                y=portfolio_curve,
                mode="lines",
                name="Optimized portfolio"
            )
        )

        backtest_fig.add_trace(
            go.Scatter(
                x=benchmark_curve.index,
                y=benchmark_curve,
                mode="lines",
                name="Equal-weight stock benchmark"
            )
        )

        backtest_fig.update_layout(
            title="Backtest Performance",
            xaxis_title="Date",
            yaxis_title="Value, base 100",
            height=550
        )

        st.plotly_chart(backtest_fig, use_container_width=True)
    else:
        st.warning("Backtest requires more data.")

with tab5:
    display_options = {display_names.get(t, t): t for t in valid_tickers}
    selected_display_name = st.selectbox("Select stock for prediction", list(display_options.keys()))
    selected_ticker = display_options[selected_display_name]

    pred_df, rmse, pred_summary = random_forest_prediction(prices, selected_ticker)

    if pred_df is None:
        st.warning("Prediction requires more historical data.")
    else:
        move_text = "higher" if pred_summary["Expected Move"] > 0 else "lower"

        answer_box(
            f"{selected_display_name} prediction reading",
            f"The latest price is <b>₹{pred_summary['Latest Price']:.2f}</b>. "
            f"The model's next estimated price is <b>₹{pred_summary['Predicted Next Price']:.2f}</b>, "
            f"which is <b>{pct(abs(pred_summary['Expected Move']))}</b> {move_text}. "
            f"Model RMSE is <b>{pred_summary['RMSE']:.2f}</b>."
        )

        pred_fig = go.Figure()
        pred_fig.add_trace(
            go.Scatter(
                x=pred_df.index,
                y=pred_df["Actual"],
                mode="lines",
                name="Actual"
            )
        )
        pred_fig.add_trace(
            go.Scatter(
                x=pred_df.index,
                y=pred_df["Predicted"],
                mode="lines",
                name="Predicted"
            )
        )

        pred_fig.update_layout(
            title=f"{selected_display_name} Actual vs Predicted Price",
            xaxis_title="Date",
            yaxis_title="Price",
            height=550
        )

        st.plotly_chart(pred_fig, use_container_width=True)

st.divider()
st.markdown(
    "<div class='small-note'>Data source: Yahoo Finance through yfinance. NSE tickers use the .NS suffix. "
    "V3 uses stable presets and skips unavailable tickers. Educational use only.</div>",
    unsafe_allow_html=True
)
