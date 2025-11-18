# app.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="CLV Simple App", layout="wide")
st.title("📊 CLV Calculator — Input & Dashboard Sederhana")
st.write("Masukkan data pelanggan, sistem akan menghitung CLV dan melakukan segmentasi otomatis.")

# -----------------------
# session state init
# -----------------------
if "data" not in st.session_state:
    st.session_state.data = []  # list of dicts: ID, Margin, Biaya_Akuisisi, CLV, Segment

# -----------------------
# Input form
# -----------------------
st.subheader("📝 Input Data Pelanggan")
with st.form("input_form", clear_on_submit=True):
    id_p = st.text_input("ID Pelanggan", max_chars=50)
    margin = st.number_input("Total Margin (Rp)", min_value=0, step=1000, format="%d")
    biaya = st.number_input("Biaya Akuisisi (Rp)", min_value=0, step=1000, format="%d")
    submitted = st.form_submit_button("Tambah / Simpan")

if submitted:
    # simple CLV model
    clv = int(margin) - int(biaya)
    # simple segmentation (ubah sesuai kebutuhan)
    if clv > 2500000:
        seg = "High Value"
    elif clv > 1000000:
        seg = "Mid Value"
    else:
        seg = "Low Value"

    st.session_state.data.append({
        "ID": id_p or f"ID_{len(st.session_state.data)+1}",
        "Margin": int(margin),
        "Biaya_Akuisisi": int(biaya),
        "CLV": clv,
        "Segment": seg
    })
    st.success(f"Data pelanggan '{id_p or '—'}' ditambahkan (CLV = {clv:,}).")

# -----------------------
# Optional: import CSV
# -----------------------
st.subheader("📥 (Opsional) Import CSV")
st.write("CSV harus mengandung kolom: ID, Margin, Biaya_Akuisisi")
csv_file = st.file_uploader("Upload CSV", type=["csv"])
if csv_file:
    try:
        df_csv = pd.read_csv(csv_file)
        if all(col in df_csv.columns for col in ["ID", "Margin", "Biaya_Akuisisi"]):
            for _, r in df_csv.iterrows():
                clv = int(r["Margin"]) - int(r["Biaya_Akuisisi"])
                if clv > 2500000:
                    seg = "High Value"
                elif clv > 1000000:
                    seg = "Mid Value"
                else:
                    seg = "Low Value"
                st.session_state.data.append({
                    "ID": r["ID"],
                    "Margin": int(r["Margin"]),
                    "Biaya_Akuisisi": int(r["Biaya_Akuisisi"]),
                    "CLV": clv,
                    "Segment": seg
                })
            st.success("CSV berhasil diimport.")
        else:
            st.error("CSV harus memiliki kolom: ID, Margin, Biaya_Akuisisi")
    except Exception as e:
        st.error(f"Gagal membaca CSV: {e}")

# -----------------------
# Data table & actions
# -----------------------
st.subheader("📄 Data Pelanggan")
if len(st.session_state.data) == 0:
    st.info("Belum ada data. Tambahkan melalui form atau import CSV.")
else:
    df = pd.DataFrame(st.session_state.data)
    st.dataframe(df, use_container_width=True)

    # simple delete per baris (index-based)
    to_delete = st.multiselect("Pilih baris (ID) untuk dihapus", options=df["ID"].tolist())
    if st.button("Hapus Terpilih") and to_delete:
        st.session_state.data = [d for d in st.session_state.data if d["ID"] not in to_delete]
        st.success("Baris terhapus.")
        st.experimental_rerun()

    # download csv
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Data (CSV)", data=csv_bytes, file_name="clv_data.csv", mime="text/csv")

# -----------------------
# Dashboard
# -----------------------
if len(st.session_state.data) > 0:
    st.subheader("📊 Dashboard")
    df = pd.DataFrame(st.session_state.data)

    col1, col2, col3 = st.columns([1,1,1])
    col1.metric("Total Pelanggan", len(df))
    col2.metric("Rata-rata CLV", f"Rp {int(df['CLV'].mean()):,}")
    col3.metric("Median CLV", f"Rp {int(df['CLV'].median()):,}")

    st.markdown("**Distribusi Segmentasi**")
    seg_count = df["Segment"].value_counts().rename_axis("Segment").reset_index(name="Jumlah")
    st.bar_chart(data=seg_count.set_index("Segment"))

    st.markdown("**Tabel ringkasan per segmen**")
    summary = df.groupby("Segment").agg(
        Jumlah=("ID", "count"),
        Avg_CLV=("CLV", "mean"),
        Median_CLV=("CLV", "median")
    ).reset_index()
    st.table(summary.style.format({"Avg_CLV":"{:,}", "Median_CLV":"{:,}"}))

st.caption("CLV simple model: CLV = Margin - Biaya Akuisisi. Ubah segmentasi / aturan jika diperlukan.")
