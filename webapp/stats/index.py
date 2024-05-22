import streamlit as st # type: ignore
from streamlit_option_menu import option_menu # type: ignore
import streamlit as st # type: ignore

from webapp.stats.charts.annual_chart import *
from webapp.stats.charts.temporal_comparison import *
from webapp.stats.charts.season_chart import *
from webapp.stats.charts.heatmaps import *
from webapp.stats.charts.trends import *

'''
IDEAS:
- Heatmap de los días más concurridos en relación la media
- Tendencia del aforo a lo largo de los meses de los últimos dos años
'''

def historic_stats_data(get_data):

    with st.spinner("Cargando datos..."):
        all_data = get_data()

    with st.sidebar:
        charts_options = {
            'Gráfica anual': annual_chart,
            'Comparación temporal': temporal_comparison_chart,
            'Por estaciones': season_chart,
            'Mapas de calor': heatmaps,
            'Tendencias': trends,
        }

        selected_chart = option_menu(
            menu_title = 'Gráficas',
            menu_icon = 'bar-chart-line',
            options = list(charts_options.keys()),
        )

        # Info
        st.info('El periodo de Mañana es hasta las 15:00 y el de Tarde es a partir de esa hora.')
        st.info('Los datos más antiguos son de Agosto del 2022.')

    # With the current selected chart, call the corresponding function
    charts_options[selected_chart](all_data)


