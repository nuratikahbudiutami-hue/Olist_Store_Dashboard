import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import folium
from streamlit_folium import st_folium

# ===============================
# 1️⃣ STREAMLIT CONFIG
# ===============================
st.set_page_config(
    page_title="Olist Store Dashboard Level Up Final",
    layout="wide"
)

# ===============================
# 2️⃣ PATH & LOAD DATA
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

@st.cache_data
def load_data():
    """Load semua CSV yang dibutuhkan"""
    product_sales_df = pd.read_csv(
        os.path.join(DATA_DIR, "product_sales_by_category.csv"),
        index_col="product_category_name_english"
    ).reset_index()
    
    city_metrics = pd.read_csv(os.path.join(DATA_DIR, "city_metrics.csv"), index_col="customer_city")
    state_metrics = pd.read_csv(os.path.join(DATA_DIR, "state_metrics.csv"), index_col="customer_state")
    
    orders_df = pd.read_csv(
        os.path.join(DATA_DIR, "orders_data.csv"),
        parse_dates=["order_purchase_timestamp", "order_delivered_customer_date"]
    )
    orders_df["delivery_time"] = (
        orders_df["order_delivered_customer_date"] - orders_df["order_purchase_timestamp"]
    ).dt.days
    
    order_items_df = pd.read_csv(os.path.join(DATA_DIR, "order_items_data.csv"))
    geo_df = pd.read_csv(os.path.join(DATA_DIR, "geospatial_sales_data.csv"))
    
    return product_sales_df, city_metrics, state_metrics, orders_df, order_items_df, geo_df

try:
    product_sales_df, city_metrics, state_metrics, orders_df, order_items_df, geospatial_sales_df = load_data()
except FileNotFoundError:
    st.error("❌ Folder `data/` atau file CSV tidak ditemukan.")
    st.stop()

# ===============================
# 3️⃣ SIDEBAR FILTER
# ===============================
st.sidebar.title("🎛️ Filter Dashboard Level Up")

# Filter Kategori Produk
category_options = sorted(product_sales_df["product_category_name_english"].dropna().unique())
selected_categories = st.sidebar.multiselect("Kategori Produk", category_options, default=category_options)

# Filter Kota
city_options = sorted(city_metrics.index.tolist())
selected_cities = st.sidebar.multiselect("Kota", city_options, default=city_options)

# Filter Negara Bagian
state_options = sorted(state_metrics.index.tolist())
selected_states = st.sidebar.multiselect("Negara Bagian", state_options, default=state_options)

# Slider Waktu Pengiriman
min_day, max_day = int(orders_df["delivery_time"].min()), int(orders_df["delivery_time"].max())
delivery_range = st.sidebar.slider("Waktu Pengiriman (hari)", min_day, max_day, (min_day, max_day))

# Slider Harga Produk
min_price, max_price = float(order_items_df["price"].min()), float(order_items_df["price"].max())
price_range = st.sidebar.slider("Harga Produk", min_price, max_price, (min_price, max_price))

# Slider Top-N
top_n = st.sidebar.slider("Top N Items untuk Chart", 5, 20, 10)

# ===============================
# 4️⃣ APPLY FILTER
# ===============================
filtered_products = product_sales_df[
    product_sales_df["product_category_name_english"].isin(selected_categories)
]

filtered_orders = orders_df[
    (orders_df["delivery_time"] >= delivery_range[0]) &
    (orders_df["delivery_time"] <= delivery_range[1])
]

filtered_items = order_items_df[
    (order_items_df["price"] >= price_range[0]) &
    (order_items_df["price"] <= price_range[1])
]

filtered_geo = geospatial_sales_df[
    (geospatial_sales_df["customer_city"].isin(selected_cities)) &
    (geospatial_sales_df["customer_state"].isin(selected_states))
]

# ===============================
# 5️⃣ KPI CARDS
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
# 6️⃣ TOP PRODUCT CATEGORY
# ===============================
st.subheader("🔰 Top Produk")
fig, ax = plt.subplots(figsize=(12,6))

if not filtered_products.empty:
    sales_col = filtered_products.columns[1]  # pastikan kolom jumlah penjualan
    top_products = filtered_products.sort_values(by=sales_col, ascending=False).head(top_n)
    sns.barplot(
        data=top_products,
        x="product_category_name_english",
        y=sales_col,
        color="mediumseagreen",
        ax=ax
    )
    ax.tick_params(axis="x", rotation=45)
else:
    ax.text(0.5, 0.5, "Tidak ada data untuk filter ini", ha='center', va='center', fontsize=14)
st.pyplot(fig)

# ===============================
# 7️⃣ DISTRIBUSI WAKTU PENGIRIMAN
# ===============================
st.subheader("🚚 Distribusi Waktu Pengiriman")
fig, ax = plt.subplots(figsize=(12,6))
if not filtered_orders.empty:
    sns.histplot(filtered_orders["delivery_time"].dropna(), bins=30, kde=True, color="cornflowerblue", ax=ax)
else:
    ax.text(0.5, 0.5, "Tidak ada data untuk filter ini", ha='center', va='center', fontsize=14)
st.pyplot(fig)

# ===============================
# 8️⃣ DISTRIBUSI HARGA PRODUK
# ===============================
st.subheader("💰 Distribusi Harga Produk")
fig, ax = plt.subplots(figsize=(12,6))
if not filtered_items.empty:
    sns.histplot(filtered_items["price"], bins=40, kde=True, color="orchid", ax=ax)
else:
    ax.text(0.5, 0.5, "Tidak ada data untuk filter ini", ha='center', va='center', fontsize=14)
st.pyplot(fig)

# ===============================
# 9️⃣ MAP GEOSPATIAL
# ===============================
st.subheader("🗺️ Distribusi Geografis Penjualan")
m = folium.Map(location=[-14.235, -51.925], zoom_start=4)

if not filtered_geo.empty:
    for _, row in filtered_geo.iterrows():
        folium.CircleMarker(
            location=[row["geolocation_lat"], row["geolocation_lng"]],
            radius=min(row["total_orders"]*0.05, 20),
            popup=f"Kota: {row['customer_city']}<br>State: {row['customer_state']}<br>Orders: {int(row['total_orders'])}<br>Sales: {row['total_sales']:.2f}",
            color="blue",
            fill=True,
            fill_opacity=0.6
        ).add_to(m)
else:
    folium.Marker(
        location=[-14.235, -51.925],
        popup="Tidak ada data untuk filter ini"
    ).add_to(m)

st_folium(m, width=900, height=500)

# ===============================
# 🔟 AUTOMATIC INSIGHT
# ===============================
st.markdown("---")
st.subheader("💡 Insight Singkat")

if filtered_geo.empty or filtered_products.empty:
    st.info("Tidak ada data untuk filter yang dipilih. Silakan sesuaikan filter di sidebar.")
else:
    top_city = filtered_geo.sort_values('total_orders', ascending=False).head(1)
    top_city_name = top_city['customer_city'].values[0] if not top_city.empty else "N/A"

    top_product = filtered_products.sort_values(filtered_products.columns[1], ascending=False).head(1)
    top_product_name = top_product.iloc[0,0] if not top_product.empty else "N/A"

    st.write(f"- Kota dengan total orders terbanyak: {top_city_name}")
    st.write(f"- Produk dengan penjualan tertinggi: {top_product_name}")
    st.write(f"- Rata-rata waktu pengiriman: {avg_delivery} hari")
    st.write(f"- Rata-rata harga produk: ${avg_price:.2f}")
