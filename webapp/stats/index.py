import streamlit as st # type: ignore
from streamlit_option_menu import option_menu # type: ignore
import streamlit as st # type: ignore

from webapp.stats.charts.annual_chart import *
from webapp.stats.charts.temporal_comparison import *
from webapp.stats.charts.season_chart import *
from webapp.stats.charts.heatmap import *
from webapp.stats.charts.trends import *
from webapp.stats.charts.day_periods_chart import *

'''
IDEAS:
- Media de personas por día anualmente *
- Comparación temporal en períodos:
    - Gráfica comparativa de aforo medio mensual por años
    - Gráfica comparativa de aforo medio diario por años
    - Estacionalidad en aforo por años
    - Comparación de la media de gente este año en relación al año pasado.
    - Comparación de la media de gente el año pasado en relación al anterior.
    - Comparación de la media de gente en un mes en relación al mes anterior.
- Estacionalidad en aforo
- Heatmap de los días más concurridos en relación la media
- Tendencia del aforo a lo largo de los meses de los últimos dos años
- Comparación de la diferencia de gente entre distintos períodos (mañana, principios de tarde, finales de tarde/noche)
Make a temporal comparison (mopnth after month, year after year) with bars marking the difference
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
            'Por períodos del día': day_periods_chart,
        }

        selected_chart = option_menu(
            menu_title = 'Gráficas',
            menu_icon = 'bar-chart-line',
            options = list(charts_options.keys()),
        )


    # With the current selected chart, call the corresponding function
    charts_options[selected_chart](all_data)


