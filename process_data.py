#!/usr/bin/python3
import ast
import os
import sys
import pandas as pd # type: ignore
import numpy as np # type: ignore
# import matplotlib.pyplot as plt # type: ignore
import argparse as ap
import datetime
from app_constants import PLACES_INDEXES, pandas_int_weekday, saturday_aperture_time, saturday_closing_time, sunday_aperture_time, sunday_closing_time

DEFAULT_DIR = "aforo"
DEFAULT_PLACE = "Gimnasio"
STATS_DIR = "statistics"
X_TICKS = 6

def get_key(dict, val):
    return next(
        (key for key, value in dict.items() if val == value),
        "key doesn't exist",
    )

# Convert str dict into each column with each value and remove negative values
def reformat_dataframe(data, filename):
    filename = filename.split('.')[0]
    _, year, _, week = filename.split('_')
    year = int(year)
    week = int(week)

    data.columns = ['day', 'time', 'aforo']
    reformatted = data['aforo'].apply(lambda x: ast.literal_eval(x)).apply(lambda x: {k: x[k][0] for k in x.keys()}).apply(pd.Series)
    data = data.drop('aforo', axis=1).assign(**reformatted)
    data['year'] = year
    data['week'] = week
    data['year_day'] = data['day'].apply(lambda x: datetime.datetime.strptime(f"{year}-W{week}-{get_key(pandas_int_weekday, x)}", "%Y-W%W-%w"))
    # parse time from the time column and apply to the year_day
    data['time'] = data['time'].apply(lambda x: datetime.datetime.strptime(x, "%H:%M").time())
    data['year_day'] = data.apply(lambda x: datetime.datetime.combine(x['year_day'], x['time']), axis=1)
    # Fix years of dates that are in the next year
    data['year'] = data['year_day'].apply(lambda x: x.year)
    # Remove all rows that have a timestamp with a minute inding in 15 or 45
    # data = data[~data['time'].apply(lambda x: x.minute in [15, 45])]
    
    data = data.reset_index(drop=True)
    # drop duplicated timestamps
    data = data[~data['year_day'].duplicated(keep='last')]
    
    # Add a column with the period of the day. After 15:00 is afternoon, before is morning
    data['period'] = data['time'].apply(lambda x: 'Tarde' if x.hour >= 15 else 'Mañana')

    num = data._get_numeric_data()
    num[num < 0] = 0
    return data

def remove_outliers(data, place):
    # Calculate Q1, Q3, and IQR
    filtered_df = data
    q1_q3 = filtered_df.groupby(['day', 'time'])[place].quantile([0.25, 0.75]).unstack(level=-1)

    if not q1_q3.empty:
        q1_q3.columns = ['Q1', 'Q3']
        q1_q3['IQR'] = q1_q3['Q1'] * 1.5

        # Merge back with the original dataframe
        data_merged = filtered_df.merge(q1_q3, left_on=['day', 'time'], right_index=True)

        # Filter out the outliers using the IQR * 1.5 rule
        filtered_df = data_merged[
            (data_merged[place] >= data_merged['Q1'] - data_merged['IQR']) &
            (data_merged[place] <= data_merged['Q3'] + data_merged['IQR'])
        ]
        filtered_df = filtered_df.drop(['Q1', 'Q3', 'IQR'], axis=1)

    # Remove the days which mean is 0
    mask = filtered_df.groupby(['year', 'day', 'week']).mean(numeric_only=True)[place].reset_index().rename(columns={place: 'mean'})
    filtered_df = filtered_df.merge(mask, on=['year', 'week', 'day'])
    filtered_df = filtered_df[filtered_df['mean'] > 0].drop('mean', axis=1)
    
    return filtered_df


def read_csv(root, file):
    data = pd.read_csv(f"{root}{file}")
    data = reformat_dataframe(data, file)
    return data

def scan_dir(folder=".", start=0, end=-1, top=-1, reverse=False, verbose=False):
    total_data = pd.DataFrame()
    if (end == 0):
        end = -1
    # walk files in name reverse order
    for root, dirs, files in os.walk(f'{folder}/', topdown=True):
        files.sort(reverse=reverse)
        if start >= 0:
            files = files[start:] if end < 0 else files[start:end]
        if (top >= 0):
            files.sort(reverse=True)
        for file in files:
            if file.endswith(".csv"):
                # only top files
                if top >= 0:
                    top -= 1
                    if top < 0:
                        break
                verbose and print(f"{root}{file}")
                data = read_csv(root, file)
                total_data = pd.concat([total_data, data])
    total_data.reset_index(drop=True, inplace=True)
    return total_data

