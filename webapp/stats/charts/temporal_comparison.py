from colorscheme import graph_colors
import streamlit as st # type: ignore
import altair as alt


def temporal_comparison_chart(data, place, virtual_max):
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
