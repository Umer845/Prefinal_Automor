import streamlit as st
from train_model_2 import calculate_risk_score  # Reuse function

def show():
    st.title("🔍 Motor Insurance Risk Profile")

    with st.form(key="risk_form"):
        col1, col2 = st.columns(2)

        with col1:
            vehicle_use = st.selectbox("Vehicle Use", ["personal", "commercial", "other"])
            vehicle_make_year = st.number_input("Vehicle Make Year", min_value=1953, max_value=2035, value=1953)

        with col2:
            sum_insured = st.number_input("Sum Insured", min_value=100000, value=500000)
            driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=25)

        submit = st.form_submit_button("Calculate Risk")

    if submit:
        vehicle_age = 2025 - vehicle_make_year
        risk_score, risk_label = calculate_risk_score(vehicle_use, vehicle_age, sum_insured, driver_age)

        # Map labels to colors
        label_colors = {
            "Low": "#4CAF50",             # Green
            "Low to Moderate": "#9C27B0", # Purple
            "Medium to High": "#FF9800",  # Orange
            "High": "#F44336"             # Red
        }

        # Risk Score box (blue theme)
        st.markdown(
            f"""
            <div style="background-color:#2196F3; padding:15px; border-radius:8px; margin-bottom:10px;">
                <h4 style="color:white; margin:0;">Risk Score: {risk_score:.2f}</h4>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Risk Label box (color based on risk)
        bg_color = label_colors.get(risk_label, "#555")
        st.markdown(
            f"""
            <div style="background-color:{bg_color}; padding:15px; border-radius:8px;">
                <h4 style="color:white; margin:0;">Risk Label: {risk_label}</h4>
            </div>
            """,
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    show()
