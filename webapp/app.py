from app_constants import places, spanish_weekday, int_weekday, PLACES_INDEXES
from streamlit_option_menu import option_menu # type: ignore
from process_data import read_csv, scan_dir, remove_outliers
from schedule import every, repeat, run_pending
# from streamlit_echarts import st_echarts
from colorscheme import graph_colors
import streamlit as st # type: ignore
import altair as alt
import pandas as pd
import datetime
import os
# from sectores import sectores

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

if COMPARE:
    mean = remove_outliers(data[(data.year_day >= from_date)], selected_place).groupby(['day', 'time']).mean().round(0)
    mean = mean.reset_index().set_index('time')[PLACES_INDEXES]
    timeframe_data.loc[mean.index.intersection(timeframe_data.index), PLACES_INDEXES] = mean
    
    # Centered days range text
    st.markdown(f"<h3 style='text-align: center;'> Media de {(from_date + datetime.timedelta(days=weekday_idx)).strftime('%d/%m/%Y')} - {(datetime.datetime.now()).strftime('%d/%m/%Y')}</h3>", unsafe_allow_html=True)

# Create view for the chart
formatted_data = timeframe_data[[selected_place, 'year_day']]

########################
# st.table(formatted_data)
# from_date.isoformat()
# 99% quantile
virtual_max = all_data[selected_place].quantile(0.992)

# with st.container():
#     col1, col2 = st.columns([1, 1])
#     with col1:
#         st.write("timeframe_data")
#         st.table(timeframe_data)
#     with col2:
#         st.write("current_data")
#         st.table(mean)

# st.markdown(f"<h2>Aforo de {selected_place}</h2>", unsafe_allow_html=True)
# Show chart

# IDEAS: 
# plot bar chart with error bars marking the 95% confidence interval for the periods
# Make a temporal comparison (mopnth after month, year after year) with bars marking the difference
# Diff heatmap
# heatmap

#TODO: Separate this into a function? 

if COMPARE:
    # Insert data from the current week for comparison
    COMPARISON_COLUMNS = ['Esta semana', selected_time_period]

    formatted_data.insert(
        1, COMPARISON_COLUMNS[0], current_data[selected_place]
    )
    formatted_data = formatted_data.rename(
        columns={selected_place: COMPARISON_COLUMNS[1]},
    )
    # Transform wide-formatted data into long-formatted data
    formatted_data = formatted_data.melt(
        id_vars=['year_day'],
        value_vars=COMPARISON_COLUMNS,
        var_name='temporal',
        value_name='Personas',
    )

    chart = (
        alt.Chart(formatted_data)
        .mark_area(
            opacity=0.7,
            interpolate='step',
        )
        .encode(
            x=alt.X('year_day:T', title='Hora', axis=alt.Axis(format='%H:%M')),
            y=alt.Y('Personas:Q', title='Personas', scale=alt.Scale(domain=(0, virtual_max))).stack(None), 
            color=alt.Color(
                'temporal:N', 
                scale=alt.Scale(range=[graph_colors['primary'], graph_colors['secondary']]),
                legend=alt.Legend(
                    title='Comparación', 
                    orient='top-left',
                    # values=['Actual', selected_week_number],
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    field="Personas", 
                    # title='Personas ' + selected_week_number.lower(),
                ),
                alt.Tooltip(
                    field='year_day', 
                    timeUnit='hoursminutes', 
                    title='Hora'
                ),
            ],
        )
    )
    # st.table(formatted_data)

else:
    chart = (
        alt.Chart(formatted_data)
        .mark_area(
            interpolate='step',
        )
        .encode(
            x=alt.X('year_day:T', title='Hora', axis=alt.Axis(format='%H:%M')),
            y=alt.Y(f'{selected_place}:Q', title='Personas', scale=alt.Scale(domain=(0, virtual_max))).stack(None), 
            color=alt.Color(
                'temporal:N', 
                scale=alt.Scale(range=[graph_colors['primary']]),
                legend=None,
            )
            ,
            tooltip=[
                alt.Tooltip(
                    field=selected_place, 
                    title='Personas'
                ),
                alt.Tooltip(
                    field='year_day', 
                    timeUnit='hoursminutes', 
                    title='Hora'
                ),
            ],
        )
    )

st.altair_chart(chart, use_container_width=True)
# sectores(data)