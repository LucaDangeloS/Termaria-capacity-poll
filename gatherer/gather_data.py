#!/usr/bin/python3
import schedule
import requests
from time import sleep, time
from bs4 import BeautifulSoup
from datetime import timedelta, datetime, date
import csv
from app_constants import places, int_weekday, time_closing, aperture_time

interval = timedelta(minutes=15)
aforo_folder = 'aforo/'
URL = 'https://termaria.deporsite.net/ocupacion-aforo'
API_URL = 'https://termaria.deporsite.net/ajax/TInnova_v2/Listado_OcupacionAforo/llamadaAjax/obtenerOcupacion'


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
    first_request = requests.get(URL)
    # Las devuelve como headers set-cookie la primera request, cada request las cambia, pero no es necesario modificarlas
    valid_cookies = first_request.cookies
    # Se extrae de una tag <meta> de la página y es obligatiorio enviarlo como header en las peticiones
    csrf_token = BeautifulSoup(first_request.text,"html.parser").find("meta",attrs={"name":"csrf-token"})["content"]

    return requests.post(API_URL,headers={"x-csrf-token":csrf_token},cookies=valid_cookies).json()


def get_week_n_year():
    year, week_num, _ = date.today().isocalendar()
    # Put a leading zero if week_num < 10
    week_num = "{:02d}".format(week_num)
    return (year, week_num)

def gather_data(week_day, time):
    print(f"Getting data for {week_day} at {time}")
    data = get_request_data()
    # Sala fitness sport id: 15
    # dictionary with the key of places and value of data
    aforos = {
        place: next(((d['Ocupacion'], d['Aforo'], d['Entradas'], d['Salidas']) for d in data if d['IdRecinto'] == placeId), None) 
    for place, placeId in places.items()
    }
    # if any of the aforos is None, skip
    if not all(aforos.values()):
        return
    write_data(week_day, time, aforos)

def write_data(week_day, time, aforos):
    year, week_n = get_week_n_year()
    with open(f'{aforo_folder}aforo_{year}_semana_{week_n}.csv', 'a+') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([week_day, time, aforos])

if __name__ == '__main__':
    accumulator = 0
    timestamps = {int_weekday[t]: [hour(x) for x in time_range(aperture_time[t], time_closing[t])] for t in int_weekday}
    for key in timestamps:
        for time in timestamps[key]:
            getattr(schedule.every(), key).at(time).do(gather_data, key, time)
            accumulator += 1
    print(f"Scheduled {accumulator} tasks")

    while True:
        schedule.run_pending()
        sleep(30)
