import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import os
import base64
from io import BytesIO
import zipfile

# ==========================================================
# KONFIGURASI HALAMAN
# ==========================================================
st.set_page_config(
    page_title="3D Surface Flatness Detection",
    page_icon="🌸",
    layout="wide"
)

# ==========================================================
# TEMA GRADASI PASTEL DENGAN EFEK VISUAL LENGKAP
# ==========================================================
st.markdown("""
<style>
/* Background tetap sama */
html, body, [class*="stApp"] {
    background: linear-gradient(135deg, #ffe6f2, #fff0d9, #ede7ff) !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Main content dengan efek glass morphism */
section.main > div {
    background: linear-gradient(180deg, #fff5fb, #f7f2ff);
    padding: 28px;
    border-radius: 28px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    backdrop-filter: blur(5px);
    border: 1px solid rgba(255, 182, 217, 0.3);
    transition: all 0.3s ease;
}

section.main > div:hover {
    box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    border: 1px solid rgba(255, 182, 217, 0.5);
}

/* Tabs dengan efek hover lengkap */
button[data-baseweb="tab"] {
    background: linear-gradient(180deg, #ede7ff, #ffe6f2) !important;
    border-radius: 20px 20px 0 0;
    font-weight: bold;
    border: 2px solid #ffb6d9 !important;
    transition: all 0.3s ease !important;
}

button[data-baseweb="tab"]:hover {
    background: linear-gradient(180deg, #e6d6ff, #ffd6ec) !important;
    transform: translateY(-3px);
    box-shadow: 0 6px 15px rgba(255, 182, 217, 0.4) !important;
    border: 2px solid #ff6ec7 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(180deg, #cdb4ff, #ffb6d9) !important;
    color: white !important;
    box-shadow: 0 4px 8px rgba(205, 180, 255, 0.3);
}

button[data-baseweb="tab"][aria-selected="true"]:hover {
    background: linear-gradient(180deg, #c0a0ff, #ff9fd4) !important;
}

/* Headings dengan efek hover */
h1, h2, h3 {
    color: #cc0066;
    font-family: 'Comic Sans MS', 'Trebuchet MS', sans-serif;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    position: relative;
}

h1:hover, h2:hover, h3:hover {
    color: #ff6ec7;
    transform: translateX(5px);
}

h1::after, h2::after, h3::after {
    content: '';
    position: absolute;
    bottom: -5px;
    left: 0;
    width: 0;
    height: 2px;
    background: linear-gradient(90deg, #ff6ec7, #cdb4ff);
    transition: width 0.3s ease;
}

h1:hover::after, h2:hover::after, h3:hover::after {
    width: 100%;
}

/* Card dengan efek hover lengkap */
.card {
    background: linear-gradient(135deg, #ffe4f2, #e8dcff);
    padding: 22px;
    border-radius: 25px;
    margin-bottom: 20px;
    border: 2px solid #ffb6d9;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transition: left 0.5s ease;
}

.card:hover::before {
    left: 100%;
}

.card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 15px 30px rgba(255, 182, 217, 0.25);
    border: 2px solid #ff6ec7;
    background: linear-gradient(135deg, #ffe4f2, #e6d6ff);
}

/* Parameter box dengan efek hover */
.param-box {
    background: linear-gradient(180deg, #ffffff, #e3f2fd);
    padding: 20px;
    border-radius: 22px;
    border: 3px solid #cdb4ff;
    box-shadow: 0 6px 20px rgba(205, 180, 255, 0.15);
    transition: all 0.3s ease;
}

.param-box:hover {
    border: 3px solid #ff6ec7;
    box-shadow: 0 10px 25px rgba(205, 180, 255, 0.25);
    transform: translateY(-3px);
}

/* Upload box dengan efek hover */
.upload-box {
    background: linear-gradient(135deg, #e8f5e9, #f3e5f5);
    padding: 25px;
    border-radius: 25px;
    margin-top: 20px;
    border: 2px dashed #4caf50;
    transition: all 0.3s ease;
}

.upload-box:hover {
    border: 2px solid #4caf50;
    background: linear-gradient(135deg, #e0f2e1, #edd8f0);
    box-shadow: 0 8px 20px rgba(76, 175, 80, 0.2);
    transform: translateY(-3px);
}

/* Metric cards dengan efek hover lengkap */
.stMetric {
    background: linear-gradient(135deg, #e3f2fd, #fce4ec);
    border-radius: 15px;
    padding: 15px;
    border: 2px solid #ba68c8;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}

.stMetric:hover {
    transform: translateY(-5px) scale(1.05);
    box-shadow: 0 12px 24px rgba(186, 104, 200, 0.25);
    border: 2px solid #ff6ec7;
    background: linear-gradient(135deg, #d9ebfc, #fbd4e3);
}

/* Button efek hover lengkap */
.stButton > button {
    background: linear-gradient(135deg, #ff6ec7, #cdb4ff) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative;
    overflow: hidden;
}

.stButton > button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s ease;
}

.stButton > button:hover::before {
    left: 100%;
}

.stButton > button:hover {
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 8px 20px rgba(255, 110, 199, 0.4) !important;
    background: linear-gradient(135deg, #ff4db8, #b39bff) !important;
}

/* Select box dengan efek hover */
.stSelectbox, .stSlider, .stRadio {
    background: rgba(255, 255, 255, 0.1);
    padding: 15px;
    border-radius: 15px;
    backdrop-filter: blur(5px);
    border: 1px solid rgba(255, 182, 217, 0.3);
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.stSelectbox:hover, .stSlider:hover, .stRadio:hover {
    border: 1px solid rgba(255, 110, 199, 0.5);
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.1), 0 0 10px rgba(255, 110, 199, 0.1);
}

/* Image containers dengan efek hover */
.stImage {
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}

.stImage:hover {
    transform: scale(1.05);
    box-shadow: 0 12px 24px rgba(0,0,0,0.2);
    border-radius: 20px;
}

/* Alert boxes dengan efek hover */
.stAlert {
    border-radius: 10px !important;
    border: none !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    transition: all 0.3s ease !important;
}

.stAlert:hover {
    box-shadow: 0 8px 16px rgba(0,0,0,0.15) !important;
    transform: translateY(-2px);
}

/* Progress bar hover */
.stProgress > div > div {
    background: linear-gradient(90deg, #ff6ec7, #cdb4ff) !important;
    border-radius: 10px;
    transition: all 0.3s ease;
}

.stProgress > div > div:hover {
    background: linear-gradient(90deg, #ff4db8, #b39bff) !important;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
    transition: all 0.3s ease;
}

::-webkit-scrollbar-track {
    background: rgba(255, 182, 217, 0.1);
    border-radius: 4px;
}

::-webkit-scrollbar-track:hover {
    background: rgba(255, 182, 217, 0.2);
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #ff6ec7, #cdb4ff);
    border-radius: 4px;
    transition: all 0.3s ease;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #ff4db8, #b39bff);
    transform: scale(1.1);
}

/* Spinner hover */
.stSpinner {
    transition: all 0.3s ease;
}

.stSpinner:hover {
    transform: rotate(180deg);
}

/* Expander dengan efek hover */
.streamlit-expanderHeader {
    transition: all 0.3s ease !important;
}

.streamlit-expanderHeader:hover {
    background: linear-gradient(135deg, #ffe6f2, #e8dcff) !important;
    border-color: #ff6ec7 !important;
}

/* Checkbox dan radio button hover */
.stCheckbox, .stRadio > div {
    transition: all 0.3s ease;
    border-radius: 5px;
    padding: 5px;
}

.stCheckbox:hover, .stRadio > div:hover {
    background: rgba(255, 110, 199, 0.1);
    transform: translateX(3px);
}

/* Select box options hover */
[data-baseweb="select"] > div {
    transition: all 0.3s ease;
}

[data-baseweb="select"] > div:hover {
    background: rgba(255, 110, 199, 0.1) !important;
}

/* Text input hover */
.stTextInput > div > div {
    transition: all 0.3s ease;
}

.stTextInput > div > div:hover {
    border-color: #ff6ec7 !important;
    box-shadow: 0 0 0 1px #ff6ec7 !important;
}

/* Number input hover */
.stNumberInput > div > div {
    transition: all 0.3s ease;
}

.stNumberInput > div > div:hover {
    border-color: #ff6ec7 !important;
    box-shadow: 0 0 0 1px #ff6ec7 !important;
}

/* File uploader hover */
.stFileUploader > div {
    transition: all 0.3s ease;
}

.stFileUploader > div:hover {
    border-color: #4caf50 !important;
    background: rgba(76, 175, 80, 0.05);
}

/* Success message hover */
div[data-testid="stSuccess"] {
    transition: all 0.3s ease !important;
}

div[data-testid="stSuccess"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(76, 175, 80, 0.2) !important;
}

/* Error message hover */
div[data-testid="stError"] {
    transition: all 0.3s ease !important;
}

div[data-testid="stError"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(244, 67, 54, 0.2) !important;
}

/* Warning message hover */
div[data-testid="stWarning"] {
    transition: all 0.3s ease !important;
}

div[data-testid="stWarning"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(255, 152, 0, 0.2) !important;
}

/* Info message hover */
div[data-testid="stInfo"] {
    transition: all 0.3s ease !important;
}

div[data-testid="stInfo"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(33, 150, 243, 0.2) !important;
}

/* Dataframe hover */
.dataframe {
    transition: all 0.3s ease !important;
}

.dataframe:hover {
    box-shadow: 0 8px 16px rgba(0,0,0,0.15) !important;
    transform: translateY(-3px);
}

/* Table hover */
.stTable {
    transition: all 0.3s ease !important;
}

.stTable:hover {
    box-shadow: 0 8px 16px rgba(0,0,0,0.15) !important;
    transform: translateY(-3px);
}

/* Caption hover */
.stCaption {
    transition: all 0.3s ease;
}

.stCaption:hover {
    color: #ff6ec7 !important;
    transform: translateX(5px);
}

/* Badge hover */
.stBadge {
    transition: all 0.3s ease !important;
}

.stBadge:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
}

/* Divider hover */
hr {
    transition: all 0.3s ease;
}

hr:hover {
    border-color: #ff6ec7 !important;
    transform: scaleX(1.1);
}

/* Container untuk kartu anggota */
.member-card-container {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border-radius: 15px;
    padding: 10px;
}

.member-card-container:hover {
    transform: translateY(-8px) scale(1.05);
    background: linear-gradient(135deg, rgba(255, 240, 247, 0.9), rgba(255, 255, 255, 0.9));
    box-shadow: 0 15px 30px rgba(255, 110, 199, 0.25);
    border: 2px solid #ffe6f2;
}

/* Container untuk foto anggota */
.member-photo-container {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border-radius: 50%;
}

.member-photo-container:hover {
    transform: scale(1.1);
    box-shadow: 0 10px 20px rgba(255, 110, 199, 0.3);
    border: 4px solid #ffb6d9 !important;
}

/* Container untuk teknologi dan fitur */
.tech-feature-container {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border-radius: 20px;
    padding: 20px;
}

.tech-feature-container:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.15);
}

/* Container untuk kontak */
.contact-container {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border-radius: 20px;
    padding: 20px;
}

.contact-container:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.15);
}

/* Container untuk versi */
.version-container {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border-radius: 20px;
    padding: 20px;
}

.version-container:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.15);
}

/* Container untuk pesan penutup */
.closing-container {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border-radius: 25px;
    padding: 30px;
}

.closing-container:hover {
    transform: translateY(-5px) scale(1.01);
    box-shadow: 0 20px 40px rgba(255, 182, 217, 0.25);
    border: 3px solid #ffb6d9 !important;
}

/* Container untuk footer */
.footer-container {
    transition: all 0.3s ease;
    border-radius: 20px;
    padding: 20px;
}

.footer-container:hover {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(248, 248, 255, 0.9));
    box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

/* Hover untuk list items */
li {
    transition: all 0.3s ease;
    padding: 5px 10px;
    border-radius: 5px;
}

li:hover {
    background: rgba(255, 110, 199, 0.1);
    transform: translateX(10px);
    color: #ff6ec7;
}

/* Hover untuk paragraphs */
p {
    transition: all 0.3s ease;
}

p:hover {
    color: #666;
    transform: translateX(3px);
}

/* Hover untuk strong tags */
strong {
    transition: all 0.3s ease;
}

strong:hover {
    color: #ff6ec7;
    text-shadow: 0 0 10px rgba(255, 110, 199, 0.3);
}

/* Hover untuk em tags */
em {
    transition: all 0.3s ease;
}

em:hover {
    color: #4CAF50;
    transform: scale(1.1);
}

/* Hover untuk code blocks */
code {
    transition: all 0.3s ease;
    border-radius: 3px;
    padding: 2px 5px;
}

code:hover {
    background: rgba(255, 110, 199, 0.1);
    color: #ff6ec7;
    transform: scale(1.05);
}

/* Hover untuk links */
a {
    transition: all 0.3s ease;
    position: relative;
    text-decoration: none !important;
}

a::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 0;
    height: 2px;
    background: linear-gradient(90deg, #ff6ec7, #cdb4ff);
    transition: width 0.3s ease;
}

a:hover::after {
    width: 100%;
}

a:hover {
    color: #ff6ec7 !important;
    transform: translateY(-2px);
}

/* Hover untuk icons */
[class*="st-emotion-cache-"]:has(> span[role="img"]),
span[role="img"] {
    transition: all 0.3s ease;
    display: inline-block;
}

[class*="st-emotion-cache-"]:has(> span[role="img"]):hover,
span[role="img"]:hover {
    transform: scale(1.2) rotate(5deg);
    color: #ff6ec7 !important;
}

/* Hover untuk semua containers umum */
div[style*="border-radius"]:not(.st-emotion-cache):not([class*="st-"]):not(.card):not(.param-box):not(.upload-box):not(.stMetric) {
    transition: all 0.3s ease;
}

div[style*="border-radius"]:not(.st-emotion-cache):not([class*="st-"]):not(.card):not(.param-box):not(.upload-box):not(.stMetric):hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.1) !important;
}

/* Smooth transition untuk semua elemen */
* {
    transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# FUNGSI BANTUAN UNTUK PROSES ANALISIS
# ==========================================================
def process_single_image(img, enable_resize, target_width, enable_blur, blur_ksize, 
                         edge_method, canny_min=None, canny_max=None, sobel_kernel=None, 
                         laplacian_kernel=None, enable_contour=False, contour_color="#FF0000",
                         contour_thickness=2, contour_min_area=100, contour_mode="Outline Only"):
    """Fungsi untuk memproses satu gambar"""
    original_img = img.copy()
    
    # Preprocessing
    if enable_resize:
        height, width = img.shape[:2]
        aspect_ratio = height / width
        target_height = int(target_width * aspect_ratio)
        img = cv2.resize(img, (target_width, target_height))
        original_img = cv2.resize(original_img, (target_width, target_height))
    
    # Konversi ke grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian Blur jika diaktifkan
    if enable_blur:
        blur = cv2.GaussianBlur(gray, (blur_ksize, blur_ksize), 0)
    else:
        blur = gray
    
    # Edge Detection berdasarkan metode yang dipilih
    if edge_method == "Canny":
        edges = cv2.Canny(blur, canny_min, canny_max)
        method_text = f"Canny({canny_min},{canny_max})"
    elif edge_method == "Sobel":
        sobelx = cv2.Sobel(blur, cv2.CV_64F, 1, 0, ksize=sobel_kernel)
        sobely = cv2.Sobel(blur, cv2.CV_64F, 0, 1, ksize=sobel_kernel)
        edges = cv2.magnitude(sobelx, sobely)
        edges = cv2.convertScaleAbs(edges)
        method_text = f"Sobel(kernel={sobel_kernel})"
    else:  # Laplacian
        edges = cv2.Laplacian(blur, cv2.CV_64F, ksize=laplacian_kernel)
        edges = cv2.convertScaleAbs(edges)
        method_text = f"Laplacian(kernel={laplacian_kernel})"
    
    # Hitung Edge STD
    edge_std = np.std(edges)
    
    # Proses contour jika diaktifkan
    contour_image = None
    filtered_contours = []
    if enable_contour:
        contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        filtered_contours = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area >= contour_min_area:
                filtered_contours.append(cnt)
        
        if contour_mode == "Outline Only":
            contour_image = np.zeros_like(img)
            cv2.drawContours(contour_image, filtered_contours, -1, 
                           tuple(int(contour_color[i:i+2], 16) for i in (1, 3, 5)), 
                           contour_thickness)
        elif contour_mode == "Filled Contours":
            contour_image = np.zeros_like(img)
            cv2.drawContours(contour_image, filtered_contours, -1, 
                           tuple(int(contour_color[i:i+2], 16) for i in (1, 3, 5)), 
                           -1)
        else:  # Contours on Original
            contour_image = original_img.copy()
            cv2.drawContours(contour_image, filtered_contours, -1, 
                           tuple(int(contour_color[i:i+2], 16) for i in (1, 3, 5)), 
                           contour_thickness)
    
    return {
        'original_img': original_img,
        'blur': blur,
        'edges': edges,
        'edge_std': edge_std,
        'method_text': method_text,
        'contour_image': contour_image,
        'filtered_contours': filtered_contours
    }

# ==========================================================
# TAB MENU
# ==========================================================
tab_home, tab_analisis, tab_about = st.tabs(
    ["🏠 Home", "🔍 Analisis", "💖 Tentang Kami"]
)

# ==========================================================
# HOME - TAB 1
# ==========================================================
with tab_home:
    st.title("🌸 3D Surface Flatness Detection")
    
    col_welcome, col_illustration = st.columns([2, 1])
    
    with col_welcome:
        st.markdown("""
        <div class="card">
        <h3 style="color:#cc0066; text-align:center;">🎯 Selamat Datang di Aplikasi Deteksi Kerataan Permukaan 3D</h3>
        
        <p style="font-size:1.1em; line-height:1.6;">
        Aplikasi ini menggunakan teknik <b>Computer Vision</b> untuk menganalisis tingkat kerataan 
        permukaan pada objek 3D menggunakan metode <b>Edge Consistency Analysis</b>.
        </p>
        
        <h4 style="color:#9c27b0;">✨ Fitur Utama:</h4>
        <ul style="font-size:1em; line-height:1.8;">
        <li>🖼️ <b>Dataset gambar bawaan</b> - contoh gambar 3D</li>
        <li>📤 <b>Upload gambar custom</b> - Gunakan gambar Anda sendiri</li>
        <li>⚙️ <b>Parameter adjustable</b> - Sesuaikan pengolahan citra</li>
        <li>📊 <b>Visualisasi lengkap</b> - Grafik dan metrik detail</li>
        <li>💾 <b>Ekspor hasil</b> - Download laporan analisis</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col_illustration:
        st.markdown("""
        <div style="text-align:center; padding:20px; border-radius:15px; background:linear-gradient(135deg, #FFF0F7, #FFFFFF); 
                    border:2px solid #FFE6F2; transition:all 0.3s ease;" class="tech-feature-container">
        <h4 style="color:#9c27b0;">🚀 Mulai Analisis</h4>
        <p>Pilih tab <b>🔍 Analisis</b> untuk mulai!</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================================
# ANALISIS - TAB 2 (DENGAN FITUR UPLOAD MULTIPLE)
# ==========================================================
with tab_analisis:
    st.title("🔍✨ Analisis Kerataan Permukaan")
    
    # Membagi layout menjadi parameter dan processing
    col_param, col_proc = st.columns([1, 3])
    
    # ---------------- SIDEBAR PARAMETER ----------------
    with col_param:
        st.markdown("<div class='param-box'><h3>⚙ Parameter Pengolahan</h3>", unsafe_allow_html=True)
        
        # Parameter preprocessing
        st.markdown("#### 🌸 Preprocessing")
        enable_resize = st.checkbox("Resize otomatis", value=True)
        if enable_resize:
            target_width = st.slider("Lebar target", 300, 1200, 600)
        enable_blur = st.checkbox("Gaussian Blur", value=True)
        if enable_blur:
            blur_ksize = st.selectbox("Ukuran kernel", [3, 5, 7, 9], index=1)
        
        # Parameter edge detection
        st.markdown("#### ✂ Edge Detection")
        edge_method = st.radio(
            "Metode deteksi tepi:",
            ["Canny", "Sobel", "Laplacian"],
            horizontal=False
        )
        
        if edge_method == "Canny":
            canny_min = st.slider("Canny Min", 10, 200, 50, help="Ambang bawah untuk deteksi tepi")
            canny_max = st.slider("Canny Max", 50, 300, 150, help="Ambang atas untuk deteksi tepi")
        elif edge_method == "Sobel":
            sobel_kernel = st.selectbox("Kernel Sobel", [3, 5], index=0)
        else:  # Laplacian
            laplacian_kernel = st.selectbox("Kernel Laplacian", [3, 5], index=0)
        
        # Parameter threshold
        st.markdown("#### 📏 Threshold Kerataan")
        flatness_threshold = st.slider(
            "Ambang kerataan (Edge STD)", 
            5.0, 100.0, 25.0, 1.0,
            help="Nilai STD edge yang menentukan kerataan. Semakin kecil, semakin ketat"
        )
        
        # Parameter Contour Overlay
        st.markdown("#### 🎨 Contour Overlay")
        enable_contour = st.checkbox("Tampilkan kontur pada gambar", value=True)
        
        if enable_contour:
            contour_color = st.color_picker("Warna kontur", "#FF0000")
            contour_thickness = st.slider("Ketebalan kontur", 1, 10, 2)
            contour_min_area = st.slider("Area kontur minimum", 50, 1000, 100, 
                                        help="Kontur dengan area di bawah ini akan diabaikan")
            contour_mode = st.radio(
                "Mode overlay kontur:",
                ["Outline Only", "Filled Contours", "Contours on Original"],
                help="""Outline Only: Hanya garis kontur\n
                       Filled Contours: Kontur diisi dengan warna\n
                       Contours on Original: Kontur ditampilkan di atas gambar asli"""
            )
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ---------------- AREA PROCESSING ----------------
    with col_proc:
        # Pilihan sumber gambar
        image_source = st.radio(
            "Sumber Gambar:",
            ["📚 Dataset", "📤 Upload Manual"],
            horizontal=True
        )
        
        if image_source == "📚 Dataset":
            # DATASET GAMBAR 
            st.markdown("### 🖼 Pilih Gambar dari Dataset")
            
            # Dataset dengan gambar-gambar
            image_files = {
                "Lampu 3D": "ft1.jpeg",
                "Kertas Lipat": "ft2.jpeg", 
                "Tangga Ilusi": "ft3.jpeg",
                "Kubus 3D": "ft4.jpeg",
                "Lukisan 3D": "ft5.jpeg",
                "Kaligrafi 3D": "ft6.jpeg",
                "Rubik": "ft7.jpeg",
                "Buah 3D": "ft8.jpeg",
                "Lumba 3D": "ft9.jpeg",
                "Segitiga 3D": "ft10.jpeg",
                "Mawar 3D": "ft11.jpeg",
                "Bola 3D": "ft12.jpeg",
                "Ruang 3D": "ft13.jpeg",
                "Balok 3D": "ft14.jpeg",
                "Anime 3D": "ft15.jpg",
                "Bintang": "ft16.jpg",
                "Kupu-Kupu 3D": "ft17.jpg",
                "Ngintip 3D": "ft18.jpg",
                "Es 3D": "ft19.jpg",
                "Dadu 3D": "ft20.jpg"
            }
            
            # Cek file yang tersedia
            available_images = {}
            for name, filename in image_files.items():
                if os.path.exists(filename):
                    available_images[name] = filename
                else:
                    st.warning(f"File {filename} tidak ditemukan. Pastikan file ada di folder yang sama.")
            
            if available_images:
                selected_name = st.selectbox(
                    "Pilih gambar contoh:",
                    list(available_images.keys()),
                    help="Pilih salah satu gambar dari dataset untuk dianalisis"
                )
                
                image_path = available_images[selected_name]
                
                # Tombol proses
                if st.button("🚀 Proses Analisis", type="primary", use_container_width=True):
                    with st.spinner("🔍 Menganalisis gambar..."):
                        try:
                            # Baca gambar
                            image = Image.open(image_path)
                            img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                            
                            # Proses gambar menggunakan fungsi
                            results = process_single_image(
                                img, enable_resize, target_width, enable_blur, blur_ksize,
                                edge_method, canny_min if edge_method == "Canny" else None,
                                canny_max if edge_method == "Canny" else None,
                                sobel_kernel if edge_method == "Sobel" else None,
                                laplacian_kernel if edge_method == "Laplacian" else None,
                                enable_contour, contour_color, contour_thickness,
                                contour_min_area, contour_mode
                            )
                            
                            edge_std = results['edge_std']
                            
                            # Tentukan status
                            if edge_std <= flatness_threshold:
                                status = "RATA ✨"
                                color = "#4CAF50"
                                icon = "✅"
                            else:
                                status = "TIDAK RATA 💥"
                                color = "#F44336"
                                icon = "⚠️"
                            
                            # Display hasil
                            st.success(f"Analisis selesai! {icon}")
                            
                            # Tampilkan gambar dalam 3 atau 4 kolom tergantung apakah kontur diaktifkan
                            st.subheader("📷 Visualisasi Hasil")
                            
                            if enable_contour and results['contour_image'] is not None:
                                c1, c2, c3, c4 = st.columns(4)
                                
                                with c1:
                                    st.image(results['original_img'], caption="🖼 Gambar Asli", use_container_width=True)
                                    st.caption(f"Ukuran: {results['original_img'].shape[1]}x{results['original_img'].shape[0]}")
                                
                                with c2:
                                    st.image(results['blur'], caption="🌙 Grayscale + Blur", use_container_width=True)
                                    st.caption(f"Kernel: {blur_ksize}x{blur_ksize}")
                                
                                with c3:
                                    st.image(results['edges'], caption=f"✂ {edge_method} Edges", use_container_width=True)
                                    st.caption(results['method_text'])
                                
                                with c4:
                                    contour_text = f"🎨 {contour_mode}"
                                    st.image(results['contour_image'], caption=contour_text, use_container_width=True)
                                    st.caption(f"Total {len(results['filtered_contours'])} kontur ditemukan")
                            else:
                                c1, c2, c3 = st.columns(3)
                                
                                with c1:
                                    st.image(results['original_img'], caption="🖼 Gambar Asli", use_container_width=True)
                                    st.caption(f"Ukuran: {results['original_img'].shape[1]}x{results['original_img'].shape[0]}")
                                
                                with c2:
                                    st.image(results['blur'], caption="🌙 Grayscale + Blur", use_container_width=True)
                                    st.caption(f"Kernel: {blur_ksize}x{blur_ksize}")
                                
                                with c3:
                                    st.image(results['edges'], caption=f"✂ {edge_method} Edges", use_container_width=True)
                                    st.caption(results['method_text'])
                            
                            # Tampilkan metrik dan status
                            st.markdown("---")
                            st.subheader("📊 Hasil Analisis")
                            
                            # Metrik dalam cards
                            if enable_contour:
                                col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
                            else:
                                col_metric1, col_metric2, col_metric3 = st.columns(3)
                            
                            with col_metric1:
                                st.markdown(f"""
                                <div class="stMetric">
                                <h4 style="color:#9c27b0;">📐 Edge STD</h4>
                                <h2 style="color:#2196F3; text-align:center;">{edge_std:.2f}</h2>
                                <p style="text-align:center;">Standar Deviasi Edge</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col_metric2:
                                st.markdown(f"""
                                <div class="stMetric">
                                <h4 style="color:#9c27b0;">🎯 Ambang</h4>
                                <h2 style="color:#FF9800; text-align:center;">{flatness_threshold:.1f}</h2>
                                <p style="text-align:center;">Batas Kerataan</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col_metric3:
                                st.markdown(f"""
                                <div class="stMetric">
                                <h4 style="color:#9c27b0;">📈 Status</h4>
                                <h2 style="color:{color}; text-align:center;">{status}</h2>
                                <p style="text-align:center;">Tingkat Kerataan</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            if enable_contour and results['contour_image'] is not None:
                                with col_metric4:
                                    st.markdown(f"""
                                    <div class="stMetric">
                                    <h4 style="color:#9c27b0;">🔍 Kontur</h4>
                                    <h2 style="color:#9C27B0; text-align:center;">{len(results['filtered_contours'])}</h2>
                                    <p style="text-align:center;">Jumlah Kontur</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            # Visualisasi grafik - DIAGRAM PERBANDINGAN
                            st.subheader("📈 Diagram Perbandingan")
                            
                            if enable_contour:
                                fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
                            else:
                                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
                            
                            # Bar chart edge vs threshold
                            bars1 = ax1.bar(["Edge STD", "Ambang"], [edge_std, flatness_threshold],
                                         color=['#FF6B8B', '#4ECDC4'], edgecolor='#333', linewidth=2)
                            ax1.axhline(y=flatness_threshold, color='red', linestyle='--', alpha=0.5)
                            ax1.set_title("Perbandingan Nilai Edge", fontsize=12, fontweight='bold')
                            ax1.set_ylabel("Nilai STD")
                            ax1.grid(True, alpha=0.3)
                            
                            for bar in bars1:
                                height = bar.get_height()
                                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                                       f'{height:.1f}', ha='center', va='bottom')
                            
                            # Pie chart status
                            if edge_std <= flatness_threshold:
                                sizes = [edge_std, flatness_threshold - edge_std]
                                colors_pie = ['#4CAF50', '#E0E0E0']
                                explode = (0.1, 0)
                            else:
                                sizes = [flatness_threshold, edge_std - flatness_threshold]
                                colors_pie = ['#F44336', '#FFCDD2']
                                explode = (0, 0.1)
                            
                            ax2.pie(sizes, explode=explode, colors=colors_pie,
                                  autopct='%1.1f%%', shadow=True, startangle=90)
                            ax2.set_title(f"Status: {status}", fontsize=12, fontweight='bold')
                            
                            if enable_contour:
                                # Histogram area kontur
                                if results['filtered_contours']:
                                    areas = [cv2.contourArea(cnt) for cnt in results['filtered_contours']]
                                    ax3.hist(areas, bins=10, color='#FFB6C1', edgecolor='black')
                                    ax3.set_title("Distribusi Area Kontur", fontsize=12, fontweight='bold')
                                    ax3.set_xlabel("Area Kontur")
                                    ax3.set_ylabel("Frekuensi")
                                    ax3.grid(True, alpha=0.3)
                                else:
                                    ax3.text(0.5, 0.5, "Tidak ada kontur\nditemukan", 
                                           ha='center', va='center', fontsize=12)
                                    ax3.set_title("Distribusi Area Kontur", fontsize=12, fontweight='bold')
                                
                                # Scatter plot kontur
                                if results['filtered_contours']:
                                    x_coords = []
                                    y_coords = []
                                    for cnt in results['filtered_contours']:
                                        M = cv2.moments(cnt)
                                        if M["m00"] != 0:
                                            cx = int(M["m10"] / M["m00"])
                                            cy = int(M["m01"] / M["m00"])
                                            x_coords.append(cx)
                                            y_coords.append(cy)
                                    
                                    if x_coords and y_coords:
                                        ax4.scatter(x_coords, y_coords, color='#9C27B0', s=50, alpha=0.6)
                                        ax4.set_title("Posisi Pusat Kontur", fontsize=12, fontweight='bold')
                                        ax4.set_xlabel("X Coordinate")
                                        ax4.set_ylabel("Y Coordinate")
                                        ax4.invert_yaxis()
                                        ax4.grid(True, alpha=0.3)
                                    else:
                                        ax4.text(0.5, 0.5, "Tidak dapat menghitung\npusat kontur", 
                                               ha='center', va='center', fontsize=12)
                                        ax4.set_title("Posisi Pusat Kontur", fontsize=12, fontweight='bold')
                                else:
                                    ax4.text(0.5, 0.5, "Tidak ada kontur\nditemukan", 
                                           ha='center', va='center', fontsize=12)
                                    ax4.set_title("Posisi Pusat Kontur", fontsize=12, fontweight='bold')
                            
                            plt.tight_layout()
                            st.pyplot(fig)
                            
                            # Detail analisis - TANPA JSON
                            with st.expander("🔍 Detail Teknis Analisis", expanded=False):
                                col_detail1, col_detail2 = st.columns(2)
                                
                                with col_detail1:
                                    st.markdown("#### ⚙️ Parameter Pengolahan")
                                    st.write(f"**Resize:** {'Aktif' if enable_resize else 'Tidak Aktif'}")
                                    if enable_resize:
                                        st.write(f"- Target Width: {target_width}px")
                                    st.write(f"**Gaussian Blur:** {'Aktif' if enable_blur else 'Tidak Aktif'}")
                                    if enable_blur:
                                        st.write(f"- Kernel Size: {blur_ksize}x{blur_ksize}")
                                    st.write(f"**Metode Edge:** {edge_method}")
                                    st.write(f"- Detail: {results['method_text']}")
                                
                                with col_detail2:
                                    st.markdown("#### 📊 Hasil Analisis")
                                    st.write(f"**Edge STD:** {edge_std:.2f}")
                                    st.write(f"**Ambang Kerataan:** {flatness_threshold:.1f}")
                                    st.write(f"**Status:** {status}")
                                    if enable_contour:
                                        st.write(f"**Jumlah Kontur:** {len(results['filtered_contours'])}")
                                    st.write(f"**Keputusan:** {'RATA' if edge_std <= flatness_threshold else 'TIDAK RATA'}")
                                    st.write(f"**Waktu Analisis:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            
                            # ==========================================================
                            # BAGIAN EKSPOR HASIL TANPA JSON
                            # ==========================================================
                            st.markdown("---")
                            st.subheader("💾 Ekspor Hasil")
                            
                            # Buat ZIP file yang berisi semua gambar hasil
                            zip_buffer = io.BytesIO()
                            
                            # Simpan semua gambar ke dalam ZIP
                            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                # 1. Simpan gambar asli
                                original_rgb = cv2.cvtColor(results['original_img'], cv2.COLOR_BGR2RGB)
                                original_pil = Image.fromarray(original_rgb)
                                original_buffer = io.BytesIO()
                                original_pil.save(original_buffer, format='PNG')
                                original_buffer.seek(0)
                                zip_file.writestr(f"original_{selected_name}.png", original_buffer.read())
                                
                                # 2. Simpan gambar blur
                                blur_pil = Image.fromarray(results['blur'])
                                blur_buffer = io.BytesIO()
                                blur_pil.save(blur_buffer, format='PNG')
                                blur_buffer.seek(0)
                                zip_file.writestr(f"blur_{selected_name}.png", blur_buffer.read())
                                
                                # 3. Simpan gambar edges
                                edges_pil = Image.fromarray(results['edges'])
                                edges_buffer = io.BytesIO()
                                edges_pil.save(edges_buffer, format='PNG')
                                edges_buffer.seek(0)
                                zip_file.writestr(f"edges_{selected_name}.png", edges_buffer.read())
                                
                                # 4. Simpan gambar kontur jika ada
                                if enable_contour and results['contour_image'] is not None:
                                    contour_rgb = cv2.cvtColor(results['contour_image'], cv2.COLOR_BGR2RGB)
                                    contour_pil = Image.fromarray(contour_rgb)
                                    contour_buffer = io.BytesIO()
                                    contour_pil.save(contour_buffer, format='PNG')
                                    contour_buffer.seek(0)
                                    zip_file.writestr(f"contour_{selected_name}.png", contour_buffer.read())
                                
                                # 5. Simpan CSV report (tanpa JSON)
                                results_df = pd.DataFrame({
                                    "Parameter": ["Gambar", "Metode Edge", "Edge STD", "Ambang", "Status", "Jumlah Kontur", "Waktu"],
                                    "Nilai": [selected_name, results['method_text'], f"{edge_std:.2f}", 
                                             f"{flatness_threshold:.1f}", status, 
                                             f"{len(results['filtered_contours']) if enable_contour else 'N/A'}", 
                                             datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                                })
                                csv_data = results_df.to_csv(index=False)
                                zip_file.writestr(f"report_{selected_name}.csv", csv_data)
                                
                                # 6. Simpan metadata sebagai TEXT file (bukan JSON)
                                metadata_text = f"""HASIL ANALISIS KERATAAN PERMUKAAN 3D
===========================================
Nama Gambar: {selected_name}
Tanggal Analisis: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

PARAMETER PENGGUNAAN:
=====================
1. Preprocessing:
   - Resize: {'Aktif' if enable_resize else 'Tidak Aktif'}
   - Target Width: {target_width if enable_resize else 'N/A'} px
   - Gaussian Blur: {'Aktif' if enable_blur else 'Tidak Aktif'}
   - Blur Kernel: {blur_ksize if enable_blur else 'N/A'}

2. Edge Detection:
   - Metode: {edge_method}
   - Detail: {results['method_text']}

3. Threshold Kerataan:
   - Ambang: {flatness_threshold:.1f}

4. Contour Analysis:
   - Aktif: {'Ya' if enable_contour else 'Tidak'}
   - Mode: {contour_mode if enable_contour else 'N/A'}
   - Area Minimum: {contour_min_area if enable_contour else 'N/A'}

HASIL ANALISIS:
===============
- Edge STD: {edge_std:.2f}
- Status: {status}
- Jumlah Kontur: {len(results['filtered_contours']) if enable_contour else 0}
- Keputusan: {'RATA' if edge_std <= flatness_threshold else 'TIDAK RATA'}

-------------------------------------------
Aplikasi 3D Surface Flatness Detection
Dibuat untuk pembelajaran Computer Vision
© sanadhiri2025
"""
                                zip_file.writestr(f"metadata_{selected_name}.txt", metadata_text)
                            
                            zip_buffer.seek(0)
                            
                            # Simpan diagram perbandingan ke buffer terpisah
                            diagram_buffer = io.BytesIO()
                            fig.savefig(diagram_buffer, format='png', dpi=150, bbox_inches='tight')
                            diagram_buffer.seek(0)
                            
                            # Tombol download
                            if enable_contour:
                                col_dl1, col_dl2, col_dl3 = st.columns(3)
                            else:
                                col_dl1, col_dl2 = st.columns(2)
                            
                            with col_dl1:
                                st.download_button(
                                    label="📦 Download All Files (ZIP)",
                                    data=zip_buffer,
                                    file_name=f"hasil_analisis_{selected_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                    mime="application/zip"
                                )
                            
                            with col_dl2:
                                st.download_button(
                                    label="📊 Download Comparison Diagram",
                                    data=diagram_buffer,
                                    file_name=f"diagram_perbandingan_{selected_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                    mime="image/png"
                                )
                            
                            if enable_contour and results['contour_image'] is not None:
                                with col_dl3:
                                    contour_buf = io.BytesIO()
                                    contour_rgb = cv2.cvtColor(results['contour_image'], cv2.COLOR_BGR2RGB)
                                    contour_pil = Image.fromarray(contour_rgb)
                                    contour_pil.save(contour_buf, format='PNG')
                                    contour_buf.seek(0)
                                    
                                    st.download_button(
                                        label="🎨 Download Contour Image",
                                        data=contour_buf,
                                        file_name=f"contour_{selected_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                        mime="image/png"
                                    )
                            
                        except Exception as e:
                            st.error(f"❌ Terjadi error saat memproses gambar: {str(e)}")
            else:
                st.warning("⚠️ Tidak ada gambar yang tersedia di dataset.")
                st.info("Pastikan file-file berikut ada di folder yang sama dengan aplikasi:")
                for name, filename in image_files.items():
                    st.write(f"- {filename}")
        
        else:  # UPLOAD SENDIRI
            st.markdown("<div class='upload-box'>", unsafe_allow_html=True)
            st.markdown("### 📤 Upload Gambar Anda")
            
            # UPLOAD MULTIPLE GAMBAR
            uploaded_files = st.file_uploader(
                "Pilih gambar dari komputer Anda (bisa lebih dari 1):",
                type=["jpg", "jpeg", "png", "bmp"],
                help="Upload satu atau lebih gambar yang ingin dianalisis",
                accept_multiple_files=True
            )
            
            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} gambar berhasil diupload")
                
                # Pilihan mode: Single atau Multiple Analysis
                analysis_mode = st.radio(
                    "Pilih Mode Analisis:",
                    ["🔍 Analisis Gambar Pilihan", "📊 Analisis Semua Gambar"],
                    horizontal=True,
                    help="Analisis satu gambar yang dipilih atau analisis semua gambar sekaligus"
                )
                
                # Buat tab untuk preview gambar
                if len(uploaded_files) > 1:
                    st.markdown("#### 👁 Preview Gambar yang Diupload")
                    tab_names = [f"Gambar {i+1}" for i in range(len(uploaded_files))]
                    tabs = st.tabs(tab_names)
                    
                    for i, tab in enumerate(tabs):
                        with tab:
                            image = Image.open(uploaded_files[i])
                            st.image(image, caption=f"Gambar {i+1}: {uploaded_files[i].name}", use_container_width=True)
                
                if analysis_mode == "🔍 Analisis Gambar Pilihan":
                    # Pilih gambar tertentu untuk dianalisis
                    if len(uploaded_files) > 1:
                        selected_index = st.selectbox(
                            "Pilih gambar untuk dianalisis:",
                            range(len(uploaded_files)),
                            format_func=lambda x: f"{x+1}. {uploaded_files[x].name}"
                        )
                        selected_file = uploaded_files[selected_index]
                    else:
                        selected_file = uploaded_files[0]
                    
                    # Tampilkan preview gambar yang dipilih
                    st.markdown(f"#### 🎯 Gambar yang Dipilih: **{selected_file.name}**")
                    image = Image.open(selected_file)
                    st.image(image, caption=f"Preview: {selected_file.name}", use_container_width=True)
                    
                    # Tombol proses untuk single image
                    if st.button("🚀 Analisis Gambar Pilihan", type="primary", use_container_width=True):
                        with st.spinner("🔍 Menganalisis gambar yang dipilih..."):
                            try:
                                # Proses gambar tunggal
                                img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                                
                                results = process_single_image(
                                    img, enable_resize, target_width, enable_blur, blur_ksize,
                                    edge_method, canny_min if edge_method == "Canny" else None,
                                    canny_max if edge_method == "Canny" else None,
                                    sobel_kernel if edge_method == "Sobel" else None,
                                    laplacian_kernel if edge_method == "Laplacian" else None,
                                    enable_contour, contour_color, contour_thickness,
                                    contour_min_area, contour_mode
                                )
                                
                                edge_std = results['edge_std']
                                
                                if edge_std <= flatness_threshold:
                                    status = "RATA ✨"
                                    color = "#4CAF50"
                                    icon = "✅"
                                else:
                                    status = "TIDAK RATA 💥"
                                    color = "#F44336"
                                    icon = "⚠️"
                                
                                st.success(f"Analisis selesai! {icon}")
                                
                                # Tampilkan gambar hasil
                                st.subheader("📷 Visualisasi Hasil")
                                
                                if enable_contour and results['contour_image'] is not None:
                                    c1, c2, c3, c4 = st.columns(4)
                                    
                                    with c1:
                                        st.image(results['original_img'], caption="🖼 Gambar Asli", use_container_width=True)
                                    
                                    with c2:
                                        st.image(results['blur'], caption="🌙 Grayscale + Blur", use_container_width=True)
                                    
                                    with c3:
                                        st.image(results['edges'], caption=f"✂ {edge_method} Edges", use_container_width=True)
                                    
                                    with c4:
                                        contour_text = f"🎨 {contour_mode}"
                                        st.image(results['contour_image'], caption=contour_text, use_container_width=True)
                                else:
                                    c1, c2, c3 = st.columns(3)
                                    
                                    with c1:
                                        st.image(results['original_img'], caption="🖼 Gambar Asli", use_container_width=True)
                                    
                                    with c2:
                                        st.image(results['blur'], caption="🌙 Grayscale + Blur", use_container_width=True)
                                    
                                    with c3:
                                        st.image(results['edges'], caption=f"✂ {edge_method} Edges", use_container_width=True)
                                
                                # Metrik
                                st.markdown("---")
                                st.subheader("📊 Hasil Analisis")
                                
                                if enable_contour:
                                    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                                else:
                                    col_m1, col_m2, col_m3 = st.columns(3)
                                
                                with col_m1:
                                    st.metric("📐 Edge STD", f"{edge_std:.2f}")
                                with col_m2:
                                    st.metric("🎯 Ambang", f"{flatness_threshold:.1f}")
                                with col_m3:
                                    st.markdown(f"<h3 style='color:{color}; text-align:center;'>{status}</h3>", unsafe_allow_html=True)
                                if enable_contour:
                                    with col_m4:
                                        st.metric("🔍 Kontur", f"{len(results['filtered_contours'])}")
                                
                                # DIAGRAM PERBANDINGAN UNTUK UPLOAD SINGLE
                                st.subheader("📈 Diagram Perbandingan")
                                
                                if enable_contour:
                                    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
                                else:
                                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
                                
                                # Bar chart edge vs threshold
                                bars1 = ax1.bar(["Edge STD", "Ambang"], [edge_std, flatness_threshold],
                                             color=['#FF6B8B', '#4ECDC4'], edgecolor='#333', linewidth=2)
                                ax1.axhline(y=flatness_threshold, color='red', linestyle='--', alpha=0.5)
                                ax1.set_title("Perbandingan Nilai Edge", fontsize=12, fontweight='bold')
                                ax1.set_ylabel("Nilai STD")
                                ax1.grid(True, alpha=0.3)
                                
                                for bar in bars1:
                                    height = bar.get_height()
                                    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                                           f'{height:.1f}', ha='center', va='bottom')
                                
                                # Pie chart status
                                if edge_std <= flatness_threshold:
                                    sizes = [edge_std, flatness_threshold - edge_std]
                                    colors_pie = ['#4CAF50', '#E0E0E0']
                                    explode = (0.1, 0)
                                else:
                                    sizes = [flatness_threshold, edge_std - flatness_threshold]
                                    colors_pie = ['#F44336', '#FFCDD2']
                                    explode = (0, 0.1)
                                
                                ax2.pie(sizes, explode=explode, colors=colors_pie,
                                      autopct='%1.1f%%', shadow=True, startangle=90)
                                ax2.set_title(f"Status: {status}", fontsize=12, fontweight='bold')
                                
                                if enable_contour:
                                    # Histogram area kontur
                                    if results['filtered_contours']:
                                        areas = [cv2.contourArea(cnt) for cnt in results['filtered_contours']]
                                        ax3.hist(areas, bins=10, color='#FFB6C1', edgecolor='black')
                                        ax3.set_title("Distribusi Area Kontur", fontsize=12, fontweight='bold')
                                        ax3.set_xlabel("Area Kontur")
                                        ax3.set_ylabel("Frekuensi")
                                        ax3.grid(True, alpha=0.3)
                                    else:
                                        ax3.text(0.5, 0.5, "Tidak ada kontur\nditemukan", 
                                               ha='center', va='center', fontsize=12)
                                        ax3.set_title("Distribusi Area Kontur", fontsize=12, fontweight='bold')
                                    
                                    # Scatter plot kontur
                                    if results['filtered_contours']:
                                        x_coords = []
                                        y_coords = []
                                        for cnt in results['filtered_contours']:
                                            M = cv2.moments(cnt)
                                            if M["m00"] != 0:
                                                cx = int(M["m10"] / M["m00"])
                                                cy = int(M["m01"] / M["m00"])
                                                x_coords.append(cx)
                                                y_coords.append(cy)
                                        
                                        if x_coords and y_coords:
                                            ax4.scatter(x_coords, y_coords, color='#9C27B0', s=50, alpha=0.6)
                                            ax4.set_title("Posisi Pusat Kontur", fontsize=12, fontweight='bold')
                                            ax4.set_xlabel("X Coordinate")
                                            ax4.set_ylabel("Y Coordinate")
                                            ax4.invert_yaxis()
                                            ax4.grid(True, alpha=0.3)
                                        else:
                                            ax4.text(0.5, 0.5, "Tidak dapat menghitung\npusat kontur", 
                                                   ha='center', va='center', fontsize=12)
                                            ax4.set_title("Posisi Pusat Kontur", fontsize=12, fontweight='bold')
                                    else:
                                        ax4.text(0.5, 0.5, "Tidak ada kontur\nditemukan", 
                                               ha='center', va='center', fontsize=12)
                                        ax4.set_title("Posisi Pusat Kontur", fontsize=12, fontweight='bold')
                                
                                plt.tight_layout()
                                st.pyplot(fig)
                                
                                # Ekspor hasil untuk single upload - TANPA JSON
                                st.markdown("---")
                                st.subheader("💾 Ekspor Hasil")
                                
                                zip_buffer = io.BytesIO()
                                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                    original_rgb = cv2.cvtColor(results['original_img'], cv2.COLOR_BGR2RGB)
                                    original_pil = Image.fromarray(original_rgb)
                                    original_buffer = io.BytesIO()
                                    original_pil.save(original_buffer, format='PNG')
                                    original_buffer.seek(0)
                                    zip_file.writestr(f"original_{selected_file.name}.png", original_buffer.read())
                                    
                                    blur_pil = Image.fromarray(results['blur'])
                                    blur_buffer = io.BytesIO()
                                    blur_pil.save(blur_buffer, format='PNG')
                                    blur_buffer.seek(0)
                                    zip_file.writestr(f"blur_{selected_file.name}.png", blur_buffer.read())
                                    
                                    edges_pil = Image.fromarray(results['edges'])
                                    edges_buffer = io.BytesIO()
                                    edges_pil.save(edges_buffer, format='PNG')
                                    edges_buffer.seek(0)
                                    zip_file.writestr(f"edges_{selected_file.name}.png", edges_buffer.read())
                                    
                                    if enable_contour and results['contour_image'] is not None:
                                        contour_rgb = cv2.cvtColor(results['contour_image'], cv2.COLOR_BGR2RGB)
                                        contour_pil = Image.fromarray(contour_rgb)
                                        contour_buffer = io.BytesIO()
                                        contour_pil.save(contour_buffer, format='PNG')
                                        contour_buffer.seek(0)
                                        zip_file.writestr(f"contour_{selected_file.name}.png", contour_buffer.read())
                                    
                                    results_df = pd.DataFrame({
                                        "Parameter": ["Gambar", "Metode Edge", "Edge STD", "Ambang", "Status", "Jumlah Kontur", "Waktu"],
                                        "Nilai": [selected_file.name, results['method_text'], f"{edge_std:.2f}", 
                                                 f"{flatness_threshold:.1f}", status, 
                                                 f"{len(results['filtered_contours']) if enable_contour else 'N/A'}", 
                                                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                                    })
                                    csv_data = results_df.to_csv(index=False)
                                    zip_file.writestr(f"report_{selected_file.name}.csv", csv_data)
                                    
                                    # Simpan metadata sebagai TEXT file
                                    metadata_text = f"""HASIL ANALISIS KERATAAN PERMUKAAN 3D
===========================================
Nama Gambar: {selected_file.name}
Tanggal Analisis: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

PARAMETER PENGGUNAAN:
=====================
1. Preprocessing:
   - Resize: {'Aktif' if enable_resize else 'Tidak Aktif'}
   - Target Width: {target_width if enable_resize else 'N/A'} px
   - Gaussian Blur: {'Aktif' if enable_blur else 'Tidak Aktif'}
   - Blur Kernel: {blur_ksize if enable_blur else 'N/A'}

2. Edge Detection:
   - Metode: {edge_method}
   - Detail: {results['method_text']}

3. Threshold Kerataan:
   - Ambang: {flatness_threshold:.1f}

4. Contour Analysis:
   - Aktif: {'Ya' if enable_contour else 'Tidak'}
   - Mode: {contour_mode if enable_contour else 'N/A'}
   - Area Minimum: {contour_min_area if enable_contour else 'N/A'}

HASIL ANALISIS:
===============
- Edge STD: {edge_std:.2f}
- Status: {status}
- Jumlah Kontur: {len(results['filtered_contours']) if enable_contour else 0}
- Keputusan: {'RATA' if edge_std <= flatness_threshold else 'TIDAK RATA'}

-------------------------------------------
Aplikasi 3D Surface Flatness Detection
Dibuat untuk pembelajaran Computer Vision
© sanadhiri2025
"""
                                    zip_file.writestr(f"metadata_{selected_file.name}.txt", metadata_text)
                                
                                zip_buffer.seek(0)
                                
                                diagram_buffer = io.BytesIO()
                                fig.savefig(diagram_buffer, format='png', dpi=150, bbox_inches='tight')
                                diagram_buffer.seek(0)
                                
                                if enable_contour:
                                    col_dl1, col_dl2, col_dl3 = st.columns(3)
                                else:
                                    col_dl1, col_dl2 = st.columns(2)
                                
                                with col_dl1:
                                    st.download_button(
                                        label="📦 Download All Files (ZIP)",
                                        data=zip_buffer,
                                        file_name=f"hasil_analisis_{selected_file.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                        mime="application/zip"
                                    )
                                
                                with col_dl2:
                                    st.download_button(
                                        label="📊 Download Comparison Diagram",
                                        data=diagram_buffer,
                                        file_name=f"diagram_perbandingan_{selected_file.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                        mime="image/png"
                                    )
                                
                                if enable_contour and results['contour_image'] is not None:
                                    with col_dl3:
                                        contour_buf = io.BytesIO()
                                        contour_rgb = cv2.cvtColor(results['contour_image'], cv2.COLOR_BGR2RGB)
                                        contour_pil = Image.fromarray(contour_rgb)
                                        contour_pil.save(contour_buf, format='PNG')
                                        contour_buf.seek(0)
                                        
                                        st.download_button(
                                            label="🎨 Download Contour Image",
                                            data=contour_buf,
                                            file_name=f"contour_{selected_file.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                            mime="image/png"
                                        )
                                
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                
                else:  # Analisis Semua Gambar
                    if st.button("🚀 Analisis Semua Gambar", type="primary", use_container_width=True):
                        with st.spinner(f"🔍 Menganalisis {len(uploaded_files)} gambar..."):
                            try:
                                all_results = []
                                
                                for i, uploaded_file in enumerate(uploaded_files):
                                    # Proses setiap gambar
                                    image = Image.open(uploaded_file)
                                    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                                    
                                    results = process_single_image(
                                        img, enable_resize, target_width, enable_blur, blur_ksize,
                                        edge_method, canny_min if edge_method == "Canny" else None,
                                        canny_max if edge_method == "Canny" else None,
                                        sobel_kernel if edge_method == "Sobel" else None,
                                        laplacian_kernel if edge_method == "Laplacian" else None,
                                        enable_contour, contour_color, contour_thickness,
                                        contour_min_area, contour_mode
                                    )
                                    
                                    # Tentukan status
                                    if results['edge_std'] <= flatness_threshold:
                                        status = "RATA"
                                        color = "#4CAF50"
                                    else:
                                        status = "TIDAK RATA"
                                        color = "#F44336"
                                    
                                    all_results.append({
                                        'nama': uploaded_file.name,
                                        'edge_std': results['edge_std'],
                                        'status': status,
                                        'color': color,
                                        'kontur': len(results['filtered_contours']) if enable_contour else 0
                                    })
                                
                                st.success(f"✅ Analisis {len(uploaded_files)} gambar selesai!")
                                
                                # Tampilkan hasil dalam tabel
                                st.subheader("📋 Hasil Analisis Semua Gambar")
                                
                                results_df = pd.DataFrame(all_results)
                                results_df.index = range(1, len(results_df) + 1)
                                
                                # Format tabel dengan warna
                                def color_status(val):
                                    if val == "RATA":
                                        return 'background-color: #C8E6C9; color: #1B5E20; font-weight: bold;'
                                    else:
                                        return 'background-color: #FFCDD2; color: #B71C1C; font-weight: bold;'
                                
                                styled_df = results_df.style.applymap(color_status, subset=['status'])
                                st.dataframe(styled_df, use_container_width=True)
                                
                                # Grafik perbandingan semua gambar
                                st.subheader("📈 Perbandingan Semua Gambar")
                                
                                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
                                
                                # Bar chart untuk semua gambar
                                x_labels = [f"Img {i+1}" for i in range(len(all_results))]
                                edge_stds = [r['edge_std'] for r in all_results]
                                colors = [r['color'] for r in all_results]
                                
                                bars = ax1.bar(x_labels, edge_stds, color=colors, edgecolor='black', linewidth=1)
                                ax1.axhline(y=flatness_threshold, color='red', linestyle='--', alpha=0.7, 
                                          label=f'Ambang: {flatness_threshold}')
                                ax1.set_title("Edge STD Semua Gambar", fontsize=14, fontweight='bold')
                                ax1.set_ylabel("Edge STD")
                                ax1.set_xlabel("Gambar")
                                ax1.grid(True, alpha=0.3)
                                ax1.legend()
                                
                                for bar in bars:
                                    height = bar.get_height()
                                    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                                           f'{height:.1f}', ha='center', va='bottom', fontsize=9)
                                
                                # Pie chart status
                                rata_count = sum(1 for r in all_results if r['status'] == "RATA")
                                tidak_rata_count = len(all_results) - rata_count
                                
                                sizes = [rata_count, tidak_rata_count]
                                labels = ['RATA', 'TIDAK RATA']
                                colors_pie = ['#4CAF50', '#F44336']
                                
                                ax2.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%',
                                      startangle=90, shadow=True, explode=(0.05, 0))
                                ax2.set_title(f"Status Keseluruhan\n({len(all_results)} gambar)", 
                                            fontsize=14, fontweight='bold')
                                
                                plt.tight_layout()
                                st.pyplot(fig)
                                
                                # Download semua hasil - TANPA JSON
                                st.markdown("---")
                                st.subheader("💾 Ekspor Semua Hasil")
                                
                                # Buat ZIP untuk semua gambar
                                all_zip_buffer = io.BytesIO()
                                
                                with zipfile.ZipFile(all_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                    # Simpan summary CSV
                                    summary_df = pd.DataFrame(all_results)
                                    summary_csv = summary_df.to_csv(index=False)
                                    zip_file.writestr("summary_all_images.csv", summary_csv)
                                    
                                    # Simpan metadata sebagai TEXT file
                                    metadata_text = f"""HASIL ANALISIS KERATAAN PERMUKAAN 3D
===========================================
ANALISIS MULTIPLE GAMBAR
========================
Tanggal Analisis: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total Gambar: {len(uploaded_files)}

PARAMETER PENGGUNAAN:
=====================
1. Preprocessing:
   - Resize: {'Aktif' if enable_resize else 'Tidak Aktif'}
   - Target Width: {target_width if enable_resize else 'N/A'} px
   - Gaussian Blur: {'Aktif' if enable_blur else 'Tidak Aktif'}
   - Blur Kernel: {blur_ksize if enable_blur else 'N/A'}

2. Edge Detection:
   - Metode: {edge_method}
   - Threshold: {flatness_threshold:.1f}

3. Contour Analysis:
   - Aktif: {'Ya' if enable_contour else 'Tidak'}
   - Area Minimum: {contour_min_area if enable_contour else 'N/A'}

STATISTIK KESELURUHAN:
======================
- Total Gambar: {len(all_results)}
- Gambar RATA: {rata_count}
- Gambar TIDAK RATA: {tidak_rata_count}
- Persentase RATA: {(rata_count/len(all_results))*100:.1f}%

DETAIL HASIL:
=============
Lihat file CSV untuk detail lengkap setiap gambar.

-------------------------------------------
Aplikasi 3D Surface Flatness Detection
Dibuat untuk pembelajaran Computer Vision
© sanadhiri2025
"""
                                    zip_file.writestr("metadata_all_images.txt", metadata_text)
                                
                                all_zip_buffer.seek(0)
                                
                                col_dl1, col_dl2 = st.columns(2)
                                
                                with col_dl1:
                                    st.download_button(
                                        label="📊 Download Summary (CSV+TXT)",
                                        data=all_zip_buffer,
                                        file_name=f"summary_analisis_{len(uploaded_files)}_gambar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                        mime="application/zip"
                                    )
                                
                                with col_dl2:
                                    # Simpan diagram ke buffer
                                    fig_buffer = io.BytesIO()
                                    fig.savefig(fig_buffer, format='png', dpi=150, bbox_inches='tight')
                                    fig_buffer.seek(0)
                                    
                                    st.download_button(
                                        label="📈 Download Comparison Chart",
                                        data=fig_buffer,
                                        file_name=f"comparison_chart_{len(uploaded_files)}_gambar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                        mime="image/png"
                                    )
                                
                            except Exception as e:
                                st.error(f"❌ Error saat menganalisis semua gambar: {str(e)}")
            
            st.markdown("</div>", unsafe_allow_html=True)

# ==========================================================
# TENTANG KAMI - TAB 3
# ==========================================================
with tab_about:
    st.title("💖 Tentang Kami")
    
    st.markdown("""
    <div class="card">
    <h3 style="color:#cc0066; text-align:center;">🌸 Tentang Aplikasi 3D Surface Flatness Detection</h3>
    
     <p style="font-size:1.1em; line-height:1.6; text-align: center;">
    Aplikasi ini dikembangkan untuk pembelajaran <b>Pengolahan Citra Digital</b> dan 
    <b>Computer Vision</b> dalam konteks analisis kerataan permukaan objek 3D.
    </p>
    </div>
    """, unsafe_allow_html=True)

    # ANGGOTA KELOMPOK 
    st.subheader("👥 Tim Pengembang")
    
    # Data anggota dengan path foto
    anggota_data = [
        {
            "nama": "Intan Puspita Puryanti",
            "npm": "23010029",
            "foto": "intan.jpeg"
        },
        {
            "nama": "Safira Putri Azzahra", 
            "npm": "23010054",
            "foto": "safira.jpeg"
        },
        {
            "nama": "Rizka Wulandari",
            "npm": "23010063",
            "foto": "rizka.jpeg"
        },
        {
            "nama": "Dhiffa Rulla Innayah",
            "npm": "23010078",
            "foto": "dhiffa.jpeg"
        }
    ]
    
    # Membuat 4 kolom dengan lebar yang sama
    col1, col2, col3, col4 = st.columns(4)
    
    # Fungsi untuk membuat kartu anggota
    def create_member_card(col, anggota, idx):
        with col:
            border_color = "#FF6EC7"
            
            try:
                if os.path.exists(anggota["foto"]):
                    foto = Image.open(anggota["foto"])
                    buffered = BytesIO()
                    foto.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    
                    st.markdown(f"""
                    <div style="text-align:center; margin-bottom:15px;">
                        <div class="member-photo-container" 
                             style="width:140px; height:140px; margin:0 auto; border-radius:50%; 
                                    border:4px solid {border_color}; overflow:hidden; 
                                    box-shadow:0 5px 15px rgba(255, 110, 199, 0.3); transition: all 0.3s ease;">
                            <img src="data:image/jpeg;base64,{img_str}" 
                                 style="width:100%; height:100%; object-fit:cover; transition: all 0.3s ease;">
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="text-align:center; margin-bottom:15px;">
                        <div class="member-photo-container"
                             style="width:140px; height:140px; margin:0 auto; border-radius:50%; 
                                    border:4px solid {border_color}; background:#FFE6F2; 
                                    display:flex; align-items:center; justify-content:center;
                                    box-shadow:0 5px 15px rgba(255, 110, 199, 0.3); transition: all 0.3s ease;">
                            <span style="font-size:50px; color:{border_color};">👤</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            except Exception as e:
                st.markdown(f"""
                <div style="text-align:center; margin-bottom:15px;">
                    <div class="member-photo-container"
                         style="width:140px; height:140px; margin:0 auto; border-radius:50%; 
                                border:4px solid {border_color}; background:#FFE6F2; 
                                display:flex; align-items:center; justify-content:center;
                                box-shadow:0 5px 15px rgba(255, 110, 199, 0.3); transition: all 0.3s ease;">
                        <span style="font-size:50px; color:{border_color};">👤</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Tampilkan nama dan NPM
            st.markdown(f"""
            <div style="text-align:center; padding:10px; background:linear-gradient(135deg, #FFF0F7, #FFFFFF); 
                        border-radius:15px; border:2px solid #FFE6F2; margin-top:5px;" class="member-card-container">
                <h4 style="color:#CC0066; margin-bottom:8px; font-size:1.1em;">{anggota['nama']}</h4>
                <p style="color:#666666; font-weight:bold; margin:0; font-size:0.95em;">
                    <span style="color:#FF6EC7;">NPM:</span> {anggota['npm']}
                </p>
                <div style="display:inline-block; background:#FFE6F2; color:#CC0066; 
                            padding:3px 12px; border-radius:20px; margin-top:8px; 
                            font-size:0.85em; font-weight:bold; border:1px solid #FFB6D9;">
                    Anggota {idx}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Tampilkan anggota
    create_member_card(col1, anggota_data[0], 1)
    create_member_card(col2, anggota_data[1], 2)
    create_member_card(col3, anggota_data[2], 3)
    create_member_card(col4, anggota_data[3], 4)
    
    # CSS untuk efek hover foto
    st.markdown("""
    <style>
    .member-photo-container:hover {
        border: 4px solid #ff4db8 !important;
        box-shadow: 
            0 0 0 6px rgba(255, 182, 217, 0.8),
            inset 0 0 20px rgba(255, 110, 199, 0.3) !important;
    }
    
    .member-photo-container:hover img {
        transform: scale(1.05);
    }
    
    .member-photo-container:hover span {
        transform: scale(1.1);
        color: #ff4db8 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Informasi teknologi dan fitur
    col_tech, col_features = st.columns(2)
    
    with col_tech:
        st.markdown("""
        <div style="background:#E8F5E9; padding:20px; border-radius:20px; border:2px solid #4CAF50; margin-bottom:20px;" class="tech-feature-container">
        <h4 style="color:#388E3C;">🔧 Teknologi yang Digunakan</h4>
        <ul style="font-size:1em; line-height:1.8;">
        <li><b>OpenCV</b> - Pengolahan citra dan computer vision</li>
        <li><b>Streamlit</b> - Framework aplikasi web interaktif</li>
        <li><b>NumPy & Pandas</b> - Pemrosesan data numerik</li>
        <li><b>Matplotlib</b> - Visualisasi data dan grafik</li>
        <li><b>Pillow</b> - Manipulasi gambar dasar</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col_features:
        st.markdown("""
        <div style="background:#F3E5F5; padding:20px; border-radius:20px; border:2px solid #9C27B0; margin-bottom:20px;" class="tech-feature-container">
        <h4 style="color:#7B1FA2;">✨ Fitur Aplikasi</h4>
        <ul style="font-size:1em; line-height:1.8;">
        <li>🎨 <b>Antarmuka user-friendly</b> dengan tema pastel</li>
        <li>🖼️ <b>Dataset bawaan</b> dengan contoh gambar 3D</li>
        <li>📤 <b>Upload multiple gambar</b> untuk analisis fleksibel</li>
        <li>⚙️ <b>Parameter adjustable</b> sesuai kebutuhan</li>
        <li>📊 <b>Visualisasi lengkap</b> dengan grafik dan metrik</li>
        <li>💾 <b>Ekspor hasil</b> - Download semua gambar hasil analisis</li>
        <li>📊 <b>Diagram perbandingan</b> - Download visualisasi grafik</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Kontak dan informasi
    st.subheader("📞 Kontak & Informasi")
    
    col_contact, col_version = st.columns(2)
    
    with col_contact:
        st.markdown("""
        <div style="background:#E3F2FD; padding:20px; border-radius:20px;" class="contact-container">
        <h5 style="color:#1976D2;">📧 Untuk informasi lebih lanjut:</h5>
        <p>Email: support@deteksikerataan.com</p>
        <p>Website: www.deteksikerataan.com</p>
        <p>GitHub: github.com/deteksi-kerataan-3d</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_version:
        st.markdown("""
        <div style="background:#FFF3E0; padding:20px; border-radius:20px;" class="version-container">
        <h5 style="color:#F57C00;">📋 Informasi Versi</h5>
        <p><b>Versi:</b> 2.2.0</p>
        <p><b>Update Terakhir:</b> Desember 2024</p>
        <p><b>Lisensi:</b> MIT Open Source</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Pesan penutup
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding:30px; background:linear-gradient(135deg, #FFE0B2, #C8E6C9); 
                border-radius:25px; border:3px solid #FFB74D;" class="closing-container">
    <h3 style="color:#FF9800;">🙏 Terima Kasih!</h3>
    <p style="font-size:1.2em;">Terima kasih telah menggunakan aplikasi Deteksi Kerataan Permukaan 3D 🌸</p>
    <p>Semoga aplikasi ini bermanfaat untuk pembelajaran dan penelitian Anda!</p>
    </div>
    """, unsafe_allow_html=True)
  
# ==========================================================
# FOOTER
# ==========================================================
st.markdown("""
<div style="text-align:center; margin-top:40px; padding:20px; color:#666; font-size:0.9em;" class="footer-container">
<hr style="border:1px solid #ddd;">
<p>© sanadhiri2025 Deteksi Kerataan Permukaan 3D • Dibuat dengan ❤️ untuk pembelajaran Computer Vision</p>
<p>Streamlit • OpenCV • Python • Multiple Upload • Comparison Diagrams • TXT Metadata</p>
</div>
""", unsafe_allow_html=True)
