from app_constants import places, spanish_weekday, int_weekday, PLACES_INDEXES
from streamlit_option_menu import option_menu # type: ignore
from process_data import read_csv, scan_dir, remove_outliers
from schedule import every, repeat, run_pending
# from streamlit_echarts import st_echarts
import streamlit as st # type: ignore
import altair as alt
import pandas as pd
import datetime
import os
# from sectores import sectores
from aforo_chart import chart, comparison_chart

# Main data
# data = scan_dir("./aforo/", -1, -1, -1, reverse=False)
# data = pd.DataFrame()
print("Refreshed")
# Tab name
st.set_page_config(page_title='Aforo de Termaria', layout='wide')

# Get current week day
curr_weekday_idx = datetime.datetime.now().weekday()
curr_week_number = datetime.datetime.now().isocalendar()[1]
curr_week_start = (datetime.datetime.now() - datetime.timedelta(days = curr_weekday_idx)).replace(hour=0, minute=0, second=0, microsecond=0)

@st.cache_data(ttl=datetime.timedelta(minutes=30), show_spinner=False)
def get_data():
    global data
    data = scan_dir("./aforo/", -1, -1, 54, reverse=False)
    return data

# def refresh_week_data():
#     global curr_weekday_idx, curr_week_number, curr_week_start
#     curr_weekday_idx = datetime.datetime.now().weekday()
#     curr_week_number = datetime.datetime.now().isocalendar()[1]
#     curr_week_start = datetime.datetime.now() - datetime.timedelta(days = curr_weekday_idx)

st.title('Aforo de Termaria')

# SIDE BAR
with st.sidebar:
    selected_weekday_options = {
        "Esta semana": curr_week_start,
        "Semana Pasada": curr_week_start - datetime.timedelta(days = 7),
        "Último mes": curr_week_start - datetime.timedelta(days = 30),
        "Últimos 3 meses": curr_week_start - datetime.timedelta(days = 90),
        "Último año": curr_week_start - datetime.timedelta(days = 365),
    }

    selected_place = option_menu(
        menu_title = 'Instalación 🏋️‍♂️',
        menu_icon = 'list',
        options = list(places.keys()),
        on_change = get_data,
        key = 'place',
    )

    selected_time_period = option_menu(
        menu_title = 'Periodo',
        menu_icon = 'calendar',
        icons = ['caret-right'] + ['none'] * 4,
        options = list(selected_weekday_options.keys()),
        # on_change = button_callback,
        key = 'week_number',
    )

# EXPANDER MENU
with st.expander('Día de la semana', True):
    selected_weekday = option_menu(
        menu_title = '',
        menu_icon = '',
        icons = ['none'] * 7,
        orientation = 'horizontal',
        options = list(spanish_weekday.values()),
        default_index = curr_weekday_idx,
        key = 'date_range'
    )

# IDEAS: 
# plot bar chart with error bars marking the 95% confidence interval for the periods
# Make a temporal comparison (mopnth after month, year after year) with bars marking the difference
# Diff heatmap
# heatmap


# Filter data
# Get the index of the selected weekday in the spanish_weekday dict
weekday_idx = list(spanish_weekday.values()).index(selected_weekday)

## Filter date variables
weekday = int_weekday[weekday_idx]
from_date = selected_weekday_options[selected_time_period]
from_date = from_date.replace(hour=0, minute=0, second=0, microsecond=0)
to_date = from_date + datetime.timedelta(days=7)

with st.spinner("Cargando datos..."):
    all_data = get_data()

COMPARE = (selected_time_period != list(selected_weekday_options.keys())[0])

# Filter data according to the selected weekday
data = all_data[all_data.day == weekday]
timeframe_data = data[(data.year_day >= from_date) & (data.year_day < to_date)]
current_data = data[data.year_day >= curr_week_start]

virtual_max = all_data[selected_place].quantile(0.992)

if COMPARE:
    mean = remove_outliers(data[(data.year_day >= from_date)], selected_place).groupby(['day', 'time']).mean().round(0)
    mean = mean.reset_index().set_index('time')[PLACES_INDEXES]
    timeframe_data.loc[mean.index.intersection(timeframe_data.index), PLACES_INDEXES] = mean
    
    # Centered days range text
    st.markdown(f"<h3 style='text-align: center;'> Media de {(from_date + datetime.timedelta(days=weekday_idx)).strftime('%d/%m/%Y')} - {(datetime.datetime.now()).strftime('%d/%m/%Y')}</h3>", unsafe_allow_html=True)
    comparison_chart(timeframe_data, current_data, selected_place, selected_weekday, virtual_max)

else:
    chart(timeframe_data, selected_place, virtual_max)
# sectores(data)