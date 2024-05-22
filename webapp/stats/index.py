import streamlit as st # type: ignore
from streamlit_option_menu import option_menu # type: ignore
import streamlit as st # type: ignore

from webapp.stats.charts.annual_chart import *
from webapp.stats.charts.temporal_comparison import *
from webapp.stats.charts.season_chart import *
from webapp.stats.charts.heatmap import *
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
            'Mapa de calor por días': heatmap,
            'Tendencias': trends,
        }

        selected_chart = option_menu(
            menu_title = 'Gráficas',
            menu_icon = 'bar-chart-line',
            options = list(charts_options.keys()),
        )


    # With the current selected chart, call the corresponding function
    charts_options[selected_chart](all_data)


