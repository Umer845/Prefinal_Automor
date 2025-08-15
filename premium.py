import streamlit as st
import pandas as pd
import joblib
from catboost import CatBoostRegressor

# Premium rate multiplier (increase to raise rate only)
PREMIUM_RATE_MULTIPLIER = 1.25  # 25% increase

def show():
    st.title("🚗 Motor Insurance Premium Prediction")

    # Load trained model & features
    try:
        model = CatBoostRegressor()
        model.load_model("models/catboost_premium_model_2.pkl")
        feature_cols = joblib.load("models/model_features_2.pkl")
        categorical_cols = joblib.load("models/model_cat_features_2.pkl")
    except:
        model = None
        st.error("❌ Model not found. Please train the model first.")

    if model:
        st.subheader("Enter Vehicle Details")

        with st.form(key="predict_form"):
            vehicle_make = st.text_input("Vehicle Make", value="Toyota")
            vehicle_model = st.text_input("Vehicle Model", value="Corolla")
            vehicle_make_year = st.number_input("Vehicle Make Year", min_value=1980, max_value=2025, value=2020)
            sum_insured = st.number_input("Sum Insured", min_value=10000, value=500000)
            
            submit = st.form_submit_button("Predict Premium")

        if submit:
            # Calculate vehicle age
            vehicle_age = 2025 - vehicle_make_year

            # Create input dict with required fields
            input_dict = {
                "VEHICLE MAKE": vehicle_make,
                "VEHICLE MODEL": vehicle_model,
                "VEHICLE MAKE YEAR": vehicle_make_year,
                "SUM INSURED": sum_insured,
                "vehicle_age": vehicle_age
            }

            # Fill missing columns with default values
            for col in feature_cols:
                if col not in input_dict:
                    input_dict[col] = 0 if col not in categorical_cols else ""

            # Prepare input dataframe
            input_df = pd.DataFrame([input_dict])[feature_cols]

            # Predict premium
            pred_premium = model.predict(input_df)[0]

            # Multiply premium by 12 (annualize it)
            pred_premium *= 12

            # Calculate original premium rate
            actual_rate = (pred_premium / sum_insured * 100) if sum_insured != 0 else 0
            min__rate = actual_rate * 0.90
            max_rate = actual_rate* PREMIUM_RATE_MULTIPLIER

            # Increase only premium rate
            actual_rate *= PREMIUM_RATE_MULTIPLIER

            # Display results
            st.markdown(
                f"""
                <div style="background-color:#2196F3; padding:15px; border-radius:8px; margin-bottom:10px;">
                    <h4 style="color:white; margin:0;">Predicted Premium: {pred_premium:,.2f}</h4>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div style="background-color:#4CAF50; padding:15px; border-radius:8px; margin-bottom:10px;">
                    <h4 style="color:white; margin:0;">Actual Premium Rate: {actual_rate:.2f}%</h4>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(
                f"""
                <div style="background-color:#FF9800; padding:15px; border-radius:8px; margin-bottom:10px;">
                    <h4 style="color:white; margin:0;">Minimum Premium Rate: {min__rate:.2f}%</h4>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(
                f"""
                <div style="background-color:#F44336; padding:15px; border-radius:8px; margin-bottom:10px;">
                    <h4 style="color:white; margin:0;">Maximum Premium Rate: {max_rate:.2f}%</h4>
                </div>
                """,
                unsafe_allow_html=True
            )

    else:
        st.info("⚠️ Train the model first by uploading dataset and clicking **Train Model**.")

if __name__ == "__main__":
    show()
