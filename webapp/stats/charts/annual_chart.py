import datetime
from streamlit_option_menu import option_menu # type: ignore
from colorscheme import graph_colors
from process_data import remove_outliers, get_key
import streamlit as st # type: ignore
import altair as alt # type: ignore
from app_constants import pandas_int_weekday, PLACES_INDEXES
import pandas as pd # type: ignore
import streamlit_toggle as toggle # type: ignore
import numpy as np

COMPARISON_COLUMNS = ['Máximo', 'Media', 'Personas', '']

# https://altair-viz.github.io/user_guide/interactions.html

@st.cache_data(ttl=datetime.timedelta(minutes=180), show_spinner=False)
def reprocess_data(data, place):
    print('Reprocessing data')
    # Add the max col and mean col
    formatted_data = remove_outliers(data, place)
    formatted_data[COMPARISON_COLUMNS[0]] = formatted_data.groupby(['year', 'day', 'week'])[place].transform('max')
    formatted_data[COMPARISON_COLUMNS[1]] = formatted_data.groupby(['year', 'day', 'week'])[place].transform('mean')
    formatted_data = formatted_data[['year', 'day', 'week', COMPARISON_COLUMNS[0], COMPARISON_COLUMNS[1]]].round(0).reset_index(drop=True)

    # Combine the year, week and day columns into a year_day column
    formatted_data['year_day'] = formatted_data.apply(lambda x: datetime.datetime.strptime(f"{x['year']}-W{x['week']}-{get_key(pandas_int_weekday, x['day'])}", "%Y-W%W-%w"), axis=1)

    # remove duplicates
    # Convert to long format adding the type column that has the values 'Máximo' and 'Media'
    formatted_data = formatted_data.drop_duplicates(subset=['year', 'day', 'week', COMPARISON_COLUMNS[0], COMPARISON_COLUMNS[1], 'year_day'])

    reformatted_data = formatted_data.melt(
        id_vars=['year_day'],
        value_vars = COMPARISON_COLUMNS[:2],
        var_name='type',
        value_name='Personas',
    )

    # merge
    formatted_data = formatted_data.merge(reformatted_data, on='year_day')
    formatted_data['tooltip_text'] = formatted_data['type'].apply(
        lambda x: 'Media' if x == 'Media' else 'Máximo'
    )

    return formatted_data


