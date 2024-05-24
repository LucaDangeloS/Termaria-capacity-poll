import streamlit as st
import plotly.express as px
from colorscheme import graph_colors
from app_constants import spanish_weekday

def process_weekly_data(data, fields = ['year'], rename=True):
    weekly_data = data.groupby(['day'] + fields).mean(numeric_only=True).round(0).reset_index()
    weekly_data['sp_day'] = weekly_data['day'].map(spanish_weekday)
    weekly_data['year_str'] = weekly_data['year'].astype(str)

    return weekly_data

def day_period_chart(data, place, title_override=None, x='year_str', x_label='Año', orders=None):

    hour_period_chart = px.bar(
        data,
        x=x,
        y=place,
        color='period',
        barmode='group',
        color_discrete_sequence=graph_colors,
        labels={
            x: x_label,
            place: 'Media de Personas',
            'period': 'Periodo'
        },
        category_orders=orders,  # Specify the order of the periods
    )

    # Update layout to handle the x-axis labels orientation and chart size
    hour_period_chart.update_layout(
        xaxis={'categoryorder': 'array'},  # Use the specified order of the months
        barmode='group',
        title={ # 
            'text': title_override or f'Comparación de la media de {place} por periodo del día',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title = x_label,
        yaxis_title='Media de Personas',
        legend_title_text = x_label,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        clickmode='none',
        dragmode='pan',
        autosize=True,
    )

    st.plotly_chart(hour_period_chart, use_container_width=True)