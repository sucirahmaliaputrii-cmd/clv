import streamlit as st
import pandas as pd

st.set_page_config(page_title="CLV Calculator", layout="wide")

st.title("📊 Customer Lifetime Value (CLV) Calculator — Simple Web App")

st.write("Upload data pelanggan, hitung CLV otomatis, dan lihat dashboard sederhana.")

uploaded = st.file_uploader("Upload file CSV", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)

    required_cols = ["ID", "Margin", "Biaya_Akuisisi"]
    if not all(col in df.columns for col in required_cols):
        st.error(f"CSV harus mengandung kolom: {required_cols}")
    else:
        df["CLV"] = df["Margin"] - df["Biaya_Akuisisi"]

        # Segmentasi sederhana
        df["Segment"] = pd.cut(
            df["CLV"],
            bins=[-10**12, 1000000, 2500000, 10**12],
            labels=["Low Value", "Mid Value", "High Value"]
        )

        st.subheader("📄 Hasil Perhitungan CLV")
        st.dataframe(df)

        # Dashboard
        st.subheader("📈 Dashboard Segmentasi")
        seg_count = df["Segment"].value_counts().reset_index()
        seg_count.columns = ["Segment", "Jumlah"]

        st.bar_chart(seg_count, x="Segment", y="Jumlah")

        st.subheader("📊 Ringkasan")
        col1, col2 = st.columns(2)
        col1.metric("Total Pelanggan", len(df))
        col2.metric("Rata-rata CLV", int(df["CLV"].mean()))

        st.download_button(
            "Download Hasil (CSV)",
            data=df.to_csv(index=False),
            file_name="CLV_Output.csv",
            mime="text/csv"
        )
