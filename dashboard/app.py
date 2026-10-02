"""
Quant System Dashboard
Run with: streamlit run app.py
"""

import ast
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Quant System Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------------
ACCENT = "#3DD9B5"      # teal-green (profit)
LOSS = "#FF5C5C"         # red (loss / drawdown)
BG = "#0E1117"
CARD_BG = "#161A23"
GRID = "#262B36"
TEXT_MUTED = "#8A93A6"

st.markdown(
    f"""
    <style>
        .stApp {{ background-color: {BG}; }}
        div[data-testid="stMetric"] {{
            background-color: {CARD_BG};
            border: 1px solid {GRID};
            border-radius: 10px;
            padding: 14px 16px 10px 16px;
        }}
        div[data-testid="stMetricLabel"] {{
            color: {TEXT_MUTED};
            font-size: 0.8rem;
        }}
        section[data-testid="stSidebar"] {{
            background-color: {CARD_BG};
            border-right: 1px solid {GRID};
        }}
        h1, h2, h3 {{
            letter-spacing: -0.02em;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------------
DATA_PATH = "equity_curve.csv"


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    def parse_time(val):
        # time column stored as a stringified python tuple e.g. "('2025.10.29 03:40',)"
        try:
            t = ast.literal_eval(val)
            val = t[0] if isinstance(t, tuple) else val
        except (ValueError, SyntaxError):
            pass
        return pd.to_datetime(val, format="%Y.%m.%d %H:%M", errors="coerce")

    df["time"] = df["time"].apply(parse_time)
    df = df.dropna(subset=["time"]).sort_values("time").reset_index(drop=True)

    # step-over-step P&L, treated as one "trade" event per row (excluding the first row)
    df["pnl"] = df["equity"].diff()
    df["cum_return_pct"] = (df["equity"] / df["equity"].iloc[0] - 1.0) * 100
    df["drawdown_pct"] = df["drawdown"] * 100

    return df


try:
    trades = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(f"Could not find `{DATA_PATH}`. Place it next to app.py.")
    st.stop()

if trades.empty:
    st.warning("No valid rows found after parsing timestamps.")
    st.stop()

# ----------------------------------------------------------------------------
# Sidebar — filters
# ----------------------------------------------------------------------------
st.sidebar.title("📈 Quant Dashboard")
st.sidebar.caption("Filter the trade / equity history")

min_date = trades["time"].min().date()
max_date = trades["time"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

mask = (trades["time"].dt.date >= start_date) & (trades["time"].dt.date <= end_date)
df = trades.loc[mask].reset_index(drop=True)

st.sidebar.metric("Rows in view", len(df))
st.sidebar.markdown("---")
st.sidebar.caption(
    "Data source: `equity_curve.csv` — equity, running peak, and drawdown "
    "recorded at each account update."
)

if df.empty:
    st.warning("No data in the selected date range.")
    st.stop()

# ----------------------------------------------------------------------------
# Stats calculations
# ----------------------------------------------------------------------------
pnl_steps = df["pnl"].dropna()
wins = pnl_steps[pnl_steps > 0]
losses = pnl_steps[pnl_steps < 0]

starting_equity = df["equity"].iloc[0]
ending_equity = df["equity"].iloc[-1]
net_pnl = ending_equity - starting_equity
total_return_pct = (ending_equity / starting_equity - 1.0) * 100

win_rate = (len(wins) / len(pnl_steps) * 100) if len(pnl_steps) else 0
avg_win = wins.mean() if len(wins) else 0
avg_loss = losses.mean() if len(losses) else 0
profit_factor = (wins.sum() / abs(losses.sum())) if losses.sum() != 0 else np.nan
max_dd_pct = df["drawdown_pct"].min()

# Sharpe-like ratio on step returns (not annualized — irregular timestamps)
step_returns = df["equity"].pct_change().dropna()
sharpe_raw = (step_returns.mean() / step_returns.std()) if step_returns.std() else np.nan

# Current drawdown status
current_dd_pct = df["drawdown_pct"].iloc[-1]

# ----------------------------------------------------------------------------
# Extended metrics — daily-resampled series for anything time-annualized
# ----------------------------------------------------------------------------
ts = df.set_index("time")
daily_equity = ts["equity"].resample("D").last().ffill()
daily_returns = daily_equity.pct_change().dropna()

n_days = max((df["time"].max() - df["time"].min()).days, 1)
cagr_pct = ((ending_equity / starting_equity) ** (365 / n_days) - 1) * 100 if starting_equity > 0 else np.nan

ann_vol_pct = daily_returns.std() * np.sqrt(252) * 100 if len(daily_returns) > 1 else np.nan
sharpe_ann = (
    (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
    if daily_returns.std() else np.nan
)
downside = daily_returns[daily_returns < 0]
sortino_ann = (
    (daily_returns.mean() / downside.std()) * np.sqrt(252)
    if len(downside) > 1 and downside.std() else np.nan
)
calmar = (cagr_pct / abs(max_dd_pct)) if max_dd_pct else np.nan

# Ulcer Index — penalizes both depth and duration of drawdowns
ulcer_index = np.sqrt((df["drawdown_pct"] ** 2).mean())

# Time underwater %
is_underwater = df["equity"] < df["peak"]
time_underwater_pct = is_underwater.mean() * 100

# Max drawdown duration (peak -> recovery, in days)
underwater_id = (is_underwater != is_underwater.shift()).cumsum()
max_dd_duration_days = 0
for _, grp in df.groupby(underwater_id):
    if grp["equity"].iloc[0] < grp["peak"].iloc[0] or is_underwater.loc[grp.index].iloc[0]:
        span = (grp["time"].iloc[-1] - grp["time"].iloc[0]).days
        max_dd_duration_days = max(max_dd_duration_days, span)

# Recovery factor — net profit vs. worst peak-to-trough dollar drawdown
dd_currency = (df["peak"] - df["equity"])
max_dd_currency = dd_currency.max()
recovery_factor = (net_pnl / max_dd_currency) if max_dd_currency else np.nan

# Expectancy per update event
loss_rate = 1 - (win_rate / 100)
expectancy = ((win_rate / 100) * avg_win) + (loss_rate * avg_loss)

# Longest win/loss streaks
sign = np.sign(pnl_steps.values)
if len(sign):
    streak_id = (sign != np.roll(sign, 1)).cumsum()
    streak_id[0] = 0
    streak_df = pd.DataFrame({"sign": sign, "streak_id": streak_id})
    streak_lengths = streak_df.groupby("streak_id").agg(sign=("sign", "first"), length=("sign", "size"))
    longest_win_streak = streak_lengths.loc[streak_lengths["sign"] > 0, "length"].max() if (streak_lengths["sign"] > 0).any() else 0
    longest_loss_streak = streak_lengths.loc[streak_lengths["sign"] < 0, "length"].max() if (streak_lengths["sign"] < 0).any() else 0
else:
    longest_win_streak = longest_loss_streak = 0

# Skew / kurtosis of step returns
skew_val = step_returns.skew() if len(step_returns) > 2 else np.nan
kurt_val = step_returns.kurt() if len(step_returns) > 2 else np.nan

# Monthly returns for heatmap + best/worst month
monthly_equity = ts["equity"].resample("ME").last()
monthly_returns_pct = monthly_equity.pct_change().dropna() * 100
best_month = monthly_returns_pct.max() if len(monthly_returns_pct) else np.nan
worst_month = monthly_returns_pct.min() if len(monthly_returns_pct) else np.nan

# Rolling Sharpe (30-day window, annualized) on the daily series
rolling_window = 30
rolling_sharpe = (
    daily_returns.rolling(rolling_window).mean() / daily_returns.rolling(rolling_window).std()
) * np.sqrt(252)

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.title("Quant System Dashboard")
st.caption(
    f"{df['time'].min():%d %b %Y, %H:%M} → {df['time'].max():%d %b %Y, %H:%M} · "
    f"{len(df):,} recorded updates"
)

# ----------------------------------------------------------------------------
# KPI row
# ----------------------------------------------------------------------------
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Net P&L", f"{net_pnl:,.2f}")
c2.metric("Total Return", f"{total_return_pct:,.2f}%")
c3.metric("Win Rate", f"{win_rate:,.1f}%")
c4.metric("Profit Factor", f"{profit_factor:,.2f}" if not np.isnan(profit_factor) else "—")
c5.metric("Max Drawdown", f"{max_dd_pct:,.2f}%")
c6.metric("Current Drawdown", f"{current_dd_pct:,.2f}%")

st.markdown("")

# ----------------------------------------------------------------------------
# Equity curve
# ----------------------------------------------------------------------------
st.subheader("Equity Curve")

fig_eq = go.Figure()
fig_eq.add_trace(
    go.Scatter(
        x=df["time"], y=df["equity"],
        mode="lines",
        line=dict(color=ACCENT, width=2),
        fill="tozeroy",
        fillcolor="rgba(61, 217, 181, 0.08)",
        name="Equity",
        hovertemplate="%{x|%d %b %Y %H:%M}<br>Equity: %{y:,.2f}<extra></extra>",
    )
)
fig_eq.add_trace(
    go.Scatter(
        x=df["time"], y=df["peak"],
        mode="lines",
        line=dict(color=TEXT_MUTED, width=1, dash="dot"),
        name="Running Peak",
        hovertemplate="%{x|%d %b %Y %H:%M}<br>Peak: %{y:,.2f}<extra></extra>",
    )
)
fig_eq.update_layout(
    height=440,
    margin=dict(l=10, r=10, t=10, b=10),
    plot_bgcolor=BG,
    paper_bgcolor=BG,
    font=dict(color="#E6E9EF"),
    xaxis=dict(gridcolor=GRID, showgrid=False),
    yaxis=dict(gridcolor=GRID, title="Equity"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    hovermode="x unified",
)
st.plotly_chart(fig_eq, use_container_width=True)

# ----------------------------------------------------------------------------
# Drawdown + P&L distribution
# ----------------------------------------------------------------------------
col_dd, col_dist = st.columns([1.4, 1])

with col_dd:
    st.subheader("Drawdown")
    fig_dd = go.Figure()
    fig_dd.add_trace(
        go.Scatter(
            x=df["time"], y=df["drawdown_pct"],
            mode="lines",
            line=dict(color=LOSS, width=1.5),
            fill="tozeroy",
            fillcolor="rgba(255, 92, 92, 0.15)",
            name="Drawdown %",
            hovertemplate="%{x|%d %b %Y %H:%M}<br>DD: %{y:.2f}%<extra></extra>",
        )
    )
    fig_dd.update_layout(
        height=340,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor=BG,
        paper_bgcolor=BG,
        font=dict(color="#E6E9EF"),
        xaxis=dict(gridcolor=GRID, showgrid=False),
        yaxis=dict(gridcolor=GRID, title="Drawdown (%)"),
        hovermode="x unified",
    )
    st.plotly_chart(fig_dd, use_container_width=True)

with col_dist:
    st.subheader("P&L per Update")
    colors = np.where(pnl_steps.reindex(df.index).fillna(0) >= 0, ACCENT, LOSS)
    fig_hist = go.Figure()
    fig_hist.add_trace(
        go.Histogram(
            x=pnl_steps,
            marker_color=ACCENT,
            opacity=0.85,
            nbinsx=40,
            name="P&L",
        )
    )
    fig_hist.update_layout(
        height=340,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor=BG,
        paper_bgcolor=BG,
        font=dict(color="#E6E9EF"),
        xaxis=dict(gridcolor=GRID, title="P&L"),
        yaxis=dict(gridcolor=GRID, title="Count"),
        bargap=0.05,
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# ----------------------------------------------------------------------------
# Secondary stats row
# ----------------------------------------------------------------------------
st.subheader("Trade Statistics")
s1, s2, s3, s4, s5 = st.columns(5)
s1.metric("Avg Win", f"{avg_win:,.2f}")
s2.metric("Avg Loss", f"{avg_loss:,.2f}")
s3.metric("Best Update", f"{pnl_steps.max():,.2f}" if len(pnl_steps) else "—")
s4.metric("Worst Update", f"{pnl_steps.min():,.2f}" if len(pnl_steps) else "—")
s5.metric("Return/Risk (raw)", f"{sharpe_raw:,.3f}" if not np.isnan(sharpe_raw) else "—")

st.caption(
    "⚠️ Return/Risk ratio is computed on raw, non-annualized step returns because "
    "update timestamps are irregular — treat as a relative, not absolute, measure."
)

# ----------------------------------------------------------------------------
# Risk-adjusted return metrics (annualized via daily-resampled equity)
# ----------------------------------------------------------------------------
def fmt_pct_capped(v, cap=100_000):
    if np.isnan(v):
        return "—"
    if abs(v) >= cap:
        return f"{v:,.3g}%"  # scientific-ish for extreme extrapolations
    return f"{v:,.2f}%"


def fmt_ratio_capped(v, cap=1_000):
    if np.isnan(v):
        return "—"
    if abs(v) >= cap:
        return f"{v:,.3g}"
    return f"{v:,.2f}"


st.subheader("Risk-Adjusted Returns")
r1, r2, r3, r4, r5 = st.columns(5)
r1.metric("CAGR", fmt_pct_capped(cagr_pct))
r2.metric("Sharpe (ann.)", f"{sharpe_ann:,.2f}" if not np.isnan(sharpe_ann) else "—")
r3.metric("Sortino (ann.)", f"{sortino_ann:,.2f}" if not np.isnan(sortino_ann) else "—")
r4.metric("Calmar", fmt_ratio_capped(calmar))
r5.metric("Ann. Volatility", f"{ann_vol_pct:,.2f}%" if not np.isnan(ann_vol_pct) else "—")

st.caption(
    "Annualized on a daily-resampled (forward-filled) equity series — assumes 252 trading days/yr. "
    f"Based on only {n_days} days of history — with only {(df['time'].max()-df['time'].min()).days} days of data, "
    "CAGR/Calmar extrapolated to a full year can look extreme for a fast-growing small account; "
    "treat **Total Return** above as the more reliable number for a track record this short."
)
if np.isnan(sortino_ann):
    st.caption(
        "Sortino shows '—' because there were no losing **daily-close** periods in this window "
        "(all drawdowns recovered intraday before end of day) — downside deviation is undefined, not zero risk."
    )

# ----------------------------------------------------------------------------
# Drawdown quality + trade behavior metrics
# ----------------------------------------------------------------------------
st.subheader("Drawdown Quality & Trade Behavior")
d1, d2, d3, d4, d5, d6 = st.columns(6)
d1.metric("Max DD Duration", f"{max_dd_duration_days} d")
d2.metric("Time Underwater", f"{time_underwater_pct:,.1f}%")
d3.metric("Ulcer Index", f"{ulcer_index:,.2f}")
d4.metric("Recovery Factor", f"{recovery_factor:,.2f}" if not np.isnan(recovery_factor) else "—")
d5.metric("Longest Win Streak", f"{int(longest_win_streak)}")
d6.metric("Longest Loss Streak", f"{int(longest_loss_streak)}")

e1, e2, e3, e4 = st.columns(4)
e1.metric("Expectancy / Update", f"{expectancy:,.2f}")
e2.metric("Best Month", f"{best_month:,.2f}%" if not np.isnan(best_month) else "—")
e3.metric("Worst Month", f"{worst_month:,.2f}%" if not np.isnan(worst_month) else "—")
e4.metric(
    "Skew / Kurtosis",
    f"{skew_val:,.2f} / {kurt_val:,.2f}" if not np.isnan(skew_val) else "—",
)

# ----------------------------------------------------------------------------
# Monthly returns heatmap
# ----------------------------------------------------------------------------
if len(monthly_returns_pct) > 0:
    st.subheader("Monthly Returns Heatmap")
    mr = monthly_returns_pct.copy()
    mr.index = mr.index.to_period("M")
    heat_df = mr.reset_index()
    heat_df.columns = ["month", "return_pct"]
    heat_df["year"] = heat_df["month"].dt.year
    heat_df["month_name"] = heat_df["month"].dt.strftime("%b")
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    pivot = heat_df.pivot(index="year", columns="month_name", values="return_pct").reindex(columns=month_order)

    fig_heat = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index.astype(str),
            colorscale=[[0, LOSS], [0.5, "#2A2E38"], [1, ACCENT]],
            zmid=0,
            text=[[f"{v:.1f}%" if pd.notna(v) else "" for v in row] for row in pivot.values],
            texttemplate="%{text}",
            textfont=dict(size=11),
            hovertemplate="%{y} %{x}<br>Return: %{z:.2f}%<extra></extra>",
            colorbar=dict(title="Return %"),
        )
    )
    fig_heat.update_layout(
        height=220 + 40 * max(len(pivot.index) - 1, 0),
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor=BG,
        paper_bgcolor=BG,
        font=dict(color="#E6E9EF"),
        xaxis=dict(side="top"),
    )
    st.plotly_chart(fig_heat, use_container_width=True)
    st.caption("Monthly return = % change of month-end equity vs. prior month-end.")

# ----------------------------------------------------------------------------
# Rolling Sharpe
# ----------------------------------------------------------------------------
if rolling_sharpe.notna().sum() > 1:
    st.subheader(f"Rolling Sharpe ({rolling_window}-Day Window, Annualized)")
    fig_roll = go.Figure()
    fig_roll.add_trace(
        go.Scatter(
            x=rolling_sharpe.index, y=rolling_sharpe.values,
            mode="lines",
            line=dict(color=ACCENT, width=1.8),
            name="Rolling Sharpe",
            hovertemplate="%{x|%d %b %Y}<br>Sharpe: %{y:.2f}<extra></extra>",
        )
    )
    fig_roll.add_hline(y=0, line_dash="dot", line_color=TEXT_MUTED)
    fig_roll.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor=BG,
        paper_bgcolor=BG,
        font=dict(color="#E6E9EF"),
        xaxis=dict(gridcolor=GRID, showgrid=False),
        yaxis=dict(gridcolor=GRID, title="Sharpe"),
        hovermode="x unified",
    )
    st.plotly_chart(fig_roll, use_container_width=True)
    st.caption("Shows whether performance is improving or degrading over time, vs. one static Sharpe for the whole history.")

# ----------------------------------------------------------------------------
# Raw data
# ----------------------------------------------------------------------------
with st.expander("View raw data"):
    st.dataframe(
        df[["time", "equity", "peak", "drawdown_pct", "pnl"]].rename(
            columns={"drawdown_pct": "drawdown_%"}
        ),
        use_container_width=True,
        height=350,
    )
