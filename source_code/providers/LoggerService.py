import os
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
from contracts.ILoggerService import ILoggerService
import Config
import csv
from concerns.LogType import LogType
from datetime import datetime

class LoggerService(ILoggerService):
    def __init__(self, transfer_type_log_file_path, errors_log_file_path):
        self._transfers_log_file_path = transfer_type_log_file_path

        self._errors_log_file_path = errors_log_file_path

    def create_log(self, log_type, payload):
        try:
            log_file_path = None

            if log_type == LogType.File_Transfer_Log:
                log_file_path = self._transfers_log_file_path
            
            else:
                log_file_path = self._errors_log_file_path

            with open(log_file_path, "a", newline='') as file_descriptor:
                writer_instance = csv.writer(file_descriptor)

                writer_instance.writerow([datetime.now(), *payload])
            
            return True
        
        except Exception as message:
            print(f"Exception at Logger service > create log method: {message}")

    def create_file_transfer_log(self, address, transfer_type, storage_path, 
            file_name, transfer_start_time, transfer_end_time, _message):
            
        return self.create_log(LogType.File_Transfer_Log, 
            [
                address[0],
                address[1],
                transfer_type, 
                storage_path, 
                file_name, 
                transfer_start_time,
                transfer_end_time, 
                transfer_end_time - transfer_start_time, 
                _message
            ])