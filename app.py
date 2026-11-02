import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import joblib
from pathlib import Path
import hmac

st.set_page_config(
    page_title="Olist E-Commerce Analytics",
    page_icon="🛒",
    layout="wide"
)


# ==========================================
# LOGIN AUTHENTICATION
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():

    st.title("Olist E-Commerce Analytics")
    st.subheader("User Login")

    with st.form("login_form"):

        username = st.text_input("User ID")

        password = st.text_input(
            "Password",
            type="password"
        )

        login_button = st.form_submit_button("Login")

    if login_button:

        correct_username = st.secrets["login"]["username"]
        correct_password = st.secrets["login"]["password"]

        valid_username = hmac.compare_digest(
            username, correct_username
        )

        valid_password = hmac.compare_digest(
            password, correct_password
        )

        if valid_username and valid_password:

            st.session_state.logged_in = True
            st.rerun()

        else:
            st.error("Invalid User ID or Password")


if not st.session_state.logged_in:
    login()
    st.stop()


# Logout button
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()


st.title("Olist E-Commerce Analytics Dashboard")

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Dashboard",
    [
        "Data Explorer",
        "Overview",
        "Sales",
        "Customers",
        "Products",
        "Sellers",
        "Delivery",
        "Payments",
        "Reviews",
        "Prediction"
    ]
)

st.write("Selected Page:", page)
# Load all 9 datasets
DATA_DIR = Path(__file__).parent / "data"

@st.cache_data
def load_data():
    table_names = [
        "orders",
        "order_items",
        "products",
        "customers",
        "sellers",
        "order_payments",
        "order_reviews",
        "geolocation",
        "product_category_name_translation"
    ]

    datasets = {}

    for name in table_names:
        file_path = DATA_DIR / f"{name}.csv"
        datasets[name] = pd.read_csv(file_path)

    return datasets

tables = load_data()


# ==========================================
# DATA EXPLORER
# ==========================================

if page == "Data Explorer":

    st.header("Data Explorer")
    st.write("Explore the 9 Olist E-Commerce datasets.")

    # Select a dataset
    selected_table = st.selectbox(
        "Select Dataset",
        list(tables.keys())
    )

    df = tables[selected_table]

    # Dataset overview
    st.subheader("Dataset Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Rows", f"{df.shape[0]:,}")

    with col2:
        st.metric("Total Columns", df.shape[1])

    with col3:
        st.metric("Missing Values", f"{df.isnull().sum().sum():,}")

    # Preview data
    st.subheader("Data Preview")

    preview_rows = st.slider(
        "Number of rows to display",
        min_value=5,
        max_value=100,
        value=10
    )

    st.dataframe(
        df.head(preview_rows),
        use_container_width=True
    )

    # Column information
    st.subheader("Column Information")

    column_info = pd.DataFrame({
        "Column Name": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Missing Values": df.isnull().sum().values,
        "Missing %": (
            df.isnull().mean().values * 100
        ).round(2)
    })

    st.dataframe(
        column_info,
        use_container_width=True
    )

    # Download selected dataset
    st.subheader("Download Dataset")

    st.download_button(
        label="Download CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=f"{selected_table}.csv",
        mime="text/csv"
    )

# ==========================================
# OVERVIEW DASHBOARD
# ==========================================

