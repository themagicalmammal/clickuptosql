#!/usr/bin/env python3
"""
Description: ClickUp API Data to sql
Written By: Dipan Nanda
Date: December 2022
"""
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from os import environ, getenv
from time import perf_counter

from pandas import DataFrame, concat
from requests import get
from sqlalchemy import create_engine
from tqdm import tqdm
from urllib3 import disable_warnings

disable_warnings()
attributes, spaces_dict, all_tasks = [], {}, DataFrame()
":param list attributes: List of keys that would be kept in sql."


class Request(object):
    """
    Generating Request(s) from Clickup
    """

    def __init__(self, url, headers=None):
        """
        Constructor for Request class

        :param str url: The url used to fetch the data
        :param dict headers: Contains headers like type and key for the url
        """
        if headers is None:
            headers = {
                "Content-Type": "application/json",
                "Authorization": getenv("clickup_api_token"),
            }
        self.url = "https://api.clickup.com/api/v2/" + url
        self.headers = headers

    def fetch_response(self, verify=False, params=None):
        """
        Fetch Response from the API

        :param bool verify: Flag for verification of response
        :param dict params: Parameters while fetching response for specific use cases
        """
        if params is None:
            params = {}
        request = get(url=self.url,
                      headers=self.headers,
                      verify=verify,
                      params=params)
        return request.json()

    @staticmethod
    def valid_response(response, fetch_string=None, error_string=None):
        """
        Fetch Response from the API

        :param dict response: Response received from the API
        :param str fetch_string: Key to use from the response
        :param str error_string: Error message to be thrown
        """
        responses = DataFrame()
        if fetch_string is None:
            responses = append_row(response=responses, record=response)
            responses.set_index(responses.columns[0], inplace=True)
            return responses
        if error_string is None:
            error_string = ("Attributes provided return a empty " +
                            fetch_string + " dataframe.")
        if len(response.get(fetch_string)):
            for i in response.get(fetch_string):
                responses = append_row(response=responses, record=i)
            try:
                responses.set_index(responses.columns[0], inplace=True)
            except KeyError:
                print(error_string)
                sys.exit()
        return responses


class Teams(Request):
    """
    Fetching Workspace(s) data
    """

    def __init__(self):
        """
        Constructor for Teams class
        """
        Request.__init__(self, url="team")

    def fetch_all_teams(self):
        """
        Fetching all Workspace(s) data from Token
        """
        return self.valid_response(self.fetch_response(), "teams",
                                   "Clickup API Token is invalid.")


class Spaces(Request):
    """
    Fetching Space(s) data
    """

    def __init__(self, team_id):
        """
        Constructor for Spaces class

        :param str team_id: Team id required for fetching space(s)
        """
        self.team_id = team_id
        Request.__init__(self, url=f"team/{self.team_id}/space")

    def fetch_spaces(self):
        """
        Fetching all Space(s) data from Workspace
        """
        return self.valid_response(self.fetch_response(), "spaces")


class Folders(Request):
    """
    Fetching Folder(s) data
    """

    def __init__(self, space_id):
        """
        Constructor for Folders class

        :param str space_id: Space id required for fetching folder(s)
        """
        self.space_id = space_id
        Request.__init__(self, url=f"space/{self.space_id}/folder")

    def fetch_folders(self):
        """
        Fetching all Folder(s) data from Spaces
        """
        query = {"archived": "false"}
        response = self.fetch_response(params=query)
        return self.valid_response(response, "folders")


class FolderLessLists(Request):
    """
    Fetching Folder Less List(s) data
    """

    def __init__(self, space_id):
        """
        Constructor for FolderLessLists class

        :param str space_id: Space id required for fetching folder less list(s)
        """
        self.space_id = space_id
        Request.__init__(self, url=f"space/{self.space_id}/list")

    def fetch_folders_lists(self):
        """
        Fetching all Folder less List(s) from Spaces
        """
        query = {"archived": "false"}
        response = self.fetch_response(params=query)
        return self.valid_response(response, "lists")


class Lists(Request):
    """
    Fetching List(s) data
    """

    def __init__(self, folder_id):
        """
        Constructor for Lists class

        :param str folder_id: Folder id required for fetching list(s)
        """
        self.folder_id = folder_id
        Request.__init__(self, url=f"folder/{self.folder_id}")

    def fetch_lists(self):
        """
        Fetching all List(s) from Folders
        """
        query = {"archived": "false"}
        response = self.fetch_response(params=query)
        return self.valid_response(response, "lists")


