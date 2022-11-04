#!/usr/bin/python3
import schedule
import requests
from time import sleep, time
from bs4 import BeautifulSoup
from datetime import timedelta, datetime, date
import csv

interval = timedelta(minutes=30)
week_aperture_time = '7:30'
week_closing_time = '22:30'
aforo_folder = 'aforo/'
URL = 'https://termaria.deporsite.net/ocupacion-aforo'
API_URL = 'https://termaria.deporsite.net/ajax/TInnova_v2/Listado_OcupacionAforo/llamadaAjax/obtenerOcupacion'
int_weekday = {
    0: 'sunday',
    1: 'monday',
    2: 'tuesday',
    3: 'wednesday',
    4: 'thursday',
    5: 'friday',
    6: 'saturday'
}
aperture_time = {
                0: '9:30', 
                1: week_aperture_time, 
                2: week_aperture_time, 
                3: week_aperture_time, 
                4: week_aperture_time, 
                5: week_aperture_time, 
                6: '9:30'
}
time_closing = {
                0: '15:00', 
                1: week_closing_time, 
                2: week_closing_time, 
                3: week_closing_time, 
                4: week_closing_time, 
                5: week_closing_time, 
                6: '21:00'
}
places = {'Talaso': 4, 'Gimnasio': 15, 'Fan Interior': 16}


def ct(time):
    today = datetime.now().strftime('%d-%m-%Y')
    return datetime.strptime(f'{today} {time}', '%d-%m-%Y %H:%M')


def hour(time):
    return time.strftime('%H:%M')


def time_range(time_init, time_end):
    time_init = ct(time_init)
    time_end = ct(time_end)
    new_time = time_init
    while new_time <= time_end:
        yield new_time
        new_time += interval

def get_request_data():
    #author: Valonso
    first_request = requests.get('https://termaria.deporsite.net/ocupacion-aforo')
    # Las devuelve como headers set-cookie la primera request, cada request las cambia, pero no es necesario modificarlas
    valid_cookies = first_request.cookies
    # Se extrae de una tag <meta> de la página y es obligatiorio enviarlo como header en las peticiones
    csrf_token = BeautifulSoup(first_request.text,"html.parser").find("meta",attrs={"name":"csrf-token"})["content"]

    return requests.post('https://termaria.deporsite.net/ajax/TInnova_v2/Listado_OcupacionAforo/llamadaAjax/obtenerOcupacion',headers={"x-csrf-token":csrf_token},cookies=valid_cookies).json()


def get_week_n_year():
    year, week_num, _ = date.today().isocalendar()
    return (year, week_num)

def gather_data(week_day, time):
    data = get_request_data()
    # Sala fitness sport id: 15
    # dictionary with the key of places and value of data
    aforos = {
        place: next(((d['Ocupacion'], d['Aforo']) for d in data if d['IdRecinto'] == placeId), None) 
    for place, placeId in places.items()
    }
    write_data(week_day, time, aforos)

def write_data(week_day, time, aforos):
    year, week_n = get_week_n_year()
    with open(f'{aforo_folder}aforo_semana_{week_n}_{year}.csv', 'a+') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([week_day, time, aforos])

if __name__ == '__main__':
    timestamps = {int_weekday[t]: [hour(x) for x in time_range(aperture_time[t], time_closing[t])] for t in int_weekday}
    for key in timestamps:
        for time in timestamps[key]:
            getattr(schedule.every(), key).at(time).do(gather_data, key, time)

    # print(get_week_n_year())

    while True:
        schedule.run_pending()
        sleep(30)
