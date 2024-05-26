import streamlit as st
import pandas as pd
import numpy as np
from fredapi import Fred
import plotly.express as px

# Your FRED API key
fred_api_key = 'ccb0a6057d3c865f4e10e7ec2c99826a'

# Initialize FRED
fred = Fred(api_key=fred_api_key)

# Function to get bond data
def get_bond_data(series_id, start_date, end_date):
    try:
        data = fred.get_series(series_id, start_date, end_date)
        return data
    except Exception as e:
        st.error(f"Error fetching data for series ID {series_id}: {e}")
        return None

# Function to calculate bond duration and convexity
def calculate_duration_convexity(bond_price, coupon_rate, years_to_maturity, ytm):
    coupon = coupon_rate * bond_price
    cash_flows = [coupon / (1 + ytm) ** t for t in range(1, years_to_maturity + 1)]
    cash_flows[-1] += bond_price / (1 + ytm) ** years_to_maturity
    duration = sum(t * cf for t, cf in enumerate(cash_flows, 1)) / sum(cash_flows)
    convexity = sum(t * (t + 1) * cf for t, cf in enumerate(cash_flows, 1)) / (sum(cash_flows) * (1 + ytm) ** 2)
    return duration, convexity

# Function to fetch spot rates
def get_spot_rates():
    try:
        spot_rate_series_ids = ['DGS1MO', 'DGS3MO', 'DGS6MO', 'DGS1', 'DGS2', 'DGS3', 'DGS5', 'DGS7', 'DGS10', 'DGS20', 'DGS30']
        spot_rates = {series_id: fred.get_series(series_id).iloc[-1] for series_id in spot_rate_series_ids}
        return spot_rates
    except Exception as e:
        st.error(f"Error fetching spot rates: {e}")
        return None

# Function to value bonds using spot rates
def value_bond_using_spot_rate(cash_flows, spot_rates):
    pv = 0
    for t, cf in enumerate(cash_flows, 1):
        spot_rate = spot_rates.get(f'DGS{t}', spot_rates.get('DGS10'))
        pv += cf / (1 + spot_rate) ** t
    return pv

# Streamlit App
st.title('Advanced Bond Analysis App')

# Bond Portfolio Management
st.subheader('Bond Portfolio Management')
num_bonds = st.slider('Select number of bonds (up to 10):', 1, 10, 1)

bonds = []

for i in range(num_bonds):
    st.write(f'**Bond {i+1}**')
    bond_name = st.text_input(f'Enter Bond Name {i+1} (Series ID):', key=f'bond_name_{i}')
    purchase_date = st.date_input(f'Enter Purchase Date for Bond {i+1}:', key=f'purchase_date_{i}')
    maturity_date = st.date_input(f'Enter Maturity Date for Bond {i+1}:', key=f'maturity_date_{i}')
    coupon_rate = st.number_input(f'Enter Coupon Rate for Bond {i+1}:', value=0.05, key=f'coupon_rate_{i}')
    bonds.append({
        'Bond Name': bond_name,
        'Purchase Date': purchase_date,
        'Maturity Date': maturity_date,
        'Coupon Rate': coupon_rate
    })

# Fetch Spot Rates
spot_rates = get_spot_rates()

# Calculate Metrics and Value Bonds
portfolio_value = 0
portfolio_duration = 0
portfolio_convexity = 0

for bond in bonds:
    bond_data = get_bond_data(bond['Bond Name'], bond['Purchase Date'], bond['Maturity Date'])
    if bond_data is not None:
        bond_price = bond_data.iloc[-1]
        years_to_maturity = (bond['Maturity Date'] - bond['Purchase Date']).days / 365
        ytm = bond_data.mean()
        duration, convexity = calculate_duration_convexity(bond_price, bond['Coupon Rate'], int(years_to_maturity), ytm)
        cash_flows = [bond['Coupon Rate'] * bond_price for _ in range(int(years_to_maturity))]
        cash_flows[-1] += bond_price
        bond_value = value_bond_using_spot_rate(cash_flows, spot_rates)
        portfolio_value += bond_value
        portfolio_duration += duration
        portfolio_convexity += convexity
        bond.update({'Duration': duration, 'Convexity': convexity, 'Value': bond_value})

# Display Portfolio Metrics
st.write(f'Total Portfolio Value: ${portfolio_value:.2f}')
st.write(f'Total Portfolio Duration: {portfolio_duration:.2f}')
st.write(f'Total Portfolio Convexity: {portfolio_convexity:.2f}')

# Interactive Visualizations
st.subheader('Interactive Visualizations')
portfolio_df = pd.DataFrame(bonds)
fig = px.bar(portfolio_df, x='Bond Name', y='Value', title='Bond Values')
st.plotly_chart(fig)
fig = px.histogram(portfolio_df, x='Duration', title='Duration Distribution')
st.plotly_chart(fig)

# Custom Reports
st.subheader('Custom Reports')
if st.button('Generate Report'):
    report = f"""
    Bond Analysis Report
    ====================
    Total Portfolio Value: ${portfolio_value:.2f}
    Total Portfolio Duration: {portfolio_duration:.2f}
    Total Portfolio Convexity: {portfolio_convexity:.2f}
    
    Bond Details
    ------------
    {portfolio_df.to_string(index=False)}
    """
    st.download_button('Download Report', data=report, file_name='bond_analysis_report.txt', mime='text/plain')
