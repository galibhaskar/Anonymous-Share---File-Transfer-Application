from strenum import StrEnum

class Response_Type(StrEnum):
    SERVICE_READY = '220'
    UTF8_MODE_ON = '200',
    UTF8_MODE_OFF = '500',
    SPECIFY_PASSWORD = '331',
    LOGIN_SUCCESS = '230',
    LOGIN_FAILED = '530',
    CLOSE_CONNECTION_SUCCESS = '221',
    CLOSE_CONNECTION_FAILED = '500',
    SYNTAX_ERROR_IN_PARAMS = '501',
    COMMAND_NOT_IMPLEMENTED = '502',
    COMMAND_NOT_IMPLEMENTED_FOR_PARAMETER = '504',
    STORAGE_PATH_CREATED = '257',
    CREATE_DIRECTORY_FAILED = '550',
    EXPIRY_DATE_SET = '000',
    EXPIRY_DATE_SET_FAILED = '001',
    DIRECTORY_CHANGED_SUCCESS = '250',
    DIRECTORY_CHANGE_FAILED = '550',
    PORT_COMMAND_SUCCESS = '200',
    PORT_COMMAND_FAILED = '500',
    OPEN_DATA_CONNECTION_FAILED = '425',
    OK_TO_SEND_DATA = '150',
    TRANSFER_COMPLETED = '226',
    TRANSFER_ABORTED = '426',
    BINARY_MODE_DATA_CONNECTION_OPENDED = '150',
    LOCAL_PROCESSING_ERROR = '451', 
    FILE_NOT_FOUND = '550', 
    DIRECTORY_LISTING = '150',
    DIRECTORY_SEND_SUCCESS = '226'
    PWD_SUCCESS = '257'

def get_response_message(response_type, args):
    if response_type == 'SERVICE_READY':
        return 'Service ready for new user; Welcome to FTP server'

    elif response_type == 'PORT_COMMAND_SUCCESS':
        return 'PORT command successful. Consider using PASV.'
    
    elif response_type == 'UTF8_MODE_ON':
        return 'Always in UTF8 mode.'
    
    elif response_type == 'UTF8_MODE_OFF':
        return ''

    elif response_type == 'SPECIFY_PASSWORD':
        return 'Please specify the password.'

    elif response_type == 'LOGIN_SUCCESS':
        return 'Login successful.'

    elif response_type == 'LOGIN_FAILED':
        return 'Login failed.'

    elif response_type == 'CLOSE_CONNECTION_SUCCESS':
        return 'Goodbye.'

    elif response_type == 'CLOSE_CONNECTION_FAILED':
        return 'Connection Close Error.'

    elif response_type == 'SYNTAX_ERROR_IN_PARAMS':
        return 'Syntax error in parameters or arguments.'
    
    elif response_type == 'COMMAND_NOT_IMPLEMENTED':
        return 'Command not implemented.'

    elif response_type == 'COMMAND_NOT_IMPLEMENTED_FOR_PARAMETER':
        return 'Command not implemented for that parameter.'
    
    elif response_type == 'PWD_SUCCESS':
        return f'{args[0]}'

    elif response_type == 'STORAGE_PATH_CREATED':
        return 'Storage Path created.'

    elif response_type == 'CREATE_DIRECTORY_FAILED':
        return 'Create directory operation failed.'

    elif response_type == 'EXPIRY_DATE_SET':
        return 'Expiration data set.'

    elif response_type == 'EXPIRY_DATE_SET_FAILED':
        return 'Expiration data set failed.'

    elif response_type == 'DIRECTORY_CHANGE_FAILED':
        return 'Failed to change directory.'
    
    elif response_type == 'DIRECTORY_CHANGED_SUCCESS':
        return 'Directory successfully changed.'

    elif response_type == 'PORT_COMMAND_FAILED':
        return 'PORT command failed.'

    elif response_type == 'OK_TO_SEND_DATA':
        return 'Ok to send data.'

    elif response_type == 'OPEN_DATA_CONNECTION_FAILED':
        return 'Failed to open data connection.'

    elif response_type == 'TRANSFER_COMPLETED':
        return 'Transfer complete.'

    elif response_type == 'TRANSFER_ABORTED':
        return 'Transfer aborted.'

    elif response_type == 'BINARY_MODE_DATA_CONNECTION_OPENDED':
        return 'Opening BINARY mode data connection.'

    elif response_type == 'LOCAL_PROCESSING_ERROR':
        return 'Requested action aborted: local error in processing.'

    elif response_type == 'FILE_NOT_FOUND':
        return 'Requested action not taken. File unavailable (e.g., file not found, no access).'
    
    elif response_type == 'DIRECTORY_LISTING':
        return 'Here comes the directory listing.'
    
    elif response_type == 'DIRECTORY_SEND_SUCCESS':
        return 'Directory send OK.'

    else:
        return ''

