import datetime
from typing import Dict
from streamlit_option_menu import option_menu # type: ignore
from colorscheme import graph_colors
from process_data import remove_outliers, get_key
import streamlit as st # type: ignore
import altair as alt # type: ignore
from app_constants import pandas_int_weekday, PLACES_INDEXES, months_spanish, spanish_weekday
import pandas as pd # type: ignore
import streamlit_toggle as toggle # type: ignore
import numpy as np
import plotly.express as px
# from streamlit_plotly_events import plotly_events

def process_monthly_data(data, place):
    month_data = data.groupby(['month', 'year']).mean(numeric_only=True).round(0).reset_index().rename(columns={place: 'month_mean'})
    month_data['month'] = month_data['month'].map(months_spanish)
    month_data.sort_values(by=['year', 'month'], inplace=True)
    month_data['year_str'] = month_data['year'].astype(str)

    return month_data

def process_weekly_data(data, place):
    weekly_data = data.groupby(['day', 'year',]).mean(numeric_only=True).round(0).reset_index().rename(columns={place: 'weekly_mean'})
    weekly_data['sp_day'] = weekly_data['day'].map(spanish_weekday)
    weekly_data['year_str'] = weekly_data['year'].astype(str)

    return weekly_data

@st.cache_data(ttl=datetime.timedelta(minutes=180), show_spinner=False)
def reprocess_data(data, place):
    print('Reprocessing data')
    clean_data = remove_outliers(data, place)
    
    ### MONTHLY DATA ###
    month_data = process_monthly_data(clean_data, place)

    ### WEEKLY DATA ###
    weekly_data = process_weekly_data(clean_data, place)
    
    return month_data, weekly_data


def temporal_comparison_chart(data):  # sourcery skip: extract-duplicate-method
    # initialize_state()

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

    selected_years = st.multiselect('Seleccionar años a comparar', options_year_1, default=options_year_1)

    data = data[(data['year'].isin(selected_years))]
    data = data.assign(month = data['year_day'].dt.month)

    monthly_data, weekly_data = reprocess_data(data, place)

    ### MONTHLY CHART ###
    months_chart = px.bar(
        monthly_data,
        x='month',
        y='month_mean',
        color='year_str',
        barmode='group',
        color_discrete_sequence=graph_colors,
        labels={
            'month': 'Mes',
            'month_mean': 'Media de Personas',
            'year_str': 'Año'
        },
        title=f'Comparación de la media de {place} por mes entre en los años {selected_years}',
        category_orders={'month': list(months_spanish.values())},  # Specify the order of the months
    )

    # Update layout to handle the x-axis labels orientation and chart size
    months_chart.update_layout(
        xaxis={'categoryorder': 'array'},  # Use the specified order of the months
        barmode='group',
        title={
            'text': f'Comparación de la media de {place} por mes entre en los años {selected_years}',
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
        clickmode='event+select',
        dragmode='select',  # Enable the cross to select areas
        autosize=True,
    )

    # Do not allow zoom in any axis
    months_chart.update_xaxes(fixedrange=True)
    months_chart.update_yaxes(fixedrange=True)

    ### CROSSFILTERING ###
    selected_points = st.plotly_chart(months_chart, use_container_width=True, on_select="rerun")
    filtered_weekly_data = weekly_data
    if selected_points:
        selected_months = pd.DataFrame([{'month': point['x'], 'year': int(point['legendgroup'])} for point in selected_points['select']['points']], columns=['month', 'year'])
        selected_months['month'] = selected_months['month'].apply(lambda x: get_key(months_spanish, x))
        # Filter the data
        selected_months_data = data[(data['year'].isin(selected_months['year'])) & (data['month'].isin(selected_months['month']))]
        filtered_weekly_data = process_weekly_data(selected_months_data, place)

    ### WEEKLY CHART ###
    weekly_chart = px.bar(
        filtered_weekly_data,
        x='sp_day',
        y='weekly_mean',
        color='year_str',
        barmode='group',
        color_discrete_sequence=graph_colors,
        labels={
            'sp_day': 'Día',
            'weekly_mean': 'Media de Personas',
            'year_str': 'Año'
        },
        title=f'Comparación de la media de {place} por día de la semana entre en los años {selected_years}',
        category_orders={'sp_day': list(spanish_weekday.values())},  # Specify the order of the weekdays
    )

    # Update layout to handle the x-axis labels orientation and chart size
    weekly_chart.update_layout(
        xaxis={'categoryorder': 'array'},  # Use the specified order of the weekdays
        barmode='group',
        title={
            'text': f'Comparación de la media de {place} por día de la semana',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Día de la Semana',
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
    )

    st.markdown("<p style='text-align: center;'> Selecciona una zona en la gráfica de barras de arriba para filtrar los datos de la gráfica de abajo</p>", unsafe_allow_html=True)

    st.plotly_chart(weekly_chart, use_container_width=True)
