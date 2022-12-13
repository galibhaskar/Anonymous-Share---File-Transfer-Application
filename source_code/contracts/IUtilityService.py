class IUtilityService():
    def scan_server_details(self):
        pass

    def scan_expiry_date(self):
        pass

    def make_connection(self, ip_address, port, source_ip = None, source_port = None):
        pass

    def listen_for_connnection(self, ip_address, port):
        pass

    def encode_port_command_payload(self, host_ip, port_number):
        pass

    def decode_port_command_payload(self,payload):
        pass