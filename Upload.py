import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

# PostgreSQL connection info
DB_PARAMS = {
    "host": "localhost",
    "database": "AutoMotor_Insurance",
    "user": "postgres",
    "password": "United2025",
    "port": 5432
}

def store_dataset_in_db(df):
    """Store uploaded dataset in PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        # Create table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS insurance_dataset (
                id SERIAL PRIMARY KEY,
                driver_age INT,
                vehicle_use VARCHAR(50),
                vehicle_make VARCHAR(50),
                vehicle_model VARCHAR(50),
                vehicle_make_year INT,
                vehicle_age INT,
                sum_insured NUMERIC(12,2),
                policy_premium NUMERIC(12,2),
                risk_percentage NUMERIC(5,2),
                risk_label VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        # Insert dataset rows
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO insurance_dataset 
                (driver_age, vehicle_use, vehicle_make, vehicle_model, vehicle_make_year, vehicle_age, sum_insured, policy_premium, risk_percentage, risk_label)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row.get("DRIVER AGE", 30),
                row.get("VEHICLE USE", "personal"),
                row.get("VEHICLE MAKE", ""),
                row.get("VEHICLE MODEL", ""),
                row.get("VEHICLE MAKE YEAR", None),
                row.get("vehicle_age", None),
                row.get("SUM INSURED", 0),
                row.get("POLICY PREMIUM", 0),
                row.get("risk_percentage", 0),
                row.get("risk_label", "Low")
            ))
        conn.commit()
        cur.close()
        conn.close()
        st.success("✅ Dataset stored in PostgreSQL successfully!")
    except Exception as e:
        st.error(f"❌ Database error: {e}")

def show():
    st.title("📤 Upload Motor Insurance Dataset")

    uploaded_file = st.file_uploader(
        "Upload your dataset (CSV, XLS, XLSX)", 
        type=["csv", "xls", "xlsx"]
    )

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:  # xls or xlsx
                df = pd.read_excel(uploaded_file)

            df.columns = df.columns.str.strip()  # remove extra spaces

            st.write("### Dataset Preview")
            st.dataframe(df.head())

            # Calculate vehicle_age if VEHICLE MAKE YEAR exists
            current_year = 2025
            if "VEHICLE MAKE YEAR" in df.columns:
                df["vehicle_age"] = current_year - df["VEHICLE MAKE YEAR"]
            else:
                df["vehicle_age"] = None

            # Fill DRIVER AGE if missing
            if "DRIVER AGE" not in df.columns:
                df["DRIVER AGE"] = 30

            # Optional: calculate risk scores if columns exist
            if "VEHICLE USE" in df.columns and "SUM INSURED" in df.columns:
                def calculate_risk_score(vehicle_use, vehicle_age, sum_insured, driver_age):
                    vehicleuse_score = 0.2 if vehicle_use.lower() == 'personal' else 1.0 if vehicle_use.lower() == 'commercial' else 0.6
                    vehicleage_score = 0.4 if vehicle_age <= 2 else 0.6 if 2 < vehicle_age <= 5 else 0.8 if 6 <= vehicle_age <= 8 else 1.0
                    suminsured_score = 0.2 if sum_insured <= 300000 else 0.4 if 300001 <= sum_insured <= 750000 else 0.6 if 750001 <= sum_insured <= 1500000 else 0.8 if 1500001 <= sum_insured <= 3000000 else 1.0
                    driverage_score = 1.0 if driver_age < 25 else 0.6 if 25 <= driver_age <= 35 else 0.4 if 36 <= driver_age <= 55 else 1.0
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

                df["risk_percentage"], df["risk_label"] = zip(*df.apply(lambda r:
                    calculate_risk_score(
                        r.get("VEHICLE USE", "personal"),
                        r.get("vehicle_age", 0),
                        r.get("SUM INSURED", 0),
                        r.get("DRIVER AGE", 30)
                    ), axis=1))

            # Store dataset in DB
            if st.button("Store Dataset in Database"):
                store_dataset_in_db(df)

        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
