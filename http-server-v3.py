import socket
import sys
import argparse
import threading
import gzip

from datetime import datetime

HTTP = "HTTP/1.1"

# NOTE PATH DEFINITIONS

STATUS_NOT_FOUND = "HTTP/1.1 404 Not Found\r\n\r\n"

# argv[2] takes the second argument of the command line: ./your_server.sh --directory /tmp/
# ./your_server.sh is argument N0, so /tmp/ is N2 since indexing starts with 0
# if there are more than 2 arguments, there is a path in the command line

# FILE_PATH = sys.argv[2] if len(sys.argv) > 2 else f"./files/"
FILE_PATH = "./files/"

# WARNINGthe server runs in a folder where the code is placed
# specifiying the directory you will have to place there all of the folders like "info", "files", "templates" 
# in order for the server to function properly
LOGS_FILE_PATH = "./info/logs.txt"

CODE_PATH = f"{FILE_PATH}files-code/"
TEMPLATE_PATH = f"./templates/"
FAVICON_PATH = f".{TEMPLATE_PATH}favicon.ico"
DOWNLOADS_PATH = f"{FILE_PATH}downloads/"
TEMPLATE_FILE_NAME = "code-frame"

print(FILE_PATH)
print(CODE_PATH)
print(TEMPLATE_PATH)
print(FAVICON_PATH)
print(DOWNLOADS_PATH)
print(FILE_PATH)


STATUS = {
    200: "OK",
    201: "Created",
    404: "Not Found",
    401: "Unauthorized"
}

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
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")
    can_reuse_port = True
    which_os = "none" # DON NOT FORGET AFTER DEBUG TO SWITCH IT TO NONE
    # check for slash symbol used in path
    while not(which_os == "linux" or which_os == "windows"):
        which_os = input("[0] Enter FULL name of the OS you are using.\n")
    if which_os.lower() == "windows":
        can_reuse_port = False
    print(f"\n[0] Using {which_os}.")
    log(f"[0] Using {which_os}.\n\n")

    # IP = "localhost"

    # is_in_whitelist_mode = True

    IP = get_local_ip()
    PORT = 4221
    handled_connections = 0
    if can_reuse_port:
        server_socket = socket.create_server((IP,PORT), reuse_port=True)
    else:
        server_socket = socket.create_server((IP,PORT))
    # server_socket.accept() # wait for client
    print(f"\n[*] Listening on {IP}:{PORT}...\n\n")
    log(f"[*] Listening on {IP}:{PORT}...")

    try:
        while True:
            connection, address = server_socket.accept()
            print(f"[*] Connection accepted from {address[0]}:{address[1]}")
            log(f"[*] Connection accepted from {address[0]}")

            ip_address = address[0]

            thread = threading.Thread(target=handle_connections, args=(connection,address))
            print(f"[v] Thread started for {ip_address}")
            thread.start()

            handled_connections += 1
            # print(f"\n[H] Connections handled: {handled_connections}\n\n")
    except KeyboardInterrupt:
        log("\n[X] Server is shutting down")
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
        # print(f"FROM PARSE_FROM_STRING lines are: {lines}")

        return self

