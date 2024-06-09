import socket
import threading
import os

def receive_file(connection, file_name):
    os.makedirs("filesofclient3", exist_ok=True)
    path_file = os.path.join("filesofclient3/", file_name)
    with open(path_file, 'wb') as file:
        while True:
            data = connection.recv(1024)
            if data.endswith(b'<END>'):
                file.write(data[:-len(b'<END>')])  # Write all data except the <END> marker
                break
            file.write(data)

def send_file(connection, file_name):
    with open(file_name, 'rb') as file:
        while True:
            data = file.read(1024)
            if not data:
                break
            connection.sendall(data)
        connection.sendall(b'<END>')
    print(f"File '{file_name}' sent successfully.")

def handle_receive(connection):
    while True:
        data = connection.recv(1024)

        if data.startswith(b'send_file'):
            _, file_name = data.split()
            receive_file(connection, file_name.decode())
            print(f"Received file: {file_name.decode()}")
        else:
            message = data.decode('utf-8')
            print(f"Received message: {message}")

def handle_send(connection):
    while True:
        message = input("Enter message to send (type 'send_file filename' to send file): ")

        if message.startswith("send_file"):
            _, file_name = message.split()
            connection.sendall(message.encode('utf-8'))
            send_file(connection, file_name)
        else:
            connection.sendall(message.encode('utf-8'))

def start_client(server_host, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))
    print(f"Connected to server at {server_host}:{server_port}")

    receive_thread = threading.Thread(target=handle_receive, args=(client_socket,))
    receive_thread.start()

    handle_send(client_socket)

if __name__ == "__main__":
    server_host = '192.168.1.26'
    server_port = 5000

    start_client(server_host, server_port)
