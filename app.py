import html
import re
from datetime import datetime
from urllib.parse import quote

import pandas as pd
import streamlit as st


# ---------- Konfigurasi (dari Streamlit Secrets) ----------
def secret(nama, default=""):
    try:
        return st.secrets.get(nama, default)
    except Exception:
        return default


SHEET_ID = secret("SHEET_ID")
SHEET_NAME = secret("SHEET_NAME", "Sheet1")
INSTANSI = secret("INSTANSI", "Pemerintah Daerah")
JUDUL = secret("JUDUL_SITUS", "Pusat Unduhan Berkas")
SUBJUDUL = secret("SUBJUDUL", "Unduh dokumen, format, dan formulir resmi dengan mudah dan cepat.")
LOGO_URL = secret("LOGO_URL", "")
KONTAK = secret("KONTAK", "")

st.set_page_config(page_title=JUDUL, page_icon="📥", layout="wide")

# ---------- Gaya (tema portal pemerintahan) ----------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --navy: #0B3B8C;
  --navy-dark: #072A66;
  --gold: #F2B705;
  --bg: #F4F7FB;
  --text: #1B2A41;
  --muted: #64748B;
  --line: #E2E8F0;
}
html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }
.stApp { background: var(--bg); }
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { max-width: 1120px; padding-top: 1.2rem; padding-bottom: 2rem; }

/* Bilah atas */
.topbar { display:flex; align-items:center; gap:12px; padding:6px 4px 14px 4px; }
.topbar img { height:44px; }
.topbar .inst { font-weight:700; color:var(--navy-dark); font-size:.95rem; letter-spacing:.02em; text-transform:uppercase; }