class Tasks(Request):
    """
    Fetching Task(s) data
    """

    def __init__(self, list_id, page_no="0"):
        """
        Constructor for Tasks class

        :param str list_id: List id required for fetching task(s)
        :param str page_no: Page No for lists with huge amount of task(s)
        """
        self.list_id = list_id
        self.page_no = page_no
        Request.__init__(
            self,
            url=f"list/{self.list_id}/task?page={page_no}&subtasks=true&include_closed=true",
        )

    def fetch_tasks(self):
        """
        Fetching all Tasks(s) from Lists
        """
        query = {
            "start_date": datetime(2022, 12, 5, 5),
            "custom_task_ids": "false",
            "include_subtasks": "false",
        }
        response = self.fetch_response(params=query)
        return self.valid_response(response, "tasks")


def append_row(response, record):
    """
    Adds a new row into the Dataframe
    """
    row = {}
    if attributes is None or len(attributes) == 0:
        attribute = list(record.keys())
    else:
        attribute = attributes
    try:
        if not type(attribute) is list:
            raise TypeError
        for j in attribute:
            if not type(j) is str:
                raise ValueError
            if j in record:
                row[j] = record[j]
        row = DataFrame([row], columns=list(row.keys()))
        response = concat([response, row])
    except TypeError:
        print("Attributes can only be lists.")
        sys.exit()
    except ValueError:
        print("Attribute values can only be strings.")
        sys.exit()
    return response


def fetch_spaces(team_id):
    """
    Function for fetching spaces inside a Workspace

    :param str team_id: Team id required for fetching space(s)
    """
    space_helper = Spaces(team_id=team_id)
    return space_helper.fetch_spaces()


def fetch_folders(space_id):
    """
    Function for fetching folders inside a space

    :param str space_id: Space id required for fetching folder(s)
    """
    folder_helper = Folders(space_id=space_id)
    list_folders_data = folder_helper.fetch_folders()
    for folder_id in list_folders_data.index:
        fetch_lists(folder_id=folder_id)
    return list_folders_data


def fetch_space_lists(space_id):
    """
    Function for fetching lists inside a space

    :param str space_id: Space id required for fetching folder(s)
    """
    folder_helper = FolderLessLists(space_id=space_id)
    list_folders_data = folder_helper.fetch_folders_lists()
    for folder_id in list_folders_data.index:
        fetch_tasks(list_id=folder_id)
    return list_folders_data


def fetch_lists(folder_id):
    """
    Function for fetching lists inside a folders

    :param str folder_id: Folder id required for fetching list(s)
    """
    list_helper = Lists(folder_id=folder_id)
    list_data = list_helper.fetch_lists()
    for list_id in list_data.index:
        with ThreadPoolExecutor() as execute:
            execute.submit(fetch_tasks, list_id)
    return list_data


def fetch_tasks(list_id):
    """
    Function for fetching tasks inside a list

    :param str list_id: List id required for fetching task(s)
    """
    global all_tasks
    for page_number in range(0, 10):
        task_helper = Tasks(list_id=list_id, page_no=str(page_number))
        tasks_data = task_helper.fetch_tasks()
        if tasks_data.empty:
            break
        all_tasks = concat([all_tasks, tasks_data])
    return all_tasks


