#!/usr/bin/python3
import ast
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

DEFAULT_DIR = "aforo"
DEFAULT_PLACE = "Gimnasio"
STATS_DIR = "statistics"
X_TICKS = 6

# Convert str dict into each column with each value and remove negative values
def reformat_dataframe(data):
    data.columns = ['day', 'time', 'aforo']
    reformatted = data['aforo'].apply(lambda x: ast.literal_eval(x)).apply(lambda x: {k: x[k][0] for k in x.keys()}).apply(pd.Series)
    data = data.drop('aforo', 1).assign(**reformatted)
    num = data._get_numeric_data()
    num[num < 0] = 0
    return data


def scan_dir(folder="."):
    total_data = pd.DataFrame()

    for root, dirs, files in os.walk(f"{folder}/"):
        for file in files:
            if file.startswith("aforo") and file.endswith(".csv"):
                print(f"{root}{file}")
                data = pd.read_csv(f"{root}{file}")
                data = reformat_dataframe(data)
                total_data = total_data.append(data)
    return total_data

def record_histogram(o_data, week_day, place, y_ticks):
    data = o_data[o_data['day'] == week_day].groupby(['day','time'], as_index = False)
    idxs = np.round(np.linspace(0, len(data) - 1, X_TICKS)).astype(int)

    mean_data = data.mean()
    median_data = data.median()

    plt.bar(mean_data['time'], mean_data[place], color='b', width=0.9, label='Mean')
    plt.bar(median_data['time'], median_data[place], color='tab:orange', width=0.5, label='Median')

    plt.legend()
    plt.xticks(mean_data.loc[idxs]['time'])
    plt.yticks(y_ticks)
    plt.title(f'{week_day.capitalize()} {place.capitalize()}')
    plt.savefig(f'{STATS_DIR}/histogram_{place}_{week_day}.png')
    plt.cla()
    plt.clf()

if __name__ == '__main__':
    if (len(sys.argv) > 1):
        try:
            day = sys.argv[1]
            comoda = sys.argv[2]
        except:
            comoda = sys.argv[1]
            day = None
    else:
        day = None
        comoda = DEFAULT_PLACE

    dir = DEFAULT_DIR
    data = scan_dir(dir)
    
    tmp = data.groupby(['day','time'], as_index = False)
    jumps = 20
    mean_max, median_max = (tmp.mean()[comoda].max(), tmp.median()[comoda].max())
    y_ticks = np.arange(0, max(mean_max, median_max) + jumps, jumps)

    if day:
        record_histogram(data, day, comoda, y_ticks)
        exit()

    if not day:
        days = data.day.unique().tolist()
        for d in days:
            record_histogram(data, d, comoda, y_ticks)
