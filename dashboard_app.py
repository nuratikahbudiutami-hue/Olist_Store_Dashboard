import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import folium
from streamlit_folium import st_folium

# ===============================
# STREAMLIT CONFIG (WAJIB PALING ATAS)
# ===============================
st.set_page_config(
    page_title="E-Commerce Sales Dashboard",
    layout="wide"
)

# ===============================
# PATH & DATA LOADING
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

@st.cache_data
def load_data():
    product_sales = pd.read_csv(
        f"{DATA_DIR}/product_sales_by_category.csv",
        index_col="product_category_name_english"
    )

    city_metrics = pd.read_csv(
        f"{DATA_DIR}/city_metrics.csv",
        index_col="customer_city"
    )

    state_metrics = pd.read_csv(
        f"{DATA_DIR}/state_metrics.csv",
        index_col="customer_state"
    )

    orders_df = pd.read_csv(
        f"{DATA_DIR}/orders_data.csv",
        parse_dates=[
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ]
    )

    orders_df["delivery_time"] = (
        orders_df["order_delivered_customer_date"]
        - orders_df["order_purchase_timestamp"]
    ).dt.days

    order_items_df = pd.read_csv(
        f"{DATA_DIR}/order_items_data.csv",
        parse_dates=["shipping_limit_date"]
    )

    geo_df = pd.read_csv(f"{DATA_DIR}/geospatial_sales_data.csv")

    return product_sales, city_metrics, state_metrics, orders_df, order_items_df, geo_df


try:
    (
        product_sales_by_category,
        city_metrics,
        state_metrics,
        orders_df,
        order_items_df,
        geospatial_sales_df
    ) = load_data()
except FileNotFoundError:
    st.error(" Folder `data/` atau file CSV tidak ditemukan.")
    st.stop()

# ===============================
# TITLE
# ===============================
st.title("🌻 OLIST STORE DASHBOARD")
st.write(
    "Dashboard interaktif untuk menampilkan hasil analisis penjualan "
    "E-Commerce Olist Store."
)

st.markdown("---")

# ===============================
# 1. TOP & BOTTOM PRODUCT CATEGORY
# ===============================
st.subheader("🔰 Kategori Produk: Penjualan Tertinggi & Terendah")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Penjualan Tertinggi")
    top_products = (
        product_sales_by_category
        .sort_values(by=product_sales_by_category.columns[0], ascending=False)
        .head(10)
        .reset_index()
    )
    top_products.columns = ["Kategori Produk", "Jumlah Item Terjual"]

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=top_products,
        x="Kategori Produk",
        y="Jumlah Item Terjual",
        color="palegreen",
        ax=ax
    )
    ax.set_title("Top 10 Kategori Produk")
    ax.tick_params(axis="x", rotation=45)
    st.pyplot(fig)

with col2:
    st.markdown("#### Penjualan Terendah")
    bottom_products = (
        product_sales_by_category
        .sort_values(by=product_sales_by_category.columns[0])
        .head(10)
        .reset_index()
    )
    bottom_products.columns = ["Kategori Produk", "Jumlah Item Terjual"]

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=bottom_products,
        x="Kategori Produk",
        y="Jumlah Item Terjual",
        color="lightcoral",
        ax=ax
    )
    ax.set_title("Bottom 10 Kategori Produk")
    ax.tick_params(axis="x", rotation=45)
    st.pyplot(fig)

st.markdown("---")

# ===============================
# 2. ORDER VOLUME
# ===============================
st.subheader("🔰 Volume Pesanan per Wilayah")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Kota Teratas")
    top_cities = city_metrics.sort_values(
        by="order_volume", ascending=False
    ).head(10).reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=top_cities,
        x="customer_city",
        y="order_volume",
        color="lightsteelblue",
        ax=ax
    )
    ax.set_title("Top 10 Kota")
    ax.tick_params(axis="x", rotation=45)
    st.pyplot(fig)

with col2:
    st.markdown("#### Negara Bagian Teratas")
    top_states = state_metrics.sort_values(
        by="order_volume", ascending=False
    ).head(10).reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=top_states,
        x="customer_state",
        y="order_volume",
        color="rosybrown",
        ax=ax
    )
    ax.set_title("Top 10 Negara Bagian")
    ax.tick_params(axis="x", rotation=45)
    st.pyplot(fig)

st.markdown("---")

# ===============================
# 3. DISTRIBUTIONS
# ===============================
st.subheader("🔰 Distribusi Pengiriman & Harga")

st.markdown("#### Waktu Pengiriman")
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(
    orders_df["delivery_time"].dropna(),
    bins=30,
    kde=True,
    color="mediumseagreen",
    ax=ax
)
st.pyplot(fig)

st.markdown("#### Harga Produk")
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(
    order_items_df["price"],
    bins=50,
    kde=True,
    color="thistle",
    ax=ax
)
st.pyplot(fig)

st.markdown("---")

# ===============================
# 4. GEOSPATIAL MAP
# ===============================
st.subheader("🔰 Distribusi Geografis Penjualan")

m = folium.Map(location=[-14.235, -51.925], zoom_start=4)

for _, row in geospatial_sales_df.iterrows():
    folium.CircleMarker(
        location=[row["geolocation_lat"], row["geolocation_lng"]],
        radius=min(row["total_orders"] * 0.05, 20),
        popup=(
            f"Kota: {row['customer_city']}<br>"
            f"State: {row['customer_state']}<br>"
            f"Total Orders: {int(row['total_orders'])}<br>"
            f"Total Sales: {row['total_sales']:.2f}"
        ),
        color="blue",
        fill=True,
        fill_opacity=0.6
    ).add_to(m)

st_folium(m, width=800, height=500)
