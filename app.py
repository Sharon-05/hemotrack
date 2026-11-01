
import streamlit as st
import pandas as pd
import math
import requests
import html
from pathlib import Path
from xgboost import XGBRegressor

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="HEMOTRACK - Real-Time Blood Availability in Kerala",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# FILE PATHS
# =========================================================

BASE_DIR = Path(__file__).parent

MODEL_FILE = BASE_DIR / "xgboost_threshold_model.json"
METADATA_FILE = BASE_DIR / "xgboost_threshold_metadata.json"
TRAINING_FILE = BASE_DIR / "threshold_training_targets.csv"

# =========================================================
# TELEGRAM ALERT FUNCTION
# =========================================================

def send_telegram_alert(message):

    try:

        url = (
            f"https://api.telegram.org/bot"
            f"{st.secrets['TELEGRAM_BOT_TOKEN']}/sendMessage"
        )

        response = requests.post(
            url,
            data={
                "chat_id": st.secrets["TELEGRAM_CHAT_ID"],
                "text": message,
                "parse_mode": "HTML"
            },
            timeout=10
        )

        return response.ok

    except Exception:
        return False


# =========================================================
# IMPORT DEMO DATA
# =========================================================

from data_demo import (
    BLOOD_BANKS,
    BLOOD_STOCK,
    KERALA_DISTRICTS,
    BLOOD_GROUPS,
    BLOOD_COMPONENTS
)


# =========================================================
# XGBOOST MODEL CONFIGURATION
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
    """Normalize blood group names."""

    return str(value).strip().replace("−", "-")


def get_training_hospital(app_hospital):
    """Map application hospital names to training names."""

    return HOSPITAL_MAPPING.get(
        str(app_hospital).strip()
    )


# =========================================================
# LOAD XGBOOST MODEL
# =========================================================

@st.cache_resource
def load_xgboost_model():

    if not MODEL_FILE.exists():

        raise FileNotFoundError(
            "xgboost_threshold_model.json was not found."
        )

    model = XGBRegressor()

    model.load_model(str(MODEL_FILE))

    return model


# =========================================================
# LOAD TRAINING CSV
# =========================================================

@st.cache_data
def load_threshold_data():

    if not TRAINING_FILE.exists():

        raise FileNotFoundError(
            "threshold_training_targets.csv was not found."
        )

    df = pd.read_csv(TRAINING_FILE)

    required_columns = (
        ["hospital", "blood_group", "threshold_target"]
        + FEATURE_COLUMNS
    )

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Missing columns in training CSV: {missing_columns}"
        )

    df["hospital"] = (
        df["hospital"].astype(str).str.strip()
    )

    df["blood_group"] = (
        df["blood_group"].apply(normalize_blood_group)
    )

    for col in FEATURE_COLUMNS:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = df.dropna(
        subset=FEATURE_COLUMNS + [
            "hospital",
            "blood_group"
        ]
    ).copy()

    return df


# =========================================================
# GENERATE EXISTING ML-PREDICTED THRESHOLDS
# =========================================================

@st.cache_data
def get_ml_threshold_table():

    model = load_xgboost_model()

    training_df = load_threshold_data()

    X = training_df[FEATURE_COLUMNS].copy()

    # Create blood group one-hot columns.

    for column in BLOOD_GROUP_FEATURES:

        X[column] = 0

    # Set the corresponding blood group feature to 1.

    for index, row in training_df.iterrows():

        blood_group = normalize_blood_group(
            row["blood_group"]
        )

        feature_name = f"blood_group_{blood_group}"

        if feature_name in BLOOD_GROUP_FEATURES:

            X.loc[index, feature_name] = 1

    # Arrange the 18 features in the correct order.

    X = X[MODEL_FEATURES]

    # Predict thresholds.

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
# GENERATE ML THRESHOLDS FOR ALL HOSPITALS
# =========================================================

