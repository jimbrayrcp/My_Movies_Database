# ################################
#   Copyright (c) 2021 Jim Bray
#       All Rights Reserved
# ################################
import json


class ConfigJson:
    """
    manages the config.json file
    """
    def __init__(self):
        self.file_name = "./config.json"
        self.j_config = {"MOVIE_API_KEY": "", "APP_SECRET_KEY": ""}
        self.config = {}

    def setup(self):
        """
        sets up the config.json file
        :return: a new empty config.json file
        """
        with open(self.file_name, "w") as f:
            json.dump(obj=self.j_config, fp=f, indent=4, sort_keys=True)

    def edit(self, key, new_value):
        """
        Exchanges a key's value for the one entered into the user form
        :param key: The key requiring a changed value
        :param new_value: The replacement value
        :return: updated config.json file
        """
        with open(self.file_name, 'r') as f:
            self.config = json.load(f)

        # edit the data
        self.config[key] = new_value

        # write it back to the file
        with open(self.file_name, 'w') as f:
            json.dump(obj=self.config, fp=f, indent=4, sort_keys=True)

    def read(self, item_to_read):
        """
        reads values from the keys of the config.json file
        :param item_to_read: the desired key to read
        :return: the value from the key requested
        """
        with open(self.file_name, "r") as file_items:
            data = json.load(file_items)
            return data[item_to_read]


if __name__ == "__main__":
    config = ConfigJson()

    # EDIT VALUES
    # config.edit(key="MOVIE_API_KEY", new_value="12")

    # GET VALUES
    val = config.read(item_to_read="MOVIE_API_KEY")
    print(val)



