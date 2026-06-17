"""
aqi_model.py
Full AQI prediction pipeline — converted from Google Colab to VS Code.

HOW TO RUN:
  1. Put your CSV in:  dashboard/data/dehradun_master_dataset_cleaned_NEW.csv
  2. Activate venv:    venv\\Scripts\\activate  (Windows)  or  source venv/bin/activate
  3. Install deps:     pip install pandas numpy matplotlib seaborn statsmodels scikit-learn tensorflow plotly
  4. Run:              python model/aqi_model.py
"""

import os
import sys
import json
import warnings
import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")

# ── Make sure utils/ is importable ────────────────────────────────────────────
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# ==========================================
# PATHS
# ==========================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_FILE = os.path.join(
    BASE_DIR,
    "data",
    "dehradun_master_dataset_cleaned.xlsx"
)

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
MODEL_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
FEATURES = [
    "pm25",
    "pm10",
    "co",
    "no2",
    "so2",
    "o3",
    "traffic_flow_speed",
    "traffic_congestion",
    "wind_speed",
    "humidity",
    "aerosol"
]

TARGET = "pm25"


def get_pm25_univariate(df):
    ts = df.groupby("datetime")["pm25"].mean()
    ts.index = pd.to_datetime(ts.index)
    ts = ts.sort_index()
    ts = ts.asfreq("h", method="ffill")
    return ts


def get_hourly_multivariate(df):
    ts = df.groupby("datetime")[FEATURES].mean()
    ts.index = pd.to_datetime(ts.index)
    ts = ts.sort_index()
    ts = ts.asfreq("h", method="ffill")
    return ts


def aqi_category(pm25):
    if pm25 <= 12:
        return "Good"
    elif pm25 <= 35.4:
        return "Moderate"
    elif pm25 <= 55.4:
        return "Unhealthy for Sensitive"
    elif pm25 <= 150.4:
        return "Unhealthy"
    elif pm25 <= 250.4:
        return "Very Unhealthy"
    return "Hazardous"


def aqi_color(category):
    colors = {
        "Good": "green",
        "Moderate": "yellow",
        "Unhealthy for Sensitive": "orange",
        "Unhealthy": "red",
        "Very Unhealthy": "purple",
        "Hazardous": "maroon",
    }

    return colors.get(category, "gray")

# ==========================================
# LOAD DATA
# ==========================================

df = pd.read_excel(DATA_FILE)

df["datetime"] = pd.to_datetime(df["datetime"])

df = df.sort_values(
    ["zone", "datetime"]
).reset_index(drop=True)



# ══════════════════════════════════════════════════════════════════════════════
# 2. BASIC EDA
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== NULL VALUES ===")
print(df.isnull().sum())

print("\n=== BASIC STATS ===")
print(df[["pm25","pm10","co","no2","so2","o3",
          "us_aqi","humidity","wind_speed","traffic_flow_speed"]].describe().round(2))

print("\n=== ZONE-WISE SAMPLE COUNT ===")
print(df["zone"].value_counts())

# ══════════════════════════════════════════════════════════════════════════════
# 3. CORRELATION HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
plt.figure(figsize=(12, 8))
corr = df[FEATURES + ["us_aqi", "traffic_congestion"]].corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
            linewidths=0.5, annot_kws={"size": 8})
plt.title("Correlation Heatmap — Dehradun AQI Dataset", fontsize=14, fontweight="bold")
plt.tight_layout()
heatmap_path = os.path.join(OUTPUT_DIR, "correlation_heatmap.png")
plt.savefig(heatmap_path, dpi=150)
plt.show()
print(f"✅ Heatmap saved → {heatmap_path}")

# ══════════════════════════════════════════════════════════════════════════════
# 4. INTERACTIVE HOURLY AQI TREND  (saves HTML — open in browser)
# ══════════════════════════════════════════════════════════════════════════════
from plotly.subplots import make_subplots
import plotly.graph_objects as go

hourly_zone = df.groupby(["hour", "zone"])["us_aqi"].mean().reset_index()
hourly_avg  = df.groupby("hour")["us_aqi"].mean().reset_index()
hourly_avg["us_aqi"] = hourly_avg["us_aqi"].round(1)

zones_list = sorted(df["zone"].unique())
colors = ["#FF6B6B","#4ECDC4","#FFD93D","#6BCB77","#FF922B",
          "#CC5DE8","#74C0FC","#F783AC","#A9E34B","#63E6BE"]
