#!/usr/bin/env python3
"""
Description: ClickUp API Data to Excel
Written By: Dipan Nanda
Date: December 2022
"""
import sys
from concurrent.futures import ThreadPoolExecutor
from os import environ, getenv, mkdir
from time import perf_counter

from excel_write import write_in_excel
from pandas import DataFrame, concat
from requests import get
from tqdm import tqdm
from urllib3 import disable_warnings

disable_warnings()
attributes = []
":param list attributes: List of keys that would be kept in excels."


class Request:
    """Generating Request(s) from Clickup"""

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
    """Fetching Workspace(s) data"""

    def __init__(self):
        """Constructor for Teams class"""
        Request.__init__(self, url="team")

    def fetch_all_teams(self):
        """Fetching all Workspace(s) data from Token"""
        return self.valid_response(self.fetch_response(), "teams",
                                   "Clickup API Token is invalid.")


class Spaces(Request):
    """Fetching Space(s) data"""

    def __init__(self, team_id):
        """
        Constructor for Spaces class

        :param str team_id: Team id required for fetching space(s)
        """
        self.team_id = team_id
        Request.__init__(self, url=f"team/{self.team_id}/space")

    def fetch_spaces(self):
        """Fetching all Space(s) data from Workspace"""
        return self.valid_response(self.fetch_response(), "spaces")


class Goals(Request):
    """Fetching Goal(s) data"""

    def __init__(self, team_id):
        """
        Constructor for Goals class

        :param str team_id: Team id required for fetching space(s)
        """
        self.team_id = team_id
        Request.__init__(self, url=f"team/{self.team_id}/goal")

    def fetch_goals(self):
        """Fetching all Goal(s) data from Teams"""
        return self.valid_response(self.fetch_response(), "goals")


class Tags(Request):
    """Fetching Tag(s) data"""

    def __init__(self, space_id):
        """
        Constructor for Tags class

        :param str space_id: Space id required for fetching tag(s)
        """
        self.space_id = space_id
        Request.__init__(self, url=f"space/{self.space_id}/tag")

    def fetch_tags(self):
        """Fetching all Tag(s) data from Spaces"""
        return self.valid_response(self.fetch_response(), "tags")


class Folders(Request):
    """Fetching Folder(s) data"""

    def __init__(self, space_id):
        """
        Constructor for Folders class

        :param str space_id: Space id required for fetching folder(s)
        """
        self.space_id = space_id
        Request.__init__(self, url=f"space/{self.space_id}/folder")

    def fetch_folders(self):
        """Fetching all Folder(s) data from Spaces"""
        query = {"archived": "false"}
        response = self.fetch_response(params=query)
        return self.valid_response(response, "folders")


class FolderLessLists(Request):
    """Fetching Folder Less List(s) data"""

    def __init__(self, space_id):
        """
        Constructor for FolderLessLists class

        :param str space_id: Space id required for fetching folder less list(s)
        """
        self.space_id = space_id
        Request.__init__(self, url=f"space/{self.space_id}/list")

    def fetch_folders_lists(self):
        """Fetching all Folder less List(s) from Spaces"""
        query = {"archived": "false"}
        response = self.fetch_response(params=query)
        return self.valid_response(response, "lists")


class Lists(Request):
    """Fetching List(s) data"""

    def __init__(self, folder_id):
        """
        Constructor for Lists class

        :param str folder_id: Folder id required for fetching list(s)
        """
        self.folder_id = folder_id
        Request.__init__(self, url=f"folder/{self.folder_id}")

    def fetch_lists(self):
        """Fetching all List(s) from Folders"""
        query = {"archived": "false"}
        response = self.fetch_response(params=query)
        return self.valid_response(response, "lists")


class List(Request):
    """Fetching List(s) data"""

    def __init__(self, list_id):
        """
        Constructor for Lists class

        :param str list_id: Folder id required for fetching list(s)
        """
        self.list_id = list_id
        Request.__init__(self, url=f"list/{self.list_id}")

    def fetch_list(self):
        """Fetching all List(s) from Folders"""
        query = {"archived": "false"}
        response = self.fetch_response(params=query)
        return self.valid_response(response)


