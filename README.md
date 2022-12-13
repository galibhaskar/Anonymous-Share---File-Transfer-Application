# Anonymous share via socket programming

This is a client-server implementation using FTP protocol written in python which focuses on transfering the files.

# Running:

To start the server/client program:

Run python server.py file so that it could accept connections from multiple clients. Then we run clients in different windows machines and get it connected to the server. 

## Running Server
1. Clone the repository in windows machine
2. Run pip install 
3. Navigate to `source_code -> server`
4. Run `>python Server.py`

## Running Client
1. Clone the repository in windows machine
2. Run pip install
3. Navigate to `source_code -> client`
4. Run `>python Client.py`

### - Connect to Server: 
#### &ensp;  creates connection to the server
    Here, client enters IP address and Port number manually to make a connect request.

### - Upload files:
#### &ensp;  Uploads the files from client to the server storage location.
    Here, client enters absolute paths of files in comma separated and server responds with the storage location path.

### - Download files
#### &ensp; Downloads the selected files from the server storage location to the client storage.
    Here, client enters the storage path and server responds with the list of files available in the storage path. 

    Then, client selects the files that he wants to download.

### - List files
#### &ensp; Displays the list of files available in the storage location.
    Here, Client requests the server for the list of files with the storage path.

### - Quit
#### &ensp; Closes the connection
    This command terminates the connection.

# Installation - 1 Deliverables:
Making and Closing the connection in between client and server.

# Installation - 2 Deliverables:
Upload, download files in between the client and server. List files in the given storage location. 

# Installation - 3 Deliverables:
Creating a GUI application and integrating it with the above mentioned functionality.

# GUI Implementation:

## Running Client
1. Clone the repository in windows machine
2. Run pip install
3. Navigate to `source_code -> client`
4. Run `>python ClientGUI.py`

### option: connect to server: 
    By selecting this option, client enters the IP address and Port number of the server. Once the client connects to server, this option will be updated to 'disconnect'
    

The homepage has three widgets:
1. Upload files
    - when client selects the upload files option, the client is allowed to select a maximum of 6 files along with the expiration date and server responds with the storage location path. The client is also allowed to copy the location path by selecting - copy to clipboard which can be used later for downloading files.
2. View files
    - client enters the copied storage path and server responds with the list of files available in the storage path.
3. Download files
    - client selects the files that he wants to download either single file or multiple files from his system. The files will be available for download only within the expiration date specified.

### option : Disconnect
    By selecting this client connection gets terminated.


![Alt text](./installations/final-installation/images/box_plot_high_loss_rate.png)