dashes = ["solid","dash","solid","dot","dashdot",
          "solid","dash","solid","dot","dashdot"]

fig = make_subplots(
    rows=2, cols=1,
    subplot_titles=(
        "Graph 1: Hourly AQI Trend by Zone (All 10 Locations)",
        "Graph 2: Overall Hourly Average AQI — Dehradun (2024–2026)",
    ),
    vertical_spacing=0.12,
)

for i, zone in enumerate(zones_list):
    zd = hourly_zone[hourly_zone["zone"] == zone].sort_values("hour")
    fig.add_trace(go.Scatter(
        x=zd["hour"], y=zd["us_aqi"].round(1),
        mode="lines", name=zone,
        line=dict(color=colors[i % len(colors)], width=2.5,
                  dash=dashes[i % len(dashes)], shape="spline"),
        hovertemplate=f"<b>{zone}</b>: %{{y:.1f}}<extra></extra>",
    ), row=1, col=1)

fig.add_trace(go.Scatter(
    x=hourly_avg["hour"], y=hourly_avg["us_aqi"],
    mode="lines+markers", name="Dehradun Overall",
    line=dict(color="#4ECDC4", width=3, shape="spline"),
    marker=dict(size=5, color="#4ECDC4"),
    fill="tozeroy", fillcolor="rgba(78,205,196,0.08)",
    hovertemplate="<b>%{x}:00</b><br>AQI: %{y}<extra></extra>",
), row=2, col=1)

peak_row = hourly_avg.loc[hourly_avg["us_aqi"].idxmax()]
low_row  = hourly_avg.loc[hourly_avg["us_aqi"].idxmin()]
fig.add_annotation(x=peak_row["hour"], y=peak_row["us_aqi"],
    text="Peak AQI", showarrow=True, arrowhead=2,
    font=dict(color="#FF6B6B", size=11), arrowcolor="#FF6B6B", ax=-80, ay=-40, row=2, col=1)
fig.add_annotation(x=low_row["hour"], y=low_row["us_aqi"],
    text="Morning low", showarrow=True, arrowhead=2,
    font=dict(color="#6BCB77", size=11), arrowcolor="#6BCB77", ax=60, ay=-40, row=2, col=1)

for axis in ["xaxis", "xaxis2"]:
    fig.update_layout(**{axis: dict(
        tickvals=list(range(0, 24)),
        ticktext=[f"{h}:00" for h in range(0, 24)],
        gridcolor="rgba(255,255,255,0.08)", color="#aaa", tickfont=dict(size=9),
    )})

