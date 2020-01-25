#  coding: utf-8 
import socketserver

from http import HTTPStatus
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()

        # Parse client headers
        headers = [header.split(" ") for header in self.data.decode().split("\r\n")]

        self.method = headers[0][0]
        self.path = headers[0][1]
        self.protocol = headers[0][2]

        # Only accept GET methods
        if (self.method == "GET"):
            # Default status, may get replaced
            statusCode = HTTPStatus.OK

            # Builds path requested by client, ignoring redundant separators and up-level references
            BASEPATH = os.getcwd() + "/www"
            requestedPath = os.path.normpath(BASEPATH + self.path)
            
            print(self.path)
            print(requestedPath)

            # Path given is correct directory but missing /, add /
            if (os.path.isdir(requestedPath) and requestedPath[-1] != "/"):
                requestedPath += "/"
                statusCode = HTTPStatus.MOVED_PERMANENTLY
            
            print(self.path)
            print(requestedPath)

            # Return index.html for paths that end in "/" and index.html exist
            if (requestedPath[-1] == "/" and os.path.isfile(requestedPath + "index.html")):
                self.path += "index.html"
                requestedPath += "index.html"
                statusCode = HTTPStatus.MOVED_PERMANENTLY

            print(self.path)
            print(requestedPath)

            # Check if requested path is a file
            if (os.path.isfile(requestedPath)):
                # File Found
                content = open(requestedPath, "r").read()
                self.sendRequest(statusCode, content)

            else:
                # No File Found
                statusCode = HTTPStatus.NOT_FOUND
                content = open("./templates/404.html", "r").read()
                self.sendRequest(statusCode, content)
        else:
            statusCode = HTTPStatus.METHOD_NOT_ALLOWED
            content = open("./templates/405.html", "r").read()
            self.sendRequest(statusCode, "")

    def getMimeType(self):
        _, fileExt = os.path.splitext(self.path)

        if (fileExt.upper() == ".HTML"):
            return "Content-Type: text/html\r\n"
        elif (fileExt.upper() == ".CSS"):
            return "Content-Type: text/css\r\n"
        else:
            return "Content-Type: text/html\r\n"

    def sendRequest(self, statusCode, content):
        # Default Response
        tempContent = open("./templates/501.html", "r").read()
        response = self.protocol + "501 Not Implemented\r\n" + self.getMimeType() + tempContent + "\r\n\r\n"
        
        if (statusCode == HTTPStatus.OK):
            print("200")
            response = self.protocol + "200 OK\r\n" + self.getMimeType() + content + "\r\n\r\n"
        elif (statusCode == HTTPStatus.MOVED_PERMANENTLY):
            print("301")
            response = self.protocol + "301 Moved Permanently\r\n" + self.getMimeType() + "Location: " + self.path + "\r\n\r\n"
        elif (statusCode == HTTPStatus.NOT_FOUND):
            print("404")
            response = self.protocol + "404 Not Found\r\n" + self.getMimeType() + content + "\r\n\r\n"
        elif (statusCode == HTTPStatus.METHOD_NOT_ALLOWED):
            print("405")
            response = self.protocol + "405 Method Not Allowed\r\n" + self.getMimeType() + content + "\r\n\r\n"

        self.request.sendall(bytearray(response, 'utf-8'))
        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
