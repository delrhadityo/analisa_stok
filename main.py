import streamlit as st
import pandas as pd
from io import BytesIO

# Judul Aplikasi
st.set_page_config(page_title="Analisis Stok Barang", layout="wide")
st.title("📦 Analisis Stok Barang Multi Distributor")

# Inisialisasi session_state untuk menyimpan data gabungan
if "data_gabungan" not in st.session_state:
    st.session_state["data_gabungan"] = pd.DataFrame(
        columns=["No", "Distributor", "Kategori", "Nama Barang", "Stok", "Harga"]
    )

# Upload File Excel
uploaded_files = st.file_uploader(
    "Upload file Excel (bisa lebih dari 1):",
    type=["xlsx", "xls"],
    accept_multiple_files=True
)

# Jika ada file yang diupload
if uploaded_files:
    for file in uploaded_files:
        df = pd.read_excel(file)

        # Validasi kolom
        expected_cols = ["No", "Distributor", "Kategori", "Nama Barang", "Stok", "Harga"]
        if not all(col in df.columns for col in expected_cols):
            st.error(f"⚠️ Kolom file {file.name} tidak sesuai format!")
            st.stop()

        # Gabungkan data
        st.session_state["data_gabungan"] = pd.concat(
            [st.session_state["data_gabungan"], df], ignore_index=True
        )

# Ambil data gabungan
data = st.session_state["data_gabungan"]

# Jika sudah ada data, tampilkan filter & tabel
if not data.empty:
    st.subheader("🔍 Filter Data")

    # Buat kolom filter
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        distributor_filter = st.multiselect(
            "Pilih Distributor:",
            options=data["Distributor"].unique(),
            default=data["Distributor"].unique()
        )
    with col2:
        kategori_filter = st.multiselect(
            "Pilih Kategori:",
            options=data["Kategori"].unique(),
            default=data["Kategori"].unique()
        )
    with col3:
        harga_min, harga_max = st.slider(
            "Rentang Harga:",
            min_value=int(data["Harga"].min()),
            max_value=int(data["Harga"].max()),
            value=(int(data["Harga"].min()), int(data["Harga"].max()))
        )
    with col4:
        stok_min, stok_max = st.slider(
            "Rentang Stok:",
            min_value=int(data["Stok"].min()),
            max_value=int(data["Stok"].max()),
            value=(int(data["Stok"].min()), int(data["Stok"].max()))
        )

    # Tambahkan kolom pencarian nama barang
    search_name = st.text_input("🔎 Cari Nama Barang:", "")

    # Filter data sesuai input user
    filtered_data = data[
        (data["Distributor"].isin(distributor_filter)) &
        (data["Kategori"].isin(kategori_filter)) &
        (data["Harga"].between(harga_min, harga_max)) &
        (data["Stok"].between(stok_min, stok_max))
    ]

    # Jika ada input pencarian nama barang → filter berdasarkan keyword
    if search_name:
        filtered_data = filtered_data[
            filtered_data["Nama Barang"].str.contains(search_name, case=False, na=False)
        ]

    # Tampilkan hasil filter
    st.subheader("📊 Hasil Analisis Stok Barang")
    st.dataframe(filtered_data, use_container_width=True)

    # Download data sebagai Excel
    def convert_to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Stok Barang")
        processed_data = output.getvalue()
        return processed_data

    excel_data = convert_to_excel(filtered_data)
    st.download_button(
        label="📥 Download Hasil Filter",
        data=excel_data,
        file_name="hasil_analisis_stok.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("📌 Silakan upload minimal 1 file Excel untuk memulai analisis.")