def optimize(frame):
    """
    Optimize the Tasks frame

    :param DataFrame frame: id that will be used for making the structure
    """
    # Filling empty values with 0 for date/time values and empty for string values.
    for i in frame.columns:
        frame[i] = frame[i].fillna(0 if "date" in i or "time" in i else "")
    # Dropping empty or un-unique rows
    for i in frame.columns:
        try:
            if len(frame[i].unique()) < 2:
                frame = frame.drop(columns=[i])
        except TypeError:
            # For cases where dataframe has dict/list values
            if len(set(str(j) for j in frame[i])) < 2:
                frame = frame.drop(columns=[i])
    # Considered either to be redundant or useless
    useless = [
        "text_content", "project", "orderindex", "watchers", "linked_tasks"
    ]
    for i in useless:
        if i in frame.columns:
            frame.drop(columns=[i], inplace=True)
    # Mapping data to reduce the amount of code
    attribute_pair = {
        "status": "status",
        "priority": "priority",
        "folder": ["name", "id"],
        "list": ["name", "id"],
        "creator": ["username", "id"],
        "space": "id",
        "assignees": ["username", "id"],
        "tags": "name",
        "dependencies": ["task_id", "depends_on"],
        "checklists": ["name", "id"],
    }
    # Optimisation according to the parameter
    for i in frame.columns:
        if i in list(attribute_pair.keys())[:6]:
            if not isinstance(attribute_pair[i], list):
                if i == "space":
                    frame[i + "_" + attribute_pair[i]] = frame[i].apply(
                        lambda x: x[attribute_pair[i]] if x != "" else "")
                    frame[i] = frame[i + "_" + attribute_pair[i]].apply(
                        lambda x: spaces_dict[x])
                else:
                    frame[i] = frame[i].apply(lambda x: x[attribute_pair[i]]
                                              if x != "" else "")
            else:
                frame[i + "_" + attribute_pair[i][-1]] = frame[i].apply(
                    lambda x: x[attribute_pair[i][-1]] if x != "" else "")
                frame[i] = frame[i].apply(lambda x: x[attribute_pair[i][0]]
                                          if x != "" else "")
        elif i in attribute_pair:
            if not isinstance(attribute_pair[i], list):
                frame[i] = frame[i].apply(lambda x: ", ".join(
                    [d[attribute_pair[i]] for d in x]) if x != "" else "")
            else:
                if i == "checklists":
                    frame[i] = frame[i].apply(lambda x: x[0]["items"]
                                              if len(x) > 0 else "")
                frame[i + "_" + attribute_pair[i][-1]] = frame[i].apply(
                    lambda x: ", ".join(
                        [str(d[attribute_pair[i][-1]]) for d in x])
                    if x != "" else "")
                frame[i] = frame[i].apply(lambda x: ", ".join(
                    [d[attribute_pair[i][0]] for d in x]) if x != "" else "")
        elif i in ["time_estimate", "time_spent"]:
            frame[i] = frame[i].apply(lambda x: int(
                time.strftime("%H%M%S", time.gmtime(x))) / pow(10, 4))
        elif "date" in i or "time" in i:
            frame[i] = frame[i].apply(lambda x: str(
                datetime.fromtimestamp(int(x) / pow(10, 3)))[:10])
        elif i == "custom_fields":
            pass
    frame.drop(columns=["custom_fields"], inplace=True)
    return frame.reindex(sorted(frame.columns), axis=1)


class Migrate2Sql(Teams):
    """
    Migrating the whole Clickup Database into sql
    """

    def __init__(
        self,
        clickup_api_token=None,
        attribute_values=None,
        spaces=None,
        optimise=False,
        sql_connection=None,
        dtype=None,
    ):
        """
        Constructor for Request class

        :param str clickup_api_token: Token to access ClickUp
        :param list attribute_values: attributes user wants on there sql
        :param list spaces: spaces user wants on there sql
        :param bool optimise: if user wants the file to be optimised
        """
        global attributes
        self.clickup_api_token = clickup_api_token
        attributes = attribute_values
        self.spaces = spaces
        self.optimize = optimise
        self.sql_connection = sql_connection
        self.dtype = dtype
        self.__set_environment__()
        Teams.__init__(self)

    def __set_environment__(self):
        """
        Set some environment variables
        """
        environ["clickup_api_token"] = self.clickup_api_token

    def start(self):
        """
        Function that migrates the ClickUp data to sql files
        """
        global spaces_dict
        teams = self.fetch_all_teams()
        start = perf_counter()
        for team_id in teams.index:
            spaces = fetch_spaces(team_id=team_id)
            spaces_dict = spaces.to_dict()["name"]
            for space_id in tqdm(
                    spaces.index if self.spaces is None else self.spaces):
                with ThreadPoolExecutor() as execute:
                    _ = [
                        execute.submit(i, space_id)
                        for i in [fetch_folders, fetch_space_lists]
                    ]
        global all_tasks
        if self.optimize:
            all_tasks = optimize(all_tasks)
        engine = create_engine("mssql+pyodbc://" + self.sql_connection)
        all_tasks.to_sql("Tasks",
                         engine,
                         if_exists="replace",
                         dtype=self.dtype)
        end = perf_counter()
        print(f"Finished in {round(end - start, 2)} second(s)")
