import re
import time

class Patterns:
    """
    Regex patters for searching for a wanted data in log string.
    WANTED_DATA = {"re": str, "x": int}
    `re` - regex compiled pattern
    `x` - while using `search` and then `group(x)` methods returns only the wanted part of a match
    """
    IP = {
        're': re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'),
        'x': 0,
    }
    DATE = {
        're': re.compile(r'\[(\d{1,2}/[JFMAMJJASOND][a-z]{1,8}/20[0-9]{2}:[0-2][0-9]:[0-5][0-9]:[0-5][0-9]) [+|-]00[01][0-9]\]'),
        'x': 1,
    }
    REQUEST = {
        're': re.compile(r'] "(.*?)"'),
        'x': 1,
    }
    PATH = {
        're': re.compile(r'] "([A-Z].*? )?([^"]*?)"'),
        'x': 2,
    }
    USER_AGENT = {
        're': re.compile(r'".*?" \d{3} \d{1,10} ".*?" "(.*?)" ".*?"$'),
        'x': 1,
    }
    STATUS_CODE = {
        're': re.compile(r'" ([1-5][0-9][0-9]) [0-9]'),
        'x': 1,
    }

class LogsFilter:
    def __init__(self, log_lines:list):
        self.lines = log_lines

    def get_filtered_data(self) -> list:
        """
        Main function from the class which returns filtered data organized in dictionaries
        """
        lines = self.remove_lines_without_ip(self.lines)
        temp_list = self.get_useful_data(lines)
        data = self.remove_invalid_records(temp_list)
        return data

    def remove_lines_without_ip(self, lines:list) -> list:
        """
        Remove lines without ip address (lines from docker or with errors)
        and return list which has only logs with requests
        """
        new_lines = []
        pattern = re.compile(" \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} ")
        for line in lines:
            if pattern.search(line) is not None:
                new_lines.append(line)
        return new_lines

    def get_useful_data(self, lines:list) -> list:
        """ Create list of dictionaries with useful data about requests """
        temp_list = []
        for line in lines:
            data = {
                "ip": None,
                "date": None,
                "request": None,
                "path": None,
                "user_agent": None,
                "status_code": None,
            }
            data = self.get_data_from_1_request(data, line)
            temp_list.append(data)
        return temp_list

    def get_data_from_1_request(self, data:dict, line:str) -> dict:
        """
        Fill dictionary with single request data and return this dictionary
        """
        ip_match = re.search(Patterns.IP["re"], line)
        data["ip"] = ip_match.group(Patterns.IP["x"])

        date_match = re.search(Patterns.DATE["re"], line)
        date = date_match.group(Patterns.DATE["x"])
        date = time.strptime(date, "%d/%b/%Y:%H:%M:%S")
        date = time.strftime("%Y/%m/%d %H:%M:%S", date)
        data["date"] = date

        request_match = re.search(Patterns.REQUEST["re"], line)
        data["request"] = request_match.group(Patterns.REQUEST["x"])

        path_match = re.search(Patterns.PATH["re"], line)
        data["path"] = path_match.group(Patterns.PATH["x"])

        user_agent_match = re.search(Patterns.USER_AGENT["re"], line)
        data["user_agent"] = user_agent_match.group(Patterns.USER_AGENT["x"])

        status_code_match = re.search(Patterns.STATUS_CODE["re"], line)
        data["status_code"] = status_code_match.group(Patterns.STATUS_CODE["x"])
        return data

    def remove_invalid_records(self, temp_list:list) -> list:
        """
        Remove records which contain requests that probably are not made by real users
        """
        def conditions(data:dict) -> bool:  # `True` if all conditions are fulfilled, otherwise `False`
            # conditions that have to be fulfilled
            cons = (
                    data["status_code"] == "200" and
                    data["user_agent"] != "-" and
                    "bot.html" not in data["user_agent"] and
                    "GET / " not in data["request"] and
                    "GET /?" not in data["request"] and
                    "favicon.ico" not in data["request"]
            )
            return cons
        data_list = [data for data in temp_list if conditions(data)]
        return data_list