if page == "Overview":

    st.header("Business Overview")
    st.write("Key performance indicators for Olist E-Commerce.")

    # Load required datasets
    orders = tables["orders"].copy()
    customers = tables["customers"].copy()
    order_items = tables["order_items"].copy()
    reviews = tables["order_reviews"].copy()

    # Calculate KPIs
    total_orders = orders["order_id"].nunique()
    total_customers = customers["customer_unique_id"].nunique()

    order_items["price"] = pd.to_numeric(
        order_items["price"], errors="coerce"
    )

    total_revenue = order_items["price"].sum()
    avg_order_value = total_revenue / total_orders

    avg_review_score = pd.to_numeric(
        reviews["review_score"], errors="coerce"
    ).mean()

    # Display KPIs
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Orders", f"{total_orders:,}")

    with col2:
        st.metric("Unique Customers", f"{total_customers:,}")

    with col3:
        st.metric("Total Product Revenue", f"R$ {total_revenue/1_000_000:,.2f}M")

    col4, col5 = st.columns(2)

    with col4:
        st.metric("Average Order Value", f"R$ {avg_order_value:,.2f}")

    with col5:
        st.metric("Average Review Score", f"{avg_review_score:.2f} / 5")

    st.divider()

    # Order Status Distribution
    st.subheader("Order Status Distribution")

    status_counts = orders["order_status"].value_counts()
    st.bar_chart(status_counts)

    # Monthly Orders Trend
    st.subheader("Monthly Orders Trend")

    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"], errors="coerce"
    )

    monthly_orders = (
        orders.dropna(subset=["order_purchase_timestamp"])
        .set_index("order_purchase_timestamp")
        .resample("MS")["order_id"]
        .nunique()
    )

    st.line_chart(monthly_orders)

# ==========================================
# SALES DASHBOARD
# ==========================================

