import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import plotly.express as px
import plotly.graph_objects as go

# Placeholder function to get bond data
def get_bond_data(api_key):
    url = f'https://financialmodelingprep.com/api/v3/bond/all?apikey={api_key}'
    response = requests.get(url)
    return response.json()

# Placeholder function to calculate bond duration and convexity
def calculate_duration_convexity(bond_price, coupon_rate, years_to_maturity, ytm):
    coupon = coupon_rate * bond_price
    cash_flows = [coupon / (1 + ytm) ** t for t in range(1, years_to_maturity + 1)]
    cash_flows[-1] += bond_price / (1 + ytm) ** years_to_maturity
    duration = sum(t * cf for t, cf in enumerate(cash_flows, 1)) / sum(cash_flows)
    convexity = sum(t * (t + 1) * cf for t, cf in enumerate(cash_flows, 1)) / (sum(cash_flows) * (1 + ytm) ** 2)
    return duration, convexity

# Placeholder function for yield curve data
def get_yield_curve_data():
    # Example data - in practice, fetch from an API
    return pd.DataFrame({
        'Maturity': [1, 2, 3, 5, 7, 10, 20, 30],
        'Yield': [0.5, 0.6, 0.7, 1.0, 1.2, 1.5, 2.0, 2.5]
    })

# Placeholder function to fetch market data
def fetch_market_data():
    # Example data - in practice, fetch from an API
    return pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', periods=100),
        'Interest Rate': np.random.rand(100)
    })

# Placeholder function for machine learning predictions
def predict_interest_rates(data):
    model = LinearRegression()
    X = np.arange(len(data)).reshape(-1, 1)
    y = data['Interest Rate'].values
    model.fit(X, y)
    return model.predict(X)

# Placeholder function for scenario analysis
def scenario_analysis(bond_price, coupon_rate, years_to_maturity, ytm, rate_change):
    new_ytm = ytm + rate_change
    duration, convexity = calculate_duration_convexity(bond_price, coupon_rate, years_to_maturity, new_ytm)
    return duration, convexity

# Streamlit App
st.title('Advanced Bond Analysis App')

# API Key Input
api_key = st.text_input('Enter your Financial Modeling Prep API Key')

if api_key:
    bond_data = get_bond_data(api_key)
    
    # Bond Data Display
    st.subheader('Bond Data')
    st.write(bond_data)
    
    # Example Bond Duration and Convexity Calculation
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
    yield_curve_data = get_yield_curve_data()
    fig = px.line(yield_curve_data, x='Maturity', y='Yield', title='Yield Curve')
    st.plotly_chart(fig)
    
    # Bond Portfolio Management
    st.subheader('Bond Portfolio Management')
    portfolio = pd.DataFrame({
        'Bond': ['Bond A', 'Bond B', 'Bond C'],
        'Price': [1000, 1000, 1000],
        'Coupon Rate': [0.05, 0.04, 0.03],
        'Years to Maturity': [10, 5, 20],
        'Yield to Maturity': [0.03, 0.025, 0.035]
    })
    st.write(portfolio)
    portfolio['Duration'] = portfolio.apply(
        lambda row: calculate_duration_convexity(row['Price'], row['Coupon Rate'], row['Years to Maturity'], row['Yield to Maturity'])[0],
        axis=1
    )
    portfolio['Convexity'] = portfolio.apply(
        lambda row: calculate_duration_convexity(row['Price'], row['Coupon Rate'], row['Years to Maturity'], row['Yield to Maturity'])[1],
        axis=1
    )
    st.write('Updated Portfolio with Duration and Convexity:', portfolio)
    
    # Market Data Analysis
    st.subheader('Market Data Analysis')
    market_data = fetch_market_data()
    fig = px.line(market_data, x='Date', y='Interest Rate', title='Interest Rate Over Time')
    st.plotly_chart(fig)
    
    # Machine Learning Predictions
    st.subheader('Machine Learning Predictions')
    predictions = predict_interest_rates(market_data)
    market_data['Predicted Interest Rate'] = predictions
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=market_data['Date'], y=market_data['Interest Rate'], mode='lines', name='Actual Rates'))
    fig.add_trace(go.Scatter(x=market_data['Date'], y=market_data['Predicted Interest Rate'], mode='lines', name='Predicted Rates'))
    st.plotly_chart(fig)
    
    # Scenario Analysis
    st.subheader('Scenario Analysis')
    rate_change = st.number_input('Interest Rate Change', value=0.01)
    if st.button('Run Scenario Analysis'):
        new_duration, new_convexity = scenario_analysis(bond_price, coupon_rate, years_to_maturity, ytm, rate_change)
        st.write(f'New Duration: {new_duration:.2f}')
        st.write(f'New Convexity: {new_convexity:.2f}')
    
    # Interactive Visualizations
    st.subheader('Interactive Visualizations')
    fig = px.histogram(portfolio, x='Duration', title='Duration Distribution')
    st.plotly_chart(fig)
    
    # Educational Resources
    st.subheader('Educational Resources')
    st.write('''
    - **Bond Basics:** Bonds are debt securities issued by entities such as governments and corporations.
    - **Duration:** Measures the sensitivity of a bond's price to changes in interest rates.
    - **Convexity:** Measures the sensitivity of the duration of a bond to changes in interest rates.
    - **Yield Curve:** A graph showing the relationship between bond yields and maturities.
    ''')
    
    # Custom Reports
    st.subheader('Custom Reports')
    if st.button('Generate Report'):
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
        {portfolio.to_string(index=False)}
        """
        st.download_button('Download Report', report)
    
    # User Authentication (Placeholder for actual implementation)
    st.subheader('User Authentication')
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    if st.button('Login'):
        st.write(f'Welcome, {username}!')
