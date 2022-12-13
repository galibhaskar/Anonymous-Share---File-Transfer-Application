import json
import Config
from contracts.IDataMappingService import IDataMappingService
from threading import Lock
from datetime import datetime, date

class DataMappingService(IDataMappingService):
    def __init__(self, location):
        self.data_mapping_location = location

    # function reads the data mapping json file
    def get_data_mapping_json(self):
        try:
            data = None

            # holding the lock to access the shared resource - data_mapping.json file 
            with Lock():

                # reading the data mapping json file in read and write mode
                with open(self.data_mapping_location, "r+") as file_pointer:

                    # converting the dat object to json
                    data = json.load(file_pointer)['data']

            # returning the data object json
            return data

        except Exception as message:
            print(f"Error at get_data_mapping_json:{message}")

    # function to overwrite the updated data mapping to data_mapping.json file 
    def overwrite_data_mapping_json(self, data):
        print(f"--------overwrite data mapping json-------------------")
        print(f"data:{data}")
        print(f"--------overwrite data mapping json-------------------")
        
        try:
            # holding the lock to access the shared resource - data_mapping.json file
            with Lock():

                # opening the file in read and write modes
                with open(self.data_mapping_location, "r+") as file_pointer:

                    # taking the file pointer to initial point
                    file_pointer.truncate(0)

                    # converting the data mapping object into string and dumping to file
                    json.dump({"data": data}, file_pointer)

        except Exception as message:
            print(f"Error at overwrite_data_mapping_json :{message}")

    # function to check whether storage path is available or not
    def is_storage_path_available(self, storage_path):

        # fetching the data mapping json object from the data_mapping.json
        data_mapping_json = self.get_data_mapping_json()

        # check whether given storage path is available in the data_mapping_json
        # if available, check the status of the storage path
        return any(list(map(lambda item: item['storage_path'] ==
                            storage_path and not item['is_deleted'], data_mapping_json)))

    # function to add new storage path item into the data_mapping.json file
    def add_storage_path_mapping(self, storage_path, expiry_date):

        # checking if storage path already exists in the data_mapping.json
        if (not self.is_storage_path_available(storage_path)):

            # fetching the data mapping json object
            data_mapping_json = self.get_data_mapping_json()

            # creating a new item with the given storage path and expiry date
            new_item = {
                "storage_path": storage_path,
                "expiry_time": expiry_date,
                "is_deleted": 0
            }

            # appending the new item to data mapping json object
            data_mapping_json.append(new_item)

            # function call to overwrite the updated data mapping json object
            self.overwrite_data_mapping_json(data_mapping_json)

            return True

        else:
            print(
                f"Error: Data mapping service > add_storage_path_mapping : storage path already exists")
            return False

    # function that deletes the expired storage paths.
    def delete_expired_storage_path(self):
        # extracting the date format from the config file
        _time_format = Config.DATE_FORMAT
        
        # using the data mapping service to fetch the data mapping json 
        _data_mapping = self.get_data_mapping_json()
        
        # converting the current date into required format
        _current_date_time = datetime.strftime(date.today(), _time_format)
        
        # converting the date string to date object
        _current_date_object = datetime.strptime(_current_date_time, _time_format).date()
        
        is_object_updated = 0

        # check for the expired items in the data mapping
        for item in _data_mapping:
            
            # skip the already deleted items
            if not item['is_deleted']:
               
                # converting the expiry date of the item into the date object
                _expiry_date_object = datetime.strptime(item['expiry_time'], _time_format).date()
                
                # print(f"expired date object:{_expiry_date_object}")
                
                # calculating the difference between the current date object and the expiry date object
                _time_difference = (_expiry_date_object - _current_date_object)
                
                # checking the total no of seconds
                if _time_difference.total_seconds() <= 0:
                    
                    # if total no of seconds is 0, update the is_deleted key
                    # Also, marking that object has been updated
                    item['is_deleted'] = is_object_updated = 1
                    
                    # informing the server that item has been expired.
                    print(f"{item['storage_path']} has been expired")

        # check whether data mapping object has been updated 
        if is_object_updated:
            
            print(f"_data_mapping after update:{_data_mapping}")

            # updating the data mapping json file. 
            self.overwrite_data_mapping_json(_data_mapping)
        pass