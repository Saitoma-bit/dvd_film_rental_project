#import libraries
import streamlit as st
import pandas as pd
import plotly.express as px




#use config page
st.set_page_config(
    page_title="DVD Rental Analysis Dashboard",
    page_icon="📀",
    layout="wide"
)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/cleaned_master_dataset.csv")
        return df
    except FileNotFoundError as e:
        st.warning(f"An error occured: {e}")

def create_sidebar_filters(df):

    st.sidebar.title("🎬 DVD Rental Dashboard")

    st.sidebar.header("Filters")

    df["rental_date"] = pd.to_datetime(df["rental_date"])
    st.write("Columns in dataset:", df.columns.tolist())
    df["payment_date"] = pd.to_datetime(df["payment_date"])

    start_date = st.sidebar.date_input(
        "Start Date",
        df["rental_date"].min().date()
    )

    end_date = st.sidebar.date_input(
        "End Date",
        df["rental_date"].max().date()
    )


    months = sorted(df["rental_month_name"].dropna().unique())

    selected_month = st.sidebar.multiselect(
        "Month",
        months,
        default=months
    )


    categories = sorted(df["category"].dropna().unique())

    selected_category = st.sidebar.multiselect(
        "Category",
        categories,
        default=categories
    )


    stores = sorted(df["store_id"].unique())

    selected_store = st.sidebar.multiselect(
        "Store",
        stores,
        default=stores
    )


    countries = sorted(df["country"].dropna().unique())

    selected_country = st.sidebar.multiselect(
        "Country",
        countries,
        default=countries
    )


    cities = sorted(df["city"].dropna().unique())

    selected_city = st.sidebar.multiselect(
        "City",
        cities,
        default=cities
    )


    staff = sorted(df["staff_name"].dropna().unique())

    selected_staff = st.sidebar.multiselect(
        "Staff",
        staff,
        default=staff
    )


    duration = st.sidebar.slider(
        "Rental Duration (days)",
        int(df["rental_duration"].min()),
        int(df["rental_duration"].max()),
        (
            int(df["rental_duration"].min()),
            int(df["rental_duration"].max())
        )
    )


    filtered_df = df[
        (df["rental_date"].dt.date >= start_date) &
        (df["rental_date"].dt.date <= end_date) &
        (df["rental_month_name"].isin(selected_month)) &
        (df["category"].isin(selected_category)) &
        (df["store_id"].isin(selected_store)) &
        (df["country"].isin(selected_country)) &
        (df["city"].isin(selected_city)) &
        (df["staff_name"].isin(selected_staff)) &
        (df["rental_duration"].between(duration[0], duration[1]))
    ]
    return filtered_df
def display_metrics(filtered_df):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("💰 Total Revenue",f"${filtered_df['payment_amount'].sum():,.2f}")

    with col2:
        st.metric("🎬 Total Rentals",f"{filtered_df['total_rentals'].sum():,}")

    with col3:
        st.metric("👥 Active Customers",f"{filtered_df['customer_id'].nunique():,}")

    with col4:
        monthly_growth = (filtered_df.groupby("rental_month_name")["payment_amount"].sum().pct_change().mean() * 100)
        st.metric("📈 Monthly Growth",f"{monthly_growth:.2f}%")

def display_chart(filtered_df):
    if len(filtered_df) == 0:
      st.warning("No filter data to display. please adjust the data from the sidebar")
      return
def executive_overview(df):

    st.header("📊 Executive Overview")
    total_revenue = df["payment_amount"].sum()

    total_rentals = df["rental_id"].nunique()

    active_customers = df["customer_id"].nunique()


    monthly_growth = (
        df.groupby("rental_month_name")["payment_amount"].sum().pct_change().mean()* 100)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Total Revenue",f"${total_revenue:,.2f}")
    with col2:
        st.metric("🎬 Total Rentals",f"{total_rentals:,}")
    with col3:
        st.metric("👥 Active Customers",f"{active_customers:,}")
    with col4:
        st.metric("📈 Monthly Growth",f"{monthly_growth:.2f}%")



    st.markdown("---")
 # Revenue Trend
    st.subheader("📈 Revenue Trend")
    revenue_trend = (
        df.groupby("rental_month_name")
        ["payment_amount"]
        .sum()
        .reset_index()
    )
    fig = px.line(
        revenue_trend,
        x="rental_month_name",
        y="payment_amount",
        markers=True,
        title="Monthly Revenue Trend"
    )
    st.plotly_chart(
        fig,
        use_container_width=True
    )
