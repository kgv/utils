import io
import itertools
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import polars as pl
import streamlit as st
from dtaidistance import dtw
from dtaidistance import dtw_visualisation as dtwvis
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import squareform

# Настройка широкого формата страницы
st.set_page_config(page_title="DTW Анализ", layout="wide")

st.title("📈 Интерактивный анализ временных рядов (DTW)")

# ==========================================
# 1. БОКОВАЯ ПАНЕЛЬ (НАСТРОЙКИ)
# ==========================================
st.sidebar.header("⚙️ Настройки алгоритма")
STEP = st.sidebar.slider(
    "Шаг прореживания (STEP)", 
    min_value=1, max_value=2000, value=10, step=1,
    help="Увеличьте, если файлы огромные и не хватает памяти."
)
WINDOW_SIZE = st.sidebar.slider(
    "Размер окна DTW", 
    min_value=1, max_value=200, value=10, step=1,
    help="Ограничение поиска пути. Меньше окно = быстрее расчет."
)

st.sidebar.header("🎨 Настройки графиков")
LINES_TO_DRAW = st.sidebar.slider(
    "Количество линий связей", 
    min_value=10, max_value=300, value=100, step=10
)
MIN_DISTANCE = st.sidebar.slider(
    "Мин. расстояние между линиями", 
    min_value=1, max_value=300, value=100, step=10
)

# ==========================================
# 2. ЗАГРУЗКА ФАЙЛОВ
# ==========================================
uploaded_files = st.file_uploader(
    "📂 Выберите CSV файлы для анализа (минимум 2)", 
    type=['csv'], 
    accept_multiple_files=True
)

if len(uploaded_files) < 2:
    st.info("Пожалуйста, загрузите как минимум ДВА файла для начала работы.")
    st.stop() # Останавливаем выполнение, пока нет файлов

# ==========================================
# 3. ФУНКЦИИ С КЭШИРОВАНИЕМ (ЧТОБЫ НЕ СЧИТАТЬ ЗАНОВО)
# ==========================================
@st.cache_data
def load_and_process_data(files, step):
    series_list = []
    names = []
    for file in files:
        # Читаем файл прямо из оперативной памяти
        df = pl.read_csv(file.getvalue(), separator=";", has_header=False)
        df_sampled = df.gather_every(step)
        target_column_name = df_sampled.columns[1]
        
        ts_array = (
            df_sampled.get_column(target_column_name)
            .cast(pl.Float64, strict=False)
            .drop_nulls()
            .to_numpy()
        )
        series_list.append(ts_array)
        
        # Очистка имени файла от расширения и суффикса {Normalized}
        base_name = file.name
        name_without_ext = os.path.splitext(base_name)[0]
        clean_name = name_without_ext.replace("{Normalized}", "").strip()
        names.append(clean_name)
        
    return series_list, names

@st.cache_data
def compute_dtw_matrix(series_list, window):
    return dtw.distance_matrix_fast(series_list, window=window)

# ==========================================
# 4. ОСНОВНАЯ ЛОГИКА И ВЫВОД
# ==========================================
with st.spinner("Загрузка и обработка данных..."):
    series_list, names = load_and_process_data(uploaded_files, STEP)
    
st.success(f"✅ Успешно загружено файлов: {len(series_list)}. Точек в каждом ряду: {len(series_list[0])}")

with st.spinner("Вычисление матрицы расстояний DTW..."):
    distance_matrix = compute_dtw_matrix(series_list, WINDOW_SIZE)

# --- ВЫВОД МАТРИЦЫ ---
st.subheader("📊 Матрица расстояний DTW")

# Делаем матрицу симметричной для красивого вывода
sym_dist_matrix = distance_matrix.copy()
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        sym_dist_matrix[j, i] = sym_dist_matrix[i, j]
np.fill_diagonal(sym_dist_matrix, 0)

# Выводим как интерактивную таблицу Pandas
df_matrix = pd.DataFrame(sym_dist_matrix, index=names, columns=names)
st.dataframe(df_matrix.style.format("{:.4f}"), use_container_width=True)

