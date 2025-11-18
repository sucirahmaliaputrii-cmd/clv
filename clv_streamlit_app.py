import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from io import StringIO

st.set_page_config(page_title="CLV Calculator Advanced", layout="wide")

st.title("📊 Customer Lifetime Value (CLV) Calculator — Advanced Version")
st.write("Input data, edit, hapus, import CSV, dan simpan ke Google Sheets.")

# -------------------------------
# 🔐 GOOGLE SHEETS CONNECTION
# -------------------------------
st.sidebar.subheader("🔐 Google Sheet Settings")
sheet_url = st.sidebar.text_input("Google Sheet URL")
cred_file = st.sidebar.file_uploader("Upload Service Account JSON", type=["json"])

if cred_file and sheet_url:
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            eval(cred_file.getvalue().decode()),
            ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"],
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_url(sheet_url).sheet1
        st.sidebar.success("Terhubung dengan Google Sheet ✔")
    except Exception as e:
        st.sidebar.error(f"Gagal Koneksi: {e}")
        sheet = None
else:
    sheet = None

# -------------------------------
# 🔧 SESSION STATE for data
# -------------------------------
if "data" not in st.session_state:
    st.session_state.data = []
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# -------------------------------
# 📥 IMPORT CSV
# -------------------------------
st.subheader("📥 Import CSV")
csv_file = st.file_uploader("Upload file CSV", type=["csv"])

if csv_file:
    df_csv = pd.read_csv(csv_file)
    if all(col in df_csv.columns for col in ["ID", "Margin", "Biaya_Akuisisi"]):
        for _, row in df_csv.iterrows():
            clv = row["Margin"] - row["Biaya_Akuisisi"]
            seg = "High Value" if clv > 2500000 else "Mid Value" if clv > 1000000 else "Low Value"
            st.session_state.data.append({
                "ID": row["ID"],
                "Margin": row["Margin"],
                "Biaya_Akuisisi": row["Biaya_Akuisisi"],
                "CLV": clv,
                "Segment": seg
            })
        st.success("Import CSV berhasil!")
    else:
        st.error("CSV harus memiliki kolom: ID, Margin, Biaya_Akuisisi")

# -------------------------------
# 📝 INPUT MANUAL + EDIT MODE
# -------------------------------
st.subheader("📝 Input / Edit Data Pelanggan")

if st.session_state.edit_index is None:
    id_val = st.text_input("ID Pelanggan")
    margin_val = st.number_input("Total Margin", min_value=0, step=1000)
    cost_val = st.number_input("Biaya Akuisisi", min_value=0, step=1000)
else:
    data = st.session_state.data[st.session_state.edit_index]
    id_val = st.text_input("ID Pelanggan", value=data["ID"])
    margin_val = st.number_input("Total Margin", min_value=0, step=1000, value=data["Margin"])
    cost_val = st.number_input("Biaya Akuisisi", min_value=0, step=1000, value=data["Biaya_Akuisisi"])

colA, colB = st.columns(2)

if colA.button("Simpan"):
    clv = margin_val - cost_val
    seg = "High Value" if clv > 2500000 else "Mid Value" if clv > 1000000 else "Low Value"

    new_data = {"ID": id_val, "Margin": margin_val, "Biaya_Akuisisi": cost_val, "CLV": clv, "Segment": seg}

    if st.session_state.edit_index is None:
        st.session_state.data.append(new_data)
    else:
        st.session_state.data[st.session_state.edit_index] = new_data
        st.session_state.edit_index = None

    st.success("Data disimpan!")

if colB.button("Batal Edit"):
    st.session_state.edit_index = None

# -------------------------------
# 📄 TABEL DATA + EDIT/HAPUS
# -------------------------------
st.subheader("📄 Data Pelanggan (Editable)")

df = pd.DataFrame(st.session_state.data)

if len(df) > 0:
    st.dataframe(df, use_container_width=True)

    for i, row in df.iterrows():
        col1, col2 = st.columns(2)
        if col1.button(f"✏️ Edit {row['ID']}"):
            st.session_state.edit_index = i
        if col2.button(f"🗑️ Hapus {row['ID']}"):
            st.session_state.data.pop(i)
            st.experimental_rerun()

# -------------------------------
# 📈 DASHBOARD
# -------------------------------
if len(df) > 0:
    st.subheader("📊 Dashboard")
    seg_count = df["Segment"].value_counts()
    st.bar_chart(seg_count)

    col1, col2 = st.columns(2)
    col1.metric("Total Pelanggan", len(df))
    col2.metric("Rata-rata CLV", int(df["CLV"].mean()))

# -------------------------------
# 💾 SIMPAN KE GOOGLE SHEETS
# -------------------------------
st.subheader("💾 Simpan ke Google Sheets")
if sheet:
    if st.button("Upload Data"):
        try:
            sheet.clear()
            sheet.update([df.columns.values.tolist()] + df.values.tolist())
            st.success("Data berhasil disimpan ke Google Sheets!")
        except Exception as e:
            st.error(f"Gagal upload: {e}")
else:
    st.info("Isi Google Sheet URL & upload credentials untuk menyimpan data.")
