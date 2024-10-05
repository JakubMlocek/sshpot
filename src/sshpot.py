import paramiko
import socket
import threading
import datetime

#basic configuration
SSH_KEY = paramiko.RSAKey.generate(2048)  
SERVER_IP = '0.0.0.0' 
SERVER_PORT = 2222
INTERACTION_MODE = 'medium'


class SSHemulation(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
    
    def check_auth_password(self, username, password):
        log_attempt(username, password, self.client_ip)
        return paramiko.AUTH_SUCCESSFUL if INTERACTION_MODE == 'medium' else paramiko.AUTH_FAILED

#logging connection attempts
def log_attempt(username, password, client_ip):
    time_of_attempt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('login_info.txt', 'a') as log_file:
        log_file.write(f"[{time_of_attempt}] Login attempt from {client_ip} - Username: {username}, Password: {password}\n")
    print(f"[INFO] [{time_of_attempt}] Logging attempt from {client_ip}: {username}:{password}")

#logging shell commands
def log_command(command, client_ip):
    time_of_command = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('commands_log.txt', 'a') as log_file:
        log_file.write(f"[{time_of_command}] Command from {client_ip}: {command}\n")
    print(f"[INFO] [{time_of_command}] Command from {client_ip}: {command}")


def emulate_shell(channel, client_ip):
    channel.send("Welcome to fake SSH server!\n")
    try:
        while True:
            channel.send("$ ")
            command = channel.recv(1024).decode('utf-8').strip()
            if not command:
                continue
            if command.lower() in ['exit', 'logout']:
                channel.send("Logging out...\n")
                break
            log_command(command, client_ip)
            channel.send(f"Command '{command}' not found.\n")
    except Exception as e:
        print(f"[ERROR] Shell error: {str(e)}")
    finally:
        channel.close() 

#handling connections
def handle_connection(client, address):
    client_ip = address[0]
    transport = paramiko.Transport(client)
    transport.add_server_key(SSH_KEY)
    server = SSHemulation(client_ip)

    try:
        transport.start_server(server=server)
        channel = transport.accept(20)
        if channel is None:
            raise Exception("Connection channel not accepted.")
        
        if INTERACTION_MODE == 'medium':
            emulate_shell(channel, client_ip)
        else:
            channel.close()
    except Exception as e:
        print(f"[ERROR] Error handling connection: {str(e)}")
    finally:
        client.close()


def start_honeypot():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(100)

    print(f"[INFO] SSHPOT Listening on {SERVER_IP}:{SERVER_PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"[INFO] Connection from {client_address}")
        threading.Thread(target=handle_connection, args=(client_socket, client_address)).start()

if __name__ == "__main__":
    start_honeypot()
