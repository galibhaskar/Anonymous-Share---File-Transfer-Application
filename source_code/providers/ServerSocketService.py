import os
import sys
import socket
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
import Config
from contracts.IServerSocketService import IServerSocketService
from concerns.Response import Response_Type, get_response_message


class ServerSocketService(IServerSocketService):
    def __init__(self, socket_instance):
        self._socket_instance = socket_instance
        self.receive_window_size = Config.MAX_BUFFER_SIZE

    def __generate_message(self, *args):
        # joining the args into a string separated by spaces
        return f"{' '.join(args)}\r\n"

    def send_response(self, response_type, additional_payload=[], args= [], response_message_key = None):
        try:
            _response_code = response_type.value

            if response_message_key:
                _response_message = get_response_message(response_message_key, args)
            
            else:
                _response_message = get_response_message(response_type, args)

            _payload = f"{';'.join([_response_message, *additional_payload])}"

            # create response info using response_type and payload
            _response_info = self.__generate_message(_response_code, _payload)

            # send the request info data to the server
            self._socket_instance.send(_response_info.encode())
            
        except Exception as e:
            print(f"Exception at Server Socket Service > send_response method:{e}")

    def receive_request(self):
        try:
            # receive the request from the client
            _request_info = self._socket_instance.recv(
                self.receive_window_size).decode()

            _request_info = _request_info.replace('\r\n','')

            # destructing the request info
            _request_command, *args = _request_info.split(" ")

            # join the separated args and split by semicolon for custom messages
            _request_info_args = f"{' '.join(args)}"

            return (_request_command, _request_info_args)

        except Exception as e:
            print(f"Exception at Server Socket Service > receive_request method:{e}")
            pass
