import datetime

places = {'Gimnasio': 15, 'Talaso': 4, 'Fan Interior': 16, "Sport": 2, }
PLACES_INDEXES = list(places.keys())
week_aperture_time = '7:30'
week_closing_time = '22:30'
int_weekday = {
    0: 'monday',
    1: 'tuesday',
    2: 'wednesday',
    3: 'thursday',
    4: 'friday',
    5: 'saturday',
    6: 'sunday',
}
pandas_int_weekday = {
    0: 'sunday',
    1: 'monday',
    2: 'tuesday',
    3: 'wednesday',
    4: 'thursday',
    5: 'friday',
    6: 'saturday',
}
spanish_weekday = {
    'monday': 'Lunes',
    'tuesday': 'Martes',
    'wednesday': 'Miércoles',
    'thursday': 'Jueves',
    'friday': 'Viernes',
    'saturday': 'Sábado',
    'sunday': 'Domingo',

}

aperture_time = {
                0: week_aperture_time, 
                1: week_aperture_time, 
                2: week_aperture_time, 
                3: week_aperture_time, 
                4: week_aperture_time, 
                5: '9:00',
                6: '9:30', 
}
time_closing = {
                0: week_closing_time, 
                1: week_closing_time, 
                2: week_closing_time, 
                3: week_closing_time, 
                4: week_closing_time, 
                5: '21:00',
                6: '15:00', 
}

seasons = [
    (datetime.datetime.strptime('03-20', '%m-%d'), 'Invierno'),
    (datetime.datetime.strptime('06-21', '%m-%d'), 'Primavera'),
    (datetime.datetime.strptime('09-23', '%m-%d'), 'Verano'),
    (datetime.datetime.strptime('12-21', '%m-%d'), 'Otoño'),
    (datetime.datetime.strptime('12-31', '%m-%d'), 'Invierno'),
]

months_spanish = {
    1: 'Enero',
    2: 'Febrero',
    3: 'Marzo',
    4: 'Abril',
    5: 'Mayo',
    6: 'Junio',
    7: 'Julio',
    8: 'Agosto',
    9: 'Septiembre',
    10: 'Octubre',
    11: 'Noviembre',
    12: 'Diciembre',
}