import datetime
from typing import Dict
from streamlit_option_menu import option_menu # type: ignore
from colorscheme import graph_colors
from process_data import remove_outliers, get_key, trim_missing_times
import streamlit as st # type: ignore
import altair as alt # type: ignore
from app_constants import pandas_int_weekday, PLACES_INDEXES, months_spanish, spanish_weekday
from stats.charts.components.day_period_chart import day_period_chart
from stats.charts.components.weekly_chart import process_weekly_data, weekly_chart
import pandas as pd # type: ignore
import numpy as np
import plotly.express as px
from stats.charts.components.heatmap_chart import heatmap_chart
# from streamlit_plotly_events import plotly_events
from stats.charts.components.place_selector import place_selector

def process_monthly_data(data):
    month_data = data.groupby(['month', 'year']).mean(numeric_only=True).round(0).reset_index()
    month_data['month'] = month_data['month'].map(months_spanish)
    # month_data.sort_values(by=['year', 'month'], inplace=True)
    month_data['year_str'] = month_data['year'].astype(str)

    return month_data

def process_period_data(data):
    # data['month'] = data['month'].map(months_spanish)
    data = data.assign(month = data['month'].map(months_spanish))
    # data['year_str'] = data['year'].astype(str)
    data = data.assign(year_str = data['year'].astype(str))
    return data.groupby(['year_str', 'period']).mean(numeric_only=True).round(0).reset_index()


def process_hour_data(data):
    # formatted_data = interpolate_missing_times(data)
    formatted_data = trim_missing_times(data)
    try:
        formatted_data = formatted_data.groupby(['day', 'time']).mean(numeric_only=True).round(0).reset_index()
        formatted_data['sp_day'] = formatted_data['day'].map(spanish_weekday)
        formatted_data['time'] = formatted_data['time'].astype(str) # Convert 'time' column to string format
        formatted_data['time'] = pd.to_datetime(formatted_data['time']) # Convert 'time' column to datetime type
        formatted_data['time'] = formatted_data['time'].dt.strftime('%H:%M')
    except KeyError:
        pass
    return formatted_data

@st.cache_data(ttl=datetime.timedelta(minutes=180), show_spinner=False)
def reprocess_data(data, place):
    clean_data = remove_outliers(data, place)
    
    ### MONTHLY DATA ###
    month_data = process_monthly_data(clean_data)

    ### WEEKLY DATA ###
    weekly_data = process_weekly_data(clean_data)
    
    ### DAY PERIOD DATA ###
    # period_data = clean_data.groupby(['month', 'period']).mean(numeric_only=True).round(0).reset_index()
    period_data = process_period_data(clean_data)

    ### HOUR DATA ###
    hour_data = process_hour_data(clean_data)

    return month_data, weekly_data, period_data, hour_data


def temporal_comparison_chart(data):  # sourcery skip: extract-duplicate-method
    with st.expander('Instalación', True):
        place = place_selector()

    options_year_1 = data.year.unique().tolist()[::-1]

    selected_years = sorted(st.multiselect('Seleccionar años para comparar', options_year_1, default=options_year_1, placeholder='Seleccionar años'))

    data = data[(data['year'].isin(selected_years))]
    data = data.assign(month = data['year_day'].dt.month)

    monthly_data, weekly_data, period_data, hour_data = reprocess_data(data, place)

    ### MONTHLY CHART ###
    months_chart = px.bar(
        monthly_data,
        x='month',
        y=place,
        color='year_str',
        barmode='group',
        color_discrete_sequence=graph_colors,
        labels={
            'month': 'Mes',
            place: 'Media de Personas',
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
        dragmode='pan',
        autosize=True,
    )

    # Do not allow zoom in any axis
    # months_chart.update_xaxes(fixedrange=True)
    # months_chart.update_yaxes(fixedrange=True)

    ### CROSSFILTERING ###
    selected_points = st.plotly_chart(months_chart, use_container_width=True, on_select="rerun")
    filtered_weekly_data = weekly_data
    filtered_period_data = period_data
    filtered_hour_data = hour_data
    if selected_points:
        selected_months = pd.DataFrame([{'month': point['x'], 'year': int(point['legendgroup'])} for point in selected_points['select']['points']], columns=['month', 'year'])
        selected_months['month'] = selected_months['month'].apply(lambda x: get_key(months_spanish, x))
        # Filter the data
        selected_months_data = data[(data['year'].isin(selected_months['year'])) & (data['month'].isin(selected_months['month']))]
        filtered_weekly_data = process_weekly_data(selected_months_data)
        filtered_period_data = process_period_data(selected_months_data)
        filtered_hour_data = process_hour_data(selected_months_data)

    st.markdown("<p style='text-align: center;'> Selecciona una zona en la gráfica de barras de arriba para filtrar los datos de las gráficas de abajo</p>", unsafe_allow_html=True)

    ### HEATMAP ###
    try:
        z_weekly = filtered_hour_data.pivot(index='sp_day', columns='time', values=place)
        z_weekly.index = pd.Categorical(z_weekly.index, categories=spanish_weekday.values(), ordered=True)
        z_weekly.sort_index(inplace=True)
        # remove seconds from index time, datetime strip seconds
        z_weekly.fillna(0, inplace=True)
        heatmap_chart(z_weekly, title_override='Mapa de calor de ocupación media por hora y día de semana', xaxis_title='Hora', yaxis_title='Día de la semana', colorscale='plasma', tooltip_override='Día: %{y}<br>Hora: %{x}<br>Media de Personas: %{z}<extra></extra>')
    except KeyError:
        pass
    ### WEEKLY CHART ###
    weekly_chart(filtered_weekly_data, place, f'Comparación de la media de {place} por día de la semana entre en los años {(selected_years)}') 

    # st.table(filtered_period_data)
    ### DAY PERDIODS CHART ###
    day_period_chart(filtered_period_data, place, f'Comparación de la media de {place} por periodo del día de los años y meses seleccionados')
