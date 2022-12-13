import os
from contracts.IStoragePathService import IStoragePathService

class StoragePathService(IStoragePathService):
    def __init__(self, root_storage_path):
        self.root_storage = root_storage_path
        self._path = os.path

    # create a directory to store files
    def __create_directory(self, file_path):
        if not self._path.exists(self._path.dirname(file_path)):
            try:
                os.makedirs(self._path.dirname(file_path))
            except Exception as e:
                print("Error:", e)

    def __get_files_info_in_directory(self, file_path):
        files_info = []
        try:
            files = os.listdir(file_path)
            os.chdir(file_path)
            if len(files) == 0:
                return files_info
            for file in files:
                files_info.append({
                    'file_name_length': len(file),
                    'file': file,
                    'file_size': os.path.getsize(file)
                })
            return files_info
        except Exception as e:
            # log here
            print("Error:{}".format(e))
            raise Exception(e)
        return files_info

    def __get_directory_size(self, file_path):
        _path = os.path
        _size = 0
        try:
            for _file in os.scandir(file_path):
                _size += _path.getsize(_file)
        except Exception as e:
            # log here
            print("Error:{}".format(e))
            raise Exception(e)
        return _size

    def __get_storage_location(self, storage_path):
        return "{}/{}".format(self.root_storage, storage_path)

    def create_storage_path(self, storage_path):
        try:
            self.__create_directory(storage_path)
        except Exception as e:
            print("Storage path creation failure")

    def fetch_files_by_storage_path(self, storage_path):
        _error_message = None
        _files_info = []
        _total_directory_size = 0
        try:
            location = self.__get_storage_location(storage_path)
            _files_info = self.__get_files_info_in_directory(location)
            _total_directory_size = self.__get_directory_size(location)
        except Exception as e:
            print("Error in fetching files:{}".format(e))
            _error_message = str(e)
        finally:
            return {
                "files_info": _files_info, 
                "directory_size": f"{_total_directory_size}",
                "error_message": _error_message
                }

    def isFileAvailable(self, file_path):
        try:
            print(self._path.isfile(file_path))
        except Exception as e:
            print(f"Exception:{e}")