fig.update_layout(
    plot_bgcolor="#1c1c2e", paper_bgcolor="#1c1c2e",
    font=dict(color="#ccc"), hovermode="x unified",
    hoverlabel=dict(bgcolor="black", font_color="white", font_size=12, bordercolor="#444"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
    height=900, margin=dict(l=55, r=30, t=60, b=60),
)
fig.update_yaxes(title_text="US AQI", gridcolor="rgba(255,255,255,0.08)", color="#aaa")

hourly_html = os.path.join(OUTPUT_DIR, "hourly_aqi_interactive.html")
fig.write_html(hourly_html)
print(f"✅ Interactive AQI chart saved → {hourly_html}")

# ══════════════════════════════════════════════════════════════════════════════
# 5. ADF STATIONARITY TEST
# ══════════════════════════════════════════════════════════════════════════════
from statsmodels.tsa.stattools import adfuller

ts_uni = get_pm25_univariate(df)
result = adfuller(ts_uni.dropna())

print("\n=== ADF TEST RESULTS ===")
print(f"ADF Statistic : {result[0]:.4f}")
print(f"p-value       : {result[1]:.4e}")
print(f"Lags Used     : {result[2]}")
print("\nCritical Values:")
for k, v in result[4].items():
    print(f"   {k}: {v:.4f}")

arima_d = 0 if result[1] < 0.05 else 1
print(f"\n{'✅ STATIONARY' if arima_d == 0 else '⚠️  NON-STATIONARY'} → using d={arima_d} for ARIMA")

# ══════════════════════════════════════════════════════════════════════════════
# 6. PLOT RAW TIME SERIES
# ══════════════════════════════════════════════════════════════════════════════
plt.figure(figsize=(14, 4))
plt.plot(ts_uni, color="steelblue", linewidth=0.6)
plt.title("Hourly PM2.5 — Dehradun Aggregate (2024–2026)")
plt.xlabel("Date")
plt.ylabel("PM2.5")
plt.tight_layout()
ts_path = os.path.join(OUTPUT_DIR, "pm25_timeseries.png")
plt.savefig(ts_path, dpi=150)
plt.show()
print(f"✅ Time series plot saved → {ts_path}")

# ══════════════════════════════════════════════════════════════════════════════
# 7. ARIMA BASELINE
# ══════════════════════════════════════════════════════════════════════════════
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error

split    = int(len(ts_uni) * 0.8)
ts_train = ts_uni[:split]
ts_test  = ts_uni[split:]
print(f"\nTrain: {len(ts_train)} hrs  |  Test: {len(ts_test)} hrs")

arima_model = ARIMA(ts_train, order=(1, arima_d, 1))
arima_fit   = arima_model.fit()
arima_pred  = arima_fit.forecast(steps=len(ts_test))
arima_pred.index = ts_test.index

arima_mae  = mean_absolute_error(ts_test, arima_pred)
arima_rmse = np.sqrt(mean_squared_error(ts_test, arima_pred))
arima_mape = np.mean(np.abs((ts_test - arima_pred) / ts_test)) * 100

print(f"\n=== ARIMA(1,{arima_d},1) BASELINE ===")
print(f"MAE  : {arima_mae:.4f}")
print(f"RMSE : {arima_rmse:.4f}")
print(f"MAPE : {arima_mape:.2f}%")

plt.figure(figsize=(14, 4))
plt.plot(ts_test.index[-500:], ts_test.values[-500:], label="Actual", color="steelblue")
plt.plot(ts_test.index[-500:], arima_pred.values[-500:], label="ARIMA Forecast",
         color="orange", linestyle="--")
plt.title(f"ARIMA(1,{arima_d},1) Forecast vs Actual PM2.5 (last 500 hrs)")
plt.legend()
plt.tight_layout()
arima_path = os.path.join(OUTPUT_DIR, "arima_forecast.png")
plt.savefig(arima_path, dpi=150)
plt.show()
print(f"✅ ARIMA forecast plot saved → {arima_path}")

# ══════════════════════════════════════════════════════════════════════════════
# 8. PREPARE DATA FOR MULTIVARIATE LSTM
# ══════════════════════════════════════════════════════════════════════════════
from sklearn.preprocessing import MinMaxScaler

ts_multi = get_hourly_multivariate(df)
print(f"\nMultivariate TS shape: {ts_multi.shape}")

scaler        = MinMaxScaler()
scaled        = scaler.fit_transform(ts_multi)

target_scaler = MinMaxScaler()
target_scaler.fit_transform(ts_multi[[TARGET]])

SEQ_LEN = 24

def create_sequences(data, seq_len):
    X, y = [], []
    for i in range(len(data) - seq_len):
        X.append(data[i : i + seq_len])
        y.append(data[i + seq_len][0])
    return np.array(X), np.array(y)

X, y = create_sequences(scaled, SEQ_LEN)
split_idx  = int(len(X) * 0.8)
X_train, X_test = X[:split_idx], X[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]

print(f"X_train: {X_train.shape}  |  X_test: {X_test.shape}")

# ══════════════════════════════════════════════════════════════════════════════
# 9. BUILD LSTM MODEL
# ══════════════════════════════════════════════════════════════════════════════
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

print(f"\nTensorFlow: {tf.__version__}")
print(f"GPU available: {tf.config.list_physical_devices('GPU')}")

tf.random.set_seed(42)

lstm_model = Sequential([
    LSTM(128, return_sequences=True, input_shape=(SEQ_LEN, len(FEATURES))),
    BatchNormalization(),
    Dropout(0.2),
    LSTM(64, return_sequences=False),
    BatchNormalization(),
    Dropout(0.2),
    Dense(32, activation="relu"),
    Dense(1),
])

lstm_model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss="huber",
    metrics=["mae"],
)
lstm_model.summary()

# ══════════════════════════════════════════════════════════════════════════════
# 10. TRAIN LSTM
# ══════════════════════════════════════════════════════════════════════════════
model_save_path = os.path.join(MODEL_DIR, "best_lstm_model.keras")