def insert_content(assembled_file, code, replace_word):
    assembled_file = assembled_file.replace(replace_word, code)
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

    print(f"\n[R] {CLIENT_IP} requested {target_request}")
    log(f"[R] {CLIENT_IP} requested {target_request}")




    if request.path == '/':
        response = Response().with_content_type("text/plain").build()

    elif request.path.startswith("/echo/"):
        echo = request.path[len("/echo/"):]
        response = Response().with_content_type("text/plain").with_body(echo).with_status_code(200).with_encoding(encodings).build()

    # elif request.path == '/user-agent':
    #     response = Response().with_content_type("text/plain").with_body(request.headers["User-Agent"]).with_encoding(encodings).build()

    elif request.path.startswith("/code/"):
        code = None
        file_name = target_request[len("/code/"):]
        file_name = file_name.split('.')[0]
        # print(f"filename: {file_name}")

        extensions = [".html", ".css", ".js"]

        if request.path.endswith("code/favicon.ico") and request.method == "GET":

                    try:
                        with open(FAVICON_PATH) as file:
                            favicon = file.read()
                            file.close()

                            print("favicon", favicon)
                            response = Response().with_content_type("image/x-icon").with_body(favicon).build()
                            
                    except:
                        response = Response().with_status_code(404).build()
                        log(f"{CLIENT_IP} HTTP 404 Not Found")
        elif request.method == "GET":
            # if request.method.endswith()

            # dict of files content like html, css, js
            files = {
                "html": None,
                "css": None,
                "js": None,
            }

            # check if they exist
            for i in range(len(extensions)):
                try:
                    with open(f"{TEMPLATE_PATH}{TEMPLATE_FILE_NAME}{extensions[i]}") as file:
                        file_content = file.read()
                        # print("[V] Found", extensions[i], "file")

                        # files.append(file_content)
                        files[extensions[i][1:]] = file_content
                except:
                    print("error in", extensions[i])

            # read code file if sucessful
            try:
                with open(f"{CODE_PATH}{file_name}.txt") as file:
                    code = file.read()
                    file.close()
            except:
                print(f"[x] File {file_name}.txt NOT FOUND")

                log(f"[X] {CLIENT_IP} File {file_name} HTTP 404 Not Found in CODE-FILES")
                response = Response().with_status_code(404).build()


            # print(request.path[len(request.path.split(".")[0]):]) #check if the file extension is js or css

            # if code sucessfully read, see if the brower requested css, js
            if request.path.startswith(f"/code/{TEMPLATE_FILE_NAME}") and request.path[len(request.path.split(".")[0]):] in extensions:
                # print(f"[B] BROWSER REQUESTED: {request.path}")

                file_extension = request.path[len(request.path.split(".")[0]):]
                if files["css"] != None and file_extension == ".css":
                    with open(f"{TEMPLATE_PATH}{TEMPLATE_FILE_NAME}.css") as file:
                        response = Response().with_content_type("text/css").with_body(files["css"]).build()
                        # print("sent css file")

                elif files["js"] != None and file_extension == ".js":
                    with open(f"{TEMPLATE_PATH}{TEMPLATE_FILE_NAME}.js") as file:
                        response = Response().with_content_type("application/javascript").with_body(files["js"]).build()
                        # print("sent js file")
            else:

                if files["html"] != None and code != None:
                    assembled_file = files["html"]
                    # these ---VARIABLE---  serves the purpose of variables and they are hardcoded in the HTML, like fstrings
                    assembled_file = insert_content(assembled_file, code, "---CODE---")
                    assembled_file = insert_content(assembled_file, file_name, "---FILE_NAME---")
                    assembled_file = insert_content(assembled_file, get_local_ip(), "---SERVER_IP---")
                    response = Response().with_content_type("text/html").with_body(assembled_file).build()
                else:
                    response = Response().with_status_code(404).build()



    elif request.path.startswith("/download/"):
        file_name = target_request[len("/download/"):]
        # NOTE that file_name must have the file's extension

        # if i search for a file in a folder that is in ./files, i might get an error on Windows
        if request.method == "GET":
            try:
                with open(f"{DOWNLOADS_PATH}{file_name}", 'r') as file:
                    file_content = file.read()
                    file.close()
                    # print(file_content)
#
                    # response = create_response(status_code_ok, status_message, "application/octet-stream", file_content)
                    response = Response().with_content_type("application/octet-stream").with_body(file_content).build()
                    # also send a nice html to tell that the download was succesful
            except:
                response = Response().with_status_code(404).build()
                log(f"[X] {CLIENT_IP} File {file_name} HTTP 404 Not Found in DOWNLOADS")
#
        elif request.method == "POST":
            log(f"[P] {CLIENT_IP} POST {file_name}")
            print(f"FILE PATH IS: {DOWNLOADS_PATH}{file_name}")
            create_file(f"{DOWNLOADS_PATH}{file_name}", request.body)
            response = Response().with_status_code(201).build()

    # OLD PIECE OF CODE, needs to be refactored
    # elif request.path.startswith("/files/"):
    #     file_name = target_request[len("/files/"):]

    #     # if i search for a file in a folder that is in ./files, i might get an error on Windows
    #     if request.method == "GET":
    #         try:
    #             with open(f"{FILE_PATH}{file_name}", 'r') as file:
    #                 # file_content = file.read()
    #                 file_name_no_extension = file_name.split(".")[0]
    #                 file_content = stich_to_html(file_name_no_extension, "./templates/")
    #                 # print(file_content)

    #                 # response = create_response(status_code_ok, status_message, "application/octet-stream", file_content)
    #                 if (file_name.endswith(".html")):
    #                     response = Response().with_content_type("text/html").with_body(file_content).build()
    #                     print("sent a html file")
    #                 else:
    #                     response = Response().with_content_type("application/octet-stream").with_body(file_content).build()
    #         except:
    #             response = Response().with_status_code(404).build()

    #     elif request.method == "POST":
    #         print(f"FILE PATH IS: {FILE_PATH}{file_name}")
    #         create_file(f"{FILE_PATH}{file_name}", request.body)
    #         response = Response().with_status_code(201).build()

    # elif request.path.startswith("/favicon.ico"):
    #     response = Response().with_content_type("")
    else:
        response = Response().with_status_code(404).build()
        log(f"[X] {CLIENT_IP} HTTP 404 Not Found ")

    connection.sendall(response)
    log(f"[C] {CLIENT_IP} connection closed. \n\n")
    connection.close()


def create_file(FILE_PATH: str, file_content):
    new_file = open(FILE_PATH, "w")
    new_file.write(file_content)
    # new_file.close() 'with' will automatically close the file in Py v3.x


if __name__ == "__main__":
    main()
