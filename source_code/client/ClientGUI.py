import customtkinter
from tkinter import *
from PIL import Image, ImageTk
import os
from utilities.FrameOptions import FrameOptions
from tkinter import filedialog
from Client import Client
from utilities.Options import Option
import subprocess
import Config
from datetime import datetime

PATH = os.path.dirname(os.path.realpath(__file__))

# Modes: "System" (standard), "Dark", "Light"
customtkinter.set_appearance_mode("Dark")

# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("blue")

# ClientGUI class
class ClientGUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # fetching the window screen width
        self._width = self.winfo_screenwidth()

        # fetching the window screen height
        self._height = self.winfo_screenheight()

        # setting the window to maximized state
        self.state('zoomed')

        self._app_title = f"Anonymous Share Application"

        # setting up the geometry of the application
        self.geometry(f"{self._width}x{self._height}")

        self.title(self._app_title)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # creating a client class instance
        self.client_instance = Client()

        # default initializations
        self.selected_frame_option = None

        self.selected_files = []

        self.clipboard_text = None

        self.storage_path = self.downloaded_location = self.ip_address = self.port_number = None

        # self.files_to_download = []

        self.expiry_date_set = None

        self.files_fetch_error = False

        self.error_message = None

        self.files_uploaded_success = self.download_sucess = self.expiry_date_error = False

        # rendering the application
        self.render_app()

    def render_app(self):
        # setting up the grid row configuration to expand the given index
        self.grid_rowconfigure(0, weight=1)

        # setting up the grid column configuration to expand the given index
        self.grid_columnconfigure(0, weight=1)

        # creating main frame
        self.main_frame = customtkinter.CTkFrame(
            master=self,
            height=(self._height),
            width=(self._width),
            corner_radius=10)

        # setting up the frame configuration in the grid
        self.main_frame.grid(
            row=0, column=0, columnspan=2,
            sticky="nsew", padx=20, pady=20)

        # setting up the grid row configuration to expand the given index
        self.main_frame.grid_rowconfigure(1, weight=1)

        # setting up the grid column configuration to expand the given index
        self.main_frame.grid_columnconfigure(0, weight=1)

        # print(f"window: {self._width}")

        # print(f"main frame: {self.main_frame['width']}")

        # rendering the header frame
        self.render_header_frame()

        print(f"selected frame option:{self.selected_frame_option}")

        # rendering the frames based on teh selected frame option
        if self.selected_frame_option == FrameOptions.Send:
            # rendering send frame
            self.render_send_frame()

        elif self.selected_frame_option == FrameOptions.View:
            # rendering view frame
            self.render_view_frame()

        elif self.selected_frame_option == FrameOptions.Receive:
            # rendering receive frame
            self.render_receive_frame()

        else:
            # rendering homepage_frame
            self.render_menu_options_frame()

    # function to render header frame
    def render_header_frame(self):
        # creating a frame
        self.frame_top = customtkinter.CTkFrame(
            master=self.main_frame,
            height=(0.5*(self._height)),
            corner_radius=10)

        # setting up the grid configuration for the frame
        self.frame_top.grid(
            row=0, column=0, columnspan=2,
            sticky="ew", padx=20, pady=20)

        # setting up the grid row configuration to expand the given index
        self.frame_top.grid_rowconfigure(0, weight=1)

        # setting up the grid column configuration to expand the given index
        self.frame_top.grid_columnconfigure(0, weight=1)

        # creating the label
        self.header_label = customtkinter.CTkLabel(
            master=self.frame_top,
            text=self._app_title,
            text_font=("Roboto Medium", -32),
            corner_radius=8,
            height=10)  # font name and size in px

        # setting up the grid configuration for the label
        self.header_label.grid(
            row=0, column=0, pady=20,
            padx=20, sticky="nwe")

        # checking whether connection is established or not
        if self.ip_address and self.port_number:
            
            # rendering the button
            self.render_flat_button(
                self.frame_top,
                "disconnect",
                0, 1, (lambda: self.disconnect())
            )

        else:
            
            # rendering the connect button if connection is not established
            self.render_flat_button(
                self.frame_top,
                "connect to server",
                0, 1, (lambda: self.connect_to_server())
            )

    # function to close the connection
    def disconnect(self):

        # send a quit command to the server
        self.client_instance.execute_command(Option.QUIT)

        # resetting the connection configs once the connection is closed
        if not self.client_instance.client_socket_descriptor:
            
            self.ip_address = None
            
            self.port_number = None
            
            self.selected_frame_option = None

            # rendering the application again
            self.render_app()
        
        pass

    def connect_to_server(self):
        # message to display in the dialog
        message = f"Enter the ip_address:port_number"
        
        while (True):
            try:
                
                # creating a dialog input
                dialog = customtkinter.CTkInputDialog(
                    text=message,
                    title="Connect to server")
                
                # fetching the input given in the dialog input
                dialog_input = dialog.get_input()

                # check if dialog is closed with any input
                if dialog_input == None:
                    break

                else:
                    
                    # extract the data from the dialog input
                    inputs = dialog_input.split(":")

                    # checking if ip and port numbers were given in specified format
                    if len(inputs) == 2:

                        # extracting the ip and port numbers
                        (ip_address, port_number) = inputs

                        # converting the port number to integer
                        port_number = int(port_number)

                        print(f"ip: {ip_address} port:{port_number}")
                        break
                    else:

                        # setting the format invalid message
                        message = "Invalid format (ip_address:port_number)"

            # catching the exception
            except Exception as message:
                message = "Invalid format (ip_address:port_number)"
                pass

        # setting up the gui parameters
        gui_params = {
            "ip_address": ip_address,
            "port": port_number
        }

        # passing the connection request command to the server
        self.client_instance.execute_command(Option.CONN, gui_params)

        # check whether connection got established or not
        if self.client_instance.client_socket_descriptor:

            # assign the ip and port number globally
            self.ip_address = ip_address

            self.port_number = port_number
            
            # re-rendering the application
            self.render_app()
        pass

    # function to create success frame
    def render_success_frame(self, success_message, parent_frame, frame_option):
        
        # creating a frame
        self.success_frame = customtkinter.CTkFrame(
            master=parent_frame,
            corner_radius=10)

        # setting up the grid configuration for the frame
        self.success_frame.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="nswe",
            padx=20,
            pady=20)

        # setting up the grid row and column configuration to expand the given index
        self.success_frame.grid_columnconfigure(0, weight=1)

        self.success_frame.grid_rowconfigure(0, weight=1)

        # creating a label
        self.text_label = customtkinter.CTkLabel(
            master=self.success_frame,
            text=success_message,
            text_font=("Roboto Medium", -20),
            corner_radius=8,
            height=10)

        # setting up the grid configuration for the label
        self.text_label.grid(
            row=0,
            column=0,
            pady=20,
            padx=20,
            sticky="nswe")

        if frame_option == FrameOptions.Send:
            try:
                # fetching the clipboard text of the client
                self.clipboard_text = self.main_frame.clipboard_get()

            except Exception:
                self.clipboard_text = None
            
            # check if storage path is copied to clipboard
            if self.storage_path != self.clipboard_text:
                text = "copy to clipboard"
                is_disabled = False

            else:
                text = "path copied"
                is_disabled = True

            # rendering the button
            self.render_flat_button(
                self.success_frame,
                text,
                1, 0, (lambda: self.copy_to_clipboard()), disabled=is_disabled)

            # rendering the button
            self.render_flat_button(
                self.success_frame,
                "click to view files", 1, 1,
                (lambda: self.fetch_files_from_server(self.storage_path, FrameOptions.View)))

        elif frame_option == FrameOptions.Receive:
            # fetching the clipboard text
            self.clipboard_text = self.main_frame.clipboard_get()

            # rendering the button
            self.render_flat_button(
                self.success_frame,
                "open downloads",
                1, 0, (lambda: self.open_downloads()))

        elif frame_option == FrameOptions.Receive or frame_option == FrameOptions.Error:
            # rendering the button
            self.render_flat_button(
                self.success_frame,
                "cancel", 1, 1,
                (lambda: self.button_clicked(None)))

    # function to open downloaded location folder
    def open_downloads(self):

        # constructing the folder location name
        folder_location_name = fr"{Config.CLIENT_FILE_STORAGE_PATH}/{self.downloaded_location}"

        # constructing the folder location path
        folder_location = os.path.realpath(folder_location_name)
        
        print(f"folder location:{folder_location}")
        
        # opening the file explorer in the given folder location path
        subprocess.Popen(f"explorer {folder_location}")

    # function to fetch files from the server
    def fetch_files_from_server(self, storage_path, targeted_frame_option):

        if storage_path == '':
            return
        
        # setting up the storage path to global
        self.storage_path = storage_path

        # creating a gui params object
        gui_params = {
            "storage_path": self.storage_path
        }

        # sending the LIST files command to the server
        (files, error_message) = self.client_instance.execute_command(
            Option.LIST, gui_params)

        # checking if there is any error message
        if error_message:
            # updating the global variable with the error details
            self.files_fetch_error = True
            
            self.error_message = error_message
            
            self.selected_files = []
        
        else:
            # updating the global variables with the file names
            file_names = list(map(lambda file_object: file_object[0], files))
            
            print(f"files from server: {files}")
            
            self.selected_files = file_names
        
        # redirecting the user to the targeted frame
        self.button_clicked(targeted_frame_option)

    # function to copy text to the client clipboard
    def copy_to_clipboard(self):

        # clearing the clipboard text
        self.main_frame.clipboard_clear()
        
        # appending the new storage path to the client clipboard
        self.main_frame.clipboard_append(self.storage_path)

        # re-rendering the application
        self.render_app()

    # function to render send frame
    def render_send_frame(self):

        # creating frame
        self.send_frame = customtkinter.CTkFrame(
            master=self.main_frame,
            corner_radius=10,
            height=(0.4*(self._height)))

        self.send_frame.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="nswe",
            padx=20,
            pady=20)

        self.send_frame.grid_columnconfigure(0, weight=1)
        
        self.send_frame.grid_rowconfigure(1, weight=1)

        if self.files_uploaded_success and self.storage_path:
            self.send_frame.grid_rowconfigure(0, weight=1)

            message = f"Files upload successful :  {self.storage_path} and expiry date :{self.expiry_date_set}"

            self.render_success_frame(
                message, self.send_frame, FrameOptions.Send)

        else:
            # creating a frame
            self.send_frame_header = customtkinter.CTkFrame(
                master=self.send_frame,
                corner_radius=10,
                height=(0.4*(self._height)))

            self.send_frame_header.grid(
                row=0,
                column=0,
                columnspan=3,
                sticky="we",
                padx=20,
                pady=20)

            self.send_frame_header.grid_columnconfigure(0, weight=1)

            # creating a label
            self.text_label = customtkinter.CTkLabel(
                master=self.send_frame_header,
                text="Upload the files you want to share (maximum - 6 files)",
                text_font=("Roboto Medium", -20),
                corner_radius=8,
                height=10)

            self.text_label.grid(
                row=0,
                column=0,
                pady=20,
                padx=20,
                sticky="we")

            if len(self.selected_files) == 0:
                # creating a button
                self.upload_files = customtkinter.CTkButton(
                    master=self.send_frame,
                    image=self.add_folder_image,
                    text="Add Files",
                    width=300,
                    text_font=("Roboto Medium", -18),
                    corner_radius=10,
                    compound="top",
                    command=self.open_dialog)

                self.upload_files.grid(row=1, column=0, columnspan=3,
                                       padx=20, pady=20, sticky="nsew")

            else:
                # self.send_frame.grid_rowconfigure(
                #     tuple(i for i in range(1, len(self.selected_files)+1)),
                #     weight=0)

                self.send_frame.grid_columnconfigure(0, weight=1)

                # rendering the files list frame
                self.render_files_list(
                    FrameOptions.Send, self.send_frame,  1, 0)

                # creating a expiry date text field
                self.expiry_date_input = customtkinter.CTkEntry(
                    master=self.send_frame,
                    placeholder_text=f"Enter expiry date (mm-dd-yyy):" if not self.expiry_date_error
                    else "Invalid expiry date (mm-dd-yyyy)",
                    width=250,
                    height=50,
                    border_width=2,
                    fg_color="default_theme" if not self.expiry_date_error
                    else "red",
                    text_color="default_theme" if not self.expiry_date_error
                    else "white",
                    placeholder_text_color="default_theme" if not self.expiry_date_error
                    else "white",
                    corner_radius=10)

                self.expiry_date_input.grid(
                    row=3,
                    column=0,
                    columnspan=2,
                    padx=20,
                    pady=20,
                    sticky="sw")

                # rendering a upload button
                self.render_flat_button(
                    self.send_frame,
                    "upload",
                    3, 0, (lambda: self.upload_files_to_server())
                )

                # rendering add more files button
                self.render_flat_button(
                    self.send_frame,
                    "add more files",
                    3, 1, (lambda: self.open_dialog("append")), disabled=(len(self.selected_files) == 6)
                )

                pass

        # rendering cancel button
        self.render_flat_button(
            self.send_frame,
            "cancel",
            3,
            2,
            (lambda: self.button_clicked(None))
        )

    # function to validate the expiry date entered
    def validate_expiry_date(self):
        try:
            # fetching the expiry date input text
            expiry_date = self.expiry_date_input.get()

            # convert the given input to required configuration format
            datetime.strptime(expiry_date, Config.DATE_FORMAT)

            # return true if format is correct
            return True

        except Exception:

            # returning false for the invalid format
            return False
        pass

    # function to upload files to the server
    def upload_files_to_server(self):
        try:
            # check whether the expiry date is valid or not
            if self.validate_expiry_date():

                self.expiry_date_error = False

                _expiry_date = self.expiry_date_input.get()

                print(f"Expiry date: {_expiry_date}")
                print(f"Files to upload: {self.selected_files}")

                # setting up the gui parameters
                gui_params = {
                    "files": self.selected_files,
                    "expiry_date": _expiry_date
                }

                # sending the upload command to the server with the gui params
                (storage_location_path, expiry_date) = self.client_instance.execute_command(
                    Option.UPLD, gui_params)

                # if upload is suuccessful
                if storage_location_path:
                    # updating the values
                    self.expiry_date_set = expiry_date
                    
                    self.files_uploaded_success = True
                    
                    self.storage_path = storage_location_path
                    
                    # re-rendering the application
                    self.render_app()

            else:
                # enabling the expiry date error
                self.expiry_date_error = True

                # re-rendering the application
                self.render_app()
            pass
        except Exception as message:
            print(f"Exception at upload file method {message}")

    # function to render files list
    def render_files_list(self, frame_option, parent_frame, row_index, col_index):
        # maximum fram column span
        frame_col_span = 6
        
        # creating a frame
        self.files_list_frame = customtkinter.CTkFrame(
            master=parent_frame,
            corner_radius=10,
            height=(self._height))

        self.files_list_frame.grid(
            row=row_index,
            column=col_index,
            columnspan=frame_col_span,
            sticky="nswe",
            padx=20,
            pady=20)

        # self.files_list_frame.grid_propagate(0)

        item_row = 0
        item_col = 0

        # fetching th width of the frame
        _width = self.files_list_frame['width']

        # calculating the no of columns that can fit into a single row
        _col_count = _width//100
        
        # getting the file count
        _files_count = len(self.selected_files)
        
        # deciding the col span of each item
        _col_span = frame_col_span // (3 if _files_count > 3 else _files_count)

        # if not frame_option == FrameOptions.View:

        # expanding the each item column grid
        self.files_list_frame.grid_columnconfigure(
            tuple(i for i in range(_col_count+1)), weight=1)

        # iterating over the selected files and rendering the items
        for (index, file_path) in enumerate(self.selected_files):

            if index and not index % _col_count:
                item_row += 1
                item_col = 0

            # render the file item
            self.render_file_item(
                frame_option, self.files_list_frame,
                file_path, item_row, item_col, _col_span)

            item_col += _col_span
        pass

    # function to render file item
    def render_file_item(self, item_mode, parent_frame, file_path, row_index, col_index, col_span=2):
        
        # extract file name from file path
        file_name = file_path.split("/")[-1]
        
        # creating a frame
        self.file_item_frame = customtkinter.CTkFrame(
            master=parent_frame,
            width=150,
            corner_radius=10)

        self.file_item_frame.grid(
            row=row_index,
            column=col_index,
            columnspan=col_span,
            sticky="we",
            padx=10,
            pady=10)

        self.file_item_frame.grid_columnconfigure(0, weight=1)

        self.file_item_frame.grid_rowconfigure(0, weight=0)

        _width = col_span * 7

        # creating a label
        self.file_name_label = customtkinter.CTkLabel(
            master=self.file_item_frame,
            text=(f"{file_name.strip()[:_width]}..." if len(
                file_name) > _width else file_name),
            text_font=("Roboto Medium", -20),
            corner_radius=8,
            height=10)

        self.file_name_label.grid(
            row=0,
            column=0,
            columnspan=1,
            pady=10,
            padx=10)

        if item_mode == FrameOptions.Send:
            # rendering a button
            self.render_flat_button(
                self.file_item_frame,
                "delete",
                0, 2,
                (lambda: self.remove_file(file_path)))

        elif item_mode == FrameOptions.Send or item_mode == FrameOptions.Receive:
            # rendering a button
            self.render_flat_button(
                self.file_item_frame,
                "download",
                0, 1,
                (lambda: self.download_file_from_server([file_name])))
        pass

    # function to download all the files listed
    def download_all_files(self):
        self.download_file_from_server(self.selected_files)
        pass

    # function to download files from the server
    def download_file_from_server(self, file_names):

        # creating gui params
        gui_params = {
            "storage_path": self.storage_path,
            "file_names": file_names
        }

        # send downloading command to the server
        (downloaded_location, error_message) = self.client_instance.execute_command(
            Option.DWLD, gui_params)
        
        # check for the error message
        if error_message:
            self.files_fetch_error = True
            
            self.error_message = error_message
            
            self.selected_files = []
            
            self.download_sucess = False
            
            self.downloaded_location = None

        # check for the downloaded location path
        elif downloaded_location:
            self.download_sucess = True
            
            self.downloaded_location = downloaded_location

        # re-rendering the application
        self.render_app()

    # function to delete files while uploading
    def remove_file(self, file_path):

        # removing the file path in the list of selected files
        self.selected_files.remove(file_path)
        
        print(f"Updated files:{self.selected_files}")
        
        # re-rendering the application
        self.render_app()
        
        pass

    # function to open dialog for uploading files
    def open_dialog(self, mode=None):

        # get the selected files list
        files = filedialog.askopenfilenames(
            title="select the files you want to upload", initialdir='/')
        
        if mode == "append":
            self.selected_files = list(
                set(self.selected_files + list(files)))[:6]
        
        else:
            self.selected_files = list(set(list(files)))[:6]
        
        print(self.selected_files)
        
        # re-rendering the application
        self.render_app()
        pass

    # function to render reusable flat button
    def render_flat_button(self, parent_frame, button_text, row_index, col_index, callback_action, position="se", disabled=False):
        
        # creating a button
        self.cancel_button = customtkinter.CTkButton(
            master=parent_frame,
            text=button_text,
            width=100,
            height=50,
            text_font=("Roboto Medium", -18),
            corner_radius=10,
            state="normal" if not disabled else "disabled",
            command=callback_action)

        self.cancel_button.grid(row=row_index, column=col_index, columnspan=1,
                                padx=20, pady=20, sticky=position)

    # function to render receive frame
    def render_receive_frame(self):

        # check for the error messages or download success message
        if self.files_fetch_error or (self.download_sucess and self.downloaded_location):
            # self.main_frame.grid_rowconfigure(0, weight=1)

            # creating a frame
            self.receive_frame = customtkinter.CTkFrame(
                master=self.main_frame,
                corner_radius=10,
                height=(0.4*(self._height)))

            self.receive_frame.grid(
                row=1,
                column=0,
                columnspan=3,
                sticky="nswe",
                padx=20,
                pady=20)

            self.receive_frame.grid_columnconfigure(0, weight=1)

            self.receive_frame.grid_rowconfigure(0, weight=1)

            # check for error message
            if self.files_fetch_error:
                self.render_success_frame(
                    f"{self.error_message}",
                    self.receive_frame, FrameOptions.Error)

            # render success message
            else:
                self.render_success_frame(
                    f"Files download successful :  {self.downloaded_location}",
                    self.receive_frame, FrameOptions.Receive)

                # rendering cancel button
                self.render_flat_button(
                    self.main_frame,
                    "cancel",
                    2,
                    1,
                    (lambda: self.button_clicked(None))
                )

        elif self.storage_path:
            # self.main_frame.grid_rowconfigure(index)

            # rendering files in storage path
            self.render_files_in_storage_path(
                FrameOptions.Receive,
                "Download files in the given storage path",
                self.main_frame, 1, 0)

        else:
            # rendering input prompt for the storage path
            self.render_storage_path_input_frame(
                FrameOptions.Receive,
                "Download files in the given storage path",
                self.main_frame, 1, 0)
        pass

    # function to render files in the storage path
    def render_files_in_storage_path(self, frame_option, title_label, parent_frame, row_index, col_index):
        
        # creating a frame
        self.view_frame = customtkinter.CTkFrame(
            master=parent_frame,
            corner_radius=10,
            height=(0.4*(self._height)))

        self.view_frame.grid(
            row=row_index,
            column=col_index,
            columnspan=2,
            sticky="nswe",
            padx=20,
            pady=20)

        self.view_frame.grid_columnconfigure(0, weight=1)
        
        self.view_frame.grid_rowconfigure(1, weight=1)

        # rendering frame title header
        self.render_frame_header(title_label, self.view_frame)

        # rendering files list frame
        self.render_files_list(frame_option, self.view_frame, 1, 0)

        if frame_option == FrameOptions.Receive:
            # rendering download all files button
            self.render_flat_button(
                parent_frame,
                "download all files",
                2,
                0,
                (lambda: self.download_all_files())
            )

        # rendering cancel button
        self.render_flat_button(
            parent_frame,
            "cancel",
            2,
            1,
            (lambda: self.button_clicked(None))
        )

        pass

    # function to render view frame
    def render_view_frame(self):

        # check for the error message
        if self.files_fetch_error:

            # self.main_frame.grid_rowconfigure(0, weight=1)
            
            # creating a frame
            self.temp_frame = customtkinter.CTkFrame(
                master=self.main_frame,
                corner_radius=10,
                height=(0.4*(self._height)))

            self.temp_frame.grid(
                row=1,
                column=0,
                columnspan=3,
                sticky="nswe",
                padx=20,
                pady=20)

            self.temp_frame.grid_columnconfigure(0, weight=1)

            self.temp_frame.grid_rowconfigure(0, weight=1)

            # rendering success frame
            self.render_success_frame(
                f"{self.error_message}",
                self.temp_frame, FrameOptions.Error)

        elif self.storage_path:
            title_label = f"files in the storage path :  {self.storage_path}"
            
            # rendering files in storage path frame
            self.render_files_in_storage_path(
                FrameOptions.View,
                title_label,
                self.main_frame, 1, 0)

        else:
            title_label = f"View files in the storage path"

            # rendering storage path input frame
            self.render_storage_path_input_frame(
                FrameOptions.View,
                title_label,
                self.main_frame, 1, 0)
        pass

    # function to render frame header
    def render_frame_header(self, frame_title_label, parent_frame):

        # creating frame
        self.view_frame_header = customtkinter.CTkFrame(
            master=parent_frame,
            corner_radius=10,
            height=(0.4*(self._height)))

        self.view_frame_header.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="nswe",
            padx=20,
            pady=20)

        self.view_frame_header.grid_columnconfigure(0, weight=1)

        # creating a label
        self.text_label = customtkinter.CTkLabel(
            master=self.view_frame_header,
            text=frame_title_label,
            text_font=("Roboto Medium", -20),
            corner_radius=8,
            height=10)

        self.text_label.grid(
            row=0,
            column=0,
            pady=20,
            padx=20,
            sticky="we")

    # function to render storage path input frame
    def render_storage_path_input_frame(self, frame_option, frame_title_label, parent_frame, row_index, col_index):
        
        # creating a frame
        self.view_frame = customtkinter.CTkFrame(
            master=parent_frame,
            corner_radius=10,
            height=(0.4*(self._height)))

        self.view_frame.grid(
            row=row_index,
            column=col_index,
            columnspan=2,
            sticky="nswe",
            padx=20,
            pady=20)

        self.view_frame.grid_columnconfigure(0, weight=1)
        self.view_frame.grid_rowconfigure(1, weight=1)

        # rendering a frame header
        self.render_frame_header(frame_title_label, self.view_frame)

        # creating a frame
        self.view_frame_body = customtkinter.CTkFrame(
            master=self.view_frame,
            corner_radius=10,
            height=(0.4*(self._height)))

        self.view_frame_body.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="nswe",
            padx=20,
            pady=20)

        self.view_frame_body.grid_columnconfigure(0, weight=1)
        
        self.view_frame_body.grid_rowconfigure(0, weight=1)

        # creating a text field
        self.entry = customtkinter.CTkEntry(
            master=self.view_frame_body,
            placeholder_text=f"Enter Storage Path",
            width=120,
            height=50,
            border_width=2,
            corner_radius=10)

        self.entry.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=20,
            pady=20,
            sticky="we")

        # rendering a get files button
        self.render_flat_button(
            self.view_frame_body,
            "get files",
            1,
            0,
            (lambda: self.fetch_files_from_server(
                self.entry.get(), frame_option))
        )

        # rendering cancel button
        self.render_flat_button(
            self.view_frame_body,
            "cancel",
            1,
            1,
            (lambda: self.button_clicked(None))
        )

    # function to render homepage
    def render_menu_options_frame(self):

        # creating a frame
        self.frame_bottom = customtkinter.CTkFrame(
            master=self.main_frame,
            corner_radius=10,

            height=(0.4*(self._height)))

        self.frame_bottom.grid(
            row=1, column=0, columnspan=2,
            sticky="nswe", padx=20, pady=20)

        self.frame_bottom.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.frame_bottom.grid_rowconfigure(0, weight=1)

        # loading image icons
        self.add_folder_image = self.load_image("/images/add-folder.png", 100)
        
        self.download_image = self.load_image("/images/download1.png", 100)
        
        self.view_image = self.load_image("/images/view.png", 100)

        # creating upload files button
        self.button_1 = customtkinter.CTkButton(
            master=self.frame_bottom,
            image=self.add_folder_image,
            text="Upload files",
            width=300,
            text_font=("Roboto Medium", -18),
            corner_radius=10,
            compound="top",
            state=("normal" if self.ip_address and self.port_number else "disabled"),
            command=(lambda: self.button_clicked(FrameOptions.Send))
        )

        self.button_1.grid(
            row=0, column=0, columnspan=1,
            padx=20, pady=20, sticky="nsew")

        # creating view files button
        self.button_2 = customtkinter.CTkButton(
            master=self.frame_bottom,
            image=self.view_image,
            text="View Files",
            width=300,
            text_font=("Roboto Medium", -18),
            corner_radius=10,
            compound="top",
            state=("normal" if self.ip_address and self.port_number else "disabled"),
            command=(lambda: self.button_clicked(FrameOptions.View))
        )

        self.button_2.grid(
            row=0, column=1, columnspan=1,
            padx=20, pady=20, sticky="nsew")

        # creating download files button
        self.button_3 = customtkinter.CTkButton(
            master=self.frame_bottom,
            image=self.download_image,
            text="Download Files",
            width=300,
            text_font=("Roboto Medium", -18),
            corner_radius=10,
            compound="top",
            state=("normal" if self.ip_address and self.port_number else "disabled"),
            command=(lambda: self.button_clicked(FrameOptions.Receive))
        )

        self.button_3.grid(
            row=0,
            column=2,
            columnspan=1,
            padx=20,
            pady=20,
            sticky="nsew")

    # button click event callback
    def button_clicked(self, option):
        
        # print(f"{option} clicked")
        
        if option == None:
            # if option is None, reset all params
            self.storage_path = None
            
            self.selected_files = []
            
            self.clipboard_text = None
            
            self.files_uploaded_success = False
            
            self.download_sucess = False
            
            self.downloaded_location = None
            
            self.expiry_date_error = False
            
            self.files_fetch_error = False
            
            self.error_message = None
        
        self.selected_frame_option = option
        
        # re-rendering the application
        self.render_app()

    # function to update the theme
    def change_appearance_mode(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def on_closing(self, event=0):
        self.destroy()

    # fuction to load image
    def load_image(self, path, image_size):
        # load rectangular image with path relative to PATH
        return ImageTk.PhotoImage(Image.open(PATH + path).resize((image_size, image_size)))


if __name__ == "__main__":
    # creating ClientGUI instance
    app = ClientGUI()

    # running the application
    app.mainloop()