callbacks = [
    EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True, verbose=1),
    ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=5, verbose=1),
    ModelCheckpoint(model_save_path, save_best_only=True, monitor="val_loss", verbose=1),
]

history = lstm_model.fit(
    X_train, y_train,
    epochs=100,
    batch_size=64,
    validation_split=0.1,
    callbacks=callbacks,
    verbose=1,
)
print("✅ Training complete!")

# ══════════════════════════════════════════════════════════════════════════════
# 11. EVALUATE LSTM
# ══════════════════════════════════════════════════════════════════════════════
y_pred_scaled = lstm_model.predict(X_test)
y_pred   = target_scaler.inverse_transform(y_pred_scaled).flatten()
y_actual = target_scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()

lstm_mae  = mean_absolute_error(y_actual, y_pred)
lstm_rmse = np.sqrt(mean_squared_error(y_actual, y_pred))
lstm_mape = np.mean(np.abs((y_actual - y_pred) / y_actual)) * 100
improvement = ((arima_mae - lstm_mae) / arima_mae) * 100

print("\n=== LSTM RESULTS ===")
print(f"MAE  : {lstm_mae:.4f}")
print(f"RMSE : {lstm_rmse:.4f}")
print(f"MAPE : {lstm_mape:.2f}%")
print(f"\n=== COMPARISON ===")
print(f"{'Model':<12} {'MAE':>10} {'RMSE':>10} {'MAPE':>10}")
print(f"{'ARIMA':<12} {arima_mae:>10.4f} {arima_rmse:>10.4f} {arima_mape:>9.2f}%")
print(f"{'LSTM':<12} {lstm_mae:>10.4f} {lstm_rmse:>10.4f} {lstm_mape:>9.2f}%")
print(f"\nMAE Improvement over ARIMA: {improvement:.2f}%")

# ══════════════════════════════════════════════════════════════════════════════
# 12. SAVE PLOTS
# ══════════════════════════════════════════════════════════════════════════════
plt.figure(figsize=(14, 5))
plt.plot(y_actual[:500], label="Actual PM2.5", color="steelblue")
plt.plot(y_pred[:500], label="LSTM Predicted", color="tomato", linestyle="--")
plt.title("LSTM Forecast vs Actual PM2.5 (first 500 test hours)")
plt.xlabel("Hours")
plt.ylabel("PM2.5 (µg/m³)")
plt.legend()
plt.tight_layout()
lstm_path = os.path.join(OUTPUT_DIR, "lstm_forecast.png")
plt.savefig(lstm_path, dpi=150)
plt.show()

plt.figure(figsize=(10, 4))
plt.plot(history.history["loss"], label="Train Loss")
plt.plot(history.history["val_loss"], label="Val Loss")
plt.title("LSTM Training History")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()
plt.tight_layout()
hist_path = os.path.join(OUTPUT_DIR, "lstm_training_history.png")
plt.savefig(hist_path, dpi=150)
plt.show()

plt.figure(figsize=(8, 8))
plt.scatter(y_actual, y_pred, alpha=0.3, color="steelblue", s=10)
plt.plot([y_actual.min(), y_actual.max()],
         [y_actual.min(), y_actual.max()], "r--", linewidth=2, label="Perfect Prediction")
plt.xlabel("Actual PM2.5 (µg/m³)")
plt.ylabel("Predicted PM2.5 (µg/m³)")
plt.title("Actual vs Predicted PM2.5 — LSTM")
plt.legend()
plt.tight_layout()
scatter_path = os.path.join(OUTPUT_DIR, "scatter_actual_vs_predicted.png")
plt.savefig(scatter_path, dpi=150)
plt.show()
print(f"✅ All plots saved → {OUTPUT_DIR}")

# ══════════════════════════════════════════════════════════════════════════════
# 13. 24-HOUR FUTURE FORECAST
# ══════════════════════════════════════════════════════════════════════════════
last_sequence = scaled[-SEQ_LEN:]
future_input  = last_sequence.copy()
future_preds  = []

for _ in range(24):
    seq  = future_input[-SEQ_LEN:].reshape(1, SEQ_LEN, len(FEATURES))
    pred = lstm_model.predict(seq, verbose=0)[0][0]
    future_preds.append(pred)
    new_row    = future_input[-1].copy()
    new_row[0] = pred
    future_input = np.vstack([future_input, new_row])

