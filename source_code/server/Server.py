# packages required for the server.py
import uuid
import time
from threading import Thread
import json
import socket
import sys
import os
import locale
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
from concerns.Response import Response_Type
from concerns.Request import Request
from concerns.TransferType import Transfer_Type
import Config
from utilities.Commands import Command
from providers.ServerSocketService import ServerSocketService as SocketService
from providers.DataMappingService import DataMappingService
from providers.ExpirationService import ExpirationService
from providers.UtilityService import UtilityService
from providers.StoragePathService import StoragePathService
from providers.LoggerService import LoggerService
from datetime import date, datetime
from concerns.LogType import LogType
import time

# active clients count
active_client_count = 0

# initializing the data mapping service
data_mapping_service = DataMappingService(Config.DATA_MAPPING_LOCATION)

# initializing the logger service
logger_service_instance = LoggerService(
                                Config.SERVER_TRANSFERS_LOG_FILE_PATH, 
                                Config.SERVER_ERROR_LOG_FILE_PATH)

# Client Request Class
class ClientRequest(Thread):
    def __init__(self, client_address, client_socket):
        Thread.__init__(self)

        self.address = client_address

        self.connection = client_socket

        # initializing the storage path service
        self._storage_service = StoragePathService(
            Config.SERVER_FILE_STORAGE_PATH)

        # initializing the socket service
        self._socket_service = SocketService(self.connection)

        self._current_working_directory = '/'

        self._data_connection_config = {
            "host_ip": "",
            "port_number": None
        }

        # initializing the utility service
        self._utility_service = UtilityService()

        print("New Connection Established for {}".format(client_address))

        print("-----------------------------------------------------------")

    def _check_options(self, args):
        # check for the UTF8 encoding
        if args == 'UTF8 ON':
            # setting the locale to UTF_8 encoding
            locale.getpreferredencoding = 'utf-8'

            # send the response to client
            return self._socket_service.send_response(
                Response_Type.UTF8_MODE_ON, 
                response_message_key = 'UTF8_MODE_ON')

        elif args == 'UTF8 OFF':
            # send the response to client
            return self._socket_service.send_response(
                Response_Type.UTF8_MODE_OFF,
                response_message_key = 'UTF8_MODE_OFF')

        else:
            _message = "COMMAND_NOT_IMPLEMENTED_FOR_PARAMETER exception in check options method"

            payload = [self.address, _message]

            logger_service_instance.create_log(LogType.Error_log, payload)
            
            # send the response to client
            return self._socket_service.send_response(
                Response_Type.COMMAND_NOT_IMPLEMENTED_FOR_PARAMETER,
                response_message_key = 'COMMAND_NOT_IMPLEMENTED_FOR_PARAMETER')

    def _check_user(self, args):
        # check for anonymous user name
        if args == 'anonymous':
            # send the response to client
            return self._socket_service.send_response(
                Response_Type.SPECIFY_PASSWORD,
                response_message_key='SPECIFY_PASSWORD')

        else:
            _message = "COMMAND_NOT_IMPLEMENTED_FOR_PARAMETER exception in check user method"

            payload = [self.address, _message]

            logger_service_instance.create_log(LogType.Error_log, payload)

            # send the response to client
            return self._socket_service.send_response(
                Response_Type.COMMAND_NOT_IMPLEMENTED_FOR_PARAMETER,
                response_message_key = 'COMMAND_NOT_IMPLEMENTED_FOR_PARAMETER')

    def _check_password(self, args):
        # send the response to client
        return self._socket_service.send_response(
            Response_Type.LOGIN_SUCCESS,
            response_message_key='LOGIN_SUCCESS')

    def _make_directory(self, args):
        try:
            storage_path = f"{Config.SERVER_FILE_STORAGE_PATH}/{args}/"
            
            # creating the storage path
            self._storage_service.create_storage_path(storage_path)

            # send the response to client
            return self._socket_service.send_response(
                Response_Type.STORAGE_PATH_CREATED,
                response_message_key = 'STORAGE_PATH_CREATED'
            )

        except Exception as message:
            _message = f"Create directory failed Exception at server.py > make directory method:{e}"

            print(_message)

            payload = [self.address, _message]

            logger_service_instance.create_log(LogType.Error_log, payload)

            # send the response to client
            return self._socket_service.send_response(
                Response_Type.CREATE_DIRECTORY_FAILED,
                response_message_key = 'CREATE_DIRECTORY_FAILED')

    def _set_expiry_date(self, args):
        args = str(args).split()

        # adding the item to data mapping json
        if data_mapping_service.add_storage_path_mapping(args[0].strip(), args[1].strip()):
            # send the response to client
            return self._socket_service.send_response(
                Response_Type.EXPIRY_DATE_SET,
                response_message_key='EXPIRY_DATE_SET')

        # send the response to client
        return self._socket_service.send_response(
            Response_Type.EXPIRY_DATE_SET_FAILED,
            response_message_key='EXPIRY_DATE_SET_FAILED')

    def _change_directory(self, args):
        if args == '/':
            # setting the current working directory value
            self._current_working_directory = "/"

            # send the response to client
            return self._socket_service.send_response(
                Response_Type.DIRECTORY_CHANGED_SUCCESS,
                response_message_key='DIRECTORY_CHANGED_SUCCESS')

        storage_path = f"{Config.SERVER_FILE_STORAGE_PATH}/{args}/"

        # check whether storage path exists
        if (not os.path.exists(storage_path)):
            _error_message = f"Storage path: {args} doesn't exists"

            print(f"{_error_message}")

            # send the response to client
            self._socket_service.send_response(
                Response_Type.DIRECTORY_CHANGE_FAILED,
                [_error_message],
                response_message_key = 'DIRECTORY_CHANGE_FAILED')

        # check whether storage is expired or not
        elif not data_mapping_service.is_storage_path_available(args):
            _error_message = f"Storage path: {args} expired"

            # send the response to client
            return self._socket_service.send_response(
                Response_Type.DIRECTORY_CHANGE_FAILED,
                [_error_message],
                response_message_key = 'DIRECTORY_CHANGE_FAILED')

        else:
            self._current_working_directory = args

            # send the response to client
            return self._socket_service.send_response(
                Response_Type.DIRECTORY_CHANGED_SUCCESS,
                response_message_key='DIRECTORY_CHANGED_SUCCESS')

    def _interpret_port(self, args):
        try:
            # decoding the args in port command
            (ip_address, port_number) = self._utility_service.decode_port_command_payload(args)

            self._data_connection_config['host_ip'] = ip_address

            self._data_connection_config['port_number'] = port_number

            # send the response to client
            return self._socket_service.send_response(
                Response_Type.PORT_COMMAND_SUCCESS,
                response_message_key = 'PORT_COMMAND_SUCCESS')

        except Exception as message:
            _message = f"Exception at server.py > interpret port method:{e}"

            print(_message)

            payload = [self.address, _message]

            logger_service_instance.create_log(LogType.Error_log, payload)

            # send the response to client
            return self._socket_service.send_response(
                Response_Type.PORT_COMMAND_FAILED,
                response_message_key = 'PORT_COMMAND_FAILED')

    def _upload_file(self, args):
        try:
            if self._data_connection_config['host_ip'] and self._data_connection_config['port_number']:
                
                # fetching the ip address of the client
                source_ip = socket.gethostbyname(socket.gethostname())

                # fetching the port of the client
                source_port = Config.DATA_CONNECTION_PORT_NUMBER

                # connecting to client for data connection
                data_connection_descriptor = self._utility_service.make_connection(
                    self._data_connection_config['host_ip'],
                    self._data_connection_config['port_number'],
                    source_ip,
                    source_port)

                if data_connection_descriptor:
                    # send the response to client
                    self._socket_service.send_response(
                        Response_Type.OK_TO_SEND_DATA,
                        response_message_key = 'OK_TO_SEND_DATA')

                    # Get the file path
                    file_path = f"{Config.SERVER_FILE_STORAGE_PATH}/{self._current_working_directory}/{args}"

                    # create storage path
                    self._storage_service.create_storage_path(file_path)

                    transfer_start_time = time.time()

                    # file_descriptor = open(file_path, "wb")

                    data_received = 0

                    # opening the file in binary write mode
                    with open(file_path, "wb") as file_descriptor:

                        # Receive file contents.
                        while True:
                            data = data_connection_descriptor.recv(
                                Config.MAX_BUFFER_SIZE)

                            # check for EOF
                            if data == Request.EOF.name.encode():
                                break

                            file_descriptor.write(data)

                            data_received += Config.MAX_BUFFER_SIZE

                            print(f"Amount of data received: {data_received}")

                            # sending acknowledgement 
                            data_connection_descriptor.send("1".encode())

                        # sending acknowledgement for end of file
                        data_connection_descriptor.send("1".encode())

                        # close the data connection
                        data_connection_descriptor.close()

                        # file_descriptor.close()
                    
                    transfer_end_time = time.time()

                    self._data_connection_config = {
                        "host_ip": "",
                        "port_number": None
                    }

                    logger_service_instance.create_file_transfer_log(
                        self.address, Transfer_Type.Upload, 
                        self._current_working_directory, args, 
                        transfer_start_time, transfer_end_time, 'TRANSFER COMPLETED')

                    # send the response to client
                    return self._socket_service.send_response(
                        Response_Type.TRANSFER_COMPLETED,
                        response_message_key='TRANSFER_COMPLETED')

                else:
                    self._data_connection_config = {
                        "host_ip": "",
                        "port_number": None
                    }

                    logger_service_instance.create_file_transfer_log(
                        self.address, Transfer_Type.Upload, 
                        self._current_working_directory, args, 
                        0, 0, 'OPEN DATA CONNECTION FAILED')

                    # send the response to client
                    return self._socket_service.send_response(
                        Response_Type.OPEN_DATA_CONNECTION_FAILED,
                        response_message_key='OPEN_DATA_CONNECTION_FAILED')

            else:
                print(f"Data connection config is invalid")

                logger_service_instance.create_file_transfer_log(
                        self.address, Transfer_Type.Upload, 
                        self._current_working_directory, args, 
                        0, 0, 'OPEN DATA CONNECTION FAILED: INVALID CONFIG')

                # send the response to client
                return self._socket_service.send_response(
                    Response_Type.OPEN_DATA_CONNECTION_FAILED,
                    response_message_key='OPEN_DATA_CONNECTION_FAILED')

        except Exception as e:
            _message = f"Exception at server.py > upload file method:{e}"

            print(_message)
            
            payload = [self.address, _message]

            logger_service_instance.create_log(LogType.Error_log, payload)

            logger_service_instance.create_file_transfer_log(
                        self.address, Transfer_Type.Upload, 
                        self._current_working_directory, args, 
                        0, 0, _message)

            self._data_connection_config = {
                "host_ip": "",
                "port_number": None
            }

            # send the response to client
            return self._socket_service.send_response(
                Response_Type.LOCAL_PROCESSING_ERROR,
                response_message_key='LOCAL_PROCESSING_ERROR')
        pass

    def _download_file(self, args):
        try:
            if self._data_connection_config['host_ip'] and self._data_connection_config['port_number']:
                # get the IP address of server
                source_ip = socket.gethostbyname(socket.gethostname())

                # get the data connection port number of server
                source_port = Config.DATA_CONNECTION_PORT_NUMBER

                # connect to client for data connection
                data_connection_descriptor = self._utility_service.make_connection(
                    self._data_connection_config['host_ip'],
                    self._data_connection_config['port_number'],
                    source_ip,
                    source_port)

                if data_connection_descriptor:
                    # Get the file path
                    file_path = f"{Config.SERVER_FILE_STORAGE_PATH}/{self._current_working_directory}/{args}"

                    try:
                        # file_descriptor = open(file_path, "r", encoding='utf-8')
                        transfer_start_time = time.time()

                        with open(file_path, "rb") as file_descriptor:
                            self._socket_service.send_response(
                                Response_Type.BINARY_MODE_DATA_CONNECTION_OPENDED,
                                response_message_key='BINARY_MODE_DATA_CONNECTION_OPENDED')

                            # Read file contents.
                            data = file_descriptor.read(Config.MAX_BUFFER_SIZE)

                            print(f"Sending file contents...")

                            data_sent = 0

                            # Send file contents.
                            while data:
                                data_connection_descriptor.send(data)

                                data = file_descriptor.read(Config.MAX_BUFFER_SIZE)

                                data_sent += Config.MAX_BUFFER_SIZE

                                print(f"Amount of data sent: {data_sent}")

                                data_connection_descriptor.recv(Config.MAX_BUFFER_SIZE)

                            # sending end of file
                            data_connection_descriptor.send(Request.EOF.encode())

                            # acknowledgement from the server
                            data_connection_descriptor.recv(Config.MAX_BUFFER_SIZE)

                            # close the data connection
                            data_connection_descriptor.close()

                        transfer_end_time = time.time()

                        self._data_connection_config = {
                            "host_ip": "",
                            "port_number": None
                        }

                        logger_service_instance.create_file_transfer_log(
                            self.address, Transfer_Type.Download, 
                            self._current_working_directory, args, 
                            transfer_start_time, transfer_end_time, 'TRANSFER COMPLETED')

                        # send the response to client
                        return self._socket_service.send_response(
                            Response_Type.TRANSFER_COMPLETED,
                            response_message_key='TRANSFER_COMPLETED')

                    except Exception as e:
                        print(
                            f"Exception at server.py > download file> file reading method:{e}")

                        logger_service_instance.create_file_transfer_log(
                            self.address, Transfer_Type.Download, 
                            self._current_working_directory, args, 
                            0, 0, 'FILE_NOT_FOUND')

                        # send the response to client
                        return self._socket_service.send_response(
                            Response_Type.FILE_NOT_FOUND,
                            response_message_key = 'FILE_NOT_FOUND')
                else:
                    self._data_connection_config = {
                        "host_ip": "",
                        "port_number": None
                    }

                    logger_service_instance.create_file_transfer_log(
                            self.address, Transfer_Type.Download, 
                            self._current_working_directory, args, 
                            0, 0, 'OPEN DATA CONNECTION FAILED')

                    # send the response to client
                    return self._socket_service.send_response(
                        Response_Type.OPEN_DATA_CONNECTION_FAILED,
                        response_message_key='OPEN_DATA_CONNECTION_FAILED')

            else:
                print(f"Data connection config is invalid")

                logger_service_instance.create_file_transfer_log(
                            self.address, Transfer_Type.Download, 
                            self._current_working_directory, args, 
                            0, 0, 'OPEN DATA CONNECTION FAILED:INVALID CONFIG')

                # send the response to client
                return self._socket_service.send_response(
                    Response_Type.OPEN_DATA_CONNECTION_FAILED,
                    response_message_key='OPEN_DATA_CONNECTION_FAILED')

        except Exception as e:
            _message = f"Exception at server.py > download file method:{e}"

            print(_message)

            self._data_connection_config = {
                "host_ip": "",
                "port_number": None
            }

            logger_service_instance.create_file_transfer_log(
                self.address, Transfer_Type.Download, 
                self._current_working_directory, args, 
                0, 0, _message)

            # send the response to client
            return self._socket_service.send_response(
                Response_Type.LOCAL_PROCESSING_ERROR,
                response_message_key='LOCAL_PROCESSING_ERROR')
        pass

    def _list_directory(self):
        try:
            if self._data_connection_config['host_ip'] and self._data_connection_config['port_number']:
                # get the IP address of server
                source_ip = socket.gethostbyname(socket.gethostname())

                # get the data connection port number of server
                source_port = Config.DATA_CONNECTION_PORT_NUMBER

                # connect to client for data connection
                data_connection_descriptor = self._utility_service.make_connection(
                    self._data_connection_config['host_ip'],
                    self._data_connection_config['port_number'],
                    source_ip,
                    source_port)

                if data_connection_descriptor:
                    # Get the storage path
                    storage_path = f"{Config.SERVER_FILE_STORAGE_PATH}/{self._current_working_directory}"

                    # check whether storage path exists or not
                    if (not os.path.exists(storage_path)):
                        print(f"Storage path: {self._current_working_directory} doesn't exists")

                        _error_message = f"Storage path: {self._current_working_directory} doesn't exists"
                        
                        # send the response to client
                        return self._socket_service.send_response(
                            Response_Type.FILE_NOT_FOUND,
                             [_error_message],
                             response_message_key = 'FILE_NOT_FOUND')

                    # check is storage path available or not
                    elif (not data_mapping_service.is_storage_path_available(self._current_working_directory)):
                        print(f"Storage path: {self._current_working_directory} expired")

                        _error_message = f"Storage path: {self._current_working_directory} expired"

                        # send the response to client
                        return self._socket_service.send_response(
                            Response_Type.FILE_NOT_FOUND, 
                            [_error_message],
                            response_message_key = 'FILE_NOT_FOUND')

                    # send the response to client
                    self._socket_service.send_response(
                        Response_Type.DIRECTORY_LISTING,
                        response_message_key='DIRECTORY_LISTING')

                    # fetch files info in the storage path
                    payload = self._storage_service.fetch_files_by_storage_path(self._current_working_directory)

                    # send the encoded payload
                    data_connection_descriptor.send(json.dumps(payload).encode())
                    
                    # receive ack from the client
                    data_connection_descriptor.recv(Config.MAX_BUFFER_SIZE)

                    # sending end of file
                    data_connection_descriptor.send(Request.EOF.encode())

                    # acknowledgement from the client
                    data_connection_descriptor.recv(Config.MAX_BUFFER_SIZE)

                    # close the data connection
                    data_connection_descriptor.close()

                    self._data_connection_config = {
                        "host_ip": "",
                        "port_number": None
                    }

                    # send the response to client
                    return self._socket_service.send_response(
                        Response_Type.DIRECTORY_SEND_SUCCESS,
                        response_message_key='DIRECTORY_SEND_SUCCESS')

                else:
                    self._data_connection_config = {
                        "host_ip": "",
                        "port_number": None
                    }

                    # send the response to client
                    return self._socket_service.send_response(
                        Response_Type.OPEN_DATA_CONNECTION_FAILED,
                        response_message_key='OPEN_DATA_CONNECTION_FAILED')

            else:
                print(f"Data connection config is invalid")

                # send the response to client
                return self._socket_service.send_response(
                    Response_Type.OPEN_DATA_CONNECTION_FAILED,
                    response_message_key='OPEN_DATA_CONNECTION_FAILED')

        except Exception as e:
            print(f"Exception at server.py > list directory method:{e}")

            self._data_connection_config = {
                "host_ip": "",
                "port_number": None
            }

            # send the response to client
            return self._socket_service.send_response(
                Response_Type.LOCAL_PROCESSING_ERROR,
                response_message_key='LOCAL_PROCESSING_ERROR')
        pass

    def _send_current_directory(self):
        # send the response to client
        return self._socket_service.send_response(
            Response_Type.PWD_SUCCESS, 
            response_message_key= 'PWD_SUCCESS', 
            args = [self._current_working_directory])

    def _close_connection(self):
        # send the response to client
        self._socket_service.send_response(
            Response_Type.CLOSE_CONNECTION_SUCCESS,
            response_message_key='CLOSE_CONNECTION_SUCCESS')
        self.connection.close()

    # Resolves the command
    def __resolve_command(self, command, args):
        # checking the commands and calling the respective functions
        if command == Request.OPTS:
            return self._check_options(args)

        elif command == Request.USER:
            return self._check_user(args)

        elif command == Request.PASS:
            return self._check_password(args)

        elif command == Request.MKD:
            return self._make_directory(args)

        elif command == Request.SETEXPIRY:
            return self._set_expiry_date(args)

        elif command == Request.CWD:
            return self._change_directory(args)

        elif command == Request.PORT:
            return self._interpret_port(args)

        elif command == Request.STOR:
            return self._upload_file(args)

        elif command == Request.RETR:
            return self._download_file(args)

        elif command == Request.QUIT:
            return self._close_connection()
        
        elif command == Request.LIST:
            return self._list_directory()
        
        elif command == Request.PWD:
            return self._send_current_directory()

        else:
            print("Cannot resolve the command")

        print("-----------------------------------------------------------")

    # initiate the connection
    def run(self):
        global active_client_count

        # send the response to client
        self._socket_service.send_response(
            Response_Type.SERVICE_READY,
            response_message_key='SERVICE_READY')

        while True:
            try:

                print("{}:listening to the client action....".format(self.address))

                print("-----------------------------------------------------------")

                # receive the command text from the client
                (command, args) = self._socket_service.receive_request()

                if (command == ""):

                    print("something went wrong...closing the {} connection".format(
                        self.address))

                    active_client_count -= 1

                    self.connection.close()

                    break

                print("command:{}".format(command))
                if not command:
                    active_client_count -= 1
                    break

                else:
                    # resolve the command
                    self.__resolve_command(command, args)

                # clear the command data
                command = None
            except Exception as message:
                print(message)

                active_client_count -= 1

                break
            except KeyboardInterrupt:
                print("quitting")
                break
            finally:
                print("-----------------------------------------------------------")

                print("Active Clients:{}".format(active_client_count))

                print("-----------------------------------------------------------")

