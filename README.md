
# Olist E-Commerce Analytics Project

## Project Overview
This project analyzes the Olist Brazilian E-Commerce dataset to identify business insights related to sales performance, customer behavior, product categories, sellers, delivery performance, payments, and customer satisfaction.

The project combines SQL, Python, Power BI, Machine Learning, and Streamlit to provide an end-to-end data analytics solution.

## Business Objectives
- Analyze sales and revenue trends.
- Understand customer purchasing behavior.
- Identify top-performing products, categories, and sellers.
- Evaluate delivery performance and customer satisfaction.
- Develop a predictive model for customer review scores.
- Present business insights through interactive dashboards.

## Tools and Technologies
- SQL Server – Data auditing and cleaning
- Python – Exploratory Data Analysis and Machine Learning
- Power BI – Interactive business dashboards
- Streamlit – Web application development
- GitHub – Project version control

## Dataset
The project uses nine Olist E-Commerce tables:

1. Orders
2. Order Items
3. Customers
4. Products
5. Sellers
6. Order Payments
7. Order Reviews
8. Geolocation
9. Product Category Name Translation

## Project Workflow
1. Data understanding and auditing
2. Data cleaning using SQL
3. Exploratory Data Analysis using Python
4. Power BI dashboard development
5. Customer review score prediction
6. Streamlit web application development
7. Deployment using Streamlit Community Cloud

## Predictive Model
The machine learning component predicts customer review scores from 1 to 5.

The deployed application uses a trained Logistic Regression classification model.

### Input Features
- Order Value
- Freight Value
- Total Items
- Delivery Days

### Output
- Predicted Customer Review Score (1–5)
- Customer Satisfaction Interpretation

## Streamlit Web Application
The deployed web application includes:

- Login and Logout
- Overview Dashboard
- Sales Dashboard
- Customer Dashboard
- Product Dashboard
- Seller Dashboard
- Delivery Dashboard
- Payment Dashboard
- Review Dashboard
- Data Explorer
- Customer Review Score Prediction

## Running the Application Locally

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Configure login credentials in `.streamlit/secrets.toml`:

```toml
[login]
username = "your_username"
password = "your_password"
```

Run the application:

```bash
streamlit run app.py
```

**Security Note:** Login credentials are not included in the GitHub repository. They must be configured separately using Streamlit secrets.

## Project Deliverables
- SQL data auditing and cleaning
- Python EDA and machine learning
- Power BI dashboards
- Predictive model
- Deployed Streamlit web application
- Final project presentation

## Conclusion
This project demonstrates an end-to-end data analytics workflow, converting raw e-commerce data into actionable business insights and a deployed predictive analytics application.
