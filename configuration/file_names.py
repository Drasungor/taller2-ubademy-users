import os

# This is a file to store the constants that indicate the names of the files used for
# program configuration

# This variable should have the name of the folder in which it is contained

dir_name = os.path.dirname(os.path.realpath(__file__))
folder_name = "/../config_files"

STATUS_MESSAGE_FILE_NAME = dir_name + folder_name + "/" + "status_messages.json"
