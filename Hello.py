import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import plotly.graph_objs as go
from scipy.optimize import newton

# Adding the image at the top
image_url = "https://i.postimg.cc/6qXZCSmP/Screenshot-2024-05-27-at-4-54-01-PM.png"
st.image(image_url, use_column_width=True)

# Function to calculate yield to maturity using Newton's method
def calculate_ytm(price, par,coupon_rate, n_periods, freq):
    coupon = coupon_rate / 100 * par / freq
    guess = 0.05  # initial guess for YTM
    def bond_price(ytm):
        return sum([coupon / (1 + ytm / freq) ** t for t in range(1, n_periods + 1)]) + par / (1 + ytm / freq) ** n_periods

    def ytm_function(ytm):
        return price - bond_price(ytm)
    
    ytm = newton(ytm_function, guess)
    return ytm * 100 * freq

# Function to calculate yield to call using Newton's method
def calculate_ytc(price, par, coupon_rate, call_price, call_date, settlement_date, freq):
    coupon = coupon_rate / 100 * par / freq
    n_periods_call = (call_date - settlement_date).days // (365 // freq)
    guess = 0.05  # initial guess for YTC
    
    def bond_price(ytc):
        return sum([coupon / (1 + ytc / freq) ** t for t in range(1, n_periods_call + 1)]) + call_price / (1 + ytc / freq) ** n_periods_call

    def ytc_function(ytc):
        return price - bond_price(ytc)
    
    ytc = newton(ytc_function, guess)
    return ytc * 100 * freq

# Function to calculate bond price from yield to maturity
def calculate_price(par, coupon_rate, ytm, n_periods, freq):
    coupon = coupon_rate / 100 * par / freq
    cash_flows = [coupon] * n_periods + [par]
    discount_factors = [(1 + ytm / (100 * freq)) ** (-i) for i in range(1, n_periods + 2)]
    price = sum(cf * df for cf, df in zip(cash_flows, discount_factors))
    return price

# User inputs
bond_type = st.selectbox("Bond Type:", ["Corporate", "Municipal", "Treasury", "Agency/GSE", "Fixed Rate"])
price = st.number_input("Price:", min_value=0.0, value=98.5, step=0.01)
annual_coupon_rate = st.number_input("Annual Coupon Rate (%):", min_value=0.0, value=5.0, step=0.01)
coupon_frequency = st.selectbox("Coupon Frequency:", ["Annual", "Semi-Annual", "Quarterly", "Monthly/GSE"])
maturity_date = st.date_input("Maturity Date:", value=datetime.today().date() + relativedelta(years=10))
callable = False
if bond_type == "Corporate":
    callable = st.checkbox("Callable")
    if callable:
        call_date = st.date_input("Call Date:", value=datetime.today().date() + relativedelta(years=5))
        call_price = st.number_input("Call Price:", min_value=0.0, value=100.0, step=0.01)
par_value = st.number_input("Par Value:", min_value=0.0, value=100.0, step=0.01)
quantity = st.number_input("Quantity:", min_value=1, value=10, step=1)
settlement_date = st.date_input("Settlement Date:", value=datetime.today().date())
total_markup = st.number_input("Total Markup:", min_value=0.0, value=0.0, step=0.01)

# Calculate button
if st.button("Calculate"):
    # Calculations
    freq_dict = {"Annual": 1, "Semi-Annual": 2, "Quarterly": 4, "Monthly/GSE": 12}
    freq = freq_dict[coupon_frequency]
    n_periods = (maturity_date - settlement_date).days // (365 // freq)
    
    st.write(f"Coupon Payment: {annual_coupon_rate / 100 * par_value / freq}")
    st.write(f"Number of Periods: {n_periods}")
    
    ytm = calculate_ytm(price, par_value, annual_coupon_rate, n_periods, freq)
    ytc = None
    if callable:
        ytc = calculate_ytc(price, par_value, annual_coupon_rate, call_price, call_date, settlement_date, freq)
    
    accrued_interest = (datetime.now().date() - settlement_date).days / 365 * (annual_coupon_rate / 100) * par_value
    total_cost = price * quantity + total_markup

    st.write(f"**Accrued Interest:** ${accrued_interest:.2f}")
    st.write(f"**Total Cost:** ${total_cost:.2f}")
    if ytm is not None:
        st.write(f"**Yield to Maturity (YTM):** {ytm:.2f}%")
    else:
        st.write("**Yield to Maturity (YTM): Calculation Error**")
    if ytc is not None:
        st.write(f"**Yield to Call (YTC):** {ytc:.2f}%")
    else:
        st.write("**Yield to Call (YTC): Not Applicable or Calculation Error**")
    
    # Yield curve plotting
    prices = np.linspace(price - 10, price + 10, 50)
    ytm_values = [calculate_ytm(p, par_value, annual_coupon_rate, n_periods, freq) for p in prices]
    ytc_values = [calculate_ytc(p, par_value, annual_coupon_rate, call_price, call_date, settlement_date, freq) for p in prices] if callable else None

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=prices, y=ytm_values, mode='lines', name='Yield to Maturity'))
    if ytc_values is not None:
        fig.add_trace(go.Scatter(x=prices, y=ytc_values, mode='lines', name='Yield to Call', line=dict(dash='dash')))
    fig.update_layout(
        title="Yield Curve",
        xaxis_title="Price",
        yaxis_title="Yield %",
        legend_title="Yields"
    )
    st.plotly_chart(fig)

# Reset button
if st.button("Reset"):
    st.experimental_rerun()

# About section
st.markdown("""
### Understanding Bond Prices and Yields:

The relationship between bond prices and yields is fundamental to bond investing. Here's a closer look at how they interact:

#### Key Concepts:

- **Inverse Relationship**: Bond prices and yields generally move in opposite directions. When a bond's price increases, its yield decreases, and vice versa.
- **Yield to Maturity (YTM)**: This is the total return expected on a bond if held until maturity. It accounts for the bond's current market price, par value, coupon interest rate, and time to maturity.
- **Yield to Call (YTC)**: For callable bonds, this is the yield assuming the bond is called (redeemed by the issuer) before its maturity date. It considers the call price and the time until the call date.
- **Yield to Worst (YTW)**: This is the lowest yield an investor can receive if the bond is called or matures early. It is the minimum between YTM and YTC.

#### How to Use the Calculator:

1. **Enter Bond Details**: Input the bond's price, par value, coupon rate, and other relevant details.
2. **Calculate Yields**: The calculator computes the YTM and YTC based on your inputs.
3. **Analyze the Chart**: The interactive chart shows how bond prices and yields relate. Hover over the chart to see specific bond and price information that updates dynamically.

#### Practical Insights:

- **Investment Decisions**: Understanding the relationship between bond prices and yields helps in making informed investment decisions.
- **Interest Rate Movements**: Keep an eye on interest rate trends, as they significantly impact bond prices and yields.
- **Bond Characteristics**: Different bonds (corporate, municipal, treasury) have unique features and risks. Consider these when analyzing yields.

Use this calculator to explore and understand how changes in bond prices affect yields, helping you optimize your bond investment strategy.
""")

