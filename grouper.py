from collections import Counter
import pandas as pd
from pandas import DataFrame

class RequiredColumnsNotInDf(Exception):
    pass

class TimeGrouper:
    MIN_REQUESTS = 7

    def __init__(self, data:DataFrame, freq:str):
        self.freq = freq
        if isinstance(data, DataFrame):
            self.data = data
        else:
            raise TypeError(f"`data` must be a DataFrame, not {type(data)}")
        self.df = None

    def get_grouped_data(self) -> DataFrame:
        """
        Main function that returns df with columns: [grouped date], [ips and number of their requests]
        and [number of ips making requests in certain time interval]
        """
        self.check_column_names(self.data)
        self.df = self.create_df(self.data, self.freq)
        self.df = self.count_number_of_ip(self.df)
        return self.df

    def check_column_names(self, df:DataFrame) -> None:
        """ Check if given df contains columns with required data """
        columns = df.columns.tolist()
        required = ["date", "ip"]
        for item in required:
            if item not in columns:
                raise RequiredColumnsNotInDf()

    def create_df(self, data:DataFrame, freq:str) -> DataFrame:
        """
        Create a df grouped by given time intervals.
        freq is freq parameter from pd.Grouper (Offset aliases); changes time intervals.
        for example. "H" - 1 hour, "5D" - 5 days, "17min"/"17T" - 17 minutes, "M" - month, "W" - week.
        """
        df = data[["date", "ip"]]
        df = df.groupby(pd.Grouper(key="date", freq=freq))["ip"].apply(list)
        df = df.reset_index(name="ips")
        return df

    def count_ip_occurrences(self, cell:list) -> list:
        """ Count number of every ip occurrence in the cell """
        c = Counter(cell)
        c = [(key, val) for key, val in c.items() if val > self.MIN_REQUESTS]
        return c

    def get_number_of_ip_in_cell(self, cell:list) -> int:
        """ Count number of items in the cell """
        return len(cell)

    def count_number_of_ip(self, df:DataFrame) -> DataFrame:
        """
        Modify df to its final form - [date], [ips and number of their requests] and [number of ips]
        """
        df["ips"] = df["ips"].apply(self.count_ip_occurrences)
        df["ips_number"] = df["ips"].apply(self.get_number_of_ip_in_cell)
        return df

    def get_records_between_dates(self, df:DataFrame, start:str, end:str) -> DataFrame:
        """
        Return new df containing only records between given dates.
        start, end - dates writen in pandas friendly format
        """
        con = (df["date"] >= start) & (df["date"] < end)
        df_2 = df.loc[con]
        return df_2