class ListFields(Request):
    """Fetching Field(s) data"""

    def __init__(self, list_id):
        """
        Constructor for ListComments class

        :param str list_id: List id required for fetching field(s)
        """
        self.list_id = list_id
        Request.__init__(self, url=f"list/{self.list_id}/field")

    def fetch_fields(self):
        """Fetching all Field(s) from Lists"""
        return self.valid_response(self.fetch_response(), "fields")


class ListComments(Request):
    """Fetching List Comment(s) data"""

    def __init__(self, list_id):
        """
        Constructor for ListComments class

        :param str list_id: List id required for fetching comment(s)
        """
        self.list_id = list_id
        Request.__init__(self, url=f"list/{self.list_id}/comment")

    def fetch_comments(self):
        """Fetching all Comment(s) from Lists"""
        return self.valid_response(self.fetch_response(), "comments")


class Tasks(Request):
    """Fetching Task(s) data"""

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
            url=f"list/{self.list_id}/task?page={page_no}"
            f"&subtasks=true&include_closed=true",
        )

    def fetch_tasks(self):
        """Fetching all Tasks(s) from Lists"""
        query = {"custom_task_ids": "true", "include_subtasks": "true"}
        response = self.fetch_response(params=query)
        return self.valid_response(response, "tasks")


class TaskComments(Request):
    """Fetching comment(s) inside a Task"""

    def __init__(self, task_id):
        """
        Constructor for Teams class

        :param str task_id: Task id required for fetching comment(s)
        """
        self.task_id = task_id
        Request.__init__(self, url=f"task/{self.task_id}/comment")

    def fetch_comments(self):
        """Fetching all Comment(s) from Task(s)"""
        return self.valid_response(self.fetch_response(), "comments")


def append_row(response, record):
    """Adds a new row into the Dataframe"""
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


def fetch_goals(team_id):
    """
    Function for fetching goals inside a Workspace

    :param str team_id: Team id required for fetching space(s)
    """
    goal_helper = Goals(team_id=team_id)
    return goal_helper.fetch_goals()


def fetch_tags(space_id):
    """
    Function for fetching tags inside a space

    :param str space_id: Space id required for fetching tag(s)
    """
    tag_helper = Tags(space_id=space_id)
    return tag_helper.fetch_tags()


def fetch_folders(space_id, location):
    """
    Function for fetching folders inside a space

    :param str space_id: Space id required for fetching folder(s)
    :param str location: location where files are saved
    """
    folder_helper = Folders(space_id=space_id)
    list_folders_data = folder_helper.fetch_folders()
    for folder_id in list_folders_data.index:
        location_in = create_location(location, folder_id)
        lists = fetch_lists(folder_id=folder_id, location=location_in)
        write_to_excel(lists, location_in, "info")
    return list_folders_data


def fetch_space_lists(space_id, location):
    """
    Function for fetching lists inside a space

    :param str space_id: Space id required for fetching folder(s)
    :param str location: location where files are saved
    """
    folder_helper = FolderLessLists(space_id=space_id)
    list_folders_data = folder_helper.fetch_folders_lists()
    for folder_id in list_folders_data.index:
        location_in = create_location(location, folder_id)
        tasks = fetch_tasks(list_id=folder_id, location=location_in)
        write_to_excel(tasks, location_in, "info")
    return list_folders_data


def fetch_lists(folder_id, location):
    """
    Function for fetching lists inside a folders

    :param str folder_id: Folder id required for fetching list(s)
    :param str location: location where files are saved
    """
    list_helper = Lists(folder_id=folder_id)
    list_data = list_helper.fetch_lists()
    for list_id in list_data.index:
        location_in = create_location(location, list_id)
        with ThreadPoolExecutor() as execute:
            result = [
                execute.submit(i, list_id)
                for i in [fetch_list, fetch_list_comments, fetch_list_fields]
            ]
            result.append(execute.submit(fetch_tasks, list_id, location_in))
        for i, j in zip(result, ["information", "comments", "fields", "info"]):
            write_to_excel(i.result(), location_in, j)
    return list_data


