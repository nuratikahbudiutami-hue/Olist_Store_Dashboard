
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import streamlit_folium
import folium
from streamlit_folium import st_folium
import os

# Menentukan direktori data yang disimpan dalam github
data_dir = os.path.join(os.getcwd(), "data")

# Memuat DataFrame
try:
    product_sales_by_category = pd.read_csv(f'{data_dir}/product_sales_by_category.csv', index_col='product_category_name_english')
    city_metrics = pd.read_csv(f'{data_dir}/city_metrics.csv', index_col='customer_city')
    state_metrics = pd.read_csv(f'{data_dir}/state_metrics.csv', index_col='customer_state')
    orders_df = pd.read_csv(f'{data_dir}/orders_data.csv', parse_dates=[
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ])
    orders_df['delivery_time'] = (
        orders_df['order_delivered_customer_date'] -
        orders_df['order_purchase_timestamp']
    ).dt.days

    order_items_df = pd.read_csv(f'{data_dir}/order_items_data.csv', parse_dates=['shipping_limit_date'])
    geospatial_sales_df = pd.read_csv(f'{data_dir}/geospatial_sales_data.csv')
except FileNotFoundError:
    st.error("Error: Data files not found. Please ensure 'data' directory and CSVs are correctly placed.")
    st.stop()

# Set Streamlit page configuration
st.set_page_config(page_title="E-Commerce Sales Dashboard", layout="wide")
st.title("OLIST STORE DASHBOARD 🌻")
st.write("Dashboard yang menunjukkan visualisasi dari hasil analisis dataframe penjualan di Olist Store")
st.write("") # Add some spacing
st.write("") # Add some spacing

# --- 1. Kategori Produk Tingkat Penjualan Tertinggi dan Terendah ---
st.subheader("🔰 Kategori Produk Tingkat Penjualan Tertinggi dan Terendah")

col1, col2 = st.columns(2)
with col1:
    # Plotting Top 10 Product Categories
    st.markdown("#### Kategori Produk Tingkat Penjualan Tertinggi")
    fig_top_products, ax_top_products = plt.subplots(figsize=(10, 6))
    top_products_df = product_sales_by_category.head(10).reset_index()
    top_products_df.columns = ['Kategori Produk', 'Jumlah Item Terjual']
    sns.barplot(x='Kategori Produk', y='Jumlah Item Terjual', data=top_products_df, color='palegreen', ax=ax_top_products)
    ax_top_products.set_title('Penjualan Tertinggi berdasarkan Kategori Produk', fontsize=12)
    ax_top_products.set_xlabel('Kategori Produk', fontsize=10)
    ax_top_products.set_ylabel('Jumlah Item Terjual', fontsize=10)
    ax_top_products.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    st.pyplot(fig_top_products)


with col2:
    # Plotting Bottom 10 Product Categories
    st.markdown("#### Kategori Produk Tingkat PenjualanTerendah")
    fig_bottom_products, ax_bottom_products = plt.subplots(figsize=(10, 6))
    bottom_products_df = product_sales_by_category.tail(10).reset_index()
    bottom_products_df.columns = ['Kategori Produk', 'Jumlah Item Terjual']
    sns.barplot(x='Kategori Produk', y='Jumlah Item Terjual', data=bottom_products_df, color='lightcoral', ax=ax_bottom_products)
    ax_bottom_products.set_title('Penjualan Terendah berdasarkan Kategori Produk', fontsize=12)
    ax_bottom_products.set_xlabel('Kategori Produk', fontsize=10)
    ax_bottom_products.set_ylabel('Jumlah Item Terjual', fontsize=10)
    ax_bottom_products.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    st.pyplot(fig_bottom_products)
st.write("") # Add some spacing
st.write("") # Add some spacing

# --- 2. Volume Pesanan per Kota dan Negara Bagian ---
st.subheader("🔰 Volume Pesanan per Kota dan Negara Bagian")

