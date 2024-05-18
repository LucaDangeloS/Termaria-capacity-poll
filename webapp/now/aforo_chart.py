import streamlit as st # type: ignore
import altair as alt
from colorscheme import graph_colors


def chart(data, place, virtual_max):
    formatted_data = data[[place, 'year_day']]

    chart = (
            alt.Chart(formatted_data)
            .mark_area(
                interpolate='step',
            )
            .encode(
                x=alt.X('year_day:T', title='Hora', axis=alt.Axis(format='%H:%M')),
                y=alt.Y(f'{place}:Q', title='Personas', scale=alt.Scale(domain=(0, virtual_max))).stack(None), 
                color=alt.Color(
                    'temporal:N', 
                    scale=alt.Scale(range=[graph_colors['primary']]),
                    legend=None,
                )
                ,
                tooltip=[
                    alt.Tooltip(
                        field=place, 
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


def comparison_chart(timeframe_data, current_data, place, time_period, virtual_max):
    # Create view for the chart
    formatted_data = timeframe_data[[place, 'year_day']]

    COMPARISON_COLUMNS = ['Esta semana', time_period]

    formatted_data.insert(
        1, COMPARISON_COLUMNS[0], current_data[place]
    )
    formatted_data = formatted_data.rename(
        columns={place: COMPARISON_COLUMNS[1]},
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
    st.altair_chart(chart, use_container_width=True)