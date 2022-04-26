import argparse
import pandas as pd

from filter import LogsFilter
from grouper import TimeGrouper

def main():
    # args setup
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="path of a file with logs")
    args = parser.parse_args()

    # most often changed variables
    encoding = "utf-16"
    time_interval = "D"

    with open(args.path, "r", encoding=encoding) as f:
        lines = f.readlines()

    data_df = interpret_data(lines, time_interval)

    # save in csv file
    data_df.to_csv("entries_by_day.csv", index=False) # date and number of visitors

def interpret_data(lines, time_interval):
    # clean data
    data = LogsFilter(lines)
    filtered_data = data.get_filtered_data()

    # create df and change date column type from obj to datetime
    df = pd.DataFrame(filtered_data)
    df["date"] = pd.to_datetime(df['date'], format='%Y/%m/%d %H:%M:%S')

    # group data into wanted time intervals
    time_grouper = TimeGrouper(data=df, freq=time_interval)
    time_modified_df = time_grouper.get_grouped_data()

    # if information only about specified period of time is wanted, not about entire one in a file
    # specified_time_df = time_grouper.get_records_between_dates(time_modified_df, "2022/04/18", "2022-04-22")

    return time_modified_df

if __name__ == "__main__":
    main()
