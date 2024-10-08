import socket
import threading
import gzip
from os import getcwd
from sys import platform

from datetime import datetime

HTTP = "HTTP/1.1"

# NOTE PATH DEFINITIONS

STATUS_NOT_FOUND = "HTTP/1.1 404 Not Found\r\n\r\n"
# WARNINGthe server runs in a folder where the code is placed
# specifiying the directory you will have to place there all of the folders like "info", "files", "templates"
# in order for the server to function properly
LOGS_FILE_PATH = "./info/logs.txt"

# TEMPLATE_PATH = f"./templates/"
TEMPLATE_PATH = f"templates/"

FILE_PATH = "/files/"
DOWNLOADS_PATH = f"{FILE_PATH}downloads/"
TEMPLATE_FILE_NAME = "__code-frame"

ERROR_FILE_NOT_FOUND = "ERROR_FILE_NOT_FOUND"

# Print Working Directory, this variable stores the path to the folder where the server operates
PWD = getcwd() + "/"

CODE_EXTENSIONS = ["c", "cpp", "py", "js", "html", "css", "jsx"]

# Words used in the template html to replace them with the contents
INSERT_CODE_HERE_WORD = "---CODE---"
INSERT_FILE_NAME_HERE_WORD = "---FILE_NAME---"
INSERT_SERVER_IP_HERE_WORD = "---SERVER_IP---"


STATUS = {
    200: "OK",
    201: "Created",
    404: "Not Found",
    401: "Unauthorized"
}

# Initializing the logs file
with open(LOGS_FILE_PATH, "a") as fp:
    pass

def read_file_at_path(file_path):
    try:
        with open(file_path, 'r') as file:
            log(f"[V] Sucesfully found file at path {file_path}")
            file_content = file.read()
            file.close()

            return file_content
    except:
        return ERROR_FILE_NOT_FOUND


def log(text):
    log_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open(LOGS_FILE_PATH, 'a') as log_file:
        log_file.write(f"[ {log_time} ]: {text}\n")

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('192.255.255.255', 1))
        IP = s.getsockname()[0] # getting from the tuple (IP, PORT) the IP
    except:
        IP = '127.0.0.1'  # fallback to localhost if necessary
    finally:
        s.close()
    return IP

def main():
    can_reuse_port = True
    which_os = platform

    if "win" in which_os.lower():
        can_reuse_port = False

    print(f"\n[0] Using {which_os}.")
    log(f"\n\n[0] Using {which_os}.\n\n")


    # is_in_whitelist_mode = True

    IP = get_local_ip()
    PORT = 4221
    handled_connections = 0
    if can_reuse_port:
        server_socket = socket.create_server((IP,PORT), reuse_port=True)
    else:
        server_socket = socket.create_server((IP,PORT))

    print(f"\n[*] Listening on {IP}:{PORT}...\n\n")
    log(f"[*] Listening on {IP}:{PORT}...")

    try:
        while True:
            connection, address = server_socket.accept()

            log(f"[*] Connection accepted from {address[0]}")

            ip_address = address[0]

            thread = threading.Thread(target=handle_connections, args=(connection,address))
            print(f"[v] Thread started for {ip_address}")
            thread.start()

            handled_connections += 1
            # print(f"\n[H] Connections handled: {handled_connections}\n\n")
    except KeyboardInterrupt:
        log("[X] Server is shutting down")
        print("\n[X] Server is shutting down")
        log(f"[X] Handled connections: {handled_connections}")
        print("Handled connections: ", handled_connections)




class Request:
    def __init__(self):
        self.protocol = HTTP
        self.method = "GET"
        self.path = None
        self.headers = None
        self.body = ""

    def get_header_value(self, header_name: str):
        try:
            return self.headers[header_name]
        except:
            return None

    def get_encodings(self) -> list:
        encodings = self.get_header_value("Accept-Encoding")

        if encodings == None:
            return list()
        else:
            return map(lambda s: s.strip(), encodings.split(','))

    def try_from_string(self, request: str):
        lines = request.split('\r\n')
        method, path, protocol = lines[0].split(' ')
        body = lines[-1]

        header_cnt = 0
        for i in lines:
            if i.find(": ") != -1:
                header_cnt += 1

        headers = {}
        # the first line is method, path, protocol
        # the last line is body

        # other lines in between first
        for i in range(header_cnt):
            header_name = lines[i+1].split(': ')[0]
            header_value = lines[i+1].split(": ")[1]

            headers.update({header_name: header_value})


        self.path = path
        self.method = method
        self.headers = headers
        self.body = body

        return self

def insert_content(assembled_file, content_to_insert, replace_word):
    assembled_file = assembled_file.replace(replace_word, content_to_insert)
    return assembled_file

