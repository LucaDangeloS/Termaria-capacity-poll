import sys
from streamlit_option_menu import option_menu # type: ignore
from process_data import scan_dir
import streamlit as st # type: ignore
import pandas as pd # type: ignore
import datetime
from now.index import now_stats_page
from stats.index import historic_stats_data

# Tab name
st.set_page_config(page_title='Aforo de Termaria', layout='wide')

# Get current week day
dt_obj = datetime.datetime.now()
curr_weekday_idx = dt_obj.weekday()
curr_week_start = (dt_obj - datetime.timedelta(days = curr_weekday_idx)).replace(hour=0, minute=0, second=0, microsecond=0)

@st.cache_data(ttl=datetime.timedelta(weeks=50), show_spinner=False)
def initial_load():
    return scan_dir("./aforo/", -1, -1, -1, reverse=False, verbose=True)

# @st.cache_data(ttl=datetime.timedelta(hours=24), show_spinner=False)
# def get_all_data(key = None):
#     global data
#     current_timestamp = dt_obj.strftime("%H:%M:%S %d/%m/%Y")
#     print(f"{current_timestamp}: Reloading all data")
#     data = scan_dir("./aforo/", -1, -1, -1, reverse=False, verbose=True)
#     return data

@st.cache_data(ttl=datetime.timedelta(minutes=5), show_spinner=False)
def get_partial_data(key = None, interval = -1):
    global data
    # get the last week loaded in data
    try:
        current_timestamp = dt_obj.strftime("%H:%M:%S %d/%m/%Y")
        current_year = dt_obj.year
        assert current_year == (data['year'].max())
        current_week = dt_obj.isocalendar()[1]
        last_week = data[data['year'] == current_year]['week'].max()
        prev_df_size = data.shape[0]
        n_last_weeks = (current_week - last_week) + 1

    except Exception as e:
        print(e, file=sys.stderr)
        return scan_dir("./aforo/", -1, -1, interval, reverse=False, verbose=True)

    data = data.drop(data[(data['year'] == current_year) & (data['week'] >= last_week)].index)
    print(f"{current_timestamp}: Reloading last {n_last_weeks} weeks")
    new_data = scan_dir("./aforo/", -1, -1, n_last_weeks, reverse=False, verbose=True)
    data = pd.concat([data, new_data])
    print(f"Dataframe increased {data.shape[0] - prev_df_size} rows.")

    return data

data = initial_load()

TABS = ['Ahora', 'Estadísticas']

# SIDE BAR
with st.sidebar:
    # Selector de ahora y estadísticas
    selected_tab = option_menu(
        menu_title = None,
        options = TABS,
        icons = ['none'] * 2,
        orientation = 'horizontal',
        # on_change = get_data,
    )

# MAIN PAGE
if selected_tab == TABS[0]:
    now_stats_page(get_partial_data, curr_week_start, curr_weekday_idx)
    
if selected_tab == TABS[1]:
    historic_stats_data(get_partial_data)
