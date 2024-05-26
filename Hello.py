import streamlit as st
import pandas as pd
import numpy as np
from fredapi import Fred
import plotly.express as px
import plotly.graph_objects as go

# Your FRED API key
fred_api_key = 'ccb0a6057d3c865f4e10e7ec2c99826a'

# Initialize FRED
fred = Fred(api_key=fred_api_key)

# Function to get bond data (e.g., 10-Year Treasury Constant Maturity Rate)
def get_bond_data(fred):
    series_id = 'DGS10'  # 10-Year Treasury Constant Maturity Rate
    data = fred.get_series(series_id)
    return data

# Function to calculate bond duration and convexity
def calculate_duration_convexity(bond_price, coupon_rate, years_to_maturity, ytm):
    coupon = coupon_rate * bond_price
    cash_flows = [coupon / (1 + ytm) ** t for t in range(1, years_to_maturity + 1)]
    cash_flows[-1] += bond_price / (1 + ytm) ** years_to_maturity
    duration = sum(t * cf for t, cf in enumerate(cash_flows, 1)) / sum(cash_flows)
    convexity = sum(t * (t + 1) * cf for t, cf in enumerate(cash_flows, 1)) / (sum(cash_flows) * (1 + ytm) ** 2)
    return duration, convexity

# Function to get yield curve data
def get_yield_curve_data(fred):
    series_ids = ['DGS1MO', 'DGS3MO', 'DGS6MO', 'DGS1', 'DGS2', 'DGS3', 'DGS5', 'DGS7', 'DGS10', 'DGS20', 'DGS30']
    data = {series_id: fred.get_series(series_id) for series_id in series_ids}
    yield_curve = pd.DataFrame(data)
    yield_curve['date'] = yield_curve.index
    return yield_curve

# Streamlit App
st.title('Advanced Bond Analysis App')

# Educational Resources
st.subheader('Educational Resources')
st.write('''
- **Bond Basics:** Bonds are debt securities issued by entities such as governments and corporations.
- **Duration:** Measures the sensitivity of a bond's price to changes in interest rates.
- **Convexity:** Measures the sensitivity of the duration of a bond to changes in interest rates.
- **Yield Curve:** A graph showing the relationship between bond yields and maturities.
''')

# Bond Data Display
st.subheader('Live Bond Data')
bond_data = get_bond_data(fred)
if bond_data is not None:
    st.write(bond_data)

# Bond Duration and Convexity Calculation
st.subheader('Bond Duration and Convexity Calculation')
bond_price = st.number_input('Bond Price', value=1000)
coupon_rate = st.number_input('Coupon Rate', value=0.05)
years_to_maturity = st.number_input('Years to Maturity', value=10)
ytm = st.number_input('Yield to Maturity', value=0.03)
if st.button('Calculate Duration and Convexity'):
    duration, convexity = calculate_duration_convexity(bond_price, coupon_rate, years_to_maturity, ytm)
    st.write(f'Duration: {duration:.2f}')
    st.write(f'Convexity: {convexity:.2f}')

# Yield Curve Analysis
st.subheader('Yield Curve Analysis')
yield_curve_data = get_yield_curve_data(fred)
if yield_curve_data is not None:
    fig = px.line(yield_curve_data, x='date', y=yield_curve_data.columns[:-1], title='Yield Curve')
    st.plotly_chart(fig)

# Bond Portfolio Management
st.subheader('Bond Portfolio Management')
num_bonds = st.slider('Select number of bonds (up to 10):', 1, 10, 1)

bonds = []
total_weight = 0

for i in range(num_bonds):
    st.write(f'**Bond {i+1}**')
    bond_name = st.text_input(f'Enter Bond Name {i+1}:', key=f'bond_name_{i}')
    bond_price = st.number_input(f'Enter Price for Bond {i+1}:', value=1000, key=f'bond_price_{i}')
    coupon_rate = st.number_input(f'Enter Coupon Rate for Bond {i+1}:', value=0.05, key=f'coupon_rate_{i}')
    years_to_maturity = st.number_input(f'Enter Years to Maturity for Bond {i+1}:', value=10, key=f'years_to_maturity_{i}')
    ytm = st.number_input(f'Enter Yield to Maturity for Bond {i+1}:', value=0.03, key=f'ytm_{i}')
    weight = st.number_input(f'Enter Weight for Bond {i+1} (%):', value=0.0, key=f'weight_{i}')
    bonds.append({
        'Bond Name': bond_name,
        'Price': bond_price,
        'Coupon Rate': coupon_rate,
        'Years to Maturity': years_to_maturity,
        'Yield to Maturity': ytm,
        'Weight': weight
    })
    total_weight += weight

st.write(f'Total Weight: {total_weight}%')

portfolio_value = sum([bond['Price'] * (bond['Weight'] / 100) for bond in bonds])
st.write(f'Total Portfolio Value: ${portfolio_value}')

if st.button('Calculate Portfolio Metrics'):
    for bond in bonds:
        bond['Duration'], bond['Convexity'] = calculate_duration_convexity(
            bond['Price'], bond['Coupon Rate'], bond['Years to Maturity'], bond['Yield to Maturity']
        )
    portfolio_df = pd.DataFrame(bonds)
    st.write('Portfolio Details:')
    st.write(portfolio_df)

# Scenario Analysis
st.subheader('Scenario Analysis')
rate_change = st.number_input('Interest Rate Change', value=0.01)
if st.button('Run Scenario Analysis'):
    new_duration, new_convexity = scenario_analysis(bond_price, coupon_rate, years_to_maturity, ytm, rate_change)
    st.write(f'New Duration: {new_duration:.2f}')
    st.write(f'New Convexity: {new_convexity:.2f}')

# Interactive Visualizations
st.subheader('Interactive Visualizations')
if 'portfolio_df' in locals():
    fig = px.histogram(portfolio_df, x='Duration', title='Duration Distribution')
    st.plotly_chart(fig)

# Custom Reports
st.subheader('Custom Reports')
if st.button('Generate Report'):
    if 'portfolio_df' in locals():
        report = f"""
        Bond Analysis Report
        ====================
        Bond Price: {bond_price}
        Coupon Rate: {coupon_rate}
        Years to Maturity: {years_to_maturity}
        Yield to Maturity: {ytm}
        Duration: {duration:.2f}
        Convexity: {convexity:.2f}
        
        Portfolio Analysis
        ------------------
        {portfolio_df.to_string(index=False)}
        """
        st.download_button('Download Report', data=report, file_name='bond_analysis_report.txt', mime='text/plain')
    else:
        st.error("Please calculate portfolio metrics first.")
