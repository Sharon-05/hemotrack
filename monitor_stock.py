
import os
import json
import math
import html
import requests
import pandas as pd

from pathlib import Path
from xgboost import XGBRegressor

from data_demo import BLOOD_BANKS, BLOOD_STOCK


# =========================================================
# FILE PATHS
# =========================================================

BASE_DIR = Path(__file__).parent

MODEL_FILE = BASE_DIR / "xgboost_threshold_model.json"
TRAINING_FILE = BASE_DIR / "threshold_training_targets.csv"
STATE_FILE = BASE_DIR / "alert_state.json"


# =========================================================
# MODEL FEATURES
# =========================================================

FEATURE_COLUMNS = [
    "mean_demand",
    "demand_std",
    "demand_p80",
    "mean_availability",
    "availability_std",
    "availability_p20",
    "mean_received",
    "mean_future_demand",
    "future_demand_p80",
    "shortage_risk_rate"
]

BLOOD_GROUP_FEATURES = [
    "blood_group_A+",
    "blood_group_A-",
    "blood_group_AB+",
    "blood_group_AB-",
    "blood_group_B+",
    "blood_group_B-",
    "blood_group_O+",
    "blood_group_O-"
]

MODEL_FEATURES = FEATURE_COLUMNS + BLOOD_GROUP_FEATURES


# =========================================================
# HOSPITAL NAME MAPPING
# =========================================================

HOSPITAL_MAPPING = {
    "Ernakulam General Hospital Blood Bank":
        "Ernakulam General Hospital",

    "Lakeshore Hospital Blood Bank - Kochi":
        "Lakeshore Hospital",

    "VPS Lakeshore Hospital Blood Bank":
        "Lakeshore Hospital",

    "Amrita Institute of Medical Sciences Blood Bank":
        "Amrita Hospital",

    "Rajagiri Hospital Blood Bank":
        "Rajagiri Hospital",

    "Sunrise Hospital Blood Bank":
        "Sunrise Hospital",

    "Lisie Hospital Blood Bank":
        "Lisie Hospital",

    "Aster Medcity Blood Bank":
        "Aster Medcity"
}


def normalize_blood_group(value):
    return str(value).strip().replace("−", "-")


# =========================================================
# LOAD MODEL AND TRAINING DATA
# =========================================================

def get_ml_threshold_table():

    if not MODEL_FILE.exists():
        raise FileNotFoundError("XGBoost model file is missing.")

    if not TRAINING_FILE.exists():
        raise FileNotFoundError("Training CSV file is missing.")

    model = XGBRegressor()
    model.load_model(str(MODEL_FILE))

    training_df = pd.read_csv(TRAINING_FILE)

    required = (
        ["hospital", "blood_group"] +
        FEATURE_COLUMNS
    )

    missing = [
        col for col in required
        if col not in training_df.columns
    ]

    if missing:
        raise ValueError(f"Missing training columns: {missing}")

    training_df["hospital"] = (
        training_df["hospital"].astype(str).str.strip()
    )

    training_df["blood_group"] = (
        training_df["blood_group"].apply(normalize_blood_group)
    )

    for col in FEATURE_COLUMNS:
        training_df[col] = pd.to_numeric(
            training_df[col], errors="coerce"
        )

    training_df = training_df.dropna(
        subset=FEATURE_COLUMNS
    ).reset_index(drop=True)

    X = training_df[FEATURE_COLUMNS].copy()

    for col in BLOOD_GROUP_FEATURES:
        X[col] = 0

    for index, row in training_df.iterrows():

        feature_name = (
            "blood_group_" +
            normalize_blood_group(row["blood_group"])
        )

        if feature_name in BLOOD_GROUP_FEATURES:
            X.loc[index, feature_name] = 1

    X = X[MODEL_FEATURES]

    predictions = model.predict(X)

    result = training_df[
        ["hospital", "blood_group"]
    ].copy()

    result["predicted_threshold"] = [
        max(0, int(math.ceil(float(value))))
        for value in predictions
    ]

    return result


# =========================================================
# COMPARE STOCK WITH ML THRESHOLD
# =========================================================