def interpolate_missing_times(data):
    # Previously the readings were taken every 30 minutes, now they are taken every 15 minutes
    # This function interpolates the missing values so the data is consistent
    # Times missing coincide with the ones ending in :15 and :45
    try:
        data = data.set_index('year_day')

        # Resample DataFrame to include missing times
        data = data.resample('15min').asfreq()
        # interpolate to fill the missing values
        numerical_columns = PLACES_INDEXES
        data[numerical_columns] = data[numerical_columns].interpolate(method='time').round(0)
        # fill non numeric columns with the previous value
        data.bfill(inplace=True)
        data['time'] = data.index.time
        # Remove times before aperture_time and time_closing for each day
        data = data.between_time('07:30', '22:30')
        # for sunday and saturday remove times before 9:00 and 9:30 and after 21:00 and 15:00
        data[data['day'].isin(['saturday'])] = data[data['day'].isin(['saturday'])].between_time(saturday_aperture_time, saturday_closing_time)
        data[data['day'].isin(['sunday'])] = data[data['day'].isin(['sunday'])].between_time(sunday_aperture_time, sunday_closing_time)
        data.reset_index(inplace=True)
    except Exception as e:
        pass
    return data

def trim_missing_times(data):
    # Remove all readings ending with :15 and :45
    data = data[~data['time'].apply(lambda x: x.minute in [15, 45])]
    return data

# def record_histogram(o_data, week_day, place, y_ticks, append_name=""):
#     data = o_data[o_data['day'] == week_day].groupby(['day','time'], as_index = False)
#     idxs = np.round(np.linspace(0, len(data) - 1, X_TICKS)).astype(int)

#     mean_data = data.mean(numeric_only=True)
#     median_data = data.median()

#     plt.bar(mean_data['time'], mean_data[place], color='b', width=0.9, label='Mean')
#     plt.bar(median_data['time'], median_data[place], color='tab:orange', width=0.5, label='Median', alpha=0.7)

#     plt.legend()
#     plt.xticks(mean_data.loc[idxs]['time'])
#     plt.yticks(y_ticks)
#     plt.title(f'{week_day.capitalize()} {place.capitalize()}')
#     plt.savefig(f'{STATS_DIR}/hist_{place}_{week_day}{append_name}.png')
#     plt.cla()
#     plt.clf()

if __name__ == '__main__':
    # Parse keyword program arguments
    # -d day
    # -p place
    # -w number of weeks
    parser = ap.ArgumentParser(prog = 'Termaria data analyzer')
    parser.add_argument("-d", "--day", type=str, default=None, required=False, help="Day of the week")
    parser.add_argument("-p", "--place", type=str, default='Gimnasio', required=False, help="Place to analyze")
    parser.add_argument("-s", "--start", type=int, default=0, required=False, help="Start week")
    parser.add_argument("-e", "--end", type=int, default=0, required=False, help="Number of weeks to analyze")
    parser.add_argument("-r", "--reverse", action='store_true', help="Reverse order of weeks")
    parser.add_argument("-l", "--latest", type=int, default=-1, required=False, help="Latest weeks to analyze")
    parser.add_argument("-a", "--append", type=str, default="", required=False, help="Append to file name")
    args = parser.parse_args()
    if (args.start > args.end):
        print("Start week must be lower than end week")
        exit()
    day = args.day
    place = args.place

    dir = DEFAULT_DIR
    data = scan_dir(dir, args.start, args.end, args.latest, args.reverse)
    
    info_dataframe = data.groupby(['day','time'], as_index = False)
    jumps = 20
    mean_max, median_max = (info_dataframe.mean(numeric_only=True)[place].max(), info_dataframe.median()[place].max())
    y_ticks = np.arange(0, max(mean_max, median_max) + jumps, jumps)

    if day:
        record_histogram(data, day, place, y_ticks, args.append)
        exit()

    days = data.day.unique().tolist()
    for d in days:
        record_histogram(data, d, place, y_ticks, args.append)
