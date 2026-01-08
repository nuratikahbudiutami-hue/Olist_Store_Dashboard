import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import folium
from streamlit_folium import st_folium

# =================================================
# STREAMLIT CONFIG (WAJIB PALING ATAS)
# =================================================
st.set_page_config(
    page_title="Olist Store Dashboard",
    layout="wide"
)

# =================================================
# PATH & DATA LOADING
# =================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

@st.cache_data
def load_data():
    product_sales = pd.read_csv(
        f"{DATA_DIR}/product_sales_by_category.csv",
        index_col="product_category_name_english"
    ).reset_index()
    city_metrics = pd.read_csv(
        f"{DATA_DIR}/city_metrics.csv"
    )
    state_metrics = pd.read_csv(
        f"{DATA_DIR}/state_metrics.csv"
    )
    orders_df = pd.read_csv(
        f"{DATA_DIR}/orders_data.csv",
        parse_dates=[
            "order_purchase_timestamp",
            "order_delivered_customer_date"
        ]
    )
    orders_df["delivery_time"] = (
        orders_df["order_delivered_customer_date"]
        - orders_df["order_purchase_timestamp"]
    ).dt.days
    order_items_df = pd.read_csv(
        f"{DATA_DIR}/order_items_data.csv"
    )
    geo_df = pd.read_csv(
        f"{DATA_DIR}/geospatial_sales_data.csv"
    )
    return product_sales, city_metrics, state_metrics, orders_df, order_items_df, geo_df
try:
    (
        product_sales_df,
        city_metrics,
        state_metrics,
        orders_df,
        order_items_df,
        geo_df
    ) = load_data()
except FileNotFoundError:
    st.error(" Folder `data/` atau file CSV tidak ditemukan.")
    st.stop()

# =================================================
# SIDEBAR FILTER (INTERAKTIF)
# =================================================
st.sidebar.title("🎛️ Filter Dashboard")
# Kategori Produk
category_options = ["All"] + sorted(
    product_sales_df["product_category_name_english"].dropna().unique()
)
selected_category = st.sidebar.selectbox(
    "Kategori Produk",
    category_options
)
# Kota
city_options = ["All"] + sorted(
    orders_df["customer_city"].dropna().unique()
)
selected_city = st.sidebar.selectbox(
    "Kota",
    city_options
)
# Negara Bagian
state_options = ["All"] + sorted(
    orders_df["customer_state"].dropna().unique()
)
selected_state = st.sidebar.selectbox(
    "Negara Bagian",
    state_options
)
# Delivery Time Slider
min_day = int(orders_df["delivery_time"].min())
max_day = int(orders_df["delivery_time"].max())
delivery_range = st.sidebar.slider(
    "Waktu Pengiriman (hari)",
    min_day,
    max_day,
    (min_day, max_day)
)
# Price Slider
min_price = float(order_items_df["price"].min())
max_price = float(order_items_df["price"].max())
price_range = st.sidebar.slider(
    "Harga Produk",
    min_price,
    max_price,
    (min_price, max_price)
)

# =================================================
# APPLY FILTER
# =================================================
filtered_orders = orders_df.copy()
if selected_city != "All":
    filtered_orders = filtered_orders[
        filtered_orders["customer_city"] == selected_city
    ]
if selected_state != "All":
    filtered_orders = filtered_orders[
        filtered_orders["customer_state"] == selected_state
    ]
filtered_orders = filtered_orders[
    (filtered_orders["delivery_time"] >= delivery_range[0]) &
    (filtered_orders["delivery_time"] <= delivery_range[1])
]
filtered_items = order_items_df[
    (order_items_df["price"] >= price_range[0]) &
    (order_items_df["price"] <= price_range[1])
]
filtered_category = product_sales_df.copy()
if selected_category != "All":
    filtered_category = filtered_category[
        filtered_category["product_category_name_english"] == selected_category
    ]
    
# =================================================
# TITLE
# =================================================
st.title("🌻 OLIST STORE DASHBOARD")
st.write("Dashboard interaktif analisis penjualan Olist Store")
st.markdown("---")

# =================================================
# PRODUCT CATEGORY
# =================================================
st.subheader("🔰 Penjualan per Kategori Produk")
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(
    data=filtered_category.sort_values(
        filtered_category.columns[1],
        ascending=False
    ).head(10),
    x="product_category_name_english",
    y=filtered_category.columns[1],
    color="mediumseagreen",
    ax=ax
)
ax.tick_params(axis="x", rotation=45)
st.pyplot(fig)
st.markdown("---")

# =================================================
# DELIVERY TIME DISTRIBUTION
# =================================================
st.subheader(" Distribusi Waktu Pengiriman")
fig, ax = plt.subplots(figsize=(12, 6))
sns.histplot(
    filtered_orders["delivery_time"].dropna(),
    bins=30,
    kde=True,
    color="cornflowerblue",
    ax=ax
)
st.pyplot(fig)

# =================================================
# PRICE DISTRIBUTION
# =================================================
st.subheader(" Distribusi Harga Produk")
fig, ax = plt.subplots(figsize=(12, 6))
sns.histplot(
    filtered_items["price"],
    bins=40,
    kde=True,
    color="orchid",
    ax=ax
)
st.pyplot(fig)
st.markdown("---")

# =================================================
# GEOSPATIAL MAP
# =================================================
st.subheader(" Distribusi Geografis Penjualan")
map_data = geo_df.copy()
if selected_city != "All":
    map_data = map_data[map_data["customer_city"] == selected_city]
if selected_state != "All":
    map_data = map_data[map_data["customer_state"] == selected_state]
m = folium.Map(location=[-14.235, -51.925], zoom_start=4)

for _, row in map_data.iterrows():
    folium.CircleMarker(
        location=[row["geolocation_lat"], row["geolocation_lng"]],
        radius=min(row["total_orders"] * 0.05, 20),
        popup=f"""
        Kota: {row['customer_city']}<br>
        State: {row['customer_state']}<br>
        Orders: {int(row['total_orders'])}<br>
        Sales: {row['total_sales']:.2f}
        """,
        color="blue",
        fill=True,
        fill_opacity=0.6
    ).add_to(m)
st_folium(m, width=800, height=500)
