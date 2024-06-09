import socket
import os
import threading

def receive_file(connection, file_name):
    os.makedirs("filesofsender", exist_ok=True)
    path_file = os.path.join("filesofsender/", file_name)
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

def prep_send(connections):
    message = input("Enter message to send (type 'send_file filename' to send file): ")

    if message.startswith("send_file"):
        _, file_name = message.split()
        for conn in connections:
            conn.sendall(message.encode('utf-8'))
            send_file(conn, file_name)
    else:
        for conn in connections:
            conn.sendall(message.encode('utf-8'))

def handle_client(connection, connections):
    while True:
        data = connection.recv(1024)

        if data.startswith(b'send_file'):
            _, file_name = data.split()
            receive_file(connection, file_name.decode())
            print(f"Received file: {file_name.decode()}")
            for conn in connections:
                if conn != connection:
                    conn.sendall(data)
                    send_file(conn, file_name.decode())
        else:
            message = data.decode('utf-8')
            print(f"Received message: {message}")
            for conn in connections:
                if conn != connection:
                    conn.sendall(data)

def start_server():
    host = '192.168.1.26'
    port = 5000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(4)  # Increase backlog to handle up to 4 pending connections
    print(f"Server listening on {host}:{port}")

    connections = []

    while len(connections) < 4:
        connection, address = server_socket.accept()
        connections.append(connection)
        print(f"Connected to {address}")

    threads = []
    for connection in connections:
        thread = threading.Thread(target=handle_client, args=(connection, connections))
        thread.start()
        threads.append(thread)

    while True:
        prep_send(connections)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    start_server()
