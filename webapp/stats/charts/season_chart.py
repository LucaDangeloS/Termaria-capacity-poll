import datetime
from typing import Dict
from streamlit_option_menu import option_menu # type: ignore
from colorscheme import graph_colors
from process_data import remove_outliers, get_key
import streamlit as st # type: ignore
import altair as alt # type: ignore
from app_constants import PLACES_INDEXES, months_spanish, seasons, spanish_weekday
from webapp.stats.charts.components.weekly_chart import process_weekly_data, weekly_chart
import pandas as pd # type: ignore
import streamlit_toggle as toggle # type: ignore
import numpy as np
import plotly.express as px
# from streamlit_plotly_events import plotly_events

def process_season_data(data):
    data['month'] = data['month'].map(months_spanish)
    data['year_str'] = data['year'].astype(str)
 
    def get_season(date, seasons):
        year = date.year
        for start, season in seasons:
            if date <= start.replace(year=year):
                return season

    # Create a column with the seasons in the seasons
    data['season'] = data['year_day'].apply(lambda x: get_season(x, seasons))

    return data

@st.cache_data(ttl=datetime.timedelta(minutes=180), show_spinner=False)
def reprocess_data(data, place):
    print('Reprocessing data')
    clean_data = remove_outliers(data, place)
    
    ### ADD SEASON DATA ###
    season_data = process_season_data(clean_data)

    ### WEEKDAY DATA ###
    weekly_data = process_weekly_data(season_data, ['season'])

    ### WEEKLY DATA ###
    # weekly_data = season_data.groupby(['season', 'year_str', 'week']).mean(numeric_only=True).groupby(['season', 'year_str']).mean(numeric_only=True).round(0).reset_index()

    ### DAY PERIOD DATA ###
    period_data = season_data.groupby(['season', 'period']).mean(numeric_only=True).round(0).reset_index()

    return season_data.groupby(['season', 'year_str']).mean(numeric_only=True).round(0).reset_index(), weekly_data, period_data


def season_chart(data):  # sourcery skip: extract-duplicate-method
    with st.expander('Instalación', True):
        place = option_menu(
            menu_title = '',
            menu_icon = '',
            icons = ['none'] * 3,
            orientation = 'horizontal',
            options = PLACES_INDEXES[:-1],
            default_index = 0,
        )

    options_year_1 = data.year.unique().tolist()[::-1]

    selected_years = sorted(st.multiselect('Seleccionar años para comparar', options_year_1, default=options_year_1, placeholder='Seleccionar años'))

    data = data[(data['year'].isin(selected_years))]
    data = data.assign(month = data['year_day'].dt.month)

    season_data, weekly_data, period_data = reprocess_data(data, place)

    ### WEEKDAY CHART ###
    weekly_chart(weekly_data, place, 'Media de día de semana por estaciones', 'season', 'Estación')

    ### SEASONS CHART ###
    season_chart = px.bar(
        season_data,
        x='season',
        y=place,
        color='year_str',
        barmode='group',
        color_discrete_sequence=graph_colors,
        labels={
            'season': 'Estación',
            place: 'Media de Personas',
            'year_str': 'Año'
        },
        category_orders={'month': list(months_spanish.values())},  # Specify the order of the months
    )

    # Update layout to handle the x-axis labels orientation and chart size
    season_chart.update_layout(
        xaxis={'categoryorder': 'array'},  # Use the specified order of the months
        barmode='group',
        title={
            'text': f'Comparación de la media de {place} por estación por años',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Mes',
        yaxis_title='Media de Personas',
        legend_title_text='Año',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        clickmode='none',
        dragmode='zoom',
        autosize=True,
    )

    # Do not allow zoom in any axis
    season_chart.update_xaxes(fixedrange=True)
    season_chart.update_yaxes(fixedrange=True)

    st.plotly_chart(season_chart, use_container_width=True)

    ### DAY PERDIODS CHART ###
    hour_period_chart = px.bar(
        period_data,
        x='season',
        y=place,
        color='period',
        barmode='group',
        color_discrete_sequence=graph_colors,
        labels={
            'season': 'Estación',
            place: 'Media de Personas',
            'period': 'Periodo'
        },
        category_orders={'month': list(months_spanish.values())},  # Specify the order of the months
    )

    # Update layout to handle the x-axis labels orientation and chart size
    hour_period_chart.update_layout(
        xaxis={'categoryorder': 'array'},  # Use the specified order of the months
        barmode='group',
        title={
            'text': f'Comparación de la media de {place} por periodo del día y por estación en los años {selected_years}',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Mes',
        yaxis_title='Media de Personas',
        legend_title_text='Año',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        clickmode='none',
        dragmode='zoom',
        autosize=True,
    )

    st.plotly_chart(hour_period_chart, use_container_width=True)