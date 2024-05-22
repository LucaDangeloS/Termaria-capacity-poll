import streamlit as st
import plotly.express as px
from colorscheme import graph_colors
from app_constants import spanish_weekday

def process_weekly_data(data, fields = ['year'], rename=True):
    weekly_data = data.groupby(['day'] + fields).mean(numeric_only=True).round(0).reset_index()
    weekly_data['sp_day'] = weekly_data['day'].map(spanish_weekday)
    weekly_data['year_str'] = weekly_data['year'].astype(str)

    return weekly_data

def weekly_chart(data, place, title_override=None, color='year_str', color_label='Año'):
    ### WEEKLY CHART ###
    weekly_chart = px.bar(
        data,
        x='sp_day',
        y=place,
        color=color,
        barmode='group',
        color_discrete_sequence=graph_colors,
        labels={
            'sp_day': 'Día',
            place: 'Media de Personas',
            color: color_label
        },
        category_orders={'sp_day': list(spanish_weekday.values())},  # Specify the order of the weekdays
    )

    # Update layout to handle the x-axis labels orientation and chart size
    weekly_chart.update_layout(
        xaxis={'categoryorder': 'array'},  # Use the specified order of the weekdays
        barmode='group',
        title={
            'text': title_override or f'Comparación de la media de {place} por día de la semana',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Día de la Semana',
        yaxis_title='Media de Personas',
        legend_title_text='Año',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        clickmode='none',
        dragmode='zoom',
    )
    st.plotly_chart(weekly_chart, use_container_width=True)