future_preds_inv = target_scaler.inverse_transform(
    np.array(future_preds).reshape(-1, 1)
).flatten()

last_time = pd.to_datetime(df["datetime"].max())
print("\n=== 24-HOUR PM2.5 FORECAST — DEHRADUN ===")
print(f"{'Hr':<5} {'Time':<22} {'PM2.5':>8}  AQI Category")
print("-" * 58)
for i, val in enumerate(future_preds_inv):
    t = last_time + datetime.timedelta(hours=i + 1)
    print(f"{i+1:<5} {str(t):<22} {val:>8.2f}  {aqi_category(val)}")

# bar chart
plt.figure(figsize=(12, 5))
hours_future = list(range(1, 25))
bar_colors   = [aqi_color(aqi_category(v)) for v in future_preds_inv]
plt.bar(hours_future, future_preds_inv, color=bar_colors, edgecolor="gray", alpha=0.85)
plt.axhline(y=12,   color="green",  linestyle="--", alpha=0.5, label="Good (12)")
plt.axhline(y=35.4, color="orange", linestyle="--", alpha=0.5, label="Moderate (35.4)")
plt.xlabel("Hours Ahead")
plt.ylabel("Predicted PM2.5 (µg/m³)")
plt.title("24-Hour PM2.5 Forecast — Dehradun")
plt.legend()
plt.tight_layout()
forecast_png = os.path.join(OUTPUT_DIR, "future_24hr_forecast.png")
plt.savefig(forecast_png, dpi=150)
plt.show()
print(f"✅ 24-hr forecast chart saved → {forecast_png}")

# ══════════════════════════════════════════════════════════════════════════════
# 14. SAVE forecast.json  ← this is what your dashboard reads
# ══════════════════════════════════════════════════════════════════════════════
forecast_output = []
for i, val in enumerate(future_preds_inv):
    t = last_time + datetime.timedelta(hours=i + 1)
    cat = aqi_category(val)
    forecast_output.append({
        "hour":     i + 1,
        "time":     str(t),
        "pm25":     round(float(val), 2),
        "category": cat,
        "color":    aqi_color(cat),
    })

dashboard_data = {
    "generated_at": str(datetime.datetime.now()),
    "forecast":     forecast_output,
    "metrics": {
        "lstm":  {"mae": round(float(lstm_mae),  4),
                  "rmse": round(float(lstm_rmse), 4),
                  "mape": round(float(lstm_mape), 2)},
        "arima": {"mae": round(float(arima_mae),  4),
                  "rmse": round(float(arima_rmse), 4),
                  "mape": round(float(arima_mape), 2)},
        "improvement_pct": round(float(improvement), 2),
    },
    "model_info": {
        "type":          "Multivariate LSTM",
        "seq_len":       SEQ_LEN,
        "features_used": len(FEATURES),
        "feature_list":  FEATURES,
    },
}

json_path = os.path.join(OUTPUT_DIR, "forecast.json")
with open(json_path, "w") as f:
    json.dump(dashboard_data, f, indent=2)
print(f"✅ forecast.json saved → {json_path}")

# ══════════════════════════════════════════════════════════════════════════════
# 15. RESULTS SUMMARY CSV
# ══════════════════════════════════════════════════════════════════════════════
results_df = pd.DataFrame({
    "Metric": ["MAE", "RMSE", "MAPE", "MAE Improvement",
               "Sequence Length", "Features Used"],
    "ARIMA":  [round(arima_mae, 4), round(arima_rmse, 4), f"{arima_mape:.2f}%",
               "-", "-", "1 (PM2.5 only)"],
    "LSTM":   [round(lstm_mae, 4), round(lstm_rmse, 4), f"{lstm_mape:.2f}%",
               f"{improvement:.2f}%", SEQ_LEN, f"{len(FEATURES)} (multivariate)"],
})
csv_path = os.path.join(OUTPUT_DIR, "model_results_summary.csv")
results_df.to_csv(csv_path, index=False)

print("\n=== FINAL RESULTS SUMMARY ===")
print(results_df.to_string(index=False))
print(f"\n✅ All outputs saved to: {OUTPUT_DIR}")
print(
    "\nFiles created:")
for f in sorted(os.listdir(OUTPUT_DIR)):
    size = os.path.getsize(os.path.join(OUTPUT_DIR, f))
    print(f"   {f:<50} {size/1024:.1f} KB")