def add_ml_threshold(data):

    data = data.copy()

    # -----------------------------------------------------
    # 1. MAP HOSPITAL NAMES
    # -----------------------------------------------------

    data["training_hospital"] = data["name"].apply(
        get_training_hospital
    )

    # Normalize blood groups.

    data["normalized_blood_group"] = (
        data["blood_group"].apply(
            normalize_blood_group
        )
    )

    # -----------------------------------------------------
    # 2. LOAD MODEL AND TRAINING DATA
    # -----------------------------------------------------

    model = load_xgboost_model()

    training_data = load_threshold_data().copy()

    threshold_table = get_ml_threshold_table().copy()

    threshold_table["normalized_blood_group"] = (
        threshold_table["blood_group"].apply(
            normalize_blood_group
        )
    )

    # -----------------------------------------------------
    # 3. GET EXISTING HOSPITAL-SPECIFIC PREDICTIONS
    # -----------------------------------------------------

    hospital_thresholds = (
        threshold_table
        .groupby(
            [
                "hospital",
                "normalized_blood_group"
            ],
            as_index=False
        )["predicted_threshold"]
        .median()
    )

    hospital_thresholds.rename(
        columns={
            "hospital": "training_hospital",
            "predicted_threshold": "specific_threshold"
        },
        inplace=True
    )

    # -----------------------------------------------------
    # 4. CREATE HISTORICAL FEATURE PROFILES
    # -----------------------------------------------------

    # Use median historical numerical features
    # separately for each blood group.

    feature_profiles = (
        training_data
        .groupby("blood_group")[FEATURE_COLUMNS]
        .median()
        .reset_index()
    )

    feature_profiles["blood_group"] = (
        feature_profiles["blood_group"].apply(
            normalize_blood_group
        )
    )

    # -----------------------------------------------------
    # 5. CREATE ALL HOSPITAL AND BLOOD GROUP COMBINATIONS
    # -----------------------------------------------------

    hospitals = data[
        ["name", "training_hospital"]
    ].drop_duplicates()

    blood_groups = data[
        ["normalized_blood_group"]
    ].drop_duplicates()

    prediction_rows = hospitals.merge(
        blood_groups,
        how="cross"
    )

    # Attach the appropriate historical feature profile.

    prediction_rows = prediction_rows.merge(
        feature_profiles,
        left_on="normalized_blood_group",
        right_on="blood_group",
        how="left"
    )

    # -----------------------------------------------------
    # 6. CREATE BLOOD GROUP ONE-HOT FEATURES
    # -----------------------------------------------------

    for column in BLOOD_GROUP_FEATURES:

        prediction_rows[column] = 0

    for index, row in prediction_rows.iterrows():

        blood_group = row["normalized_blood_group"]

        feature_name = f"blood_group_{blood_group}"

        if feature_name in BLOOD_GROUP_FEATURES:

            prediction_rows.loc[index, feature_name] = 1

    # -----------------------------------------------------
    # 7. PREPARE MODEL INPUT
    # -----------------------------------------------------

    # Use exactly the same 18 features as model training.

    X_new = prediction_rows[MODEL_FEATURES].copy()

    # Fill missing numerical features using training medians.

    feature_medians = training_data[
        FEATURE_COLUMNS
    ].median()

    X_new[FEATURE_COLUMNS] = (
        X_new[FEATURE_COLUMNS].fillna(
            feature_medians
        )
    )

    X_new = X_new.fillna(0)

    # -----------------------------------------------------
    # 8. GENERATE NEW XGBOOST PREDICTIONS
    # -----------------------------------------------------

    generated_predictions = model.predict(X_new)

    prediction_rows["generated_threshold"] = [
        max(0, int(math.ceil(float(value))))
        for value in generated_predictions
    ]

    generated_thresholds = prediction_rows[
        [
            "name",
            "normalized_blood_group",
            "generated_threshold"
        ]
    ].copy()

    # -----------------------------------------------------
    # 9. MERGE EXISTING HOSPITAL-SPECIFIC PREDICTIONS
    # -----------------------------------------------------

    data = data.merge(
        hospital_thresholds,
        on=[
            "training_hospital",
            "normalized_blood_group"
        ],
        how="left"
    )

    # -----------------------------------------------------
    # 10. MERGE NEWLY GENERATED PREDICTIONS
    # -----------------------------------------------------

    data = data.merge(
        generated_thresholds,
        on=[
            "name",
            "normalized_blood_group"
        ],
        how="left"
    )

    # -----------------------------------------------------
    # 11. SELECT FINAL THRESHOLD
    # -----------------------------------------------------

    # Use the existing hospital-specific prediction
    # wherever available.
    #
    # Otherwise use the newly generated XGBoost prediction.

    data["predicted_threshold"] = (
        data["specific_threshold"].combine_first(
            data["generated_threshold"]
        )
    )

    # -----------------------------------------------------
    # 12. IDENTIFY THRESHOLD SOURCE
    # -----------------------------------------------------

    data["threshold_source"] = (
        "Hospital-specific ML"
    )

    data.loc[
        data["specific_threshold"].isna()
        & data["generated_threshold"].notna(),
        "threshold_source"
    ] = "XGBoost generated estimate"

    data.loc[
        data["predicted_threshold"].isna(),
        "threshold_source"
    ] = "Unavailable"

    # -----------------------------------------------------
    # 13. REMOVE TEMPORARY COLUMNS
    # -----------------------------------------------------

    data.drop(
        columns=[
            "specific_threshold",
            "generated_threshold"
        ],
        inplace=True,
        errors="ignore"
    )

    return data


