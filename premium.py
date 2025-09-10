import streamlit as st
import pandas as pd
import joblib
from catboost import CatBoostRegressor
import psycopg2
import numpy as np

# PostgreSQL connection info
DB_PARAMS = {
    "host": "localhost",
    "database": "AutoMotor_Insurance",
    "user": "postgres",
    "password": "United2025",
    "port": 5432
}

def get_min_max_rate(vehicle_make, vehicle_model):
    """Fetch min and max premium rate (%) from DB for a given make & sub-make"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                MIN(policy_premium / sum_insured * 100) AS min_rate,
                MAX(policy_premium / sum_insured * 100) AS max_rate
            FROM insurance_dataset
            WHERE LOWER(vehicle_make) = %s AND LOWER(vehicle_model) = %s
        """, (vehicle_make.lower(), vehicle_model.lower()))
        result = cur.fetchone()
        cur.close()
        conn.close()
        if result and result[0] is not None:
            return result[0], result[1]
        else:
            return None, None
    except Exception as e:
        st.error(f"❌ Database error: {e}")
        return None, None

def show():
    st.title("🚗 Motor Insurance Premium Prediction")

    # Load trained model & features
    try:
        model = CatBoostRegressor()
        model.load_model("models/catboost_premium_model.pkl")
        feature_cols = joblib.load("models/model_features.pkl")
        categorical_cols = joblib.load("models/model_cat_features.pkl")
    except:
        model = None
        st.error("❌ Model not found. Please train the model first.")

    if model:
        st.subheader("Enter Vehicle Details")

        # Input widgets
        vehicle_make = st.text_input("Vehicle Make", value="Toyota")
        vehicle_model = st.text_input("Vehicle Model (Sub-make)", value="Corolla")
        vehicle_make_year = st.number_input("Vehicle Make Year", min_value=1980, max_value=2025, value=2020)
        sum_insured = st.number_input("Sum Insured", min_value=10000, value=500000)

        vehicle_age = 2025 - vehicle_make_year

        # Prepare input for model
        input_dict = {
            "vehicle_make": vehicle_make,
            "vehicle_model": vehicle_model,
            "vehicle_make_year": vehicle_make_year,
            "sum_insured": sum_insured,
            "vehicle_age": vehicle_age
        }

        # Fill missing columns for model
        for col in feature_cols:
            if col not in input_dict:
                input_dict[col] = 0 if col not in categorical_cols else ""

        input_df = pd.DataFrame([input_dict])[feature_cols]

        # Predict base premium rate (%) using model
        base_pred_rate = model.predict(input_df)[0]

        # Adjust premium rate dynamically based on vehicle age and sum insured
        # Newer cars are lower risk, older cars higher risk
        age_factor = 1 + (vehicle_age / 20)  # older cars increase rate up to ~1.2x
        # Higher sum insured slightly increases rate
        sum_insured_factor = 1 + ((sum_insured - 500000) / 5000000)  # small adjustment

        pred_rate = base_pred_rate * age_factor * sum_insured_factor

        # Fetch historical min/max rates from DB
        min_rate_db, max_rate_db = get_min_max_rate(vehicle_make, vehicle_model)

        # Use prediction-based min/max if no historical data
        if min_rate_db is None:
            min_rate_db = pred_rate * 0.8
        if max_rate_db is None:
            max_rate_db = pred_rate * 1.2

        # Clip to historical range
        pred_rate = np.clip(pred_rate, min_rate_db, max_rate_db)

        # Calculate actual premium
        pred_annual = sum_insured * pred_rate / 100

        # Display results
        st.markdown(f"""
            <div style="background-color:#2196F3; padding:15px; border-radius:8px; margin-bottom:10px;">
                <h4 style="color:white; margin:0;">Predicted Premium: PKR {pred_annual:,.0f}</h4>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style="background-color:#4CAF50; padding:15px; border-radius:8px; margin-bottom:10px;">
                <h4 style="color:white; margin:0;">Predicted Premium Rate: {pred_rate:.2f}%</h4>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style="background-color:#FF9800; padding:15px; border-radius:8px; margin-bottom:10px;">
                <h4 style="color:white; margin:0;">Minimum Historical Rate: {min_rate_db:.2f}%</h4>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style="background-color:#F44336; padding:15px; border-radius:8px; margin-bottom:10px;">
                <h4 style="color:white; margin:0;">Maximum Historical Rate: {max_rate_db:.2f}%</h4>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    show()
