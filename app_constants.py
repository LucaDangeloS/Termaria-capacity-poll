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

seasons = {
    'spring': ['03-20', '06-21'],
    'summer': ['06-21', '09-23'],
    'fall': ['09-23', '12-21'],
    'winter': ['12-21', '03-20'],
}
