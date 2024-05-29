# [Fixed Income: Bond Price & Yield Calculator](https://bond-calculator.streamlit.app/)

## Overview
This interactive web application allows users to calculate bond prices and yields (Yield to Maturity and Yield to Call) and visualize their relationship. It's a useful tool for fixed income investors and financial professionals, providing real-time insights into bond valuation.

## Features
- **Yield to Maturity (YTM) Calculation**: Calculate the total return expected on a bond if held until maturity.
- **Yield to Call (YTC) Calculation**: For callable bonds, calculate the yield assuming the bond is called before its maturity date.
- **Duration and Convexity Metrics**: Provides detailed calculations of Macaulay Duration, Modified Duration, Key Rate Duration, and Convexity, including separate metrics for callable bonds.
- **Price and Yield Relationship Visualization**: Interactive chart showing how bond prices and yields relate.
- **Reset Functionality**: Reset inputs and start fresh.
- **Structured Output**: Results are presented in a clean, structured table format.
- **Detailed Explanations**: Understand key concepts related to bond prices and yields.

## Technologies
- **Streamlit**: For creating a user-friendly and interactive web interface.
- **Python**: Handles computational logic, including financial calculations.
- **NumPy**: Used for numerical operations and handling arrays.
- **SciPy**: Utilized for optimizing functions and finding roots.
- **Plotly**: For interactive and visually appealing charting.

### Key Concepts

- **Inverse Relationship**: Bond prices and yields generally move in opposite directions. When a bond's price increases, its yield decreases, and vice versa.
- **Yield to Maturity (YTM)**: This is the total return expected on a bond if held until maturity. It accounts for the bond's current market price, par value, coupon interest rate, and time to maturity.
- **Yield to Call (YTC)**: For callable bonds, this is the yield assuming the bond is called (redeemed by the issuer) before its maturity date. It considers the call price and the time until the call date.
- **Yield to Worst (YTW)**: This is the lowest yield an investor can receive if the bond is called or matures early. It is the minimum between YTM and YTC.
- **Duration**: This measures the sensitivity of the bond's price to changes in interest rates. Types of duration include Macaulay Duration, Modified Duration, and Key Rate Duration.
- **Convexity**: This measures the sensitivity of the duration of the bond to changes in interest rates. It provides an estimate of the change in duration for a change in yield.

### How to Use the Calculator

1. **Enter Bond Details**: Input the bond's price, par value, coupon rate, and other relevant details.
2. **Calculate Yields**: The calculator computes the YTM and YTC based on your inputs.
3. **Analyze the Chart**: The interactive chart shows how bond prices and yields relate. Hover over the chart to see specific bond and price information that updates dynamically.
4. **Review the Metrics**: The calculator provides key metrics such as coupon payment, number of periods, accrued interest, total cost, yield to maturity, duration, and convexity in a structured table. For callable bonds, additional metrics such as yield to call, callable duration, and callable convexity are also provided.

### Practical Insights

- **Investment Decisions**: Understanding the relationship between bond prices and yields helps in making informed investment decisions.
- **Interest Rate Movements**: Keep an eye on interest rate trends, as they significantly impact bond prices and yields.
- **Bond Characteristics**: Different bonds (corporate, municipal, treasury) have unique features and risks. Consider these when analyzing yields.

Use this calculator to explore and understand how changes in bond prices affect yields, helping you optimize your bond investment strategy.

## Contributing

We encourage contributions from the community, whether they are feature improvements, bug fixes, or documentation enhancements. Follow these steps to contribute:

1. **Fork the Repository**: Fork the project to your GitHub account.
2. **Clone Your Fork**: Download your fork to your computer.
3. **Create a New Branch**: Switch to a new branch for your changes.
4. **Make Changes**: Implement your changes or improvements.
5. **Commit Your Changes**: Save your changes with a clear commit message.
6. **Push to GitHub**: Upload the changes to your fork.
7. **Submit a Pull Request**: Open a pull request from your branch to the main project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, raise an issue on the GitHub repository. We aim to address issues promptly and help resolve any challenges users may face.

Thank you for using or contributing to the Fixed Income: Bond Price & Yield Calculator application!

# [Link to App](https://bond-calculator.streamlit.app/)
