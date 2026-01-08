# Olist_Store_Dashboard
Melakukan analisis untuk dataframe pada Olist Store yang kemudian divisualisasikan dan ditampilkan dalam dashboard

## Cara Menjalankan Aplikasi Streamlit

Untuk menjalankan dashboard Streamlit, ikuti langkah-langkah berikut:

1. Pastikan berada di direktori yang sama dengan `dashboard_app.py` dan folder `data` yang berisi file CSV.
2. Buka terminal atau command prompt.
3. Jalankan perintah berikut:
   ```bash
   !pip install streamlit_folium
   !wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
   !chmod +x cloudflared-linux-amd64
   !streamlit run /content/drive/MyDrive/Colab_Notebooks/data/dashboard_app.py --server.port 8501 &>/content/streamlit.log &
   !./cloudflared-linux-amd64 tunnel --url http://localhost:8501
   ```
4. Streamlit akan membuka tab baru di browser web dan secara otomatis yang menampilkan dashboard.