class Response:
    def __init__(self, supported_encodings = ["gzip"]):
        self.protocol = HTTP
        self.status_code = 200
        self.body = ""
        self.headers = {} # dict
        self.supported_encodings = supported_encodings
        self.body_encoding = None


    def with_header(self, header_name, header_value):
        self.headers.update({header_name: header_value})
        return self


    def with_protocol(self, protocol):
        self.protocol = protocol
        return self

    def with_content_type(self, content_type):
        self.with_header("Content-Type", content_type)
        return self

    def with_body(self, body):
        if body == None:
            self.body = ""
        else:
            self.body = body
        return self

    def with_encoding(self, list_of_encodings):
        for encoding in list_of_encodings:
            if encoding in self.supported_encodings:
                self.with_header("Content-Encoding", encoding)
                self.body_encoding = encoding
                break

        return self

    def encode_body(self):
        if self.body_encoding == "gzip":
            gzipped_data = gzip.compress(self.body.encode())
            self.body = gzipped_data


        return self

    def with_status_code(self, code):
        self.status_code = code
        return self

    def build(self):
        if not(self.body_encoding == None):
            self = self.encode_body()

        self.with_header("Content-Length", len(self.body))

        headers = map(lambda kv: f'{kv[0]}: {kv[1]}\r\n', self.headers.items())
        headers = ''.join(headers)

        if not(self.body_encoding == None):
            response = f"{self.protocol} {self.status_code} {STATUS[self.status_code]}\r\n{headers}\r\n".encode()
            response += self.body
            return response
        else:
            response = f"{self.protocol} {self.status_code} {STATUS[self.status_code]}\r\n{headers}\r\n{self.body}"
            return response.encode()


def handle_connections(connection: socket.socket, address):
    CLIENT_IP = address[0]

    # getting the request and reading it
    request = Request().try_from_string(connection.recv(1024).decode())

    target_request = request.path
    response = ''
    protocol = request.protocol

    encodings = request.get_encodings()

    # print(f"\n[R] {CLIENT_IP} requested {target_request}")
    # log(f"[R] {CLIENT_IP} requested {target_request}")

    file_content = read_file_at_path(f"{PWD}{request.path[1:]}")
    # request splitted to know the file name and its path
    is_code = False
    file_extension = request.path.split("/")[-1].split(".")[-1].lower()
    if  file_extension in CODE_EXTENSIONS:
        # in the if I'm getting the extension without dot, like "css" and not ".css"
        is_code = True


    # '**' before the request says that it will be a command and not a file path
    if request.path.startswith("/**echo/"):
        echo = request.path[len("/**echo/"):]
        response = Response().with_content_type("text/plain").with_body(echo).with_status_code(200).with_encoding(encodings).build()

        print(f"\n[R] {CLIENT_IP} ECHO {echo}")
        log(f"[R] {CLIENT_IP} ECHO {echo}")


    # if the requested file exists and it is code and ITS NOT A TEMPLATE FILE
    elif is_code and (not file_content.startswith(ERROR_FILE_NOT_FOUND)) and (not TEMPLATE_FILE_NAME in request.path):
        # Insert the code file contents in the template html

        print(f"\n[R] {CLIENT_IP} requested {request.path}")
        log(f"[R] {CLIENT_IP} requested {request.path}")

        template_html_path = f"{TEMPLATE_PATH}{TEMPLATE_FILE_NAME}.html"

        template_html = read_file_at_path(template_html_path)
        # inserting code in html
        template_html = insert_content(template_html, file_content, "---CODE---")
        # inserting file name in html
        template_html = insert_content(template_html, request.path.split("/")[-1], INSERT_FILE_NAME_HERE_WORD)
        # inserting server's IP
        template_html = insert_content(template_html, get_local_ip(), INSERT_SERVER_IP_HERE_WORD)

        # print(html_to_send, "HTML TO SEND")

        response = Response().with_content_type("text/html").with_body(template_html).build()

    elif TEMPLATE_FILE_NAME in request.path and (not "html" in request.path):
        # if it is a template file


        template_file_extension = request.path.split(".")[-1].lower()
        print(f"\n[R] {CLIENT_IP} requested TEMPLATE {TEMPLATE_FILE_NAME}.{template_file_extension}")
        log(f"[R] {CLIENT_IP} requested {TEMPLATE_FILE_NAME}.{template_file_extension}")

        if template_file_extension == "js":
            response = Response().with_content_type("text/javascript").with_body(read_file_at_path(f"{TEMPLATE_PATH}{TEMPLATE_FILE_NAME}.{template_file_extension}")).build()
        elif template_file_extension == "css":
            response = Response().with_content_type("text/css").with_body(read_file_at_path(f"{TEMPLATE_PATH}{TEMPLATE_FILE_NAME}.{template_file_extension}")).build()

    elif request.path.startswith("/"):
        # if the requeseted file isn't a file with a code extension, then send it as a application/octet-stream
        print(f"\n[R] {CLIENT_IP} DOWNLOAD {request.path}")
        log(f"[R] {CLIENT_IP} DOWNLOAD {request.path}")

        if file_content.startswith(ERROR_FILE_NOT_FOUND):
            response = Response().with_status_code(404).build()
            log(f"[X] {CLIENT_IP} HTTP 404 Not Found file at path {request.path}")
            print(f"[X] {CLIENT_IP} HTTP 404 Not Found file at path {request.path}")
        else:
            response = Response().with_content_type("application/octet-stream").with_body(file_content).build()

    else:
        response = Response().with_status_code(404).build()
        log(f"[X] {CLIENT_IP} HTTP 404 Not Found ")

    connection.sendall(response)
    log(f"[C] {CLIENT_IP} connection closed. \n\n")
    connection.close()


if __name__ == "__main__":
    main()
