import streamlit as st
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
import requests
from scipy.optimize import minimize

# Helper function to fetch bond data from Financial Prep Data API
def get_bond_data(api_key):
    url = f"https://financialmodelingprep.com/api/v3/treasury?apikey={api_key}"
    response = requests.get(url)
    return response.json()

# Helper functions for bond calculations
def bond_price(face_value, coupon_rate, periods, market_rate):
    coupon = face_value * coupon_rate
    price = sum([coupon / (1 + market_rate) ** t for t in range(1, periods + 1)])
    price += face_value / (1 + market_rate) ** periods
    return price

def bond_duration(face_value, coupon_rate, periods, market_rate):
    coupon = face_value * coupon_rate
    duration = sum([t * (coupon / (1 + market_rate) ** t) for t in range(1, periods + 1)])
    duration += periods * (face_value / (1 + market_rate) ** periods)
    price = bond_price(face_value, coupon_rate, periods, market_rate)
    return duration / price

def run_scenario_analysis(bonds, rates):
    results = []
    for rate in rates:
        portfolio_value = sum([bond_price(bond['face_value'], bond['coupon_rate'], bond['periods'], rate) for bond in bonds])
        results.append({'rate': rate, 'value': portfolio_value})
    return pd.DataFrame(results)

# Helper function to predict interest rates using ARIMA model
def predict_interest_rates(data, periods=10):
    model = ARIMA(data, order=(5, 1, 0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=periods)
    return forecast

# Optimization function for portfolio rebalancing
def optimize_portfolio(initial_allocations, target_duration, bonds):
    def objective(weights):
        portfolio_duration = sum([weights[i] * bond_duration(**bond) for i, bond in enumerate(bonds)])
        return abs(portfolio_duration - target_duration)

    constraints = (
        {'type': 'eq', 'fun': lambda weights: sum(weights) - 1},
    )
    bounds = [(0, 1) for _ in initial_allocations]
    result = minimize(objective, initial_allocations, constraints=constraints, bounds=bounds)
    return result.x

# Automated rebalancing
def rebalance_portfolio(portfolio, target_duration, threshold=0.1):
    current_duration = sum([bond_duration(bond['face_value'], bond['coupon_rate'], bond['periods'], bond['market_rate']) for bond in portfolio])
    if abs(current_duration - target_duration) > threshold:
        initial_allocations = [bond['weight'] for bond in portfolio]
        optimized_allocations = optimize_portfolio(initial_allocations, target_duration, portfolio)
        for i, bond in enumerate(portfolio):
            bond['weight'] = optimized_allocations[i]
    return portfolio

# Streamlit App
st.title("Fixed Income Portfolio Management")

# Input API Key
api_key = st.text_input("Enter your API Key")
if api_key:
    bond_data = get_bond_data(api_key)
    st.write(bond_data)

    # Sample data for interest rate prediction
    interest_rate_data = pd.Series([2.5, 2.7, 2.9, 3.0, 3.2, 3.1, 3.3, 3.5, 3.6, 3.8])
    
    # Predict next 10 periods
    predicted_rates = predict_interest_rates(interest_rate_data)
    
    # Plotting the predicted interest rates
    plt.figure(figsize=(10, 5))
    plt.plot(predicted_rates, marker='o', linestyle='--', color='r')
    plt.title('Predicted Interest Rates')
    plt.xlabel('Periods')
    plt.ylabel('Interest Rate')
    st.pyplot(plt)

    # Scenario Analysis
    st.header("Scenario Analysis")
    
    # Example bond data
    bonds = [{'face_value': 1000, 'coupon_rate': 0.05, 'periods': 10, 'market_rate': 0.03, 'weight': 0.5},
             {'face_value': 1000, 'coupon_rate': 0.04, 'periods': 5, 'market_rate': 0.03, 'weight': 0.5}]

    # User inputs for scenarios
    rate_scenarios = st.slider("Interest Rate Scenarios", 0.01, 0.10, (0.02, 0.04, 0.06, 0.08))
    
    # Run scenario analysis
    scenario_results = run_scenario_analysis(bonds, rate_scenarios)
    st.write(scenario_results)

    # Automated Rebalancing
    st.header("Automated Rebalancing")
    target_duration = st.number_input("Target Portfolio Duration", value=1.0)
    rebalanced_portfolio = rebalance_portfolio(bonds, target_duration)
    st.write(rebalanced_portfolio)


