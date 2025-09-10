import streamlit as st
import pandas as pd
import numpy as np
from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib
import os
import psycopg2

st.title("🚗 Motor Insurance Premium Prediction & DB Storage")

# --- PostgreSQL connection info ---
DB_PARAMS = {
    "host": "localhost",
    "database": "AutoMotor_Insurance",
    "user": "postgres",
    "password": "United2025",
    "port": 5432
}

# --- Risk Scoring Function ---
def calculate_risk_score(vehicle_use, vehicle_age, sum_insured, driver_age):
    if vehicle_use.lower() == 'personal':
        vehicleuse_score = 0.2
    elif vehicle_use.lower() == 'commercial':
        vehicleuse_score = 1.0
    else:
        vehicleuse_score = 0.6

    if vehicle_age <= 2:
        vehicleage_score = 0.4
    elif 2 < vehicle_age <= 5:
        vehicleage_score = 0.6
    elif 6 <= vehicle_age <= 8:
        vehicleage_score = 0.8
    else:
        vehicleage_score = 1.0

    if sum_insured <= 300000:
        suminsured_score = 0.2
    elif sum_insured <= 750000:
        suminsured_score = 0.4
    elif sum_insured <= 1500000:
        suminsured_score = 0.6
    elif sum_insured <= 3000000:
        suminsured_score = 0.8
    else:
        suminsured_score = 1.0

    if driver_age < 25:
        driverage_score = 1.0
    elif 25 <= driver_age <= 35:
        driverage_score = 0.6
    elif 36 <= driver_age <= 55:
        driverage_score = 0.4
    else:
        driverage_score = 1.0

    raw_score = vehicleuse_score + vehicleage_score + suminsured_score + driverage_score

    if 1.2 <= raw_score < 1.8:
        label = "Low"
    elif 1.8 <= raw_score < 2.4:
        label = "Low to Moderate"
    elif 2.4 <= raw_score < 3.0:
        label = "Medium to High"
    else:
        label = "High"

    return raw_score, label

# --- File Upload ---
uploaded_file = st.file_uploader("Upload your Motor Insurance dataset (CSV)", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # --- Normalize columns to match DB ---
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    st.write("### Dataset Preview")
    st.dataframe(df.head())

    # --- Select Target Column ---
    target_col = st.selectbox("Select Target Column (Premium)", df.columns)

    # --- Vehicle Age ---
    current_year = 2025
    if "vehicle_make_year" in df.columns:
        df["vehicle_age"] = current_year - df["vehicle_make_year"]
    else:
        st.error("❌ 'vehicle_make_year' column not found.")
        st.stop()

    if "driver_age" not in df.columns:
        st.warning("⚠ 'driver_age' missing, filling default 30.")
        df["driver_age"] = 30

    # --- Risk Score ---
    df["risk_percentage"], df["risk_label"] = zip(*df.apply(lambda r:
        calculate_risk_score(
            r.get("vehicle_use", "personal"),
            r["vehicle_age"],
            r["sum_insured"],
            r["driver_age"]
        ), axis=1))

    # --- Store in DB ---
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        for _, row in df.iterrows():
            sql = """
            INSERT INTO insurance_dataset
            (driver_age, vehicle_use, vehicle_make, vehicle_model, vehicle_make_year, vehicle_age,
             sum_insured, policy_premium, risk_percentage, risk_label)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            cur.execute(sql, (
                int(row["driver_age"]),
                row["vehicle_use"],
                row["vehicle_make"],
                row["vehicle_model"],
                int(row["vehicle_make_year"]),
                int(row["vehicle_age"]),
                float(row["sum_insured"]),
                float(row[target_col]),
                float(row["risk_percentage"]),
                row["risk_label"]
            ))
        conn.commit()
        cur.close()
        conn.close()
        st.success("✅ Dataset stored in PostgreSQL database!")
    except Exception as e:
        st.error(f"❌ Database error: {e}")

    # --- Features & Target ---
    feature_cols = [c for c in df.columns if c != target_col]
    X = df[feature_cols]
    y = df[target_col]

    categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # --- Train Model ---
    if st.button("Train Model"):
        # Scale target to reduce high premium effect
        y_train_scaled = y_train / 1000
        y_test_scaled = y_test / 1000

        model = CatBoostRegressor(
            iterations=2000,
            learning_rate=0.05,
            depth=8,
            loss_function="RMSE",
            eval_metric="RMSE",
            cat_features=categorical_cols,
            random_seed=42,
            verbose=False
        )
        model.fit(X_train, y_train_scaled, eval_set=(X_test, y_test_scaled), plot=False)

        y_pred_scaled = model.predict(X_test)
        y_pred = y_pred_scaled * 1000  # scale back

        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        accuracy = 100 * (1 - (abs(y_test - y_pred) / y_test).mean())

        st.subheader("📊 Model Performance")
        st.write(f"**R² Score:** {r2:.4f}")
        st.write(f"**MAE:** {mae:,.2f}")
        st.write(f"**RMSE:** {rmse:,.2f}")
        st.write(f"🎯 **Accuracy:** {accuracy:.2f}%")

        os.makedirs("models", exist_ok=True)
        model.save_model("models/catboost_premium_model.pkl")
        joblib.dump(feature_cols, "models/model_features.pkl")
        joblib.dump(categorical_cols, "models/model_cat_features.pkl")
        st.success("✅ Model trained and saved in `models/` folder")
