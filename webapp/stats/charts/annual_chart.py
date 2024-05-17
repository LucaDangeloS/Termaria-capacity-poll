import datetime
import random
from colorscheme import graph_colors
from process_data import remove_outliers, get_key
import streamlit as st # type: ignore
import altair as alt
from app_constants import pandas_int_weekday


def annual_chart(data):
    random_week = random.randint(1, 52)
    # formatted_data = data[(data.week == random_week) & (data.year == 2023) & (data.day == 'monday')]
    # add row iwht the 0.75 quantile
    # formatted_data['q_75'] = formatted_data['Gimnasio'].quantile(0.75)
    place = 'Gimnasio'

    formatted_data = remove_outliers(data, place).groupby(['year', 'day', 'week']).mean(numeric_only=True).reset_index()
    # Combine the year, week and day columns into a datetime column, using the get_key(pandas_int_weekday, day) function to get the weekday index
    formatted_data['year_day'] = formatted_data.apply(lambda x: datetime.datetime.strptime(f"{x['year']}-W{x['week']}-{get_key(pandas_int_weekday, x['day'])}", "%Y-W%W-%w"), axis=1)
    formatted_data.sort_values(by=['year_day'], ascending=False, inplace=True)
    # print(formatted_data)# x['year']}-W{x['week']}-{x['day']
    chart = alt.Chart(formatted_data).mark_area(
            interpolate='step',
        ).encode(
            x=alt.X('year_day:T', title='Día', axis=alt.Axis(format='%Y - %d/%m')),
            y=alt.Y('Gimnasio:Q', title='Personas', scale=alt.Scale(domain=(0, 160))).stack(None), 
            color=alt.Color(
                'temporal:N', 
                scale=alt.Scale(range=[graph_colors['primary']]),
                legend=None,
            )
            ,
            tooltip=[
                alt.Tooltip(
                    field='Gimnasio', 
                    title='Personas'
                ),
                alt.Tooltip(
                    field='year_day', 
                    timeUnit='utcyearmonthdate', 
                    title='Hora'
                ),
            ],
        )
    max_line = alt.Chart(formatted_data).mark_rule(color='red').encode(
        y='max(Gimnasio):Q',
        size=alt.value(2),
    )

    mean_line = alt.Chart(formatted_data).mark_rule(color='blue').encode(
        y='mean(Gimnasio):Q',
        size=alt.value(2),
    )

    # st.altair_chart((chart + max_line + mean_line), use_container_width=True)
    st.altair_chart((chart), use_container_width=True)

    st.table(formatted_data)

    # st.write(formatted_data['Gimnasio'].mean())
    # st.write(formatted_data['Gimnasio'].max())

