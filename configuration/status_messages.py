import json
import configuration.file_names as file_names

MESSAGE_NAME_FIELD = "message"

class StatusMessages:
    def __init__(self):
        self.json_data = json.load(open(file_names.STATUS_MESSAGE_FILE_NAME))

    #Returns a dictionary of the type {"status": str, "message": str} given the context in 
    #which the method is called, which is the name of the dictionary in the status json file
    def get_message(self, context: str):
        return self.json_data[context]



public_status_messages = StatusMessages()