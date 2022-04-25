import re
import time

class Patterns:
    # if using search -> group(x)
    IP = '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'  # x = 0
    DATE = '\[(\d{1,2}/[JFMAMJJASOND][a-z]{1,8}/20[0-9]{2}:[0-2][0-9]:[0-5][0-9]:[0-5][0-9]) [+|-]00[01][0-9]\]'  # x = 1
    REQUEST = '] "(.*?)"'  # x = 1
    PATH = '] "([A-Z].*? )?([^"]*?)"'  # x = 2
    USER_AGENT = '".*?" \d{3} \d{1,10} ".*?" "(.*?)" ".*?"$'  # x = 1
    STATUS_CODE = '" ([1-5][0-9][0-9]) [0-9]'  # x = 1

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
        pattern = " \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} "
        for line in lines:
            if re.search(pattern, line) is not None:
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
        Fill dictionary with single request data and return the dictionary
        """
        ip_match = re.search(Patterns.IP, line)
        data["ip"] = ip_match.group(0)

        date_match = re.search(Patterns.DATE, line)
        date = date_match.group(1)
        date = time.strptime(date, "%d/%b/%Y:%H:%M:%S")
        date = time.strftime("%Y/%m/%d %H:%M:%S", date)
        data["date"] = date

        request_match = re.search(Patterns.REQUEST, line)
        data["request"] = request_match.group(1)

        path_match = re.search(Patterns.PATH, line)
        data["path"] = path_match.group(2)

        user_agent_match = re.search(Patterns.USER_AGENT, line)
        data["user_agent"] = user_agent_match.group(1)

        status_code_match = re.search(Patterns.STATUS_CODE, line)
        data["status_code"] = status_code_match.group(1)
        return data

    def remove_invalid_records(self, temp_list:list) -> list:
        """
        Remove records which contain requests that probably are not made by real user
        """
        def conditions(data) -> bool:  # `True` if all conditions are fulfilled, otherwise `False`
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
