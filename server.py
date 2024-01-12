import socket
import time
global client_connected 


def write_to_file(data):
    with open('received_letters.txt', 'w') as file:
        file.write(data)

def write_to_file_conf(client_connected):
    with open('Connection_status.txt', 'w') as file:  
        file.write(str(client_connected))
        

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 64321))
server_socket.listen(1)
print("Server is listening for connections...")

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")
    client_connected = True
    write_to_file_conf(client_connected)
    last_heartbeat_received_time = time.time()

    while client_connected:
        try:
            client_socket.settimeout(3)  # Reduce timeout for more frequent checks

            data = client_socket.recv(1024).decode()

            if data and client_connected:
                if data == 'heartbeat':
                    # Update the last heartbeat time and don't log anything
                    last_heartbeat_received_time = time.time()
                    client_socket.send(b'heartbeat_ack')
                else:
                    # Log and process other data
                    print(f"Data received: {data,client_connected}")
                    write_to_file(data)
                   
                    client_socket.send(f"Received {data}".encode('utf-8'))

            # Check for client heartbeat, disconnect if it's been too long
            if time.time() - last_heartbeat_received_time > 10:
                client_connected = False
                write_to_file_conf(client_connected)  
                print(f"Heartbeat not received. Client {client_address} may have disconnected.")
                break

        except socket.timeout:
            # During timeout, just check if heartbeat was received in time
            if time.time() - last_heartbeat_received_time > 10:
                print(f"Heartbeat not received for too long. Client {client_address} may have disconnected.")
                client_connected = False
                write_to_file_conf(client_connected)  
                break

        except socket.error as e:
            print(f"Socket error with {client_address}: {e}")
            client_connected = False
            break

    client_socket.close()

server_socket.close()
