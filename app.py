import streamlit as st
import pandas as pd
import requests
import datetime
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(page_title="Prakiraan Cuaca Cerdas", page_icon="🌦️", layout="centered")

# ======================
# HEADER
# ======================
st.markdown("""
<div style="text-align:center; background-color:#0077b6; padding:20px; border-radius:10px;">
    <h1 style="color:white;">🌦️ Prakiraan Cuaca Cerdas</h1>
    <p style="color:#caf0f8; font-size:18px;">Data real-time dari OpenWeatherMap + Prediksi AI</p>
</div>
""", unsafe_allow_html=True)

# ======================
# INPUT LOKASI
# ======================
lokasi = st.text_input("Masukkan nama kota:", "Polewali")
api_key = "de799ea4217088a049f14f92c337c282"

@st.cache_data
def ambil_cuaca_sekarang(lokasi):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={lokasi}&appid={api_key}&units=metric&lang=id"
    return requests.get(url).json()

@st.cache_data
def ambil_prakiraan(lokasi):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={lokasi}&appid={api_key}&units=metric&lang=id"
    return requests.get(url).json()

# ======================
# CUACA SAAT INI
# ======================
if st.button("🌤️ Tampilkan Cuaca Saat Ini"):
    data = ambil_cuaca_sekarang(lokasi)
    if data.get("cod") != 200:
        st.error("❌ Kota tidak ditemukan.")
    else:
        suhu = data['main']['temp']
        kelembapan = data['main']['humidity']
        kondisi = data['weather'][0]['description'].capitalize()
        tekanan = data['main']['pressure']
        angin = data['wind']['speed']
        lat, lon = data['coord']['lat'], data['coord']['lon']

        st.markdown(f"""
        <div style='background-color:#e0f7fa; padding:20px; border-radius:10px;'>
            <h3 style='color:#0077b6;'>📍 {lokasi.capitalize()}</h3>
            <h2 style='color:#023e8a;'>🌡️ {suhu}°C</h2>
            <p style='color:#023e8a;'>🌤️ {kondisi}</p>
            <p style='color:#023e8a;'>💧 Kelembapan: {kelembapan}%</p>
            <p style='color:#023e8a;'>🌬️ Angin: {angin} m/s</p>
            <p style='color:#023e8a;'>🔽 Tekanan Udara: {tekanan} hPa</p>
        </div>
        """, unsafe_allow_html=True)

        # Tampilkan peta lokasi
        st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))

# ======================
# PRAKIRAAN 3 HARI + AI
# ======================
if st.button("📆 Lihat Prakiraan & Prediksi AI"):
    data_forecast = ambil_prakiraan(lokasi)
    if data_forecast.get("cod") != "200":
        st.error("❌ Data prakiraan tidak ditemukan.")
    else:
        df_list = []
        for entry in data_forecast['list']:
            waktu = datetime.datetime.fromtimestamp(entry['dt'])
            suhu = entry['main']['temp']
            kelembapan = entry['main']['humidity']
            kondisi = entry['weather'][0]['description'].capitalize()
            df_list.append({"Waktu": waktu, "Suhu (°C)": suhu, "Kelembapan (%)": kelembapan, "Kondisi": kondisi})

        df = pd.DataFrame(df_list)
        df3 = df[df["Waktu"] < (datetime.datetime.now() + datetime.timedelta(days=3))]

        st.subheader(f"🌦️ Prakiraan Cuaca 3 Hari ke Depan - {lokasi.capitalize()}")
        st.dataframe(df3)

        # Grafik suhu dan kelembapan
        fig = px.line(df3, x="Waktu", y="Suhu (°C)", title="Grafik Perubahan Suhu", line_shape="spline", markers=True)
        st.plotly_chart(fig)

        # -------------------------
        # 🔮 MODEL PREDIKSI AI
        # -------------------------
        st.subheader("🤖 Prediksi Suhu 6 Jam ke Depan (AI)")
        df3["Jam"] = np.arange(len(df3))
        model = LinearRegression()
        model.fit(df3[["Jam"]], df3["Suhu (°C)"])
        jam_pred = np.array([[len(df3) + 2]])  # Prediksi 6 jam kemudian
        suhu_pred = model.predict(jam_pred)[0]
        st.success(f"📈 Perkiraan suhu 6 jam mendatang: {suhu_pred:.2f}°C")

        # Visualisasi prediksi
        fig_pred = px.scatter(df3, x="Jam", y="Suhu (°C)", title="Prediksi Tren Suhu (AI)")
        fig_pred.add_scatter(x=[len(df3)+2], y=[suhu_pred], mode="markers+text", text=["Prediksi"], name="Prediksi", marker=dict(size=10))
        st.plotly_chart(fig_pred)