# =========================================================
# LOAD ML DATA SAFELY
# =========================================================

try:

    ML_THRESHOLD_DATA = get_ml_threshold_table()

    ML_AVAILABLE = True

    ML_ERROR = None

except Exception as error:

    ML_THRESHOLD_DATA = pd.DataFrame()

    ML_AVAILABLE = False

    ML_ERROR = str(error)


# =========================================================
# SESSION STATE
# =========================================================

if "search_triggered" not in st.session_state:

    st.session_state.search_triggered = False


# =========================================================
# TELEGRAM LOW-STOCK ALERT SYSTEM
# =========================================================

@st.cache_resource
def _sent_alerts():

    return set()


def check_low_stock(force=False):

    if not ML_AVAILABLE:

        return "model_error"

    merged = BLOOD_STOCK.merge(
        BLOOD_BANKS,
        left_on="hospital_id",
        right_on="id",
        how="inner"
    )

    # Ignore unverified stock records.

    merged = merged[
        merged["verification_status"] != "not_verified"
    ].copy()

    # Add ML thresholds for all hospitals.

    merged = add_ml_threshold(merged)

    # Keep records with available predictions.

    merged = merged.dropna(
        subset=["predicted_threshold"]
    )

    # Compare stock against predicted thresholds.

    low = merged[
        merged["units_available"] <
        merged["predicted_threshold"]
    ].sort_values("units_available")

    if low.empty:

        return "none"

    signature = str(sorted(zip(
        low["hospital_id"],
        low["blood_group"],
        low["component"],
        low["units_available"],
        low["predicted_threshold"]
    )))

    sent = _sent_alerts()

    if signature in sent and not force:

        return "already_sent"

    lines = []

    for _, row in low.head(15).iterrows():

        units = int(row["units_available"])

        threshold = int(row["predicted_threshold"])

        tag = (
            "OUT OF STOCK"
            if units == 0
            else f"{units} units left"
        )

        threshold_source = html.escape(
            str(row["threshold_source"])
        )

        lines.append(
            f"• {html.escape(str(row['name']))}: "
            f"<b>{html.escape(str(row['blood_group']))}</b> "
            f"{html.escape(str(row['component']))} - "
            f"{tag} "
            f"({threshold_source}: {threshold} units)"
        )

    extra = len(low) - 15

    message = (
        "🩸 <b>HEMOTRACK Low Blood Stock Alert</b>\n\n"
        + "\n".join(lines)
    )

    if extra > 0:

        message += f"\n…and {extra} more"

    message += (
        "\n\nPlease confirm availability directly "
        "with the blood bank."
    )

    if send_telegram_alert(message):

        sent.add(signature)

        return "sent"

    return "failed"


# Check low stock automatically.

alert_status = check_low_stock()


# =========================================================
# SIDEBAR - TELEGRAM ALERTS
# =========================================================

with st.sidebar:

    st.markdown("### 🔔 Telegram Alerts")

    if st.button("Send low-stock alert now"):

        result = check_low_stock(force=True)

        if result == "sent":

            st.success(
                "Alert sent to Telegram!"
            )

        elif result == "none":

            st.info(
                "No ML low-stock items right now."
            )

        elif result == "model_error":

            st.error(
                "ML model is unavailable."
            )

        elif result == "already_sent":

            st.info(
                "The current low-stock alert was already sent."
            )

        else:

            st.error(
                "Could not send. Check Telegram secrets."
            )


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

:root {
    --primary: #c0392b;
    --dark: #2c3e50;
}

h1, h2, h3 {
    color: var(--dark);
    font-weight: 700;
}

.header-section {
    background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%);
    padding: 50px 30px;
    border-radius: 15px;
    color: white;
    margin-bottom: 40px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(192, 57, 43, 0.2);
}