# Server start method
def server_start(host_ip, port_number):
    global active_client_count
    try:
        print("Server is getting launched...")

        # creating socket
        socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        socket_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        address = (host_ip, port_number)

        socket_connection.bind(address)

        print("server listening on {}...".format(address))

        # creating a thread of expiration service and schedule the job with 60-seconds
        service_thread_instance = ExpirationService(1000)

        # starting the expiration service thread
        service_thread_instance.start()

        # print("-----------------------------------------------------------")

        while True:
            try:
                # listening to the clients
                socket_connection.listen()

                # accept the new connection and get the socket and address of client
                client_socket, client_address = socket_connection.accept()

                # incrementing the active client count when there is a new connection to the server.
                active_client_count += 1

                print("\nNew connection detected\n")

                print("-----------------------------------------------------------")

                print("Active Clients:{}".format(active_client_count))

                print("-----------------------------------------------------------")

                # create a client request thread with the client address and client socket
                client_request_instance = ClientRequest(
                    client_address, client_socket)

                # starting the client request thread
                client_request_instance.start()
            except Exception as message:
                print(
                    "some error occurred in the connection with client - {}".format(client_address))

                print("-----------------------------------------------------------")

                break
            except KeyboardInterrupt:
                print("quitting")
                break

    except KeyboardInterrupt:
        print("quitting")

    except Exception as message:
        print("message:", message)
        print("-----------------------------------------------------------")


if __name__ == "__main__":
    # host_ip is the IP address of the server.
    host_ip = socket.gethostbyname(socket.gethostname())

    # port_number is the port at which server runs
    port_number = 210

    # starting the server
    server_start(host_ip, port_number)
