from strenum import StrEnum

class Command(StrEnum):
    UPLD = 'Upload files',
    LIST = 'List files',
    DWLD = 'Download files',
    QUIT = 'Quit',