.header-section h1 {
    margin: 0;
    font-size: 3rem;
    font-weight: 800;
    color: white;
}

.header-section p {
    margin: 15px 0 0 0;
    font-size: 1.2rem;
    color: white;
}

.header-stats {
    display: flex;
    justify-content: space-around;
    margin-top: 30px;
    gap: 20px;
}

.stat-box {
    background: rgba(255,255,255,0.15);
    padding: 15px 25px;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.2);
}

.stat-box-num {
    font-size: 2.5rem;
    font-weight: 800;
}

.stat-box-label {
    font-size: 0.9rem;
    opacity: 0.9;
}

.filter-section {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    padding: 30px;
    border-radius: 12px;
    margin-bottom: 30px;
    border: 1px solid #dee2e6;
}

.stat-card {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border-left: 4px solid #c0392b;
}

.stat-card h3 {
    margin: 0 0 10px 0;
    color: #7f8c8d;
    font-size: 0.9rem;
}

.stat-card .number {
    font-size: 2.5rem;
    font-weight: 800;
    color: #c0392b;
}

.demo-badge {
    display: inline-block;
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    margin-bottom: 20px;
}

.footer-section {
    background: #2c3e50;
    color: white;
    padding: 30px;
    border-radius: 10px;
    margin-top: 40px;
    text-align: center;
}

.footer-section h3 {
    color: white;
}

.footer-section p {
    color: white;
    opacity: 0.9;
}

@media (max-width: 768px) {

    .header-section h1 {
        font-size: 2rem;
    }

    .header-stats {
        flex-direction: column;
    }

}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER SECTION
# =========================================================

st.html("""
<div class="header-section">

    <h1>🩸 HEMOTRACK</h1>

    <p>Real-Time Blood Availability in Kerala</p>

    <div class="header-stats">

        <div class="stat-box">
            <div class="stat-box-num">15</div>
            <div class="stat-box-label">Blood Banks (Ernakulam)</div>
        </div>

        <div class="stat-box">
            <div class="stat-box-num">8</div>
            <div class="stat-box-label">Blood Groups</div>
        </div>

        <div class="stat-box">
            <div class="stat-box-num">4</div>
            <div class="stat-box-label">Components</div>
        </div>

    </div>

</div>
""")


# =========================================================
# SEARCH FILTER SECTION
# =========================================================

st.markdown(
    '<div class="filter-section">',
    unsafe_allow_html=True
)

st.markdown("## 🔍 Search Blood Availability")

col1, col2, col3, col4 = st.columns(
    4,
    gap="medium"
)

with col1:

    state = st.selectbox(
        "🗺️ State",
        ["Kerala"],
        disabled=True,
        label_visibility="collapsed"
    )

with col2:

    district = st.selectbox(
        "📍 District",
        ["Select District..."] + KERALA_DISTRICTS,
        label_visibility="collapsed",
        index=0
    )

with col3:

    blood_group = st.selectbox(
        "🩸 Blood Group",
        ["Select Blood Group..."] + BLOOD_GROUPS[1:],
        label_visibility="collapsed",
        index=0
    )

with col4:

    component = st.selectbox(
        "🧪 Component",
        ["Select Component..."] + BLOOD_COMPONENTS[1:],
        label_visibility="collapsed",
        index=0
    )


col_search1, col_search2, col_search3 = st.columns(
    [2, 1, 1],
    gap="small"
)

with col_search1:

    if st.button(
        "🔎 Search Blood Availability",
        use_container_width=True,
        type="primary"
    ):

        st.session_state.search_triggered = True

with col_search2:

    if st.button(
        "🔄 Reset",
        use_container_width=True
    ):

        st.session_state.search_triggered = False

        st.rerun()


st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# RESULTS SECTION
# =========================================================