col1, col2 = st.columns(2)
with col1:
    # Plotting Top 10 Cities by Order Volume
    st.markdown("#### Kota Teratas berdasarkan Volume Pesanan")
    fig_top_cities, ax_top_cities = plt.subplots(figsize=(10, 6))
    top_cities_df = city_metrics['order_volume'].head(10).reset_index()
    top_cities_df.columns = ['Nama Kota', 'Total Volume Pesanan']
    sns.barplot(x='Nama Kota', y='Total Volume Pesanan', data=top_cities_df, color='lightsteelblue', ax=ax_top_cities)
    ax_top_cities.set_title('Kota Teratas berdasarkan Volume Pesanan', fontsize=12)
    ax_top_cities.set_xlabel('Nama Kota', fontsize=10)
    ax_top_cities.set_ylabel('Total Volume Pesanan', fontsize=10)
    ax_top_cities.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    st.pyplot(fig_top_cities)
with col2:
    # Plotting Top 10 States by Order Volume
    st.markdown("#### Negara Bagian Teratas berdasarkan Volume Pesanan")
    fig_top_states, ax_top_states = plt.subplots(figsize=(10, 6))
    top_states_df = state_metrics['order_volume'].head(10).reset_index()
    top_states_df.columns = ['Nama Negara Bagian', 'Total Volume Pesanan']
    sns.barplot(x='Nama Negara Bagian', y='Total Volume Pesanan', data=top_states_df, color='rosybrown', ax=ax_top_states)
    ax_top_states.set_title('Negara Bagian Teratas berdasarkan Volume Pesanan', fontsize=12)
    ax_top_states.set_xlabel('Nama Negara Bagian', fontsize=10)
    ax_top_states.set_ylabel('Total Volume Pesanan', fontsize=10)
    ax_top_states.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    st.pyplot(fig_top_states)
st.write("") # Add some spacing
st.write("") # Add some spacing

# --- 3. Distribusi Waktu Pengiriman dan Harga Produk ---
st.subheader("🔰 Distribusi Waktu Pengiriman dan Harga Produk")
# Plotting Delivery Time Histogram
st.markdown("#### Distribusi Waktu Pengiriman")
fig_delivery_time, ax_delivery_time = plt.subplots(figsize=(10, 6))
sns.histplot(orders_df['delivery_time'], bins=30, kde=True, color='mediumseagreen', ax=ax_delivery_time)
ax_delivery_time.set_title('Distribusi Waktu Pengiriman', fontsize=12)
ax_delivery_time.set_xlabel('Waktu Pengiriman (Hari)', fontsize=10)
ax_delivery_time.set_ylabel('Jumlah Pengiriman', fontsize=10)
plt.tight_layout()
st.pyplot(fig_delivery_time)

# Plotting Product Price Histogram
st.markdown("#### Distribusi Harga Produk")
fig_price_dist, ax_price_dist = plt.subplots(figsize=(10, 6))
sns.histplot(order_items_df['price'], bins=50, kde=True, color='thistle', ax=ax_price_dist)
ax_price_dist.set_title('Distribusi Harga Produk', fontsize=12)
ax_price_dist.set_xlabel('Harga', fontsize=10)
ax_price_dist.set_ylabel('Jumlah Pesanan', fontsize=10)
plt.tight_layout()
st.pyplot(fig_price_dist)
st.write("") # Add some spacing
st.write("") # Add some spacing

# --- 4. Distribusi Geografis Penjualan ---
st.subheader(" 🔰 Distribusi Geografis Penjualan")
st.markdown("#### Peta Interaktif Distribusi Penjualan")

m = folium.Map(location=[-1.235, -51.925], zoom_start=4)

for index, row in geospatial_sales_df.iterrows():
    folium.CircleMarker(
        location=[row['geolocation_lat'], row['geolocation_lng']],
        radius=min(row['total_orders'] * 0.05, 20),
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.6,
        popup=f"City: {row['customer_city']}<br>State: {row['customer_state']}<br>Total Orders: {int(row['total_orders'])}<br>Total Sales: {row['total_sales']:.2f}"
    ).add_to(m)

st_folium(m, width=700, height=500)
