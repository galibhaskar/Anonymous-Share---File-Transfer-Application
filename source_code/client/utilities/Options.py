from strenum import StrEnum

class Option(StrEnum):
    CONN = 'Connect to server',
    UPLD = 'Upload files',
    LIST = 'List files',
    DWLD = 'Download files',
    QUIT = 'Quit',
    MANUAL = 'Manual'
