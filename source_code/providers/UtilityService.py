import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
import Config
import socket
from datetime import datetime, date
from contracts.IUtilityService import IUtilityService

class UtilityService(IUtilityService):
    def __init__(self):
        pass

    # scan ip address and port number of the server and returns the scanned input
    def scan_server_details(self):
        try:

            ip_address = input("Enter Server IP:")

            return (ip_address, Config.CONTROL_CONNECTION_PORT_NUMBER)
        
        except Exception as e:
            print(f"Exception at scan_server_details:{e}")

    # scan expiry date of the storage path
    def scan_expiry_date(self):
        while(True):
            try:
                # scanning expiry date from the user
                expiry_date = input("Enter the expiry date in the format(mm-dd-yyyy):")

                datetime.strptime(expiry_date, Config.DATE_FORMAT)

                return expiry_date
            
            except Exception as message:
                print(f"Invalid date format.Please try again...")

    # Establishes connection between client and server with specified IP address and Port number
    def make_connection(self, ip_address, port, source_ip = None, source_port = None):

        # Create a client socket descriptor which can maintain a TCP connection with the server
        socket_descriptor = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        
        socket_descriptor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        if source_ip and source_port:
            socket_descriptor.bind((source_ip, source_port))

        try:
            # connecting to the given ip_address and port number
            socket_descriptor.connect((ip_address, port))

            print(f"socket connected...")

        except Exception as e:
            socket_descriptor = None
            
            print(f"Connection establishment failed")

        finally:
            return socket_descriptor

    # Establishes connection between client and server with specified IP address and Port number
    def listen_for_connnection(self, ip_address, port):

        # Create a client socket descriptor which can maintain a TCP connection with the server
        socket_descriptor = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)

        socket_descriptor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            # connecting to the given ip_address and port number
            socket_descriptor.bind((ip_address, port))

            socket_descriptor.listen()

            print(f"socket listening...")

        except Exception as e:
            socket_descriptor = None
            
            print(f"Connection establishment failed")

        finally:
            return socket_descriptor

    def encode_port_command_payload(self, host_ip, port_number):
        # PORT ( h1,h2,h3,h4,p1,p2 )
        (h1, h2, h3, h4) = host_ip.split(".")

        # (p1 * 256) + p2 = data port
        (p1, p2) = (port_number//256, port_number % 256)

        payload = f"{h1},{h2},{h3},{h4},{p1},{p2}"
    
        return payload
    
    def decode_port_command_payload(self,payload):
        # PORT ( h1,h2,h3,h4,p1,p2 )
        (h1, h2, h3, h4, p1, p2) = payload.split(",")

        ip_address = f"{'.'.join([h1,h2,h3,h4])}"

        # (p1 * 256) + p2 = data port
        port_number = (int(p1) * 256) + int(p2) 
    
        return (ip_address, port_number)