def annual_chart(data):
    with st.expander('Instalación', True):
        place = option_menu(
            menu_title = '',
            menu_icon = '',
            icons = ['none'] * 3,
            orientation = 'horizontal',
            options = PLACES_INDEXES[:-1],
            default_index = 0,
        )

    selector_options = [
        'Inicio de los tiempos',
    ] + data.year.unique().tolist()[::-1]

    with st.container():
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_period_option = st.selectbox('Selecciona el período', selector_options)
            selected_first = (selected_period_option == selector_options[0])
        with col2:
            # Toggle para marcar desde
            st.write('\n')  # Add a newline for vertical spacing
            st.write('\n')  # Add another newline for vertical spacing
            from_toggle = st.checkbox('Desde', selected_first, disabled=selected_first)

        with st.container():
            col1, col2, col3, col4 = st.columns(4)
            # add some padding in the left
            with col1:
                chart_max_toggle = st.checkbox('Máximo', value=True)
            with col2:
                chart_mean_toggle = st.checkbox('Media', value=True) * 2
            with col3:
                chart_media_semanal_toggle = st.checkbox('Media Semanal', value=True)
            with col4:
                trend_line_toggle = st.checkbox('Linea de tendencia', value=False)

    if selected_first:
        data = data
    else:
        data = data[data.year >= selected_period_option] if from_toggle else data[data.year == selected_period_option]

    formatted_data = reprocess_data(data, place)
    virtual_max = formatted_data['Personas'].max() * 1.2

    comparison_idx =  (chart_max_toggle + chart_mean_toggle)
    comparison = COMPARISON_COLUMNS[comparison_idx - 1]

    ### Main chart
    if comparison_idx == 3:
        chart = alt.Chart(formatted_data).mark_area(
                opacity=0.9,
                interpolate='step',
            ).encode(
                x=alt.X('year_day:T', title='Día', axis=alt.Axis(format='%Y - %d/%m')),
                y=alt.Y('Personas:Q', title='Personas', scale=alt.Scale(domain=(0, virtual_max))).stack(None), 
                color=alt.Color(
                    'type:N',
                    scale=alt.Scale(range=[graph_colors['primary'], graph_colors['secondary']]),
                    legend=alt.Legend(
                        title='', 
                        orient='top-left',
                    ),
                ),
                # Conditional tooltip based on the type
                tooltip=[
                    alt.Tooltip(
                        field='Personas', 
                        title='Personas'
                    ),
                    alt.Tooltip(
                        field='tooltip_text', 
                        title='Tipo'
                    ),
                    alt.Tooltip(
                        field='year_day', 
                        timeUnit='utcyearmonthdate', 
                        title='Día'
                    ),
                ],
            )
        
    elif comparison_idx > 0:

        chart = alt.Chart(formatted_data).mark_area(
                opacity=0.9,
                interpolate='step',
            ).encode(
                x=alt.X('year_day:T', title='Día', axis=alt.Axis(format='%Y - %d/%m')),
                y=alt.Y(f'{comparison}:Q', title='Personas', scale=alt.Scale(domain=(0, virtual_max))).stack(None), 
                color=alt.value(graph_colors['primary'] if comparison == 'Media' else graph_colors['secondary']),
                tooltip=[
                    alt.Tooltip(
                        field=comparison, 
                        title=f'{comparison} de Personas'
                    ),
                    alt.Tooltip(
                        field='year_day', 
                        timeUnit='utcyearmonthdate', 
                        title='Día'
                    ),
                ],
            ).interactive(
                bind_x = False
            )
    else:
        # empty dummy chart
        chart = alt.Chart(pd.DataFrame()).mark_point().encode(
            # x=alt.X('year_day:T', title='Día', axis=alt.Axis(format='%Y - %d/%m')),
            # y=alt.Y('Personas:Q', title='Personas', scale=alt.Scale(domain=(0, virtual_max))),
        ).interactive(
            bind_x = False
        )

    ### Get years from the data that have the first week of the year
    years = data[data.week == 1].year.unique()
    year_dummy_df = pd.DataFrame({'year': years, 'year_day': pd.to_datetime([f"{year}-01-01" for year in years])})
    year_lines = alt.Chart(year_dummy_df).mark_rule(color='blue').encode(
        x=alt.X('year_day:T', title='Año', axis=alt.Axis(format='%Y')),
        size=alt.value(1),
    ).interactive(
        bind_x = False
    )

    # Create a df with each week ofevery year, keeping the year_day column with the first day of the week
    mean_week = formatted_data.groupby(['year', 'week']).agg(
        {
            'Personas' : 'mean',
            'year_day': 'last'
        }
    ).round(0).reset_index()

    ### Add red dots in the mean of each week
    if chart_media_semanal_toggle:
        mean_week_chart = alt.Chart(mean_week).mark_circle(color='red').encode(
            x=alt.X('year_day:T', title='', axis=alt.Axis(format='%Y - %d/%m')),
            y=alt.Y('Personas:Q', title='Personas', scale=alt.Scale(domain=(0, virtual_max))),
            tooltip=[
                alt.Tooltip(
                    field='Personas', 
                    title='Media de Personas'
                ),
                alt.Tooltip(
                    field='week',
                    title='Semana',
                ),
                alt.Tooltip(
                    field='year_day', 
                    timeUnit='utcyearmonthdate', 
                    title='Hora'
                ),
            ],
            size=alt.value(50),
        ).interactive(
            bind_x = False
        )
    else:
        mean_week_chart = alt.Chart(pd.DataFrame()).mark_point().encode()

    @st.cache_data(ttl=datetime.timedelta(minutes=180), show_spinner=False)
    def calculate_trend_line(data):
        z = np.polyfit(data.index, data['Personas'], 1)
        p = np.poly1d(z)
        data['trend'] = p(data.index).round(2)
        data['slope'] = z[0].round(2)
        return data

    ### Add a trend line using polyfit the mean of each week
    if trend_line_toggle:
        mean_week = calculate_trend_line(mean_week)
        trend_line = alt.Chart(mean_week).mark_line(color='black').encode(
            x='year_day:T',
            y=alt.Y('trend:Q', title='', scale=alt.Scale(domain=(0, virtual_max))),
            size=alt.value(4),
            tooltip=[	
                alt.Tooltip(
                    field='trend', 
                    title='Tendencia'
                ),
                alt.Tooltip(
                    field='year_day', 
                    timeUnit='utcyearmonthdate', 
                    title='Día'
                ),
                alt.Tooltip(
                    field='slope', 
                    title='Pendiente'
                ),
            ],
        ).interactive(
            bind_x = False
        )
    else:
        trend_line = alt.Chart(pd.DataFrame()).mark_line().encode().interactive(
            bind_x = False
        )
        # trend_line = alt.Chart(mean_week).transform_loess(
        #     'year_day', 'Personas', groupby=['year'], as_=['year_day', 'Personas']
        # ).mark_line(color='black').encode(
        #     x='year_day:T',
        #     y='Personas:Q',
        # )

    st.altair_chart((chart + year_lines + mean_week_chart + trend_line), use_container_width=True)