# --- ИЕРАРХИЧЕСКАЯ КЛАСТЕРИЗАЦИЯ ---
st.subheader("🌳 Иерархическая кластеризация (Дендрограмма)")
fig_cluster = plt.figure(figsize=(10, 5))
condensed_dist = squareform(sym_dist_matrix)
Z = linkage(condensed_dist, method='average')
dendrogram(Z, labels=names, leaf_rotation=45, leaf_font_size=10)
plt.title("Иерархическая кластеризация временных рядов (DTW)", fontsize=14)
plt.ylabel("Расстояние (DTW Distance)")
plt.tight_layout()
st.pyplot(fig_cluster)

# Экспорт дендрограммы
buf_png_cluster = io.BytesIO()
fig_cluster.savefig(buf_png_cluster, format="png", bbox_inches="tight")
buf_svg_cluster = io.BytesIO()
fig_cluster.savefig(buf_svg_cluster, format="svg", bbox_inches="tight")

dl_col1, dl_col2 = st.columns(2)
dl_col1.download_button("⬇️ Скачать дендрограмму (PNG)", buf_png_cluster.getvalue(), "dendrogram.png", "image/png")
dl_col2.download_button("⬇️ Скачать дендрограмму (SVG)", buf_svg_cluster.getvalue(), "dendrogram.svg", "image/svg")

# --- ВИЗУАЛИЗАЦИЯ ПАР ---
st.subheader("🔗 Графики путей трансформации (DTW)")

# Создаем 2 колонки, чтобы графики выводились сеткой (по 2 в ряд)
cols = st.columns(2)
col_idx = 0

for i, j in itertools.combinations(range(len(series_list)), 2):
    s1 = series_list[i]
    s2 = series_list[j]
    name1 = names[i]
    name2 = names[j]
    
    path = dtw.warping_path(s1, s2, window=WINDOW_SIZE)
    path_enriched = [(idx, pair, s1[pair[0]] + s2[pair[1]]) for idx, pair in enumerate(path)]
    path_sorted_by_height = sorted(path_enriched, key=lambda item: item[2], reverse=True)

    selected_pairs = []
    selected_indices = []

    for idx, pair, height in path_sorted_by_height:
        is_too_close = False
        for sel_idx in selected_indices:
            if abs(idx - sel_idx) < MIN_DISTANCE:
                is_too_close = True
                break
        
        if not is_too_close:
            selected_pairs.append(pair)
            selected_indices.append(idx)
            
        if len(selected_pairs) == LINES_TO_DRAW:
            break

    path_final = sorted(selected_pairs, key=lambda pair: pair[0])

    fig, ax = dtwvis.plot_warping(s1, s2, path_final)
    fig.suptitle(f"{name1} vs {name2}\n(Топ-{len(path_final)} пиков, шаг >= {MIN_DISTANCE})", fontsize=12)
    
    # Отрисовываем график в нужной колонке
    with cols[col_idx % 2]:
        st.pyplot(fig)
        
        # Экспорт графиков путей
        buf_png = io.BytesIO()
        fig.savefig(buf_png, format="png", bbox_inches="tight")
        buf_svg = io.BytesIO()
        fig.savefig(buf_svg, format="svg", bbox_inches="tight")
        
        # Кнопки скачивания под каждым графиком
        btn_col1, btn_col2 = st.columns(2)
        btn_col1.download_button("⬇️ PNG", buf_png.getvalue(), f"dtw_{name1}_vs_{name2}.png", "image/png", key=f"png_{i}_{j}")
        btn_col2.download_button("⬇️ SVG", buf_svg.getvalue(), f"dtw_{name1}_vs_{name2}.svg", "image/svg", key=f"svg_{i}_{j}")
        
        st.write("---") # Разделитель для красоты
    
    col_idx += 1

# python -m streamlit run "d:/git/kgv/#Article/2026.SearchingOfSustainableVegetableOilSubstitutesAStudy/_py/Dynamic Time Warping/dendrogram_from_csv/3.py"

# C-70|0|238.85235524506146|255.49186409576242|185.29214772912042|77.8797220466116|147.25326952941919
# C-108|238.85235524506146|0|217.78498312751535|273.2871037541223|262.92560359303013|262.5773565003038
# C-1210|255.49186409576242|217.78498312751535|0|261.01696087226674|255.52353993649228|255.67734483024577
# H-150|185.29214772912042|273.2871037541223|261.01696087226674|0|149.63125396454737|162.0082960438761
# H-242|77.8797220466116|262.92560359303013|255.52353993649228|149.63125396454737|0|107.32470446756686
# Н-1564|147.25326952941919|262.5773565003038|255.67734483024577|162.0082960438761|107.32470446756686|0