# Revenue by Store
    st.subheader("🏬 Revenue by Store")
    store_revenue = (
        df.groupby("store_id")
        ["payment_amount"]
        .sum()
        .reset_index()
    )
    fig2 = px.bar(
        store_revenue,
        x="store_id",
        y="payment_amount",
        title="Revenue Performance by Store"
    )
    st.plotly_chart(
        fig2,
        use_container_width=True
    )
    
def customer_analytics(df):
    st.header("👥 Customer Analytics")
    st.subheader("🏆 Top Customers by Revenue")

    top_customers = (
        df.groupby(["customer_id", "customer_name"])["payment_amount"]
        .sum()
        .reset_index()
        .sort_values("payment_amount", ascending=False)
        .head(10)
    )

    # Adding currency formatting and hovering adjustments
    fig1 = px.bar(
        top_customers,
        x="customer_name",
        y="payment_amount",
        title="Top 10 Customers by Revenue",
        text="payment_amount",
        labels={"customer_name": "Customer Name", "payment_amount": "Payment Amount"}
    )
    fig1.update_traces(texttemplate='%{text:$.2s}', textposition='inside')
    fig1.update_layout(yaxis_tickprefix='$')

    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("🔄 Customer Retention")
    customer_rentals = (
        df.groupby("customer_id")
        ["rental_id"]
        .count()
        .reset_index()
    )
    customer_rentals.columns = [
        "customer_id",
        "total_rentals"
    ]
    retained_customers = (
        customer_rentals[
            customer_rentals["total_rentals"] > 1
        ]
        .shape[0]
    )
    total_customers = df["customer_id"].nunique()
    retention_rate = (
        total_customers /
        retained_customers
    ) * 100
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "🔁 Returning Customers",
            f"{retained_customers:,}"
        )
    with col2:
        st.metric(
            "📊 Retention Rate",
            f"{retention_rate:.2f}%"
        )
        
    st.subheader("⚠️ Churn Risk Customers")
    last_rental = (
        df.groupby("customer_id")
        ["rental_date"]
        .max()
        .reset_index()
    )
    latest_date = df["rental_date"].max()
    last_rental["days_since_last_rental"] = (
        latest_date -
        last_rental["rental_date"]
    ).dt.days
    churn_risk = last_rental[
        last_rental["days_since_last_rental"] > 90
    ]
    st.write(
        f"Customers with no rental activity for more than 90 days: *{len(churn_risk):,}*"
    )
    st.dataframe(
        churn_risk.sort_values(
            "days_since_last_rental",
            ascending=False
        ),
        use_container_width=True
    )
def film_category_performance(df):

    st.header("🎬 Film & Category Performance")
    st.subheader("🏆 Top Performing Films")
    top_films = (
        df.groupby("film_title")
        .agg(
            total_revenue=("payment_amount", "sum"),
            total_rentals=("rental_id", "count")
        )
        .reset_index()
        .sort_values(
            "total_revenue",
            ascending=False
        ).head(10))
    fig1 = px.bar(
        top_films,
        x="film_title",
        y="total_revenue",
        title="Top 10 Films by Revenue",
        text="total_revenue"
    )
    fig1.update_traces(texttemplate='%{text:$.2s}', textposition='inside')
    st.plotly_chart(
        fig1,
        use_container_width=True
    )
    st.subheader("📂 Revenue by Category")
    category_revenue = (
        df.groupby("category")
        ["payment_amount"]
        .sum()
        .reset_index()
        .sort_values(
            "payment_amount",
            ascending=False
        )
    )
    fig2 = px.pie(
        category_revenue,
        names="category",
        values="payment_amount",
        title="Revenue Contribution by Category"
    )
    st.plotly_chart(fig2,use_container_width=True)
    st.subheader("📦 Inventory Risk Analysis")
    inventory_risk = (
        df.groupby("film_title")
        .agg(
            rentals=("rental_id", "count"),
            inventory=("inventory_id", "nunique")
        )
        .reset_index()
    )
    inventory_risk["rental_pressure"] = (
        inventory_risk["rentals"] /
        inventory_risk["inventory"]
    )
    high_risk = (
        inventory_risk
        .sort_values(
            "rental_pressure",
            ascending=False
        )
        .head(10)
    )
    st.write(
        "Films with high rental demand compared to available inventory:"
    )
    st.dataframe(
        high_risk,
        use_container_width=True
    )
