import json
import os


class JSON:
    """
    Class used to contain a JSON file's information and data in a neat fashion.
    """

    def __init__(self, file_name, folder):
        """(str, str) -> JSON

        Creates a new JSON object that contains the data located at the json
        file folder/file_name.

        :param file_name: the file name of the JSON file we want to load into
        the new JSON instance

        :param folder: the folder where the file with name file_name resides
        """
        self.file_name = file_name
        self.folder = folder
        self.data = load_json_file(self.file_name, self.folder)

    def get_section(self, index, section):
        """(int, str) -> dict

        Gets the section of the json file with key section of the index-th
        element in the JSON.

        :param index: the index number of the item in the dictionary list of
        the JSON instance

        :param section: the key we want to visit

        """
        # test_num starts from 0
        return self.data[index][section]


def load_json_file(file_name, file_folder):
    """(str, str) ->  json data (dict?)

    Loads the data of the json file with path file_folder/file_name

    :param file_name: the name of the json we want to extract data from
    :param file_folder: the folder where the desired file resides

    :return: a json data object
    """
    file_path = (os.sep).join([file_folder, file_name])
    data_file = open(file_path)
    data = json.load(data_file)
    return data
