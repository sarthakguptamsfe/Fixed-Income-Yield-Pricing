import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import plotly.graph_objs as go
from scipy.optimize import newton

st.set_page_config(page_title="Fixed Income: Bond Price & Yield Calculator")

# Adding the image at the top
image_url = "https://i.postimg.cc/9XRnzD6S/Screenshot-2024-05-27-at-5-20-28-PM.png"
st.image(image_url, use_column_width=True)

# Explanation of par value
st.markdown("""
**Par Value**: The amount of money that the bond issuer agrees to pay the bondholder upon maturity. 
This value is the basis on which interest (coupon payments) is calculated.
""")

# Function to calculate yield to maturity using Newton's method
def calculate_ytm(price, par, coupon_rate, n_periods, freq):
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

# Function to calculate Macaulay duration
def calculate_macaulay_duration(par, coupon_rate, ytm, n_periods, freq):
    coupon = coupon_rate / 100 * par / freq
    cash_flows = [coupon] * n_periods + [par]
    discount_factors = [(1 + ytm / (100 * freq)) ** (-i) for i in range(1, n_periods + 2)]
    present_values = [cf * df for cf, df in zip(cash_flows, discount_factors)]
    durations = [t * pv for t, pv in enumerate(present_values, start=1)]
    macaulay_duration = sum(durations) / sum(present_values)
    return macaulay_duration / freq

# Function to calculate modified duration
def calculate_modified_duration(macaulay_duration, ytm, freq):
    return macaulay_duration / (1 + ytm / (100 * freq))

# Function to calculate key rate duration
def calculate_key_rate_duration(price, par, coupon_rate, ytm, n_periods, freq):
    shock = 0.01  # 1% interest rate shock
    key_rate_durations = []

    for period in range(1, n_periods + 1):
        bumped_ytm = ytm / 100 + shock
        price_up = calculate_price(par, coupon_rate, bumped_ytm * 100, n_periods, freq)
        price_down = calculate_price(par, coupon_rate, (ytm / 100 - shock) * 100, n_periods, freq)
        
        key_rate_duration = (price_down - price_up) / (2 * price * shock)
        key_rate_durations.append(key_rate_duration)
    
    return np.mean(key_rate_durations)

# Function to calculate convexity
def calculate_convexity(price, par, coupon_rate, ytm, n_periods, freq):
    coupon = coupon_rate / 100 * par / freq
    convexity = 0
    for t in range(1, n_periods + 1):
        convexity += (coupon / (1 + ytm / freq) ** t) * (t * (t + 1))
    convexity += (par / (1 + ytm / freq) ** n_periods) * (n_periods * (n_periods + 1))
    convexity = convexity / ((price * (1 + ytm / freq) ** 2) * freq ** 2)
    return convexity / 100

# User inputs
bond_type = st.selectbox("Bond Type:", ["Corporate", "Treasury", "Municipal", "Agency/GSE", "Fixed Rate"])
price = st.number_input("Price:", min_value=0.0, value=98.5, step=0.01)
annual_coupon_rate = st.number_input("Annual Coupon Rate (%):", min_value=0.0, value=5.0, step=0.01)
coupon_frequency = st.selectbox("Coupon Frequency:", ["Annual", "Semi-Annual", "Quarterly", "Monthly/GSE"])
maturity_date = st.date_input("Maturity Date:", value=datetime.today().date() + relativedelta(years=10))
callable = False
error_message = ""
if bond_type == "Corporate":
    callable = st.checkbox("Callable")
    if callable:
        # Default call date is set to one year before maturity date
        call_date = st.date_input("Call Date:", value=maturity_date - relativedelta(years=1))
        call_price = st.number_input("Call Price:", min_value=0.0, value=100.0, step=0.01)
        if call_date >= maturity_date:
            error_message = "Error: Call date must be earlier than maturity date."

par_value = st.number_input("Par Value:", min_value=0.0, value=100.0, step=0.01)
quantity = st.number_input("Quantity:", min_value=1, value=10, step=1)
settlement_date = st.date_input("Settlement Date:", value=datetime.today().date())
total_markup = st.number_input("Total Markup:", min_value=0.0, value=0.0, step=0.01)
duration_type = st.selectbox("Duration Type:", ["Macaulay", "Modified", "Key Rate"])

# Show error message if call date is invalid
if error_message:
    st.error(error_message)

# Create columns for buttons
col1, col2, _ = st.columns([2, 1, 6])  # Adjusted column widths

# Calculate button
if col1.button("Calculate"):
    if error_message:
        st.error("Cannot calculate because of invalid call date.")
    else:
        # Calculations
        freq_dict = {"Annual": 1, "Semi-Annual": 2, "Quarterly": 4, "Monthly/GSE": 12}
        freq = freq_dict[coupon_frequency]
        n_periods = (maturity_date - settlement_date).days // (365 // freq)
        
        if n_periods <= 0:
            st.error("Error: Settlement date must be before the maturity date.")
        else:
            st.write(f"Coupon Payment: {annual_coupon_rate / 100 * par_value / freq}")
            st.write(f"Number of Periods: {n_periods}")
            
            ytm = calculate_ytm(price, par_value, annual_coupon_rate, n_periods, freq)
            ytc = None
            if callable:
                ytc = calculate_ytc(price, par_value, annual_coupon_rate, call_price, call_date, settlement_date, freq)
            
            macaulay_duration = calculate_macaulay_duration(par_value, annual_coupon_rate, ytm, n_periods, freq)
            if duration_type == "Macaulay":
                duration = macaulay_duration
            elif duration_type == "Modified":
                duration = calculate_modified_duration(macaulay_duration, ytm, freq)
            elif duration_type == "Key Rate":
                duration = calculate_key_rate_duration(price, par_value, annual_coupon_rate, ytm, n_periods, freq)
            
            convexity = calculate_convexity(price, par_value, annual_coupon_rate, ytm, n_periods, freq)
            
            accrued_interest = (datetime.now().date() - settlement_date).days / 365 * (annual_coupon_rate / 100) * par_value
            total_cost = price * quantity + total_markup

            st.write(f"Accrued Interest: ${accrued_interest:.2f}")
            st.write(f"Total Cost: ${total_cost:.2f}")
            st.write(f"Yield to Maturity (YTM): {ytm:.2f}%")
            if callable:
                st.write(f"Yield to Call (YTC): {ytc:.2f}%")
            else:
                st.write("Yield to Call (YTC): Not Applicable or Calculation Error")
            st.write(f"Macaulay Duration: {macaulay_duration:.2f} years")
            st.write(f"Convexity: {convexity:.2f}")
            
            # Plotting the graph
            prices = np.linspace(price - 10, price + 10, 50)
            ytm_values = [calculate_ytm(p, par_value, annual_coupon_rate, n_periods, freq) for p in prices]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=ytm_values, y=prices, mode='lines', name='Price vs. Yield'))
            fig.update_layout(
                xaxis_title="Yield (%)",
                yaxis_title="Price",
                legend_title="Duration"
            )
            st.plotly_chart(fig)

# Reset button
if col2.button("Reset"):
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