/* Hero */
.hero {
  background: linear-gradient(120deg, var(--navy-dark) 0%, var(--navy) 60%, #1E5BC6 100%);
  border-radius: 18px; padding: 44px 40px; color:#fff; position:relative; overflow:hidden;
  box-shadow: 0 10px 30px rgba(11,59,140,.25);
}
.hero::after {
  content:""; position:absolute; right:-60px; top:-60px; width:260px; height:260px;
  border-radius:50%; background: rgba(255,255,255,.07);
}
.hero::before {
  content:""; position:absolute; left:0; bottom:0; height:5px; width:100%;
  background: linear-gradient(90deg, var(--gold), transparent);
}
.hero .tag { display:inline-block; background:rgba(242,183,5,.18); color:var(--gold);
  padding:4px 12px; border-radius:999px; font-size:.78rem; font-weight:600; margin-bottom:14px; }
.hero h1 { color:#fff; font-size:2.2rem; font-weight:800; margin:0 0 8px 0; line-height:1.2; padding:0; }
.hero p { color:#D6E2F7; font-size:1.02rem; margin:0; max-width:620px; }

/* Statistik */
.stats { display:flex; gap:14px; margin:18px 0 6px 0; flex-wrap:wrap; }
.stat { background:#fff; border:1px solid var(--line); border-radius:12px; padding:12px 18px; min-width:150px; }
.stat b { display:block; font-size:1.4rem; color:var(--navy); font-weight:800; }
.stat span { color:var(--muted); font-size:.82rem; }

/* Input */
div[data-testid="stTextInput"] input, div[data-baseweb="select"] > div {
  background:#fff !important; border-radius:10px !important; border:1px solid var(--line) !important;
}
div[data-testid="stTextInput"] label, div[data-testid="stSelectbox"] label { font-weight:600; color:var(--text); }

/* Kartu */
.jumlah { color:var(--muted); font-size:.9rem; margin:10px 0 12px 2px; }
.grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap:16px; }
.card {
  background:#fff; border:1px solid var(--line); border-radius:14px; padding:18px;
  display:flex; flex-direction:column; gap:14px; transition:all .18s ease;
  border-top:3px solid transparent;
}
.card:hover { transform:translateY(-3px); box-shadow:0 12px 26px rgba(15,40,90,.12); border-top-color:var(--gold); }
.card .head { display:flex; gap:14px; align-items:flex-start; }
.ico { flex:0 0 44px; height:44px; border-radius:11px; background:#E8F0FD; color:var(--navy);
  display:flex; align-items:center; justify-content:center; }
.card h3 { margin:0; padding:0; font-size:1rem; font-weight:700; color:var(--text); line-height:1.4; }
.badge { display:inline-block; background:#FFF6D6; color:#8A6500; font-size:.72rem; font-weight:600;
  padding:2px 10px; border-radius:999px; margin-bottom:6px; }
.btn {
  display:flex; align-items:center; justify-content:center; gap:8px; text-decoration:none !important;
  background:var(--navy); color:#fff !important; padding:10px 14px; border-radius:10px;
  font-weight:600; font-size:.9rem; transition:background .15s;
}
.btn:hover { background:var(--navy-dark); }

/* Kosong & footer */
.kosong { text-align:center; background:#fff; border:1px dashed var(--line); border-radius:14px;
  padding:40px; color:var(--muted); }
.foot { margin-top:34px; padding-top:18px; border-top:1px solid var(--line); color:var(--muted);
  font-size:.85rem; display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px; }

@media (max-width:640px) {
  .hero { padding:30px 22px; } .hero h1 { font-size:1.6rem; }
}
</style>
""",
    unsafe_allow_html=True,
)

ICON_FILE = (
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
    '<polyline points="14 2 14 8 20 8"/><line x1="9" y1="13" x2="15" y2="13"/>'
    '<line x1="9" y1="17" x2="15" y2="17"/></svg>'
)
ICON_DOWN = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/>'
    '<line x1="12" y1="15" x2="12" y2="3"/></svg>'
)


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


def cari_kolom(df, *alias):
    peta = {c.lower(): c for c in df.columns}
    for a in alias:
        if a.lower() in peta:
            return peta[a.lower()]
    return None


def link_unduh(link: str):
    link = link.strip()
    if "/folders/" in link:
        return link, "Buka Folder"
    for pola in (r"/d/([a-zA-Z0-9_-]+)", r"[?&]id=([a-zA-Z0-9_-]+)"):
        m = re.search(pola, link)
        if m:
            return f"https://drive.google.com/uc?export=download&id={m.group(1)}", "Unduh Berkas"
    return link, "Buka Tautan"


def kartu(nama, kategori, link):
    url, label = link_unduh(link)
    badge = f'<span class="badge">{html.escape(kategori)}</span><br>' if kategori else ""
    return (
        '<div class="card">'
        f'<div class="head"><div class="ico">{ICON_FILE}</div>'
        f'<div>{badge}<h3>{html.escape(nama)}</h3></div></div>'
        f'<a class="btn" href="{html.escape(url, quote=True)}" target="_blank" rel="noopener">'
        f"{ICON_DOWN}{label}</a>"
        "</div>"
    )


# ---------- Tampilan ----------
logo = f'<img src="{html.escape(LOGO_URL, quote=True)}" alt="Logo">' if LOGO_URL else ""
st.markdown(
    f'<div class="topbar">{logo}<div class="inst">{html.escape(INSTANSI)}</div></div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="hero"><span class="tag">Layanan Berkas Digital</span>'
    f"<h1>{html.escape(JUDUL)}</h1><p>{html.escape(SUBJUDUL)}</p></div>",
    unsafe_allow_html=True,
)

if not SHEET_ID:
    st.error("SHEET_ID belum diatur. Isi di Settings → Secrets pada Streamlit Cloud.")
    st.stop()

try:
    df = muat_data(SHEET_ID, SHEET_NAME)
except Exception as e:
    st.error(
        "Gagal membaca Google Sheets. Pastikan akses sheet 'Siapa saja yang memiliki link' "
        "(Pelihat) dan nama tab sudah benar."
    )
    st.caption(f"Detail: {e}")
    st.stop()

k_nama = cari_kolom(df, "Nama Berkas", "Nama", "Judul")
k_link = cari_kolom(df, "Link", "Tautan")
k_kat = cari_kolom(df, "Kategori")

if not k_nama or not k_link:
    st.error("Baris pertama sheet harus berisi kolom: Nama Berkas, Kategori (opsional), Link.")
    st.stop()

data = pd.DataFrame(
    {
        "nama": df[k_nama].str.strip(),
        "kategori": df[k_kat].str.strip() if k_kat else "",
        "link": df[k_link].str.strip(),
    }
)
data = data[(data["nama"] != "") & (data["link"] != "")].reset_index(drop=True)
daftar_kategori = sorted({k for k in data["kategori"] if k})

st.markdown(
    f'<div class="stats"><div class="stat"><b>{len(data)}</b><span>Total berkas</span></div>'
    f'<div class="stat"><b>{len(daftar_kategori)}</b><span>Kategori</span></div></div>',
    unsafe_allow_html=True,
)

c1, c2 = st.columns([2, 1])
kata = c1.text_input("Cari berkas", placeholder="Ketik nama berkas...")
if daftar_kategori:
    pilih = c2.selectbox("Kategori", ["Semua kategori"] + daftar_kategori)
else:
    pilih = "Semua kategori"

hasil = data
if kata:
    hasil = hasil[hasil["nama"].str.lower().str.contains(kata.lower(), regex=False)]
if pilih != "Semua kategori":
    hasil = hasil[hasil["kategori"] == pilih]

if hasil.empty:
    st.markdown('<div class="kosong">Tidak ada berkas yang cocok dengan pencarian Anda.</div>',
                unsafe_allow_html=True)
else:
    st.markdown(f'<div class="jumlah">Menampilkan {len(hasil)} berkas</div>', unsafe_allow_html=True)
    cards = "".join(kartu(r.nama, r.kategori, r.link) for r in hasil.itertuples())
    st.markdown(f'<div class="grid">{cards}</div>', unsafe_allow_html=True)

kontak_html = f"<span>{html.escape(KONTAK)}</span>" if KONTAK else ""
st.markdown(
    f'<div class="foot"><span>© {datetime.now().year} {html.escape(INSTANSI)}</span>{kontak_html}</div>',
    unsafe_allow_html=True,
)

if st.button("Muat ulang data"):
    st.cache_data.clear()
    st.rerun()