# Response_Messages = {}

# Response_Messages[Response_Type.SERVICE_READY] = 'Service ready for new user; Welcome to FTP server'
# Response_Messages[Response_Type.UTF8_MODE_OFF] = ''
# Response_Messages[Response_Type.UTF8_MODE_ON] = 'Always in UTF8 mode.'
# Response_Messages[Response_Type.SPECIFY_PASSWORD] = 'Please specify the password.'
# Response_Messages[Response_Type.LOGIN_SUCCESS] = 'Login successful.'
# Response_Messages[Response_Type.LOGIN_FAILED] = 'Login failed.'
# Response_Messages[Response_Type.CLOSE_CONNECTION_SUCCESS] = 'Goodbye.'
# Response_Messages[Response_Type.CLOSE_CONNECTION_FAILED] = 'Connection Close Error.'
# Response_Messages[Response_Type.SYNTAX_ERROR_IN_PARAMS.name] = 'Syntax error in parameters or arguments.'
# Response_Messages[Response_Type.COMMAND_NOT_IMPLEMENTED.name] = 'Command not implemented.'
# Response_Messages[Response_Type.COMMAND_NOT_IMPLEMENTED_FOR_PARAMETER.name] = 'Command not implemented for that parameter.'
# Response_Messages[Response_Type.STORAGE_PATH_CREATED.name] = 'Storage Path created.'
# Response_Messages[Response_Type.CREATE_DIRECTORY_FAILED.name] = 'Create directory operation failed.'
# Response_Messages[Response_Type.EXPIRY_DATE_SET.name] = 'Expiration data set.'
# Response_Messages[Response_Type.EXPIRY_DATE_SET_FAILED.name] = 'Expiration data set failed.'
# Response_Messages[Response_Type.DIRECTORY_CHANGE_FAILED.name] = 'Failed to change directory.'
# Response_Messages[Response_Type.DIRECTORY_CHANGED_SUCCESS.name] = 'Directory successfully changed.'
# Response_Messages[Response_Type.PORT_COMMAND_FAILED.name] = 'PORT command failed.'
# Response_Messages[Response_Type.PORT_COMMAND_SUCCESS.name] = 'PORT command successful. Consider using PASV.'
# Response_Messages[Response_Type.OK_TO_SEND_DATA.name] = 'Ok to send data.'
# Response_Messages[Response_Type.OPEN_DATA_CONNECTION_FAILED.name] = 'Failed to open data connection.'
# Response_Messages[Response_Type.TRANSFER_COMPLETED.name] = 'Transfer complete.'
# Response_Messages[Response_Type.TRANSFER_ABORTED.name] = 'Transfer aborted.'
# Response_Messages[Response_Type.BINARY_MODE_DATA_CONNECTION_OPENDED.name] = 'Opening BINARY mode data connection.'
# Response_Messages[Response_Type.LOCAL_PROCESSING_ERROR.name] = 'Requested action aborted: local error in processing.'
# Response_Messages[Response_Type.FILE_NOT_FOUND.name] = 'Requested action not taken. File unavailable (e.g., file not found, no access).'
# Response_Messages[Response_Type.DIRECTORY_LISTING.name] = 'Here comes the directory listing.'
# Response_Messages[Response_Type.DIRECTORY_SEND_SUCCESS.name] = 'Directory send OK.'

# 501 Syntax error in parameters or arguments.
# 502 Command not implemented.
# 503 Bad sequence of commands.
# 504 Command not implemented for that parameter.



