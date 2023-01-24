#!/usr/bin/python3
import ast
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse as ap

DEFAULT_DIR = "aforo"
DEFAULT_PLACE = "Gimnasio"
STATS_DIR = "statistics"
X_TICKS = 6

# Convert str dict into each column with each value and remove negative values
def reformat_dataframe(data):
    data.columns = ['day', 'time', 'aforo']
    reformatted = data['aforo'].apply(lambda x: ast.literal_eval(x)).apply(lambda x: {k: x[k][0] for k in x.keys()}).apply(pd.Series)
    data = data.drop('aforo', axis=1).assign(**reformatted)
    num = data._get_numeric_data()
    num[num < 0] = 0
    return data


def scan_dir(folder=".", start=0, end=-1, top=-1):
    total_data = pd.DataFrame()
    # walk files in name reverse order
    for root, dirs, files in os.walk(f'{folder}/', topdown=True):
        files.sort()
        if start >= 0:
            files = files[start:end]
        if (top >= 0):
            files.sort(reverse=True)
        for file in files:
            if file.endswith(".csv"):
                # only top files
                if top >= 0:
                    top -= 1
                    if top < 0:
                        break
                print(f"{root}{file}")
                data = pd.read_csv(f"{root}{file}")
                data = reformat_dataframe(data)
                total_data = pd.concat([total_data, data])
    return total_data

def record_histogram(o_data, week_day, place, y_ticks, append_name=""):
    data = o_data[o_data['day'] == week_day].groupby(['day','time'], as_index = False)
    idxs = np.round(np.linspace(0, len(data) - 1, X_TICKS)).astype(int)

    mean_data = data.mean()
    median_data = data.median()

    plt.bar(mean_data['time'], mean_data[place], color='b', width=0.9, label='Mean')
    plt.bar(median_data['time'], median_data[place], color='tab:orange', width=0.5, label='Median', alpha=0.7)

    plt.legend()
    plt.xticks(mean_data.loc[idxs]['time'])
    plt.yticks(y_ticks)
    plt.title(f'{week_day.capitalize()} {place.capitalize()}')
    plt.savefig(f'{STATS_DIR}/hist_{place}_{week_day}{append_name}.png')
    plt.cla()
    plt.clf()

if __name__ == '__main__':
    # Parse keyword program arguments
    # -d day
    # -p place
    # -w number of weeks
    parser = ap.ArgumentParser(prog = 'Termaria data analyzer')
    parser.add_argument("-d", "--day", type=str, default=None, required=False, help="Day of the week")
    parser.add_argument("-p", "--place", type=str, default='Gimnasio', required=False, help="Place to analyze")
    parser.add_argument("-s", "--start", type=int, default=0, required=False, help="Start week")
    parser.add_argument("-e", "--end", type=int, default=-1, required=False, help="Number of weeks to analyze")
    parser.add_argument("-l", "--latest", type=int, default=-1, required=False, help="Latest weeks to analyze")
    parser.add_argument("-a", "--append", type=str, default="", required=False, help="Append to file name")
    args = parser.parse_args()
    if (args.start > args.end):
        print("Start week must be lower than end week")
        exit()
    day = args.day
    comoda = args.place

    dir = DEFAULT_DIR
    data = scan_dir(dir, args.start, args.end, args.latest)
    
    tmp = data.groupby(['day','time'], as_index = False)
    jumps = 20
    mean_max, median_max = (tmp.mean()[comoda].max(), tmp.median()[comoda].max())
    y_ticks = np.arange(0, max(mean_max, median_max) + jumps, jumps)

    if day:
        record_histogram(data, day, comoda, y_ticks, args.append)
        exit()

    days = data.day.unique().tolist()
    for d in days:
        record_histogram(data, d, comoda, y_ticks, args.append)