def find_low_stock():

    stock = BLOOD_STOCK.merge(
        BLOOD_BANKS,
        left_on="hospital_id",
        right_on="id",
        how="inner"
    )

    stock = stock[
        stock["verification_status"] != "not_verified"
    ].copy()

    stock["training_hospital"] = (
        stock["name"].map(HOSPITAL_MAPPING)
    )

    stock["normalized_blood_group"] = (
        stock["blood_group"].apply(normalize_blood_group)
    )

    thresholds = get_ml_threshold_table()

    thresholds["normalized_blood_group"] = (
        thresholds["blood_group"].apply(normalize_blood_group)
    )

    stock = stock.merge(
        thresholds[
            [
                "hospital",
                "normalized_blood_group",
                "predicted_threshold"
            ]
        ],
        left_on=[
            "training_hospital",
            "normalized_blood_group"
        ],
        right_on=[
            "hospital",
            "normalized_blood_group"
        ],
        how="left"
    )

    stock["units_available"] = pd.to_numeric(
        stock["units_available"], errors="coerce"
    )

    stock = stock.dropna(
        subset=["units_available", "predicted_threshold"]
    )

    low = stock[
        stock["units_available"] <
        stock["predicted_threshold"]
    ].copy()

    return low


# =========================================================
# PREVENT REPEATED TELEGRAM ALERTS
# =========================================================

def load_previous_alerts():

    if not STATE_FILE.exists():
        return set()

    with open(STATE_FILE, "r") as file:
        return set(json.load(file))


def save_alerts(alert_keys):

    with open(STATE_FILE, "w") as file:
        json.dump(sorted(alert_keys), file, indent=4)


def make_alert_key(row):

    return "|".join([
        str(row["hospital_id"]),
        normalize_blood_group(row["blood_group"]),
        str(row["component"])
    ])


# =========================================================
# SEND TELEGRAM MESSAGE
# =========================================================

# =========================================================
# SEND TELEGRAM MESSAGE
# =========================================================

def send_telegram_alert(message):

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        raise RuntimeError("Telegram secrets are not configured.")

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        },
        timeout=20
    )

    # Read Telegram's response
    result = response.json()

    if not result.get("ok"):
        print("Telegram API error:", result.get("description"))
        raise RuntimeError("Telegram rejected the alert message.")

    print("Telegram message sent successfully.")

# =========================================================
# MAIN MONITORING FUNCTION
# =========================================================

def main():

    print("HEMOTRACK: Starting scheduled stock monitoring.")

    low_stock = find_low_stock()

    current_keys = {
        make_alert_key(row)
        for _, row in low_stock.iterrows()
    }

    previous_keys = load_previous_alerts()

    # A new alert is needed only for newly low-stock items.
    new_keys = current_keys - previous_keys

    if not current_keys:

        print("No low-stock items found.")

        # Clear previous alerts so a future shortage
        # can generate a new notification.
        save_alerts(set())

        return

    if not new_keys:

        print("Low-stock items already reported. No repeat alert.")

        # Remove recovered items from the saved state.
        save_alerts(current_keys)

        return

    new_low = low_stock[
        low_stock.apply(
            lambda row: make_alert_key(row) in new_keys,
            axis=1
        )
    ]

    lines = []

    for _, row in new_low.iterrows():

        units = int(row["units_available"])
        threshold = int(row["predicted_threshold"])

        status = (
            "OUT OF STOCK"
            if units == 0
            else f"{units} units available"
        )

        lines.append(
            f"• <b>{html.escape(str(row['name']))}</b>\n"
            f"Blood group: {html.escape(str(row['blood_group']))}\n"
            f"Component: {html.escape(str(row['component']))}\n"
            f"Stock: {status}\n"
            f"Predicted threshold: {threshold} units"
        )

    message = (
        "🩸 <b>HEMOTRACK - Automatic ML Low Stock Alert</b>\n\n"
        + "\n\n".join(lines)
        + "\n\nPlease verify the stock with the blood bank."
    )

    # Save the new state only after Telegram succeeds.
    send_telegram_alert(message)

    save_alerts(current_keys)

    print(f"Telegram alert sent for {len(new_keys)} new low-stock item(s).")


if __name__ == "__main__":
    main()
