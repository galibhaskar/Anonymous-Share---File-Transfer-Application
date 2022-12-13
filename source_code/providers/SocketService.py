import os
import sys
import socket
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
import Config
from contracts.ISocketService import ISocketService
from concerns.Response import Response_Type

class SocketService(ISocketService):
    def __init__(self, socket_instance):
        self._socket_instance = socket_instance
        self.receive_window_size = Config.MAX_BUFFER_SIZE

    def __generate_message(self, *args):
        # joining the args into a string separated by spaces
        return f"{' '.join(args)}\r\n"

    # command : Request Enum
    # payload : list of strings
    def send_request(self, command, payload=[]):
        try:
            # create request info using command and payload
            _request_info = self.__generate_message(command, *payload)

            # send the request info data to the server
            self._socket_instance.send(_request_info.encode())

        except Exception as e:
            print(f"Exception at Socket Service > send_request method:{e}")

    def receive_response(self):
        try:
            # receive the data from the server
            _response = self._socket_instance.recv(self.receive_window_size).decode()

            _response = _response.replace('\r\n', '')

            # destructing the response list
            _response_code, *args = _response.split(" ")

            # join the separated args and split by semicolon for custom messages
            _response_args = f"{' '.join(args)}".split(';')

            return (_response_code, _response_args)

        except Exception as e:
            print(f"Exception at Socket Service > receive_response method:{e}")