def store_staff_performance(df):

    st.header("🏬 Store & Staff Performance")



    st.subheader("🏪 Store Revenue Comparison")


    store_comparison = (
        df.groupby("store_id")
        .agg(
            total_revenue=("payment_amount", "sum"),
            total_rentals=("rental_id", "count"),
            customers=("customer_id", "nunique")
        )
        .reset_index()
    )


    fig1 = px.bar(
        store_comparison,
        x="store_id",
        y="total_revenue",
        title="Revenue Comparison Between Stores",
        text="total_revenue"
    )


    st.plotly_chart(
        fig1,
        use_container_width=True
    )





    st.subheader("📊 Store Performance Details")


    store_comparison["average_rental_value"] = (
        store_comparison["total_revenue"] /
        store_comparison["total_rentals"]
    )


    st.dataframe(
        store_comparison,
        use_container_width=True
    )



    st.subheader("👨‍💼 Staff Efficiency")


    staff_efficiency = (
        df.groupby(
            ["staff_id", "staff_name"]
        )
        .agg(
            total_revenue=("payment_amount", "sum"),
            rentals_processed=("rental_id", "count"),
            customers_served=("customer_id", "nunique")
        )
        .reset_index()
    )


    staff_efficiency["revenue_per_rental"] = (
        staff_efficiency["total_revenue"] /
        staff_efficiency["rentals_processed"]
    )


    fig2 = px.bar(
        staff_efficiency.sort_values(
            "total_revenue",
            ascending=False
        ).head(10),
        x="staff_name",
        y="total_revenue",
        title="Top Performing Staff by Revenue",
        text="total_revenue"
    )


    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.subheader("🏆 Staff Performance Ranking")


    st.dataframe(
        staff_efficiency.sort_values(
            "total_revenue",
            ascending=False
        ),
        use_container_width=True
    )
def geographic_insights(df):

    st.header("🌍 Geographic Insights")



    st.subheader("🌎 Revenue by Country")


    country_revenue = (
        df.groupby("country")
        ["payment_amount"]
        .sum()
        .reset_index()
        .sort_values(
            "payment_amount",
            ascending=False
        )
        .head(15)
    )


    fig1 = px.bar(
        country_revenue,
        x="country",
        y="payment_amount",
        title="Top Countries by Revenue",
        text="payment_amount"
    )


    st.plotly_chart(
        fig1,
        use_container_width=True
    )



    st.subheader("🏙️ Revenue by City")


    city_revenue = (
        df.groupby(
            ["city", "country"]
        )
        ["payment_amount"]
        .sum()
        .reset_index()
        .sort_values(
            "payment_amount",
            ascending=False
        )
        .head(20)
    )


    fig2 = px.bar(
        city_revenue,
        x="city",
        y="payment_amount",
        color="country",
        title="Top Cities by Revenue",
        text="payment_amount"
    )


    st.plotly_chart(
        fig2,
        use_container_width=True
    )




    st.subheader("📍 Regional Customer Preferences")


    regional_preferences = (
        df.groupby("country")
        .agg(
            customers=("customer_id", "nunique"),
            rentals=("rental_id", "count"),
            revenue=("payment_amount", "sum")
        )
        .reset_index()
        .sort_values(
            "revenue",
            ascending=False
        )
    )


    regional_preferences["average_customer_value"] = (
        regional_preferences["revenue"] /
        regional_preferences["customers"]
    )


    st.dataframe(
        regional_preferences,
        use_container_width=True
    )
def download_button(df):

    st.sidebar.markdown("---")

    st.sidebar.subheader("📥 Export Data")


    csv = df.to_csv(
        index=False
    ).encode("utf-8")


    st.sidebar.download_button(
        label="Download Filtered Data",
        data=csv,
        file_name="DVD_Rental_Analysis_Report.csv",
        mime="text/csv"
    )
def main():

    df = load_data()


    if df is None:
        st.error("Dataset could not be loaded.")
        return


    # Sidebar Navigation

    page = st.sidebar.radio(
        "📌 Dashboard Pages",
        [
            "Executive Overview",
            "Customer Analytics",
            "Film & Category Performance",
            "Store & Staff Performance",
            "Geographic Insights"
        ]
    )


    # Filters

    filtered_df = create_sidebar_filters(df)


    # Download Button

    download_button(filtered_df)



    # Main Dashboard Title

    st.title("📀 DVD Rental Business Intelligence Dashboard")


    # Pages

    if page == "Executive Overview":

        executive_overview(filtered_df)



    elif page == "Customer Analytics":

        customer_analytics(filtered_df)



    elif page == "Film & Category Performance":

        film_category_performance(filtered_df)



    elif page == "Store & Staff Performance":

        store_staff_performance(filtered_df)



    elif page == "Geographic Insights":

        geographic_insights(filtered_df)
main()