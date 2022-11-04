#!/usr/bin/python3
import ast
import os
import pandas as pd

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

# data = scan_dir()
# days = data.day.unique().tolist()
# ax = data[data['day'] =='monday'].groupby(['day','time']).mean()

# fig = ax.get_figure()
# ax = s.hist(columns=['colA', 'colB'])
# try one of the following
# fig = ax[0].get_figure()
# fig = ax[0][0].get_figure()

# fig.savefig('histogram.png')
