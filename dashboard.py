import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def show():
    # Example data for motor insurance dashboard
    data_premium = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
        "Total Premium": [12000, 13500, 14000, 15500, 16800, 15000, 16000],
        "Claims Paid": [3000, 3500, 2800, 5000, 4200, 4600, 3900]
    })

    risk_profile = {
        "Low Risk": 45,
        "Medium Risk": 35,
        "High Risk": 20
    }

    premium_distribution = {
        "Comprehensive": 55,
        "Third-Party": 35,
        "Third-Party Fire & Theft": 10
    }

    premium_rate_by_age = {
        "18-25": 1800,
        "26-35": 1500,
        "36-50": 1200,
        "51+": 1000
    }

    # Dashboard title
    st.title("🚗 Motor Insurance Dashboard")

    # Top KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Premium", "$1,350", delta="+5%")
    col2.metric("Total Policies", "2,450", delta="+3%")
    col3.metric("Claims Ratio", "28%", delta="-2%")
    col4.metric("Loss Ratio", "35%", delta="+1%")

    # Premium vs Claims trend
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=data_premium["Month"], y=data_premium["Total Premium"],
        mode='lines+markers', name='Total Premium'
    ))
    fig1.add_trace(go.Scatter(
        x=data_premium["Month"], y=data_premium["Claims Paid"],
        mode='lines+markers', name='Claims Paid'
    ))
    fig1.update_layout(title="Monthly Premium vs Claims Paid", template="plotly_dark")
    st.plotly_chart(fig1, use_container_width=True)

    # Two columns for pie charts
    col1, col2 = st.columns(2)

    # Risk profile pie chart
    fig2 = px.pie(
        names=list(risk_profile.keys()),
        values=list(risk_profile.values()),
        title="Risk Profile Distribution",
        template="plotly_dark",
        color_discrete_sequence=px.colors.sequential.Blues
    )
    col1.plotly_chart(fig2, use_container_width=True)

    # Premium type distribution
    fig3 = px.pie(
        names=list(premium_distribution.keys()),
        values=list(premium_distribution.values()),
        title="Premium Type Distribution",
        template="plotly_dark",
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    col2.plotly_chart(fig3, use_container_width=True)

    # Bar chart: Premium rate by age group
    fig4 = px.bar(
        x=list(premium_rate_by_age.keys()),
        y=list(premium_rate_by_age.values()),
        title="Average Premium Rate by Age Group",
        template="plotly_dark",
        labels={"x": "Age Group", "y": "Premium Rate ($)"}
    )
    st.plotly_chart(fig4, use_container_width=True)


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    show()
