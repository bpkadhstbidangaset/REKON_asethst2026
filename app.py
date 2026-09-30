import re
from urllib.parse import quote

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Pusat Unduhan Berkas", page_icon="📥", layout="centered")


# ---------- Konfigurasi ----------
def ambil_secret(nama, default=""):
    try:
        return st.secrets.get(nama, default)
    except Exception:
        return default


SHEET_ID = ambil_secret("SHEET_ID")
SHEET_NAME = ambil_secret("SHEET_NAME", "Sheet1")
JUDUL_SITUS = ambil_secret("JUDUL_SITUS", "Pusat Unduhan Berkas")
SUBJUDUL = ambil_secret("SUBJUDUL", "Silakan cari dan unduh berkas yang Anda perlukan.")


# ---------- Data ----------
@st.cache_data(ttl=300, show_spinner="Memuat daftar berkas...")
def muat_data(sheet_id: str, sheet_name: str) -> pd.DataFrame:
    url = (
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq"
        f"?tqx=out:csv&sheet={quote(sheet_name)}"
    )
    df = pd.read_csv(url, dtype=str).fillna("")
    df.columns = [c.strip() for c in df.columns]
    return df


def id_dari_link(link: str) -> str:
    for pola in (r"/d/([a-zA-Z0-9_-]+)", r"[?&]id=([a-zA-Z0-9_-]+)"):
        m = re.search(pola, link)
        if m:
            return m.group(1)
    return ""


def link_unduh(link: str):
    """Kembalikan (url, label). Folder dibuka biasa, file diunduh langsung."""
    link = link.strip()
    if "/folders/" in link:
        return link, "📂 Buka Folder"
    fid = id_dari_link(link)
    if fid:
        return f"https://drive.google.com/uc?export=download&id={fid}", "⬇️ Unduh"
    return link, "🔗 Buka Tautan"


# ---------- Tampilan ----------
st.title(f"📥 {JUDUL_SITUS}")
st.caption(SUBJUDUL)

if not SHEET_ID:
    st.error("SHEET_ID belum diatur. Tambahkan di Settings → Secrets pada Streamlit Cloud.")
    st.stop()

try:
    df = muat_data(SHEET_ID, SHEET_NAME)
except Exception as e:
    st.error(
        "Gagal membaca Google Sheets. Pastikan akses sheet diatur "
        "'Siapa saja yang memiliki link' (Pelihat) dan nama sheet benar."
    )
    st.caption(f"Detail: {e}")
    st.stop()

wajib = {"Judul", "Link"}
if not wajib.issubset(df.columns):
    st.error("Sheet harus memiliki kolom 'Judul' dan 'Link' pada baris pertama.")
    st.stop()

for kolom in ("Kategori", "Deskripsi", "Tanggal", "Aktif"):
    if kolom not in df.columns:
        df[kolom] = ""

# Sembunyikan baris yang Aktif-nya "tidak"/"no"/"false"/"0", dan baris tanpa link
df = df[df["Link"].str.strip() != ""]
df = df[~df["Aktif"].str.strip().str.lower().isin(["tidak", "no", "false", "0", "n"])]

# Pencarian & filter
kolom_cari, kolom_kategori = st.columns([2, 1])
kata = kolom_cari.text_input("🔍 Cari berkas", placeholder="Ketik judul atau deskripsi...")

kategori = sorted({k.strip() for k in df["Kategori"] if k.strip()})
pilih = kolom_kategori.selectbox("Kategori", ["Semua"] + kategori)

hasil = df
if kata:
    k = kata.lower()
    hasil = hasil[
        hasil["Judul"].str.lower().str.contains(k, regex=False)
        | hasil["Deskripsi"].str.lower().str.contains(k, regex=False)
    ]
if pilih != "Semua":
    hasil = hasil[hasil["Kategori"].str.strip() == pilih]

st.write(f"**{len(hasil)}** berkas ditemukan")

if hasil.empty:
    st.info("Tidak ada berkas yang cocok.")

for i, baris in hasil.reset_index(drop=True).iterrows():
    with st.container(border=True):
        kiri, kanan = st.columns([4, 1], vertical_alignment="center")
        with kiri:
            st.subheader(baris["Judul"])
            info = " • ".join(x for x in (baris["Kategori"], baris["Tanggal"]) if x.strip())
            if info:
                st.caption(info)
            if baris["Deskripsi"].strip():
                st.write(baris["Deskripsi"])
        with kanan:
            url, label = link_unduh(baris["Link"])
            st.link_button(label, url, use_container_width=True)

st.divider()
if st.button("🔄 Muat ulang data"):
    st.cache_data.clear()
    st.rerun()
