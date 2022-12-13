# packages required for the client.py
import os
import sys
import json
import uuid
import socket
import random
import locale
import requests
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
import Config
from providers.SocketService import SocketService
from providers.UtilityService import UtilityService
from providers.StoragePathService import StoragePathService
from providers.LoggerService import LoggerService
from utilities.Options import Option
from inquirer import List, prompt, Checkbox, themes
from datetime import datetime
from concerns.Request import Request
from concerns.Response import Response_Type
from concerns.TransferType import Transfer_Type
import time

# initializing the logger service
logger_service_instance = LoggerService(
                                Config.CLIENT_TRANSFERS_LOG_FILE_PATH, 
                                Config.CLIENT_ERROR_LOG_FILE_PATH)

# custom theme for tkinter
class CustomTheme(themes.Default):
    """Custom theme replacing X with Y and o with N"""

    def __init__(self):
        super().__init__()
        self.Checkbox.selected_icon = "Y"
        self.Checkbox.unselected_icon = "N"

# Client class
class Client():
    # initialize the client socket descriptor to None
    def __init__(self):
        # setting the character encoding to UTF-8
        locale.getpreferredencoding = 'utf-8'

        self.client_socket_descriptor = None

        # fetching the IP address of the client
        self.host_ip = socket.gethostbyname(socket.gethostname())

        # initializing the Utility service
        self._utility_service = UtilityService()

        self._socket_service = None

        # initializing the Storage Path service
        self._storage_service = StoragePathService(
            Config.CLIENT_FILE_STORAGE_PATH)

    # executes the selected option given by the user
    def execute_command(self, option, gui_params=None):
        if option == Option.CONN:
            print("connection command:")

            print("-----------------------------------------------------------")

            if self.client_socket_descriptor == None:
                # destructure the gui_params
                if gui_params:
                    ip_address, port = gui_params['ip_address'], gui_params['port']

                else:
                    # Scan IP address and Port number
                    ip_address, port = self._utility_service.scan_server_details()

                # create connection with the scanned IP address and Port number
                self.connect_to_server(ip_address, port)

            else:
                print("Connection already exists")

            print("-----------------------------------------------------------")

        elif option == Option.UPLD:
            print("upload command received")

            if self.client_socket_descriptor != None:
                # destructing the gui params
                if gui_params:
                    files = gui_params['files']
                    expiry_date = gui_params['expiry_date']
                else:
                    # accept file path in comma seperated form
                    user_input = input(
                        "Enter your file path in comma separated:")

                    files = user_input.split(",")
                    
                    # scan the expiry date input from the user
                    expiry_date = self._utility_service.scan_expiry_date()

                # generating global unique identifier.
                storage_location = str(uuid.uuid4())

                # upload multiple files
                return self.upload_multiple_files(files, storage_location, expiry_date)

            else:
                print("Connection is not established")

            print("-----------------------------------------------------------")

        elif option == Option.LIST:
            print("list command received")

            if self.client_socket_descriptor != None:
                # destructure the gui_params
                if gui_params:
                    storage_path = gui_params['storage_path']

                else:
                    # Scan storage path
                    storage_path = input("Enter storage location:")

                # Fetch files in the storage path
                return self.display_files_in_storage_path(storage_path)

            else:
                print("Connection is not established")
            print("-----------------------------------------------------------")

        elif option == Option.DWLD:
            print("download command received")

            if self.client_socket_descriptor != None:
                # destructure the gui_params
                if gui_params:
                    storage_path = gui_params['storage_path']
                    files_to_download = gui_params['file_names']

                else:
                    # Scan storage path
                    storage_path = input("Enter storage location:")

                    # accept file path in comma seperated form
                    user_input = input(
                        "Enter your file path in comma separated:")

                    files_to_download = user_input.split(",")

                # download the list of files from the given storage path
                return self.download_multiple_files(files_to_download, storage_path)
            else:
                print("Connection is not established")
            print("-----------------------------------------------------------")

        elif option == Option.QUIT:
            print("Quit command received")

            if self.client_socket_descriptor != None:
                # close the control connection
                self.disconnect_from_server()

            else:
                print("Connection is not established")
                print("-----------------------------------------------------------")

        elif option == Option.MANUAL:
            print("Manual mode ON...enter quit to terminate")

            command = input()

            while(command.strip() != "quit"):
                request_command, *args = command.split()

                request_command = request_command.strip()

                if request_command == "connect":
                    if len(args) !=2:
                        # Scan IP address and Port number
                        ip_address, port = self._utility_service.scan_server_details()
                    else:
                        ip_address, port = args
                        
                        # execute connect command
                        (_, _message) = self._execute_connect_command(ip_address, int(port))

                        if _message:
                            print(message)
                
                elif self.client_socket_descriptor:
                    if request_command == Request.USER:
                        if len(args) == 1:
                            # execute user command
                            (_, _message) = self._execute_user_command(args[0])

                            if _message:
                                print(_message)

                        else:
                            print("invalid arguments")
                        
                    elif request_command == Request.PASS:
                        if len(args) == 1:
                            # execute pass command
                            (_, _message) = self._execute_pass_command(args[0])

                            if _message:
                                print(_message)

                        else:
                            print("invalid arguments")                        

                    elif request_command == Request.STOR:
                        if len(args) != 2:
                            # accept file path in comma seperated form
                            user_input = input(
                                "Enter your file path in comma separated:")

                            files_to_upload = user_input.split(",")
                            
                            # scan the expiry date input from the user
                            expiry_date = self._utility_service.scan_expiry_date()
                        
                        else:
                            files_to_upload = args[0].split(",")

                            expiry_date = args[1]

                        # generating global unique identifier.
                        storage_path = str(uuid.uuid4())
                    
                        self.upload_multiple_files(files_to_upload, storage_path, expiry_date)
                
                    elif request_command == Request.PWD:
                        # execute pwd command
                        (_, _message) = self._execute_pwd_command()

                        if _message:
                            print(_message)
                    
                    elif request_command == Request.MKD:
                        if len(args) == 1:
                            # execute mkd command
                            (_, _message) = self._execute_mkd_command(args[0])

                            if _message:
                                print(_message)

                        else:
                            print("invalid arguments")
                        
                    elif request_command == Request.CWD:
                        if len(args) == 1:
                            # execute change working directory(cwd) command
                            (_, _message) = self._execute_cwd_command(args[0])

                            if _message:
                                print(_message)
                        
                        else:
                            print("invalid arguments")

                    elif request_command == Request.RETR:
                        if len(args) != 2:
                            # Scan storage path
                            storage_path = input("Enter storage location:")

                            # accept file path in comma seperated form
                            user_input = input(
                                "Enter your file path in comma separated:")

                            files_to_download = user_input.split(",")
                        
                        else:
                            storage_path = args[0]

                            files_to_download = args[1]

                        # download the list of files from the given storage path
                        self.download_multiple_files(files_to_download, storage_path)
                    
                    elif request_command == Request.LIST:
                        if len(args) != 1:
                            # Scan storage path
                            storage_path = input("Enter storage location:")
                        
                        else:
                            storage_path = args[0]

                        # Fetch files in the storage path
                        self.display_files_in_storage_path(storage_path)

                    elif request_command == Request.QUIT:
                        self.disconnect_from_server()

                    else:
                        print("command not supported")

                else:
                    print(f"connection not established")

                command = input()
            print("Manual mode exited.")

        else:
            print("Invalid option...please try again")
            print("-----------------------------------------------------------")

    def _execute_connect_command(self, ip_address, port):
            # connecting to the server 
            self.client_socket_descriptor = self._utility_service.make_connection(
                ip_address, port)

            # initializing the socket service instance
            self._socket_service = SocketService(self.client_socket_descriptor)

            print("-----------------------------------------------------------")

            # receive the response from the server
            response_code, response_args = self._socket_service.receive_response()

            # check the response code
            if response_code == Response_Type.SERVICE_READY:
                # print the response message
                print(f"{' '.join([response_code, *response_args])}")
                return (None, None)

            else:
                # handling unknown response codes
                _message = f"Response Code Error: {' '.join([response_code, *response_args])}"
                print(f"{_message}")
                return (None, _message)

    def _execute_utf_command(self):
            # send the request to the server
            self._socket_service.send_request(Request.OPTS, ['UTF8', 'ON'])

            # receive the response from the server
            response_code, response_args = self._socket_service.receive_response()

            # check the response code
            if response_code == Response_Type.UTF8_MODE_ON:
                print(f"{' '.join([response_code, *response_args])}")
                return (None,None)

            else:
                _message = f"Response Code Error: {' '.join([response_code, *response_args])}"
                print(f"{_message}")
                return (None, _message)
            
    def _execute_user_command(self, user_name):       
            # send the request to the server
            self._socket_service.send_request(Request.USER, [user_name])

            # receive the response from the server
            response_code, response_args = self._socket_service.receive_response()

            # check the response code
            if response_code == Response_Type.SPECIFY_PASSWORD:
                print(f"{' '.join([response_code, *response_args])}")
                return (None,None)

            else:
                _message = f"Response Code Error: {' '.join([response_code, *response_args])}"
                print(f"{_message}")
                return (None, _message)

    def _execute_pass_command(self, password):
            # send the request to the server
            self._socket_service.send_request(Request.PASS, [password])

            # receive the response from the server
            response_code, response_args = self._socket_service.receive_response()

            # check the response code
            if response_code == Response_Type.LOGIN_SUCCESS:
                print(f"{' '.join([response_code, *response_args])}")
                return (None,None)

            # check the response code
            elif response_code == Response_Type.LOGIN_FAILED:
                _message = ' '.join([response_code, *response_args])
                print(f"{_message}")
                return (None, _message)

            else:
                _message = f"Response Code Error: {' '.join([response_code, *response_args])}"
                print(f"{_message}")
                return (None, _message)

    # Establishes connection between client and server with specified IP address and Port number
    def connect_to_server(self, ip_address, port):
        try:
            # execute connect command
            (_, _message) = self._execute_connect_command(ip_address, port)

            if _message:
                return (None, _message)

            # execute UTF command
            (_, _message) = self._execute_utf_command()

            if _message:
                return (None, _message)

            # execute USER command
            (_, _message) = self._execute_user_command('anonymous')

            if _message:
                return (None, _message)
            
            # execute PASS command
            (_, _message) = self._execute_pass_command('')

            if _message:
                return (None, _message)\

            # execute CWD command
            (_, _message) = self._execute_cwd_command('/')

            if _message:
                return (None, _message)

        except Exception as e:
            self.client_socket_descriptor = None
            print(f"Exception at Client.py > connect_to_server method:{e}")

    def _execute_port_command(self, data_connection_port):
        # public_ip = requests.get('https://api.ipify.org/').text

        # encoding the ip address and port number for the PORT command payload
        payload = self._utility_service.encode_port_command_payload(
            self.host_ip, data_connection_port)

        # send the request to the server
        self._socket_service.send_request(Request.PORT, [payload])

        # receive the response from the server
        response_code, response_args = self._socket_service.receive_response()

        # check the response code
        if response_code == Response_Type.PORT_COMMAND_SUCCESS:
            print(f"{' '.join([response_code, *response_args])}")
            return True

        # check the response code
        elif response_code == Response_Type.PORT_COMMAND_FAILED:
            print(f"{' '.join([response_code, *response_args])}")
            return False

        # handling unknown response codes
        else:
            print(f"Response Code Error: {' '.join([response_code, *response_args])}")
            return False

    def __transfer_file(self, storage_path, file_name, file_path, transfer_type):
        # generating the random data connection port number
        data_connection_port = random.randint(2000, 65535)

        # execute the port command using given data connection port
        port_command_success = self._execute_port_command(data_connection_port)

        if not port_command_success:
            logger_service_instance.create_file_transfer_log(
                self.address, transfer_type, 
                storage_path, file_name, 
                0, 0, 'PORT_COMMAND_FAILED')
            return False
       
        # listening for the data connection in PASSIVE mode
        data_connection_descriptor = self._utility_service.listen_for_connnection(
            self.host_ip, data_connection_port)

        # checking the type of transfer
        if transfer_type == Transfer_Type.Upload:
            # send the request to the server
            self._socket_service.send_request(Request.STOR, [file_name])

            # ---------------------------------------------------------------------------------------

            # accept the new connection and get the socket and address of client
            client_data_socket, client_address = data_connection_descriptor.accept()

            # receive the response from the server
            response_code, response_args = self._socket_service.receive_response()

            print(f"client connection detected")

            # ---------------------------------------------------------------------------------------
            
            # check the response code
            if response_code == Response_Type.OK_TO_SEND_DATA:
                print(f"{' '.join([response_code, *response_args])}")
            
            # check the response code
            elif response_code == Response_Type.OPEN_DATA_CONNECTION_FAILED:
                _message = f"{' '.join([response_code, *response_args])}"
                
                print(_message)

                logger_service_instance.create_file_transfer_log(
                    client_address, transfer_type, 
                    storage_path, file_name, 
                    0, 0, _message)

                return False

            # handling unknown response codes
            else:
                _message = f"Response Code Error: {' '.join([response_code, *response_args])}"
                
                print(_message)
                
                logger_service_instance.create_file_transfer_log(
                    client_address, transfer_type, 
                    storage_path, file_name, 
                    0, 0, _message)

                return False

            print(f"{os.path.getsize(file_path)} bytes")

            transfer_start_time = time.time()
            
            # opening the file in binary read mode
            with open(file_path, "rb") as file_descriptor:
                # Read file contents.
                data = file_descriptor.read(Config.MAX_BUFFER_SIZE)

                # setting the encoding type to UTF-8
                encoding_type = 'utf-8'

                # print(f"{type(data)}")

                # data = data.encode(encoding_type)

                # print(chardet.detect(data))

                print(f"Sending file contents...")

                data_sent = 0

                # Send file contents.
                while data:
                    # send the data to the server
                    client_data_socket.send(data)

                    # client_data_socket.send(bytes(data, encoding_type))

                    data = file_descriptor.read(Config.MAX_BUFFER_SIZE)

                    data_sent += Config.MAX_BUFFER_SIZE

                    print(f"Amount of data sent: {data_sent}")

                    # acknowledgement from the server
                    client_data_socket.recv(Config.MAX_BUFFER_SIZE)

                # sending end of file
                client_data_socket.send(Request.EOF.name.encode())

                # acknowledgement from the server
                client_data_socket.recv(Config.MAX_BUFFER_SIZE)

                # close the data connection
                client_data_socket.close()
            
            transfer_end_time = time.time()

        else:
            # send the request to the server
            self._socket_service.send_request(Request.RETR, [file_name])

            # ---------------------------------------------------------------------------------------

            # accept the new connection and get the socket and address of client
            client_data_socket, client_address = data_connection_descriptor.accept()

            print(f"client connection detected")

            # ---------------------------------------------------------------------------------------
            
            # receive the response from the server
            response_code, response_args = self._socket_service.receive_response()

            # check the response code
            if response_code == Response_Type.BINARY_MODE_DATA_CONNECTION_OPENDED:
                print(f"{' '.join([response_code, *response_args])}")

            # handling unknown response codes
            else:
                _message = f"Response Code Error: {' '.join([response_code, *response_args])}"

                print(_message)

                logger_service_instance.create_file_transfer_log(
                    client_address, transfer_type, 
                    storage_path, file_name, 
                    0, 0, _message)

                return False

            print(f"receiving file contents...")

            transfer_start_time = time.time()

            # opening the file in binary write mode
            with open(file_path, "wb") as file_descriptor:

                data_received = 0

                # Receive file contents.
                while True:
                    # receive the content from the server
                    data = client_data_socket.recv(Config.MAX_BUFFER_SIZE)

                    # check EOF is sent
                    if data == Request.EOF.name.encode():
                        break

                    # writing data to the file
                    file_descriptor.write(data)

                    data_received += Config.MAX_BUFFER_SIZE

                    print(f"Amount of data received: {data_received}")

                    # sending acknowledgement for end of file
                    client_data_socket.send("1".encode())

                # sending acknowledgement for end of file
                client_data_socket.send("1".encode())

                # close the data connection
                client_data_socket.close()
            
            transfer_end_time = time.time()

        # receive the response from the server
        response_code, response_args = self._socket_service.receive_response()

        # check the response code
        if response_code == Response_Type.TRANSFER_COMPLETED:
            print(f"{' '.join([response_code, *response_args])}")

            logger_service_instance.create_file_transfer_log(
                client_address, transfer_type, 
                storage_path, file_name, 
                transfer_start_time, transfer_end_time, 'TRANSFER COMPLETED')

            return True

        # handling unknown response codes
        else:
            _message = f"Response Code Error: {' '.join([response_code, *response_args])}"

            print(_message)
            
            logger_service_instance.create_file_transfer_log(
                client_address, transfer_type, 
                storage_path, file_name, 
                0, 0, _message)

            return False

    def __upload_file(self, storage_path, file_path):
        try:
            # generating the file name from the file path
            file_path = file_path.strip()

            if file_path.count("\\"):
                file_name = file_path.split('\\')[-1]

            else:
                file_name = file_path.split("/")[-1]

            # calling transfer file function
            transfer_success = self.__transfer_file(storage_path, file_name, file_path, Transfer_Type.Upload)

            if not transfer_success:
                return False
            
            return True

        except Exception as e:
            print(f"Exception at Client.py > upload file method:{e}")
            return False
        
    def _execute_mkd_command(self, storage_path):
            # send the request to the server
            self._socket_service.send_request(Request.MKD, [storage_path])

            # receive the response from the server
            response_code, response_args = self._socket_service.receive_response()

            # check the response code
            if response_code == Response_Type.STORAGE_PATH_CREATED:
                print(f"{' '.join([response_code, *response_args])}")
                return (None, None)

            # check the response code
            elif response_code == Response_Type.CREATE_DIRECTORY_FAILED:
                _message = ' '.join([response_code, *response_args])
                print(f"{_message}")
                return (None, _message)

            # handling unknown response codes
            else:
                _message = f"Response Code Error: {' '.join([response_code, *response_args])}"
                print(f"{_message}")
                return (None, _message)

    def upload_multiple_files(self, files_to_upload, storage_path, expiry_date):
        try:
            # execute change working directory(cwd) command
            (_, _message) = self._execute_cwd_command("/")

            if _message:
                return (None, _message)

            # execute change working directory(cwd) command
            (_, _message) = self._execute_mkd_command(storage_path)

            if _message:
                return (None, _message)

            # send the request to the server
            self._socket_service.send_request(Request.SETEXPIRY, [storage_path, expiry_date])

            # receive the response from the server
            response_code, response_args = self._socket_service.receive_response()

            # check the response code
            if response_code == Response_Type.EXPIRY_DATE_SET:
                print(f"{' '.join([response_code, *response_args])}")

            # handling unknown response codes
            else:
                _message = f"Response Code Error: {' '.join([response_code, *response_args])}"
                print(f"{_message}")
                return (None, _message)

            # execute cwd command
            self._execute_cwd_command(storage_path)
            
            upload_status = []

            # upload each file and get the status of upload
            for file_path in files_to_upload:
                upload_status.append(self.__upload_file(storage_path, file_path))

            # checking if all files are uploaded
            if all(upload_status):
                print(f"files upload successful to the storage :{storage_path}")
                return (storage_path, expiry_date)
            
            return (None, 'upload error')

        except Exception as e:
            print(f"Exception at Client.py > upload multiple files method:{e}")
            
            return (None, None)

    def __download_file(self, server_storage_path, client_storage_location_path, file_name):
        try:
            # Creates a file path to store files
            file_path = f"{Config.CLIENT_FILE_STORAGE_PATH}/{client_storage_location_path}/{file_name}"

            # creating the storage path on client side
            self._storage_service.create_storage_path(file_path)

            # calling transfer file function
            return self.__transfer_file(server_storage_path, file_name, file_path,Transfer_Type.Download)

        except Exception as e:
            print(f"Exception at Client.py > download file method:{e}")
            pass

    def _execute_pwd_command(self):
        # send the request to the server
        self._socket_service.send_request(Request.PWD)

        # receive the response from the server
        response_code, response_args = self._socket_service.receive_response()

        # check the response code
        if response_code == Response_Type.PWD_SUCCESS:
            print(f"{' '.join([response_code, *response_args])}")
            return (response_args, None)

        # handling unknown response codes
        else:
            _message = f"Response Code Error: {' '.join([response_code, *response_args])}"
            print(f"{_message}")
            return (None, _message)

    def _execute_cwd_command(self, storage_path, skip_pwd = False):
        try:
            payload = f"{storage_path}"

            if not skip_pwd:
                # execute the cwd command
                (response_args, _message) = self._execute_pwd_command()

                if _message:
                    return (None, _message)
                
                # checking whether storage path and current directory are same or root
                if response_args[0] == storage_path or (
                        response_args[0] == "/" 
                        and response_args[0] == storage_path) :
                    return (None, None)
                
                # checking whether the current directory is root
                elif response_args[0] == "/" and response_args[0] != storage_path:
                    payload = f"{storage_path}"
                
                # checking whether the current directory is same as storage path requested
                elif response_args[0] != f"/{storage_path}":
                    (_, _message) = self._execute_cwd_command("/", skip_pwd = True)

                    if _message:
                        return (None, _message)

                    payload = f"{storage_path}"
                
            # send the request to the server
            self._socket_service.send_request(Request.CWD, [payload])

            # receive the response from the server
            response_code, response_args = self._socket_service.receive_response()

            # check the response code
            if response_code == Response_Type.DIRECTORY_CHANGED_SUCCESS:
                print(f"{' '.join([response_code, *response_args])}")
                return (None, None)

            # check the response code
            elif response_code == Response_Type.DIRECTORY_CHANGE_FAILED:
                # _message = ' '.join([response_code, *response_args])
                _message = response_args[-1]
                print(f"{_message}")
                return (None, _message)

            # handling unknown response codes
            else:
                _message = f"Response Code Error: {' '.join([response_code, *response_args])}"
                print(f"{_message}")
                return (None, _message)
                
            return (None, None)

        except Exception as message:
            print(f"Exception at Client.py > execute cwd command method:{message}")
            return (None, message)


    def download_multiple_files(self, files_to_download, server_storage_path):
        try:
            # execute the cwd command
            (_, _message) = self._execute_cwd_command(server_storage_path)

            if _message:
                return (None, _message)

            # generate an random guid for the storage location
            client_storage_location_path = str(uuid.uuid4())

            download_status = []

            # download all the files requested and get the download status
            for file_name in files_to_download:
                download_status.append(self.__download_file(server_storage_path, client_storage_location_path, file_name))

            # checking all the files are downloaded or not
            if all(download_status):
                print(f"files download successful to the storage :{client_storage_location_path}")
                return (client_storage_location_path, None)

            return (None, 'download error')

        except Exception as message:
            print(f"Exception at Client.py > download multiple files method:{message}")


    def display_files_in_storage_path(self, storage_path):
        try:
            # generating the random port for data connection
            data_connection_port = random.randint(2000, 65535)

            # execute the cwd command
            (_, _message) = self._execute_cwd_command(storage_path)

            if _message:
                return (None, _message)

            # executing the port command
            port_command_status = self._execute_port_command(data_connection_port)

            if not port_command_status:
                return ([],"Internal Error")

            # send the request to the server
            self._socket_service.send_request(Request.LIST, [storage_path])

            # opening the data connection and entering the PASSIVE mode
            data_connection_descriptor = self._utility_service.listen_for_connnection(
            self.host_ip, data_connection_port)

            # ---------------------------------------------------------------------------------------

            # accept the new connection and get the socket and address of client
            client_data_socket, client_address = data_connection_descriptor.accept()

            print(f"client connection detected")

            # ---------------------------------------------------------------------------------------
            
            # receive the response from the server
            response_code, response_args = self._socket_service.receive_response()

            # check the response code
            if response_code == Response_Type.DIRECTORY_LISTING:
                print(f"{' '.join([response_code, *response_args])}")

            # handling unknown response codes
            else:
                _message = f"Response Code Error: {' '.join([response_code, *response_args])}"
                print(f"{_message}")
                return (None, _message)
            
            data_received = 0

            content = None

            # Receive file contents.
            while True:
                # receive data from server
                data = client_data_socket.recv(Config.MAX_BUFFER_SIZE)

                # check for EOF
                if data.decode() == Request.EOF.name:
                    break

                # unoacking the json data
                content = json.loads(data.decode())

                # sending acknowledgement
                client_data_socket.send("1".encode())

                data_received += Config.MAX_BUFFER_SIZE

                print(f"Amount of data received: {data_received}")

            # sending acknowledgement for end of file
            client_data_socket.send("1".encode())

            # close the data connection
            client_data_socket.close()

            # print(f"content: {content}")

            print(f"-------------------------------------------------------------")

            files_fetched = []

            # collect information regarding the files in the response payload sent from server
            for _file_info in content["files_info"]:
                print(f"{_file_info['file']} - {_file_info['file_size']} bytes")
                files_fetched.append((_file_info['file'], _file_info['file_size']))
            
            print(f"Total directory size : {content['directory_size']} bytes")

            print(f"-------------------------------------------------------------")

            # receive the response from the server
            response_code, response_args = self._socket_service.receive_response()

            # check the response code
            if response_code == Response_Type.DIRECTORY_SEND_SUCCESS:
                print(f"{' '.join([response_code, *response_args])}")
                return (files_fetched, None)

            # handling unknown response codes
            else:
                _message = f"Response Code Error: {' '.join([response_code, *response_args])}"
                print(f"{_message}")
                return (None, _message)

        except Exception as message:
            print(f"Exception at Client.py > display files in storage path method:{message}")

    def disconnect_from_server(self):
        try:
            # send the request to the server
            self._socket_service.send_request(Request.QUIT)

            # receive the response from the server
            response_code, response_args = self._socket_service.receive_response()

            # check the response code
            if response_code == Response_Type.CLOSE_CONNECTION_SUCCESS:
                self.client_socket_descriptor.close()
                self.client_socket_descriptor = None
                print(f"{' '.join([response_code, *response_args])}")

            # check the response code
            elif response_code == Response_Type.CLOSE_CONNECTION_FAILED:
                _message = ' '.join([response_code, *response_args])
                print(f"{_message}")
                return (None, _message)

            # handling unknown response codes
            else:
                _message = f"Response Code Error: {' '.join([response_code, *response_args])}"
                print(f"{_message}")
                return (None, _message)

        except Exception as e:
            print(f"Exception at Client.py > disconnect from server method:{e}")


if __name__ == "__main__":
    # Client Side Menu options
    MenuOptions = [
        List(
            "option",
            "What action do you want to perform?",
            [option.value for option in Option]
        )
    ]

    # creating client instance
    client_instance = Client()

    while True:
        try:
            # taking the user selection
            response = prompt(MenuOptions)

            if response == None:
                break

            # execute the selected option
            client_instance.execute_command(response['option'])

        except Exception as message:
            print("Error:", message)

    print("client program closed")
    print("-----------------------------------------------------------")