if page == "Sales":

    st.header("Sales Performance Dashboard")
    st.write("Revenue trends, product performance and regional sales.")

    # Load datasets
    sales_orders = tables["orders"].copy()
    sales_items = tables["order_items"].copy()
    sales_products = tables["products"].copy()
    sales_customers = tables["customers"].copy()
    sales_categories = tables["product_category_name_translation"].copy()

    # Prepare data
    sales_items["price"] = pd.to_numeric(
        sales_items["price"], errors="coerce"
    )

    sales_orders["order_purchase_timestamp"] = pd.to_datetime(
        sales_orders["order_purchase_timestamp"], errors="coerce"
    )

    # Join tables at order-item level
    sales = sales_items.merge(
        sales_orders[
            ["order_id", "customer_id", "order_purchase_timestamp"]
        ],
        on="order_id",
        how="left",
        validate="many_to_one"
    )

    sales = sales.merge(
        sales_products[["product_id", "product_category_name"]],
        on="product_id",
        how="left",
        validate="many_to_one"
    )

    sales = sales.merge(
        sales_customers[["customer_id", "customer_state"]],
        on="customer_id",
        how="left",
        validate="many_to_one"
    )

    sales = sales.merge(
        sales_categories,
        on="product_category_name",
        how="left",
        validate="many_to_one"
    )

    # KPIs
    total_sales = sales["price"].sum()
    total_sales_orders = sales["order_id"].nunique()
    total_items = len(sales)

    avg_sales_order = (
        total_sales / total_sales_orders
        if total_sales_orders > 0 else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Revenue", f"R$ {total_sales/1_000_000:,.2f}M")

    with col2:
        st.metric("Orders with Items", f"{total_sales_orders:,}")

    with col3:
        st.metric("Items Sold", f"{total_items:,}")

    with col4:
        st.metric("Average Sales per Order", f"R$ {avg_sales_order:,.2f}")

    st.divider()

    # Monthly revenue
    st.subheader("Monthly Revenue Trend")

    monthly_sales = (
        sales.dropna(subset=["order_purchase_timestamp"])
        .set_index("order_purchase_timestamp")
        .resample("MS")["price"]
        .sum()
    )

    st.line_chart(monthly_sales)

    # Top categories
    st.subheader("Top 10 Product Categories by Revenue")

    category_sales = (
        sales.groupby("product_category_name_english",
                      dropna=False)["price"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    st.bar_chart(category_sales)

    # Top products
    st.subheader("Top 10 Products by Revenue")

    product_sales = (
        sales.groupby("product_id")["price"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    st.bar_chart(product_sales)

    # Regional sales
    st.subheader("Revenue by Customer State")

    state_sales = (
        sales.groupby("customer_state")["price"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(state_sales)

    st.caption(
        "Revenue represents product item prices, excluding freight. "
        "Regional revenue is attributed to the customer's state."
    )

# ==========================================
# CUSTOMERS DASHBOARD
# ==========================================

if page == "Customers":

    st.header("Customer Analytics Dashboard")
    st.write("Customer distribution, retention and purchase behavior.")

    # Load required datasets
    cust = tables["customers"].copy()
    cust_orders = tables["orders"].copy()

    # Customer KPIs
    total_customer_records = len(cust)
    unique_customers = cust["customer_unique_id"].nunique()
    total_states = cust["customer_state"].nunique()
    total_cities = cust["customer_city"].nunique()

    # Calculate repeat customers using completed order history
    customer_orders = cust_orders[
        ["order_id", "customer_id"]
    ].merge(
        cust[["customer_id", "customer_unique_id"]],
        on="customer_id",
        how="inner",
        validate="many_to_one"
    )

    purchase_counts = (
        customer_orders.groupby("customer_unique_id")["order_id"]
        .nunique()
    )

    repeat_customers = (purchase_counts > 1).sum()
    repeat_rate = (
        repeat_customers / len(purchase_counts) * 100
        if len(purchase_counts) > 0 else 0
    )

    # KPI cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Unique Customers", f"{unique_customers:,}")

    with col2:
        st.metric("Repeat Customers", f"{repeat_customers:,}")

    with col3:
        st.metric("Repeat Customer Rate", f"{repeat_rate:.2f}%")

    col4, col5 = st.columns(2)

    with col4:
        st.metric("Customer States", total_states)

    with col5:
        st.metric("Customer Cities", f"{total_cities:,}")

    st.divider()

    # Customers by state
    st.subheader("Top 10 States by Unique Customers")

    state_customers = (
        cust.groupby("customer_state")["customer_unique_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(10)
    )

    st.bar_chart(state_customers)

    # Customers by city
    st.subheader("Top 10 Cities by Unique Customers")

    city_customers = (
        cust.groupby(["customer_state", "customer_city"])[
            "customer_unique_id"
        ]
        .nunique()
        .sort_values(ascending=False)
        .head(10)
    )

    city_customers.index = [
        f"{city}, {state}"
        for state, city in city_customers.index
    ]

    st.bar_chart(city_customers)

    # Customer purchase frequency
    st.subheader("Customer Purchase Frequency")

    frequency = (
        purchase_counts.value_counts()
        .sort_index()
        .rename_axis("Number of Orders")
        .rename("Customers")
    )

    st.bar_chart(frequency)

    # New vs repeat customers
    st.subheader("One-Time vs Repeat Customers")

    one_time = (purchase_counts == 1).sum()

    customer_segments = pd.DataFrame({
        "Customer Type": ["One-Time", "Repeat"],
        "Customers": [one_time, repeat_customers]
    })

    st.bar_chart(
        customer_segments.set_index("Customer Type")
    )

    st.caption(
        "Repeat customers are identified using customer_unique_id "
        "with more than one distinct order."
    )
# ==========================================
# PRODUCTS ANALYTICS DASHBOARD
# ==========================================

if page == "Products":

    st.header("Products Analytics Dashboard")
    st.write("Product performance, category distribution and pricing analysis.")

    products = tables["products"]
    order_items = tables["order_items"]

    # Merge product and order item information
    product_sales = order_items.merge(
        products,
        on="product_id",
        how="left"
    )

    # KPI Section
    total_products = products["product_id"].nunique()
    total_categories = products["product_category_name"].nunique()
    total_items_sold = len(order_items)
    average_price = order_items["price"].mean()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Products", f"{total_products:,}")

    with col2:
        st.metric("Product Categories", f"{total_categories:,}")

    with col3:
        st.metric("Items Sold", f"{total_items_sold:,}")

    with col4:
        st.metric("Average Product Price", f"R$ {average_price:,.2f}")

    st.divider()

    # Top categories by revenue
    st.subheader("Top 10 Categories by Revenue")

    category_revenue = (
        product_sales.groupby("product_category_name")["price"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    st.bar_chart(category_revenue)

    # Top categories by items sold
    st.subheader("Top 10 Categories by Items Sold")

    category_items = (
        product_sales.groupby("product_category_name")
        .size()
        .sort_values(ascending=False)
        .head(10)
    )

    st.bar_chart(category_items)

    # Product price distribution
    st.subheader("Product Price Distribution")

    price_bins = pd.cut(
        order_items["price"],
        bins=[0, 50, 100, 200, 500, float("inf")],
        labels=["0-50", "50-100", "100-200", "200-500", "500+"],
        include_lowest=True
    )

    price_distribution = (
        price_bins.value_counts()
        .reindex(["0-50", "50-100", "100-200", "200-500", "500+"])
    )

    st.bar_chart(price_distribution)

    # Top products by sales revenue
    st.subheader("Top 10 Products by Revenue")

    top_products = (
        order_items.groupby("product_id")["price"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    top_products.columns = ["Product ID", "Revenue (R$)"]

    st.dataframe(
        top_products,
        use_container_width=True,
        hide_index=True
    )

# ==========================================
# SELLERS ANALYTICS DASHBOARD
# ==========================================

if page == "Sellers":

    st.header("Sellers Analytics Dashboard")
    st.write("Seller performance, revenue contribution and geographical distribution.")

    # Load datasets
    sellers_df = tables["sellers"].copy()
    items_df = tables["order_items"].copy()

    # Ensure price is numeric
    items_df["price"] = pd.to_numeric(
        items_df["price"], errors="coerce"
    )

    # Merge order items with sellers
    seller_sales = items_df.merge(
        sellers_df[
            ["seller_id", "seller_state", "seller_city"]
        ],
        on="seller_id",
        how="left",
        validate="many_to_one"
    )

    # Calculate KPIs
    total_sellers = sellers_df["seller_id"].nunique()
    active_sellers = items_df["seller_id"].nunique()
    total_seller_revenue = items_df["price"].sum()
    average_revenue_per_seller = (
        total_seller_revenue / active_sellers
        if active_sellers > 0 else 0
    )

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Sellers", f"{total_sellers:,}")

    with col2:
        st.metric("Active Sellers", f"{active_sellers:,}")

    with col3:
        st.metric(
            "Total Seller Revenue",
            f"R$ {total_seller_revenue / 1_000_000:,.2f}M"
        )

    with col4:
        st.metric(
            "Avg Revenue per Seller",
            f"R$ {average_revenue_per_seller:,.2f}"
        )

    st.divider()

    # Top sellers by revenue
    st.subheader("Top 10 Sellers by Revenue")

    top_sellers_revenue = (
        seller_sales.groupby("seller_id")["price"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    st.bar_chart(top_sellers_revenue)

    # Top sellers by items sold
    st.subheader("Top 10 Sellers by Items Sold")

    top_sellers_items = (
        seller_sales.groupby("seller_id")
        .size()
        .sort_values(ascending=False)
        .head(10)
    )

    st.bar_chart(top_sellers_items)

    # Seller revenue by state
    st.subheader("Top 10 Seller States by Revenue")

    seller_state_revenue = (
        seller_sales.groupby("seller_state")["price"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    st.bar_chart(seller_state_revenue)

    # Seller distribution by state
    st.subheader("Top 10 States by Number of Sellers")

    seller_state_counts = (
        sellers_df.groupby("seller_state")["seller_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(10)
    )

    st.bar_chart(seller_state_counts)

    st.caption(
        "Revenue is based on order item prices and excludes "
        "freight charges. Active sellers are sellers appearing "
        "in the order items dataset."
    )

# ==========================================
# DELIVERY ANALYTICS DASHBOARD
# ==========================================

if page == "Delivery":

    st.header("Delivery Analytics Dashboard")
    st.write("Delivery performance, shipping delays and customer satisfaction.")

    # Load required datasets
    orders_df = tables["orders"].copy()
    reviews_df = tables["order_reviews"].copy()

    # Convert date columns
    date_columns = [
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]

    for col in date_columns:
        orders_df[col] = pd.to_datetime(
            orders_df[col], errors="coerce"
        )

    # Only delivered orders with valid delivery dates
    delivered_orders = orders_df[
        (orders_df["order_status"] == "delivered") &
        (orders_df["order_delivered_customer_date"].notna()) &
        (orders_df["order_estimated_delivery_date"].notna())
    ].copy()

    # Calculate delivery duration
    delivered_orders["delivery_days"] = (
        delivered_orders["order_delivered_customer_date"] -
        delivered_orders["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400

    # Calculate delay relative to estimated date
    delivered_orders["delay_days"] = (
        delivered_orders["order_delivered_customer_date"] -
        delivered_orders["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86400

    # Compare calendar dates for delivery status
    actual_date = (
        delivered_orders["order_delivered_customer_date"].dt.normalize()
    )

    estimated_date = (
        delivered_orders["order_estimated_delivery_date"].dt.normalize()
    )

    delivered_orders["delivery_status"] = "On Time"

    delivered_orders.loc[
        actual_date < estimated_date,
        "delivery_status"
    ] = "Early"

    delivered_orders.loc[
        actual_date > estimated_date,
        "delivery_status"
    ] = "Late"

    # KPI calculations
    total_delivered = len(delivered_orders)

    late_deliveries = (
        delivered_orders["delivery_status"] == "Late"
    ).sum()

    late_delivery_rate = (
        late_deliveries / total_delivered * 100
        if total_delivered > 0 else 0
    )

    average_delivery_days = (
        delivered_orders["delivery_days"]
        .where(delivered_orders["delivery_days"] >= 0)
        .mean()
    )

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Delivered Orders",
            f"{total_delivered:,}"
        )

    with col2:
        st.metric(
            "Late Deliveries",
            f"{late_deliveries:,}"
        )

    with col3:
        st.metric(
            "Late Delivery Rate",
            f"{late_delivery_rate:.2f}%"
        )

    with col4:
        st.metric(
            "Avg Delivery Time",
            f"{average_delivery_days:.1f} Days"
        )

    st.divider()

    # Delivery status distribution
    st.subheader("Delivery Performance Distribution")

    delivery_counts = (
        delivered_orders["delivery_status"]
        .value_counts()
        .reindex(["Early", "On Time", "Late"], fill_value=0)
    )

    st.bar_chart(delivery_counts)

    # Monthly late delivery trend
    st.subheader("Monthly Late Delivery Rate")

    delivered_orders["delivery_month"] = (
        delivered_orders["order_delivered_customer_date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    monthly_delivery = (
        delivered_orders.groupby("delivery_month")
        .agg(
            total_orders=("order_id", "nunique"),
            late_orders=(
                "delivery_status",
                lambda x: (x == "Late").sum()
            )
        )
    )

    monthly_delivery["late_rate"] = (
        monthly_delivery["late_orders"] /
        monthly_delivery["total_orders"] * 100
    )

    st.line_chart(monthly_delivery["late_rate"])

    # Delivery time distribution
    st.subheader("Delivery Time Distribution")

    delivery_bins = pd.cut(
        delivered_orders["delivery_days"].where(
            delivered_orders["delivery_days"] >= 0
        ),
        bins=[0, 5, 10, 15, 20, 30, float("inf")],
        labels=[
            "0-5", "5-10", "10-15",
            "15-20", "20-30", "30+"
        ],
        include_lowest=True
    )

    delivery_distribution = (
        delivery_bins.value_counts()
        .reindex([
            "0-5", "5-10", "10-15",
            "15-20", "20-30", "30+"
        ], fill_value=0)
    )

    st.bar_chart(delivery_distribution)

    # Relationship between delivery and reviews
    st.subheader("Average Review Score by Delivery Status")

    # One review score per order to avoid duplicate joins
    reviews_df["review_score"] = pd.to_numeric(
        reviews_df["review_score"], errors="coerce"
    )

    order_reviews = (
        reviews_df.groupby("order_id", as_index=False)
        ["review_score"].mean()
    )

    delivery_reviews = delivered_orders.merge(
        order_reviews,
        on="order_id",
        how="left",
        validate="one_to_one"
    )

    average_reviews = (
        delivery_reviews.groupby("delivery_status")
        ["review_score"]
        .mean()
        .reindex(["Early", "On Time", "Late"])
    )

    st.bar_chart(average_reviews)

    st.caption(
        "Delivery analysis includes delivered orders with "
        "valid actual and estimated delivery dates. "
        "Delivery status is based on calendar dates."
    )

# ==========================================
# PAYMENTS ANALYTICS DASHBOARD
# ==========================================

if page == "Payments":

    st.header("Payments Analytics Dashboard")
    st.write(
        "Payment methods, transaction values and installment analysis."
    )

    # Load payment dataset
    payments_df = tables["order_payments"].copy()

    # Convert numeric columns
    payments_df["payment_value"] = pd.to_numeric(
        payments_df["payment_value"], errors="coerce"
    )

    payments_df["payment_installments"] = pd.to_numeric(
        payments_df["payment_installments"], errors="coerce"
    )

    # Calculate KPIs
    total_payment_records = len(payments_df)
    total_payment_value = payments_df["payment_value"].sum()
    total_payment_orders = payments_df["order_id"].nunique()

    average_payment_per_order = (
        total_payment_value / total_payment_orders
        if total_payment_orders > 0 else 0
    )

    # Display KPI cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Payment Records",
            f"{total_payment_records:,}"
        )

    with col2:
        st.metric(
            "Orders with Payments",
            f"{total_payment_orders:,}"
        )

    with col3:
        st.metric(
            "Total Payment Value",
            f"R$ {total_payment_value / 1_000_000:,.2f}M"
        )

    with col4:
        st.metric(
            "Avg Payment per Order",
            f"R$ {average_payment_per_order:,.2f}"
        )

    st.divider()

    # Payment method distribution
    st.subheader("Payment Method Distribution")

    payment_method_counts = (
        payments_df["payment_type"]
        .value_counts()
    )

    st.bar_chart(payment_method_counts)

    # Payment value by payment method
    st.subheader("Total Payment Value by Method")

    payment_method_value = (
        payments_df.groupby("payment_type")["payment_value"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(payment_method_value)

    # Installment distribution
    st.subheader("Payment Installment Distribution")

    installment_counts = (
        payments_df["payment_installments"]
        .value_counts()
        .sort_index()
    )

    st.bar_chart(installment_counts)

    # Average payment value by method
    st.subheader("Average Payment Value by Method")

    average_method_value = (
        payments_df.groupby("payment_type")["payment_value"]
        .mean()
        .sort_values(ascending=False)
    )

    st.bar_chart(average_method_value)

    st.divider()

    # Data quality indicators
    st.subheader("Payment Data Quality Indicators")

    zero_value_payments = (
        payments_df["payment_value"] == 0
    ).sum()

    zero_installment_payments = (
        payments_df["payment_installments"] == 0
    ).sum()

    undefined_payment_types = (
        payments_df["payment_type"] == "not_defined"
    ).sum()

    dq1, dq2, dq3 = st.columns(3)

    with dq1:
        st.metric(
            "Zero-Value Records",
            f"{zero_value_payments:,}"
        )

    with dq2:
        st.metric(
            "Zero-Installment Records",
            f"{zero_installment_payments:,}"
        )

    with dq3:
        st.metric(
            "Undefined Payment Types",
            f"{undefined_payment_types:,}"
        )

    st.caption(
        "Payment values include all payment records, "
        "including sequential payments for the same order. "
        "Total payment value may include freight and other "
        "charges, unlike product-only sales revenue."
    )

# ==========================================
# REVIEWS ANALYTICS DASHBOARD
# ==========================================

if page == "Reviews":

    st.header("Reviews Analytics Dashboard")
    st.write(
        "Customer satisfaction, review score distribution "
        "and feedback analysis."
    )

    # Load datasets
    reviews_df = tables["order_reviews"].copy()
    orders_df = tables["orders"].copy()

    # Convert review scores to numeric
    reviews_df["review_score"] = pd.to_numeric(
        reviews_df["review_score"],
        errors="coerce"
    )

    # Calculate KPIs
    total_reviews = len(reviews_df)
    average_review_score = reviews_df["review_score"].mean()

    positive_reviews = (
        reviews_df["review_score"] >= 4
    ).sum()

    negative_reviews = (
        reviews_df["review_score"] <= 2
    ).sum()

    positive_review_rate = (
        positive_reviews / reviews_df["review_score"].notna().sum() * 100
        if reviews_df["review_score"].notna().sum() > 0 else 0
    )

    # Display KPI cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Review Records",
            f"{total_reviews:,}"
        )

    with col2:
        st.metric(
            "Average Review Score",
            f"{average_review_score:.2f} / 5"
        )

    with col3:
        st.metric(
            "Positive Reviews",
            f"{positive_reviews:,}"
        )

    with col4:
        st.metric(
            "Positive Review Rate",
            f"{positive_review_rate:.2f}%"
        )

    st.divider()

    # Review score distribution
    st.subheader("Review Score Distribution")

    review_distribution = (
        reviews_df["review_score"]
        .value_counts()
        .reindex([1, 2, 3, 4, 5], fill_value=0)
        .sort_index()
    )

    st.bar_chart(review_distribution)

    # Positive, neutral and negative review groups
    st.subheader("Customer Satisfaction Categories")

    reviews_df["satisfaction_category"] = "Neutral"

    reviews_df.loc[
        reviews_df["review_score"] >= 4,
        "satisfaction_category"
    ] = "Positive"

    reviews_df.loc[
        reviews_df["review_score"] <= 2,
        "satisfaction_category"
    ] = "Negative"

    satisfaction_counts = (
        reviews_df.loc[
            reviews_df["review_score"].notna(),
            "satisfaction_category"
        ]
        .value_counts()
        .reindex(
            ["Positive", "Neutral", "Negative"],
            fill_value=0
        )
    )

    st.bar_chart(satisfaction_counts)

    # Monthly average review score
    st.subheader("Monthly Average Review Score")

    orders_df["order_purchase_timestamp"] = pd.to_datetime(
        orders_df["order_purchase_timestamp"],
        errors="coerce"
    )

    # Aggregate scores per order before merging
    order_review_scores = (
        reviews_df.groupby("order_id", as_index=False)
        ["review_score"].mean()
    )

    review_orders = order_review_scores.merge(
        orders_df[
            ["order_id", "order_purchase_timestamp"]
        ],
        on="order_id",
        how="inner",
        validate="one_to_one"
    )

    review_orders["purchase_month"] = (
        review_orders["order_purchase_timestamp"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    monthly_reviews = (
        review_orders.groupby("purchase_month")
        ["review_score"]
        .mean()
        .sort_index()
    )

    st.line_chart(monthly_reviews)

    # Review comment availability
    st.subheader("Review Comment Availability")

    has_comment = (
        reviews_df["review_comment_message"]
        .fillna("")
        .astype(str)
        .str.strip()
        .ne("")
    )

    comment_counts = pd.Series({
        "With Comments": int(has_comment.sum()),
        "Without Comments": int((~has_comment).sum())
    })

    st.bar_chart(comment_counts)

    st.divider()

    # Additional review indicators
    st.subheader("Review Quality Indicators")

    review_id_duplicates = (
        reviews_df["review_id"].duplicated().sum()
    )

    reviews_with_comments = int(has_comment.sum())

    q1, q2, q3 = st.columns(3)

    with q1:
        st.metric(
            "Negative Reviews (1–2)",
            f"{negative_reviews:,}"
        )

    with q2:
        st.metric(
            "Reviews With Comments",
            f"{reviews_with_comments:,}"
        )

    with q3:
        st.metric(
            "Repeated Review IDs",
            f"{review_id_duplicates:,}"
        )

    st.caption(
        "Positive reviews are scores 4–5, neutral reviews "
        "are score 3, and negative reviews are scores 1–2. "
        "Monthly trends use purchase dates and the mean "
        "review score per order."
    )

# ==========================================
# CUSTOMER REVIEW SCORE PREDICTION DASHBOARD
# ==========================================

if page == "Prediction":

    st.header("Customer Review Score Prediction")
    st.write(
        "Predict customer review scores (1 to 5) "
        "using the trained Logistic Regression model."
    )

    st.divider()

    # Load saved model and scaler
    model_path = (
        Path(__file__).parent
        / "model"
        / "olist_logistic_model.pkl"
    )

    @st.cache_resource
    def load_prediction_model(path):
        return joblib.load(path)

    if not model_path.exists():
        st.error("Model file not found. Check the model folder.")

    else:
        try:
            model_package = load_prediction_model(str(model_path))

            model = model_package["model"]
            scaler = model_package["scaler"]

            st.success("Machine learning model loaded successfully!")

            st.subheader("Enter Order Details")

            # User input fields
            col1, col2 = st.columns(2)

            with col1:
                order_value = st.number_input(
                    "Order Value (R$)",
                    min_value=0.0,
                    value=150.0,
                    step=10.0
                )

                freight_value = st.number_input(
                    "Freight Value (R$)",
                    min_value=0.0,
                    value=20.0,
                    step=5.0
                )

            with col2:
                total_items = st.number_input(
                    "Total Items",
                    min_value=1,
                    value=1,
                    step=1
                )

                delivery_days = st.number_input(
                    "Delivery Time (Days)",
                    min_value=0.0,
                    value=10.0,
                    step=1.0
                )

            st.divider()

            # Predict customer review score
            if st.button(
                "Predict Review Score",
                type="primary"
            ):

                feature_columns = [
                    "order_value",
                    "freight_value",
                    "total_items",
                    "delivery_days"
                ]

                input_data = pd.DataFrame(
                    [[
                        order_value,
                        freight_value,
                        total_items,
                        delivery_days
                    ]],
                    columns=feature_columns
                )

                # Apply saved scaler
                if scaler is not None:
                    scaled_input = scaler.transform(input_data)
                else:
                    scaled_input = input_data

                # Generate prediction
                prediction = model.predict(scaled_input)

                predicted_score = int(prediction[0])

                st.subheader("Prediction Result")

                st.metric(
                    "Predicted Customer Review Score",
                    f"{predicted_score} / 5"
                )

                if predicted_score >= 4:
                    st.success(
                        "Predicted customer satisfaction: Positive"
                    )

                elif predicted_score == 3:
                    st.info(
                        "Predicted customer satisfaction: Neutral"
                    )

                else:
                    st.warning(
                        "Predicted customer satisfaction: Negative"
                    )

                st.caption(
                    "Prediction generated using the trained "
                    "Logistic Regression classification model."
                )

        except Exception as e:
            st.error(f"Prediction model error: {e}")
