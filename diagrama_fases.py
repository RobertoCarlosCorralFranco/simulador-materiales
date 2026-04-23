import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# ==========================================
# CONFIGURACIÓN E IDENTIDAD INSTITUCIONAL
# ==========================================
TEC_GREEN = '#006B3F'
st.set_page_config(page_title="Laboratorio Fe-C - Tecmilenio", layout="wide")

st.markdown(f"""
    <style>
    .main-title {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 28px; font-weight: bold; text-align: center; }}
    .section-header {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 20px; font-weight: bold; border-bottom: 1.5px solid {TEC_GREEN}; padding-bottom: 5px; margin-top: 20px; }}
    .step-box {{ padding: 20px; border: 1px solid #e6e6e6; border-left: 6px solid {TEC_GREEN}; background-color: #ffffff; margin-bottom: 15px; border-radius: 4px; line-height: 1.6; font-family: 'serif'; }}
    .alert-box {{ padding: 15px; background-color: #f8f9fa; border-radius: 4px; font-weight: bold; color: #333; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">Tema 13: Diagrama de Fases Hierro-Carbono (Fe-C)</p>', unsafe_allow_html=True)

# ==========================================
# FUNCIONES MATEMÁTICAS (INTERPOLACIÓN)
# ==========================================
def interpolar_x(y_target, p1, p2):
    """Obtiene la coordenada X en una recta dada una coordenada Y (Temperatura)."""
    x1, y1 = p1
    x2, y2 = p2
    if y1 == y2: return x1
    return x1 + (x2 - x1) * (y_target - y1) / (y2 - y1)

# Puntos clave del diagrama estándar
pt_fusion = (0, 1539)
pt_eutectico = (4.3, 1130)
pt_max_sol_aust = (2.0, 1130)
pt_eutectoide = (0.83, 723)
pt_aust_baja = (0, 910)
pt_max_sol_fer = (0.025, 723)

# ==========================================
# LÓGICA DE DATOS Y CONTROLES
# ==========================================
st.sidebar.header("Parámetros del Material")
carbono = st.sidebar.slider("Contenido de Carbono (% C)", 0.0, 6.67, 0.40, step=0.01)
temperatura = st.sidebar.slider("Temperatura (°C)", 400, 1600, 1000, step=1)

st.sidebar.markdown("---")
st.sidebar.caption("Prof. Roberto Carlos Corral Franco\nUniversidad Tecmilenio")

# Clasificación Industrial
if carbono <= 2.0:
    clasificacion = "Acero"
    sub_clas = "Hipo-Eutectoide" if carbono < 0.83 else "Eutectoide" if carbono == 0.83 else "Hiper-Eutectoide"
else:
    clasificacion = "Fundición (Cast Iron)"
    sub_clas = "Hipo-Eutéctica" if carbono < 4.3 else "Eutéctica" if carbono == 4.3 else "Hiper-Eutéctica"

# Determinación de Fase y Regla de la Palanca
fase_actual = ""
fase_izq = ""
fase_der = ""
c_izq = 0.0
c_der = 0.0
es_bifasica = False

# Lógica simplificada de fronteras a la temperatura actual
if temperatura < 723:
    fase_actual = "Ferrita (α) + Cementita (Fe₃C)"
    es_bifasica = True
    fase_izq = "Ferrita (α)"
    fase_der = "Cementita (Fe₃C)"
    c_izq = 0.025 * (temperatura/723) # Aproximación simplificada de solubilidad
    c_der = 6.67

elif 723 <= temperatura <= 1130:
    x_a3 = interpolar_x(temperatura, pt_aust_baja, pt_eutectoide)
    x_acm = interpolar_x(temperatura, pt_eutectoide, pt_max_sol_aust)
    
    if carbono < x_a3:
        fase_actual = "Ferrita (α) + Austenita (γ)"
        es_bifasica = True
        fase_izq, fase_der = "Ferrita (α)", "Austenita (γ)"
        c_izq, c_der = 0.0, x_a3
    elif x_a3 <= carbono <= x_acm:
        fase_actual = "Austenita (γ) [100% Solución Sólida]"
        es_bifasica = False
    else:
        fase_actual = "Austenita (γ) + Cementita (Fe₃C)"
        es_bifasica = True
        fase_izq, fase_der = "Austenita (γ)", "Cementita (Fe₃C)"
        c_izq, c_der = x_acm, 6.67

elif 1130 < temperatura <= 1539:
    x_solidus = interpolar_x(temperatura, pt_fusion, pt_max_sol_aust)
    x_liquidus = interpolar_x(temperatura, pt_fusion, pt_eutectico)
    
    if carbono < x_solidus:
        fase_actual = "Austenita (γ) [100% Solución Sólida]"
        es_bifasica = False
    elif x_solidus <= carbono <= x_liquidus:
        fase_actual = "Austenita (γ) + Líquido (L)"
        es_bifasica = True
        fase_izq, fase_der = "Austenita (γ)", "Líquido (L)"
        c_izq, c_der = x_solidus, x_liquidus
    else:
        fase_actual = "Líquido (L) [100% Fundido]"
        es_bifasica = False
else:
    fase_actual = "Líquido (L) [100% Fundido]"
    es_bifasica = False

# ==========================================
# RENDERIZADO VISUAL
# ==========================================
col_plot, col_calc = st.columns([1.2, 1])

with col_plot:
    st.markdown('<p class="section-header">Plano Termodinámico</p>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(7, 6))
    
    # Dibujar polígonos de fases con colores suaves
    # Ferrita + Cementita
    ax.add_patch(Polygon([(0,400), (6.67,400), (6.67,723), (0.025,723)], closed=True, fill=True, color='#e2f0d9', alpha=0.7))
    # Austenita + Cementita
    ax.add_patch(Polygon([(0.83,723), (6.67,723), (6.67,1130), (2.0,1130)], closed=True, fill=True, color='#fff2cc', alpha=0.7))
    # Austenita (Gamma)
    ax.add_patch(Polygon([(0,910), (0.83,723), (2.0,1130), (0,1539)], closed=True, fill=True, color='#fce4d6', alpha=0.8))
    # Austenita + Líquido
    ax.add_patch(Polygon([(0,1539), (2.0,1130), (4.3,1130)], closed=True, fill=True, color='#deebf7', alpha=0.8))
    
    # Líneas principales
    ax.plot([0, 6.67], [723, 723], color='black', linewidth=1.5) # Eutectoide A1
    ax.plot([2.0, 6.67], [1130, 1130], color='black', linewidth=1.5) # Eutéctico
    ax.plot([0, 0.83], [910, 723], color='black', linewidth=1.5) # A3
    ax.plot([0.83, 2.0], [723, 1130], color='black', linewidth=1.5) # Acm
    ax.plot([0, 2.0], [1539, 1130], color='black', linewidth=1.5) # Solidus
    ax.plot([0, 4.3], [1539, 1130], color='black', linewidth=1.5) # Liquidus
    
    # Etiquetas de zona
    ax.text(0.6, 1000, r'$\gamma$ (Austenita)', fontsize=11, color='#b28900', weight='bold')
    ax.text(3.5, 550, r'$\alpha + Fe_3C$ (Perlita / Cementita)', fontsize=11, color='#385723', weight='bold')
    ax.text(4.0, 900, r'$\gamma + Fe_3C$', fontsize=11, color='#bf8f00', weight='bold')
    ax.text(3.0, 1350, r'Líquido', fontsize=12, color='#2e75b6', weight='bold')
    
    # Marcador Dinámico y Tie Line
    ax.plot(carbono, temperatura, 'ro', markersize=8, markeredgecolor='black')
    
    if es_bifasica and c_der > c_izq:
        ax.plot([c_izq, c_der], [temperatura, temperatura], 'r--', linewidth=2)
        ax.plot(c_izq, temperatura, 'bo', markersize=5)
        ax.plot(c_der, temperatura, 'bo', markersize=5)

    ax.set_xlim(0, 6.67)
    ax.set_ylim(400, 1600)
    ax.set_xlabel("Contenido de Carbono (% C)", fontsize=10, weight='bold')
    ax.set_ylabel("Temperatura (°C)", fontsize=10, weight='bold')
    ax.grid(True, linestyle=':', alpha=0.6)
    
    st.pyplot(fig)

with col_calc:
    st.markdown('<p class="section-header">Análisis Microestructural</p>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="alert-box">
        <b>Clasificación:</b> {clasificacion} ({sub_clas})<br>
        <b>Coordenada:</b> {carbono}% C a {temperatura}°C<br>
        <span style="color:{TEC_GREEN}; font-size:18px;"><b>Fase Presente:</b> {fase_actual}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="section-header">Cálculo: Regla de la Palanca</p>', unsafe_allow_html=True)
    
    if es_bifasica:
        if carbono <= c_izq:
            w_izq, w_der = 100.0, 0.0
        elif carbono >= c_der:
            w_izq, w_der = 0.0, 100.0
        else:
            w_izq = ((c_der - carbono) / (c_der - c_izq)) * 100
            w_der = ((carbono - c_izq) / (c_der - c_izq)) * 100
            
        st.markdown(f"""
        <div class="step-box">
            <b>1. Identificar Isoterma (Tie Line):</b><br>
            Límite Izquierdo ({fase_izq}): <b>{c_izq:.2f}% C</b><br>
            Límite Derecho ({fase_der}): <b>{c_der:.2f}% C</b>
        </div>
        <div class="step-box">
            <b>2. Fracción de {fase_izq}:</b><br>
            W = ({c_der:.2f} - {carbono:.2f}) / ({c_der:.2f} - {c_izq:.2f})<br>
            <b>Resultado = {w_izq:.1f}%</b>
        </div>
        <div class="step-box">
            <b>3. Fracción de {fase_der}:</b><br>
            W = ({carbono:.2f} - {c_izq:.2f}) / ({c_der:.2f} - {c_izq:.2f})<br>
            <b>Resultado = {w_der:.1f}%</b>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("El material se encuentra en una zona de Solución Sólida Única (Monofásica). No existe segregación de fases, por lo tanto, la Regla de la Palanca no es aplicable.")