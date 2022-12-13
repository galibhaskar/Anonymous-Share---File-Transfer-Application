class IDataMappingService():
    def get_data_mapping_json(self):
        pass

    def overwrite_data_mapping_json(self, data):
        pass

    def is_storage_path_available(self, storage_path):
        pass
    
    def add_storage_path_mapping(self, storage_path, expiry_date):
        pass

    def modify_storage_path_mapping(self, storage_path):
        pass
    
    def delete_expired_storage_path(self):
        pass