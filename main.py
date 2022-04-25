import pandas as pd

from filter import LogsFilter
from grouper import TimeGrouper


if __name__ == "__main__":
    # --------------------- #
    # crucial, variable data:
    file_path = "out.log"
    encoding = "utf-16"
    time_interval = "D"
    # --------------------- #

    with open(file_path, "r", encoding=encoding) as f:
        lines = f.readlines()

    # clean data
    data = LogsFilter(lines)
    filtered_data = data.get_filtered_data()

    # create df and change date column type from obj to datetime
    df = pd.DataFrame(filtered_data)
    df["date"] = pd.to_datetime(df['date'], format='%Y/%m/%d %H:%M:%S')

    # group data into wanted time intervals
    time_grouper = TimeGrouper(data=df, freq=time_interval)
    time_modified_df = time_grouper.get_grouped_data()
    # new_df = time_grouper.get_records_between_dates(log_time_modified_df, "2021/10/18", "2021-10-26")

    # save in csv file
    df.to_csv("requests_full_info.csv", index=False) # info about every request
    time_modified_df.to_csv("entries_by_day.csv", index=False) # date and number of visitors
