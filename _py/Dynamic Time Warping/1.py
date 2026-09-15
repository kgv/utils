import streamlit as st
import polars as pl
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw

# Настройка страницы Streamlit
st.set_page_config(page_title="DTW Выравнивание", layout="wide")
st.title("📈 Выравнивание хроматограмм (DTW)")

def load_signal(uploaded_file):
    """Загружает Y-значения из загруженного CSV файла"""
    # Streamlit передает файл как файлоподобный объект, Polars умеет его читать
    df = pl.read_csv(uploaded_file, separator=';', has_header=False)
    return df[df.columns[1]].to_numpy()

# ==========================================
# 2. ЗАГРУЗКА ФАЙЛОВ (Ваш код)
# ==========================================
uploaded_files = st.file_uploader(
    "📂 Выберите CSV файлы для анализа (минимум 2). Желательно загружать файлы после Z-score.", 
    type=['csv'], 
    accept_multiple_files=True
)

if len(uploaded_files) < 2:
    st.info("Пожалуйста, загрузите как минимум ДВА файла для начала работы.")
    st.stop() # Останавливаем выполнение, пока нет файлов

# ==========================================
# 3. ВЫБОР ФАЙЛОВ ДЛЯ СРАВНЕНИЯ
# ==========================================
st.write("### Настройка сравнения")
file_names = [f.name for f in uploaded_files]

col1, col2 = st.columns(2)
with col1:
    file1_name = st.selectbox("Выберите первый файл (Эталон):", file_names, index=0)
with col2:
    # По умолчанию выбираем второй файл в списке
    file2_name = st.selectbox("Выберите второй файл (Смещенный):", file_names, index=1)

# Находим сами объекты файлов по выбранным именам
file1 = next(f for f in uploaded_files if f.name == file1_name)
file2 = next(f for f in uploaded_files if f.name == file2_name)

st.write("### Настройки алгоритма")
# Ползунок от 1 до 200, по умолчанию 30
radius_val = st.slider(
    "Ширина окна поиска (Radius)", 
    min_value=1, 
    max_value=200, 
    value=30, 
    step=1,
    help="Определяет, насколько сильно можно сдвигать график. Чем больше значение, тем сильнее алгоритм может смещать пики для их совмещения, но расчет займет чуть больше времени."
)

# ==========================================
# 4. ЗАПУСК DTW И ВИЗУАЛИЗАЦИЯ
# ==========================================
if st.button("🚀 Запустить выравнивание (DTW)"):
    
    with st.spinner("Вычисляем оптимальный путь выравнивания... Это может занять несколько секунд."):
        # Загружаем сигналы
        # Важно: возвращаем указатель файла в начало, если файл читается повторно
        file1.seek(0)
        file2.seek(0)
        
        y1 = load_signal(file1)
        y2 = load_signal(file2)
        
        # Запуск DTW
        distance, path = fastdtw(y1, y2, radius=radius_val)
        
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
    ax2.set_title("После DTW (Пики синхронизированы)", fontsize=14)
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend()
    
    plt.tight_layout()
    
    # Выводим график в Streamlit
    st.pyplot(fig)

# python -m streamlit run "d:/git/kgv/#Article/2026.SearchingOfSustainableVegetableOilSubstitutesAStudy/_py/Dynamic Time Warping/1.py"