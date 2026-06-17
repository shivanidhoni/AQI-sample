from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

# =====================================
# APP INITIALIZATION
# =====================================
app = FastAPI(title="VayuDrishti AQI API")

# =====================================
# CORS CONFIGURATION
# =====================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================
# LOAD DATASET
# =====================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "dehradun_master_dataset_cleaned.xlsx")

df = pd.DataFrame()

try:
    df = pd.read_excel(FILE_PATH)

    df.columns = df.columns.str.strip()

    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(
            df["datetime"],
            errors="coerce"
        )

    if "zone" in df.columns:
        df["zone"] = (
            df["zone"]
            .astype(str)
            .str.lower()
            .str.strip()
        )

    print(f"✅ Dataset loaded successfully ({len(df)} rows)")

except Exception as e:
    print("❌ Dataset loading error:", e)

# =====================================
# HOME API
# =====================================
@app.get("/")
def home():
    return {
        "status": "API running successfully"
    }

# =====================================
# SHOW ALL AVAILABLE ZONES
# =====================================
@app.get("/zones/")
def get_zones():

    if df.empty:
        return {"error": "Dataset not loaded"}

    zones = sorted(df["zone"].dropna().unique().tolist())

    return {
        "total_zones": len(zones),
        "zones": zones
    }

# =====================================
# CHAT API
# =====================================
@app.get("/chat/")
def chat(query: str):

    if df.empty:
        return {"error": "Dataset not loaded"}

    query = query.lower().strip()

    matched_zone = None

    # ---------------------------------
    # SMART MATCHING
    # ---------------------------------
    for zone in df["zone"].dropna().unique():

        zone_clean = str(zone).lower().strip()

        if query == zone_clean:
            matched_zone = zone
            break

        if query in zone_clean:
            matched_zone = zone
            break

    # ---------------------------------
    # IF ZONE FOUND
    # ---------------------------------
    if matched_zone:

        zone_df = df[df["zone"] == matched_zone]

        zone_df = zone_df.dropna(subset=["datetime"])

        if zone_df.empty:
            return {
                "error": "No AQI data available"
            }

        latest = zone_df.sort_values(
            by="datetime",
            ascending=False
        ).iloc[0]

        return {
            "type": "aqi",
            "zone": latest["zone"].title(),
            "aqi": round(float(latest["eu_aqi"]), 2),
            "pm25": round(float(latest["pm25"]), 2),
            "time": str(latest["datetime"])
        }

    # ---------------------------------
    # IF ZONE NOT FOUND
    # ---------------------------------
    return {
        "type": "text",
        "response": (
            "Zone not found. Try: Rajpur, ISBT, Clock Tower, "
            "Prem Nagar, Sahastradhara, Doon Hospital, "
            "Doon School, Max Hospital."
        )
    }