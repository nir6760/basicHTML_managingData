import socket
import os
import string
import hw1_utils
import HTTPHandler
import time


"""
 Implements a simple HTTP/1.0 Server

"""
# Define socket host and port
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8888
NUM_BYTES_REQUEST = 4096

#create error html string
def create_error_html(error_num):
    error_html = "<html>\n\
                <head>\n\
                    <title>" + str(error_num) + " error</title>\n\
                </head>\n\
                <body>\n\
                <h1>" + str(error_num) + " ERROR </h1>\n\
                 </br></br>\n\
                <button onclick=\"home_red()\">Main Page</button>\n\
                <script>\n\
                    function home_red() {\n\
                    window.location.assign(\"http://localhost:8888\")\n\
                }\n\
                </script >\n\
                </body>\n\
                </html>"
    return error_html

def make_http_time_string(time_struct):

    '''Input struct_time and output HTTP header-type time string'''

    return time.strftime('%a, %d %b %Y %H:%M:%S GMT',

            time_struct)

# handle request method
def handle_request(request):

    http = HTTPHandler.HTTPHandler
    # Parse headers
    print(request)
    # Parse HTTP headers
    dict = hw1_utils.decode_http(request)
    # print("******************************************************************************")
    # for k, v in dict.items():
    #     print(k, " ------- ", v)
    # print("******************************************************************************")
    type_content = dict['Accept'].split('/')
    try:
        # Filename
        req_list = dict['Request'].split()
        filename = req_list[1]

        if req_list[0] == "GET":
            content = http.get(None, filename, type_content[0])
            return 200, content
        else:
            content = create_error_html(501)
            return 501, content
    except FileNotFoundError:
        with open('html_pages/not_found_page.html') as not_found_file:
            not_found_content = not_found_file.read()
        return 404, not_found_content


if __name__ == "__main__":
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(('localhost', 8888))
            server_socket.settimeout(None)
            server_socket.listen(1)
            print('Listening on port %s ...' % SERVER_PORT)
            # Wait for client connections
            client_connection, addr = server_socket.accept()
            with client_connection:
                # Get the client request
                request = client_connection.recv(NUM_BYTES_REQUEST)
                if not request or request== "\r\n".encode():
                    continue
                try:
                    status, content = handle_request(request)
                    # Send HTTP response
                    if status == 200:
                        if content:
                            if str(content).find("html") > 0:
                                # Send HTTP response
                                client_connection.sendall('HTTP/1.1 200 OK\r\n'.encode())
                                client_connection.sendall(("Date: " + make_http_time_string(time.localtime())
                                                          + "\r\n").encode())
                                client_connection.sendall("Content-Type: text/html\r\n\r\n".encode())
                                client_connection.sendall(content.encode())
                            else:  # image
                                # Send HTTP response
                                client_connection.sendall('HTTP/1.1 200 OK\r\n'.encode())
                                client_connection.sendall(("Date: " + make_http_time_string(time.localtime())
                                                           + "\r\n").encode())
                                client_connection.sendall("Content-Type: image/png\r\n".encode())
                                client_connection.sendall("Accept-Ranges: bytes\r\n\r\n".encode())
                                client_connection.sendall(content) #allready in bytes
                        else:
                            client_connection.sendall(('HTTP/1.1 500'+' Internal Server Error\r\n').encode())
                            client_connection.sendall(("Date: " + make_http_time_string(time.localtime())
                                                       + "\r\n").encode())
                            client_connection.sendall("Content-Type: text/html\r\n\r\n".encode())
                            client_connection.sendall(create_error_html(500).encode())
                    else:  # 404 or 501
                        err_str = ' NOT FOUND\r\n' if status==404 else ' NOT GET\r\n'
                        client_connection.sendall(
                            ('HTTP/1.1 ' + str(status) + err_str).encode())
                        client_connection.sendall(("Date: " + make_http_time_string(time.localtime())
                                                   + "\r\n").encode())
                        client_connection.sendall("Content-Type: text/html\r\n\r\n".encode())
                        client_connection.sendall(content.encode())
                except Exception as e:# 500
                    print(e)
                    client_connection.sendall(('HTTP/1.1 500' + ' Internal Server Error\r\n').encode())
                    client_connection.sendall(("Date: " + make_http_time_string(time.localtime())
                                               + "\r\n").encode())
                    client_connection.sendall("Content-Type: text/html\r\n\r\n".encode())
                    client_connection.sendall(create_error_html(500).encode())
                client_connection.close()
    # Close socket
    #server_socket.close()
