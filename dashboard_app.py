import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import folium
from streamlit_folium import st_folium

# ===============================
# STREAMLIT CONFIG
# ===============================
st.set_page_config(
    page_title="Olist Store Dashboard Level Up Final",
    layout="wide"
)

# ===============================
# PATH & LOAD DATA
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

@st.cache_data
def load_data():
    product_sales_df = pd.read_csv(f"{DATA_DIR}/product_sales_by_category.csv", index_col="product_category_name_english").reset_index()
    city_metrics = pd.read_csv(f"{DATA_DIR}/city_metrics.csv", index_col="customer_city")
    state_metrics = pd.read_csv(f"{DATA_DIR}/state_metrics.csv", index_col="customer_state")
    orders_df = pd.read_csv(f"{DATA_DIR}/orders_data.csv", parse_dates=["order_purchase_timestamp", "order_delivered_customer_date"])
    orders_df["delivery_time"] = (orders_df["order_delivered_customer_date"] - orders_df["order_purchase_timestamp"]).dt.days
    order_items_df = pd.read_csv(f"{DATA_DIR}/order_items_data.csv")
    geo_df = pd.read_csv(f"{DATA_DIR}/geospatial_sales_data.csv")
    return product_sales_df, city_metrics, state_metrics, orders_df, order_items_df, geo_df

try:
    product_sales_df, city_metrics, state_metrics, orders_df, order_items_df, geospatial_sales_df = load_data()
except FileNotFoundError:
    st.error("❌ Folder `data/` atau file CSV tidak ditemukan.")
    st.stop()

# ===============================
# SIDEBAR FILTER
# ===============================
st.sidebar.title("🎛️ Filter Dashboard Level Up")

# Multiselect Produk
category_options = sorted(product_sales_df["product_category_name_english"].dropna().unique())
selected_categories = st.sidebar.multiselect("Kategori Produk", category_options, default=category_options)

# Multiselect Kota
city_options = sorted(city_metrics.index.tolist())
selected_cities = st.sidebar.multiselect("Kota", city_options, default=city_options)

# Multiselect Negara Bagian
state_options = sorted(state_metrics.index.tolist())
selected_states = st.sidebar.multiselect("Negara Bagian", state_options, default=state_options)

# Delivery Time Slider
min_day, max_day = int(orders_df["delivery_time"].min()), int(orders_df["delivery_time"].max())
delivery_range = st.sidebar.slider("Waktu Pengiriman (hari)", min_day, max_day, (min_day, max_day))

# Price Slider
min_price, max_price = float(order_items_df["price"].min()), float(order_items_df["price"].max())
price_range = st.sidebar.slider("Harga Produk", min_price, max_price, (min_price, max_price))

# Top-N Slider
top_n = st.sidebar.slider("Top N Items untuk Chart", 5, 20, 10)

# ===============================
# APPLY FILTER
# ===============================
filtered_products = product_sales_df[product_sales_df["product_category_name_english"].isin(selected_categories)]
filtered_orders = orders_df[
    (orders_df["delivery_time"] >= delivery_range[0]) &
    (orders_df["delivery_time"] <= delivery_range[1])
]
filtered_items = order_items_df[
    (order_items_df["price"] >= price_range[0]) &
    (order_items_df["price"] <= price_range[1])
]
filtered_geo = geospatial_sales_df[
    geospatial_sales_df["customer_city"].isin(selected_cities) &
    geospatial_sales_df["customer_state"].isin(selected_states)
]

# ===============================
# KPI CARDS
# ===============================
st.title("🌻 OLIST STORE DASHBOARD - LEVEL UP FINAL")
st.markdown("Dashboard interaktif tingkat lanjut")

total_orders = int(filtered_orders.shape[0]) if not filtered_orders.empty else 0
total_sales = float(filtered_items["price"].sum()) if not filtered_items.empty else 0
avg_delivery = round(filtered_orders["delivery_time"].mean(), 2) if not filtered_orders.empty else 0
avg_price = round(filtered_items["price"].mean(), 2) if not filtered_items.empty else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Total Orders", total_orders)
col2.metric("💵 Total Sales", f"${total_sales:,.2f}")
col3.metric("⏱️ Rata-rata Delivery", f"{avg_delivery} hari")
col4.metric("🏷️ Rata-rata Harga", f"${avg_price:,.2f}")

st.markdown("---")

# ===============================
# TOP PRODUCT CATEGORY
# ===============================
st.subheader("🔰 Top Produk")
fig, ax = plt.subplots(figsize=(12,6))
if not filtered_products.empty:
    top_products = filtered_products.sort_values(by=filtered_products.columns[1], ascending=False).head(top_n)
    sns.barplot(data=top_products, x="product_category_name_english", y=filtered_products.columns[1], color="mediumseagreen", ax=ax)
    ax.tick_params(axis="x", rotati_
