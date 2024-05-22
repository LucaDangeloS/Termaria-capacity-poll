import streamlit as st
import plotly.express as px
from colorscheme import graph_colors
from app_constants import spanish_weekday, months_spanish
import pandas as pd
import plotly.graph_objects as go

def heatmap_chart(data, title_override=None, xaxis_title=None, yaxis_title=None, colorscale='Viridis', tooltip_override=None, override_colorbar=None):

    heatmap = go.Figure(data=go.Heatmap(
        z=data.values,
        x=data.columns,
        y=data.index,
        textfont={"size":20},
        colorscale=colorscale,
        hovertemplate=tooltip_override or 'Mes: %{y}<br>Día: %{x}<br>Media de Personas: %{z}<extra></extra>',
        hoverongaps=False,
        zmin=10,
    ))

    heatmap.update_layout(
        title=title_override or 'Heatmap de Ocupación del Gimnasio',
        xaxis_title=xaxis_title or 'Día',
        yaxis_title=yaxis_title or 'Día de la Semana',
    )

    # Mostrar el heatmap en Streamlit
    st.plotly_chart(heatmap, use_container_width=True)