if st.session_state.search_triggered:

    if (
        district == "Select District..."
        or blood_group == "Select Blood Group..."
        or component == "Select Component..."
    ):

        st.error(
            "❌ Please complete all selections to search"
        )

        st.info(
            "💡 Select District, Blood Group, and Blood Component"
        )

    else:

        # Merge hospital and stock data.

        merged_data = BLOOD_STOCK.merge(
            BLOOD_BANKS,
            left_on="hospital_id",
            right_on="id",
            how="inner"
        )

        # Generate ML thresholds for all hospitals.

        if ML_AVAILABLE:

            try:

                merged_data = add_ml_threshold(
                    merged_data
                )

            except Exception as error:

                st.error(
                    f"Could not generate ML thresholds: {error}"
                )

                merged_data["predicted_threshold"] = pd.NA

                merged_data["threshold_source"] = "Unavailable"

        else:

            merged_data["predicted_threshold"] = pd.NA

            merged_data["threshold_source"] = "Unavailable"

        # Apply selected filters.

        filtered_stock = merged_data[
            (merged_data["district"] == district)
            & (
                merged_data["blood_group"].apply(
                    normalize_blood_group
                ) == normalize_blood_group(blood_group)
            )
            & (merged_data["component"] == component)
        ].copy()

        if filtered_stock.empty:

            col1, col2 = st.columns([1, 1])

            with col1:

                st.warning(
                    f"❌ No {blood_group} {component} "
                    f"available in {district}"
                )

            with col2:

                st.info(
                    "💡 Try a different district or blood component"
                )

        else:

            # =================================================
            # STATISTICS
            # =================================================

            hospital_ids = filtered_stock[
                "hospital_id"
            ].unique()

            available_count = len(
                filtered_stock[
                    filtered_stock["units_available"] > 0
                ]
            )

            st.markdown(
                f"### 📊 Results: {blood_group} • "
                f"{component} • {district}"
            )

            stat_col1, stat_col2, stat_col3 = st.columns(3)

            with stat_col1:

                st.markdown(
                    f'<div class="stat-card">'
                    f'<h3>Hospitals</h3>'
                    f'<div class="number">{len(hospital_ids)}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            with stat_col2:

                st.markdown(
                    f'<div class="stat-card">'
                    f'<h3>In Stock</h3>'
                    f'<div class="number">{available_count}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            with stat_col3:

                total_units = filtered_stock[
                    "units_available"
                ].sum()

                st.markdown(
                    f'<div class="stat-card">'
                    f'<h3>Total Units</h3>'
                    f'<div class="number">{total_units}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            st.markdown("---")

            # =================================================
            # HOSPITAL CARDS
            # =================================================

            for idx, (_, stock_row) in enumerate(
                filtered_stock.sort_values(
                    "units_available",
                    ascending=False
                ).iterrows()
            ):

                hospital_id = stock_row["hospital_id"]

                units = int(
                    stock_row["units_available"]
                )

                max_units = 30

                hospital_name = stock_row["name"]

                hospital_addr = stock_row["address"]

                phone = stock_row["phone"]

                maps_link = stock_row["google_maps_link"]

                ml_threshold = stock_row[
                    "predicted_threshold"
                ]

                threshold_source = stock_row[
                    "threshold_source"
                ]

                # ---------------------------------------------
                # DETERMINE STOCK STATUS
                # ---------------------------------------------

                if stock_row["verification_status"] == "not_verified":

                    status_text = "🔲 Not Verified"

                    units_display = "—"

                    progress_pct = 0

                elif units == 0:

                    status_text = "❌ Out of Stock"

                    units_display = "0 units"

                    progress_pct = 0

                elif pd.isna(ml_threshold):

                    status_text = "⚪ Threshold Unavailable"

                    units_display = f"{units} units"

                    progress_pct = min(
                        (units / max_units) * 100,
                        100
                    )

                elif threshold_source == "XGBoost generated estimate":

                    if units < ml_threshold:

                        status_text = "⚠️ Low Stock (XGBoost Estimate)"

                    else:

                        status_text = "🔵 XGBoost Estimate"

                    units_display = f"{units} units"

                    progress_pct = min(
                        (units / max_units) * 100,
                        100
                    )

                elif units < ml_threshold:

                    status_text = "⚠️ Low Stock"

                    units_display = f"{units} units"

                    progress_pct = min(
                        (units / max_units) * 100,
                        100
                    )

                else:

                    status_text = "✅ Available"

                    units_display = f"{units} units"

                    progress_pct = min(
                        (units / max_units) * 100,
                        100
                    )

                # ---------------------------------------------
                # HOSPITAL CARD
                # ---------------------------------------------

                with st.container(border=True):

                    col_name, col_status = st.columns([3, 1])

                    with col_name:

                        st.markdown(
                            f"### {hospital_name}"
                        )

                        st.markdown(
                            f"📍 {hospital_addr}"
                        )

                    with col_status:

                        st.markdown(
                            f"#### {status_text}"
                        )

                    st.divider()

                    # -----------------------------------------
                    # HOSPITAL INFORMATION
                    # -----------------------------------------

                    grid_col1, grid_col2 = st.columns(2)

                    with grid_col1:

                        st.metric(
                            "Stock Level",
                            units_display
                        )

                        st.progress(
                            progress_pct / 100
                            if progress_pct > 0
                            else 0
                        )

                        if stock_row["verification_status"] == "not_verified":

                            st.metric(
                                "ML Predicted Threshold",
                                "Not verified"
                            )

                        elif pd.notna(ml_threshold):

                            if threshold_source == "XGBoost generated estimate":

                                st.metric(
                                    "XGBoost Estimated Threshold",
                                    f"{int(ml_threshold)} units"
                                )

                                st.caption(
                                    "Generated by the existing XGBoost "
                                    "model using historical blood-group "
                                    "feature profiles."
                                )

                            else:

                                st.metric(
                                    "ML Predicted Threshold",
                                    f"{int(ml_threshold)} units"
                                )

                        else:

                            st.metric(
                                "ML Predicted Threshold",
                                "Unavailable"
                            )

                    with grid_col2:

                        st.metric(
                            "Blood Group",
                            stock_row["blood_group"]
                        )

                        st.metric(
                            "Component",
                            stock_row["component"]
                        )

                    st.divider()

                    # -----------------------------------------
                    # ACTION BUTTONS
                    # -----------------------------------------

                    btn_col1, btn_col2, btn_col3 = st.columns(3)

                    with btn_col1:

                        cleaned_phone = (
                            str(phone)
                            .replace("+91-", "")
                            .replace("-", "")
                        )

                        st.link_button(
                            "☎️ Call Now",
                            f"tel:{cleaned_phone}",
                            use_container_width=True
                        )

                    with btn_col2:

                        st.link_button(
                            "📍 Get Directions",
                            maps_link,
                            use_container_width=True
                        )

                    with btn_col3:

                        if st.button(
                            "ℹ️ Details",
                            key=f"info_{hospital_id}_{idx}",
                            use_container_width=True
                        ):

                            verification = (
                                str(
                                    stock_row["verification_status"]
                                )
                                .replace("_", " ")
                                .title()
                            )

                            if pd.notna(ml_threshold):

                                threshold_display = (
                                    f"{int(ml_threshold)} units "
                                    f"({threshold_source})"
                                )

                            else:

                                threshold_display = "Unavailable"

                            st.info(
                                f"""
                                **Hospital Name:** {hospital_name}

                                **Address:** {hospital_addr}

                                **Phone:** {phone}

                                **Verification:** {verification}

                                **Last Updated:** {str(stock_row['update_time'])[:10]}

                                **Data Source:** {stock_row['source']}

                                **Threshold:** {threshold_display}
                                """
                            )

                st.markdown("")


# =========================================================
# FOOTER SECTION
# =========================================================

st.html("""
<div class="footer-section">

    <h3>🩸 HEMOTRACK - Blood Bank Finder</h3>

    <p><strong>Data Source:</strong> eRaktKosh (Demo Mode)</p>

    <p><strong>Coverage:</strong> Kerala - Currently Ernakulam (15 hospitals)</p>

    <p><strong>⚠️ Important Disclaimer:</strong></p>

    <p style="font-size: 0.9rem; margin: 10px 0;">

        This is a <strong>DEMO application</strong> for testing and
        demonstration purposes only.

        Always confirm blood availability
        <strong>directly with the blood bank</strong>
        by calling them before visiting.

        Stock levels may change throughout the day.

    </p>

    <p style="margin-top: 20px;
              border-top: 1px solid rgba(255,255,255,0.2);
              padding-top: 15px;">

        Built with ❤️ using Streamlit | Data: eRaktKosh Portal

        <br>

        <small>
            © 2026 HEMOTRACK.
            In partnership with Government of India - Blood Bank Directory
        </small>

    </p>

</div>
""")


# =========================================================
# TELEGRAM TEST ALERT
# =========================================================

if st.button("Send test alert"):

    if send_telegram_alert(
        "🩸 Test alert from HEMOTRACK"
    ):

        st.success(
            "Test alert sent successfully!"
        )

    else:

        st.error(
            "Failed to send test alert. Check Telegram secrets."
        )
