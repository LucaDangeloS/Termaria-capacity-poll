import streamlit as st # type: ignore
from app_constants import spanish_weekday, int_weekday, PLACES_INDEXES
from streamlit_option_menu import option_menu # type: ignore
from process_data import remove_outliers
import streamlit as st # type: ignore
import datetime
from now.aforo_chart import chart, comparison_chart

def debug(timeframe_data, current_data):
    with st.container():
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write("Datos de timeframe_data")
                st.table(timeframe_data)
            with col2:
                st.write("Datos de current_data")
                st.table(current_data)

def now_stats_page(get_data, curr_week_start, curr_weekday_idx):

    st.title('Aforo de Termaria')

    with st.sidebar:
        selected_weekday_options = {
                "Esta semana": curr_week_start,
                "Semana Pasada": curr_week_start - datetime.timedelta(weeks = 1),
                "Último mes": curr_week_start - datetime.timedelta(weeks = 4),
                "Últimos 3 meses": curr_week_start - datetime.timedelta(weeks = 4*3),
                "Último año": curr_week_start - datetime.timedelta(weeks = 52),
            }

        selected_place = option_menu(
            menu_title = 'Instalación 🏋️‍♂️',
            menu_icon = 'list',
            options = PLACES_INDEXES,
        )

        selected_time_period = option_menu(
            menu_title = 'Periodo',
            menu_icon = 'calendar',
            icons = ['caret-right'] + ['none'] * 4,
            options = list(selected_weekday_options.keys()),
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
        )

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

    ### DATA PROCESSING ###
    # Filter data according to the selected weekday
    data = all_data[all_data.day == weekday]
    timeframe_data = data[(data.year_day >= from_date) & (data.year_day < to_date)]
    current_data = data[data.year_day >= curr_week_start]
    virtual_max = all_data[selected_place].quantile(0.992)
    
    @st.cache_data(ttl=datetime.timedelta(minutes=15), show_spinner=False)
    def add_mean_data(timeframe_data, current_data):
        ### MORE DATA PROCESSING ###
        mean = remove_outliers(data[(data.year_day >= from_date) & (data.year_day < curr_week_start)], selected_place).groupby(['day', 'time']).mean(numeric_only=True).round(0)
        mean = mean.reset_index().set_index('time')[PLACES_INDEXES]
        timeframe_data = timeframe_data.set_index('time')
        current_data = current_data.set_index('time')
        # drop duplicated keeping the last
        # timeframe_data = timeframe_data[~timeframe_data.index.duplicated(keep='last')]
        # current_data = current_data[~current_data.index.duplicated(keep='last')]
        timeframe_data.loc[mean.index.intersection(timeframe_data.index), PLACES_INDEXES] = mean

        return timeframe_data, current_data

    if COMPARE:
        timeframe_data, current_data = add_mean_data(timeframe_data, current_data)

        # Centered days range text
        st.markdown(f"<h3 style='text-align: center;'> Media de {(from_date + datetime.timedelta(days=weekday_idx)).strftime('%d/%m/%Y')} - {(curr_week_start).strftime('%d/%m/%Y')}</h3>", unsafe_allow_html=True)

        comparison_chart(timeframe_data, current_data, selected_place, f"Media {selected_time_period}", virtual_max)

    else:
        chart(timeframe_data, selected_place, virtual_max)