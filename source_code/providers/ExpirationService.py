import time
import Config
from threading import Thread
from datetime import date, datetime
from providers.DataMappingService import DataMappingService

class ExpirationService(Thread):
    def __init__(self, scheduler_length):
        # initializing the thread instance
        Thread.__init__(self)
        
        # creating a local variable
        self._scheduler_length = scheduler_length

        # creating an instance of data mapping service with the data mapping location
        self._data_mapping_service = DataMappingService(Config.DATA_MAPPING_LOCATION)

    def run(self):
        while(True):
            # creating a timer for the scheduled lenth
            time.sleep(self._scheduler_length)

            # informing the server that expiration service has been triggered.
            print(f"expiration service triggered at: {datetime.now()}")
            
            # calling the delete expired storage path service for deleting the expired storage paths
            self._data_mapping_service.delete_expired_storage_path()