def fetch_list(list_id):
    """
    Function for fetching comments inside a task

    :param str list_id: List id required for fetching info about list
    """
    list_helper = List(list_id=list_id)
    return list_helper.fetch_list()


def fetch_list_comments(list_id):
    """
    Function for fetching comments inside a list

    :param str list_id: List id required for fetching comment(s)
    """
    comment_helper = ListComments(list_id=list_id)
    return comment_helper.fetch_comments()


def fetch_list_fields(list_id):
    """
    Function for fetching comments inside a list

    :param str list_id: List id required for fetching comment(s)
    """
    field_helper = ListFields(list_id=list_id)
    return field_helper.fetch_fields()


def fetch_tasks(list_id, location):
    """
    Function for fetching tasks inside a list

    :param str list_id: List id required for fetching task(s)
    :param str location: location where files are saved
    """
    tasks_data_full = DataFrame()
    for page_number in range(0, 10):
        task_helper = Tasks(list_id=list_id, page_no=str(page_number))
        tasks_data = task_helper.fetch_tasks()
        if tasks_data.empty:
            break
        for task_id in tasks_data.index:
            location_in = create_location(location, task_id)
            task_comments = fetch_task_comments(task_id=task_id)
            write_to_excel(task_comments, location_in, "comments")
        tasks_data_full = concat([tasks_data_full, tasks_data])
    return tasks_data_full


def fetch_task_comments(task_id):
    """
    Function for fetching comments inside a task

    :param str task_id: Task id required for fetching comment(s)
    """
    comment_helper = TaskComments(task_id=task_id)
    return comment_helper.fetch_comments()


def create_location(location, name_id):
    """
    Function for fetching comments inside a task

    :param str location: location where files are saved
    :param str name_id: id that will be used for making the structure
    """
    location = location + "/" + name_id + "/"
    mkdir(location)
    return location


def write_to_excel(frame, location, name):
    """
    Function for fetching comments inside a task

    :param DataFrame frame: dataframe that will be put inside Excel file
    :param str location: location where files are saved
    :param str name: Name of the file
    """
    if not frame.empty:
        write_in_excel(frame, location + name + ".xlsx", "All Data", True)
    return False


class Migrate2Excel(Teams):
    """Migrating the whole Clickup Database into Excel"""

    def __init__(self,
                 location,
                 clickup_api_token=None,
                 attribute_values=None):
        """
        Constructor for Request class

        :param str location: location where files are saved
        :param str clickup_api_token: Token to access ClickUp
        :param dict attribute_values: attributes user wants on there excel
        """
        global attributes
        self.clickup_api_token = clickup_api_token
        self.location = location
        attributes = attribute_values
        self.__set_environment__()
        Teams.__init__(self)

    def __set_environment__(self):
        """Set some environment variables"""
        environ["clickup_api_token"] = self.clickup_api_token

    def start(self):
        """Function that migrates the ClickUp data to Excel files"""
        teams = self.fetch_all_teams()
        write_to_excel(teams, self.location, "info")
        start = perf_counter()
        for team_id in teams.index:
            location = create_location(self.location, team_id)
            spaces = fetch_spaces(team_id=team_id)
            goals = fetch_goals(team_id=team_id)
            for i, j in zip([spaces, goals], ["info", "goals"]):
                write_to_excel(i, location, j)
            for space_id in tqdm(spaces.index):
                location_in = create_location(location, space_id)
                with ThreadPoolExecutor() as execute:
                    result = [
                        execute.submit(i, space_id, location_in)
                        for i in [fetch_folders, fetch_space_lists]
                    ]
                    result.append(execute.submit(fetch_tags, space_id))
                for i, j in zip(result, ["info", "lists", "Tags"]):
                    write_to_excel(i.result(), location_in, j)
        end = perf_counter()
        print(f"Finished in {round(end - start, 2)} second(s)")
