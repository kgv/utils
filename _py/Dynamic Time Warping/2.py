import streamlit as st
import polars as pl
import numpy as np
import matplotlib.pyplot as plt

# Импортируем dtaidistance вместо fastdtw
from dtaidistance import dtw

st.set_page_config(page_title="DTW Выравнивание", layout="wide")
st.title("📈 Выравнивание хроматограмм (dtaidistance)")

def load_signal(uploaded_file):
    """Загружает Y-значения из загруженного CSV файла"""
    df = pl.read_csv(uploaded_file, separator=';', has_header=False)
    # ВАЖНО: dtaidistance требует, чтобы данные были строго в формате float64 (double)
    return df[df.columns[1]].drop_nulls().to_numpy().astype(np.float64)

# ==========================================
# 1. ЗАГРУЗКА ФАЙЛОВ
# ==========================================
uploaded_files = st.file_uploader(
    "📂 Выберите CSV файлы для анализа (минимум 2). Желательно после Z-score.", 
    type=['csv'], 
    accept_multiple_files=True
)

if len(uploaded_files) < 2:
    st.info("Пожалуйста, загрузите как минимум ДВА файла для начала работы.")
    st.stop()

# ==========================================
# 2. ВЫБОР ФАЙЛОВ ДЛЯ СРАВНЕНИЯ
# ==========================================
st.write("### Настройка сравнения")
file_names = [f.name for f in uploaded_files]

col1, col2 = st.columns(2)
with col1:
    file1_name = st.selectbox("Выберите первый файл (Эталон):", file_names, index=0)
with col2:
    file2_name = st.selectbox("Выберите второй файл (Смещенный):", file_names, index=1)

file1 = next(f for f in uploaded_files if f.name == file1_name)
file2 = next(f for f in uploaded_files if f.name == file2_name)

# ==========================================
# 3. НАСТРОЙКИ АЛГОРИТМА
# ==========================================
st.write("### Настройки алгоритма")

col_opt1, col_opt2 = st.columns(2)

with col_opt1:
    window_val = st.slider(
        "Ширина окна поиска (Window)", 
        min_value=1, 
        max_value=500, 
        value=50, 
        step=5
    )

with col_opt2:
    downsample_val = st.slider(
        "Прореживание данных (Downsampling)", 
        min_value=1, 
        max_value=100, 
        value=20, 
        step=1,
        help="Берет каждую N-ю точку. Если у вас 400 000 строк, прореживание = 20 оставит 20 000 строк. Это спасет оперативную память и ускорит расчет, не меняя форму пиков."
    )

# ==========================================
# 4. ЗАПУСК DTW И ВИЗУАЛИЗАЦИЯ
# ==========================================
if st.button("🚀 Запустить выравнивание (DTW)"):
    
    with st.spinner("Вычисляем оптимальный путь выравнивания..."):
        file1.seek(0)
        file2.seek(0)
        
        y1 = load_signal(file1)
        y2 = load_signal(file2)
        
        # --- ПРИМЕНЯЕМ ПРОРЕЖИВАНИЕ ---
        y1 = y1[::downsample_val]
        y2 = y2[::downsample_val]
        
        # --- РАСЧЕТ ЧЕРЕЗ DTAIDISTANCE ---
        distance = dtw.distance(y1, y2, window=window_val)
        
        # --- РАСЧЕТ ЧЕРЕЗ DTAIDISTANCE ---
        # 1. Считаем дистанцию (с учетом окна)
        distance = dtw.distance(y1, y2, window=window_val)
        
        # 2. Получаем путь выравнивания (с учетом окна)
        path = dtw.warping_path(y1, y2, window=window_val)
        
        # Распаковываем путь выравнивания
        path_x = [p[0] for p in path]
        path_y = [p[1] for p in path]
        
        # Создаем выровненные массивы
        y1_aligned = y1[path_x]
        y2_aligned = y2[path_y]
        
    st.success(f"✅ Готово! DTW Дистанция: **{distance:.4f}**")
    
    # Отрисовка графиков
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # График 1: До выравнивания
    ax1.plot(y1, label=file1_name, color='#1f77b4', alpha=0.8, linewidth=1.5)
    ax1.plot(y2, label=file2_name, color='#d62728', alpha=0.8, linewidth=1.5)
    ax1.set_title("До DTW (Исходные сигналы)", fontsize=14)
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend()
    
    # График 2: После выравнивания
    ax2.plot(y1_aligned, label=f"{file1_name} (выровнен)", color='#1f77b4', alpha=0.8, linewidth=1.5)
    ax2.plot(y2_aligned, label=f"{file2_name} (выровнен)", color='#d62728', alpha=0.8, linewidth=1.5)
    ax2.set_title(f"После DTW (Окно = {window_val})", fontsize=14)
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend()
    
    plt.tight_layout()
    st.pyplot(fig)

# python -m streamlit run "d:/git/kgv/#Article/2026.SearchingOfSustainableVegetableOilSubstitutesAStudy/_py/Dynamic Time Warping/2.py"