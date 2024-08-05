import datetime
from colorscheme import graph_colors
import streamlit as st # type: ignore
import altair as alt
from app_constants import pandas_int_weekday, PLACES_INDEXES, months_spanish, int_weekday, spanish_weekday
from process_data import interpolate_missing_times, remove_outliers, get_key, trim_missing_times
from streamlit_option_menu import option_menu
from stats.charts.components.heatmap_chart import heatmap_chart
from stats.charts.components.weekly_chart import process_weekly_data # type: ignore
import plotly.graph_objects as go
import pandas as pd
from stats.charts.components.place_selector import place_selector


def process_yearly_data(data):
    data['month'] = data['month'].map(months_spanish)
    yearly_period_data = data.groupby(['month', 'month_day', 'period']).mean(numeric_only=True).round(0).reset_index()
    yearly_data = yearly_period_data.groupby(['month', 'month_day']).mean(numeric_only=True).round(0).reset_index()
    return yearly_period_data, yearly_data

# def process_monthly_data(data):
#     data = data.groupby(['month_day']).mean(numeric_only=True).round(0).reset_index()
#     return data

def process_hour_data(data):
    # formatted_data = interpolate_missing_times(data)
    formatted_data = trim_missing_times(data)
    formatted_data = formatted_data.groupby(['day', 'time']).mean(numeric_only=True).round(0).reset_index()
    formatted_data['sp_day'] = formatted_data['day'].map(spanish_weekday)
    formatted_data['time'] = formatted_data['time'].astype(str) # Convert 'time' column to string format
    formatted_data['time'] = pd.to_datetime(formatted_data['time']) # Convert 'time' column to datetime type
    formatted_data['time'] = formatted_data['time'].dt.strftime('%H:%M')
    return formatted_data

@st.cache_data(ttl=datetime.timedelta(minutes=180), show_spinner=False)
def reprocess_data(data, place):
    clean_data = remove_outliers(data, place)
    clean_data = clean_data.assign(month = clean_data['year_day'].dt.month)
    clean_data = clean_data.assign(month = clean_data['month'].map(months_spanish))
    clean_data = clean_data.assign(year_str = clean_data['year'].astype(str))
    clean_data['month'] = clean_data['year_day'].dt.month
    clean_data['month_day'] = clean_data['year_day'].dt.day
    clean_data.drop(columns=['year', 'week'], inplace=True)

    ### YEARLY DATA###
    # separated by day period
    yearly_period_data, yearly_data = process_yearly_data(clean_data)

    ### MONTHLY DATA ###
    # monthly_data = process_monthly_data(clean_data)

    ## HOUR DATA ##
    hour_data = process_hour_data(clean_data)

    return yearly_period_data, yearly_data, hour_data

def heatmaps(data):
    with st.expander('Instalación', True):
        place = place_selector()

    options_year_1 = data.year.unique().tolist()[::-1]
    selected_year = sorted(st.multiselect('Seleccionar años', options_year_1, default=options_year_1, placeholder='Seleccionar años'))

    data = data[data['year'].isin(selected_year)]
    yearly_period_data, yearly_data, hour_data = reprocess_data(data, place)

    # ### HOUR WEEKLY DATA ###
    # z_weekly = hour_data.pivot(index='sp_day', columns='time', values=place)
    # z_weekly.index = pd.Categorical(z_weekly.index, categories=spanish_weekday.values(), ordered=True)
    # z_weekly.sort_index(inplace=True)
    # # remove seconds from index time, datetime strip seconds
    # z_weekly.fillna(0, inplace=True)
    # heatmap_chart(z_weekly, title_override='Ocupación media por hora del día y semana', xaxis_title='Hora', yaxis_title='Día de la semana', colorscale='plasma', tooltip_override='Día: %{y}<br>Hora: %{x}<br>Media de Personas: %{z}<extra></extra>')

    ### YEARLY DATA ###
    z_yearly = yearly_data.pivot(index='month', columns='month_day', values=place)
    z_yearly.index = pd.Categorical(z_yearly.index, categories=months_spanish.values(), ordered=True)
    z_yearly.sort_index(inplace=True)
    z_yearly.fillna(0, inplace=True)
    heatmap_chart(z_yearly, title_override='Ocupación media por día del año', xaxis_title='Día', yaxis_title='Mes', colorscale='plasma')

    ### YEARLY PERIOD DATA ###
    diffs = yearly_period_data.pivot_table(index=['month', 'month_day'], columns='period', values=place).reset_index()
    if not diffs.empty:
        diffs['diff'] = diffs['Tarde'] - diffs['Mañana']
        diffs = diffs.pivot(index='month', columns='month_day', values='diff').fillna(0)
    diffs.index = pd.Categorical(diffs.index, categories=months_spanish.values(), ordered=True)
    diffs.sort_index(inplace=True)
    
    limit = max(abs(diffs.min().min()), diffs.max().max())

    heatmap = go.Figure(data=go.Heatmap(
        z=diffs.values,
        x=diffs.columns,
        y=diffs.index,
        textfont={"size":20},
        colorscale='RdBu',
        hovertemplate='Mes: %{y}<br>Día: %{x}<br>Diferencia media: %{z}<extra></extra>',
        hoverongaps=False,
        zmin=-limit,  # Center the colorscale around zero
        zmid=0,  # Center the colorscale around zero
        zmax=limit,
            colorbar=dict(
            tickvals=[-limit, 0, limit],  # Specify the tick positions
            ticktext=['Más por la mañana', 'Equilibrado', 'Más por la tarde'],  # Specify the corresponding tick labels
            title=''  # Set the title of the colorbar
        )
    ))

    heatmap.update_layout(
        title='Diferencia de media (Tarde - Mañana) por día del año',
        xaxis_title='Día',
        yaxis_title='Mes',
    )

    st.plotly_chart(heatmap, use_container_width=True)
    
