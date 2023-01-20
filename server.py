#  coding: utf-8 
import socketserver
import re
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Richmond Naviza
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

"""
Extra Sources:
https://docs.python.org/3/library/socketserver.html
https://docs.python.org/3/library/os.path.html
https://docs.python.org/3/library/re.html?highlight=re#module-re
Some minor code snippets were copied from the lab demo
"""

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        data_list = re.split(' |\\r|\\n', self.data.decode("utf-8"))
        request_type = data_list[0]
        file_requested = data_list[1]

        # Post/Put/Delete is not allowed
        if request_type in ["POST", "PUT", "DELETE"]:
            self.request.sendall("HTTP/1.1 405 Method Not Allowed\r\n".encode('utf-8'))
            return
        
        # Check if it's a folder
        if os.path.isdir("./www" + file_requested):
            # Missing the "/" at the end of the request (and not /)
            if file_requested != "/" and file_requested[-1] != "/":
                # I copied this syntax from the response from "curl google.com"
                self.request.sendall(("HTTP/1.1 301 Moved Permanently\r\nLocation: "+file_requested+"/\r\n").encode('utf-8'))
                return
            # Check if the file actually exists in the ./www
            if not file_requested.endswith("index.html"):
                file_requested += "index.html"

        file_requested = os.path.abspath("./www" + file_requested)
        # If the file does not exist or not inside the .www/ subfolder
        if not os.path.isfile(file_requested) or \
            not file_requested.startswith(os.path.abspath("./www")):
            self.request.sendall(("HTTP/1.1 404 File not found\r\n").encode('utf-8'))
            return

        content_type = "html" if file_requested.__contains__("html") else "css"

        with open(file_requested, 'r') as file:
            # Just for the formal HTTP Response
            header = "HTTP/1.1 200 OK\r\nContent-Type: text/" + content_type +  "; charset=utf-8\r\n"
            data = file.read().encode('utf-8')
            header += ("Content-Length: " + str(len(data)) + "\r\n\r\n")
            self.request.sendall(header.encode('utf-8') + data)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print("Starting the server")
    server.serve_forever()
