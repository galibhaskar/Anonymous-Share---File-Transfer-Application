from strenum import StrEnum

class Request(StrEnum):
    PORT = 'PORT',
    OPTS = 'OPTS',
    USER = 'USER',
    PASS = 'PASS',
    STOR = 'STOR',
    MKD = 'MKD',
    PWD = 'PWD',
    CWD = 'CWD',
    LIST = 'LIST',
    RETR = 'RETR',
    QUIT = 'QUIT',
    SETEXPIRY = 'SETEXPIRY'
    EOF = 'EOF',
