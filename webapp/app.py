from streamlit_option_menu import option_menu # type: ignore
from process_data import scan_dir
import streamlit as st # type: ignore
import datetime
from now.index import now_stats_page
from stats.index import historic_stats_data

# Tab name
st.set_page_config(page_title='Aforo de Termaria', layout='wide')

# curr_week_number = datetime.datetime.now().isocalendar()[1]
# Get current week day
curr_weekday_idx = datetime.datetime.now().weekday()
curr_week_start = (datetime.datetime.now() - datetime.timedelta(days = curr_weekday_idx)).replace(hour=0, minute=0, second=0, microsecond=0)

@st.cache_data(ttl=datetime.timedelta(minutes=60), show_spinner=False)
def get_all_data(key = None):
    global data
    data = scan_dir("./aforo/", -1, -1, -1, reverse=False)
    return data

@st.cache_data(ttl=datetime.timedelta(minutes=15), show_spinner=False)
def get_partial_data(key = None, interval = 54):
    global data
    data = scan_dir("./aforo/", -1, -1, interval, reverse=False)
    return data

# IDEAS: 
# plot bar chart with error bars marking the 95% confidence interval for the periods

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
    historic_stats_data(get_all_data)