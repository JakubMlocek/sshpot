import paramiko
import socket
import threading

#basic configuration
SSH_KEY = paramiko.RSAKey.generate(2048)  
SERVER_IP = '0.0.0.0' 
SERVER_PORT = 2222 


class SSHemulation(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
    
    def check_auth_password(self, username, password):
        log_attempt(username, password, self.client_ip)
        return paramiko.AUTH_FAILED


def log_attempt(username, password, client_ip):
    with open('login_info.txt', 'a') as log_file:
        log_file.write(f"Login attempt from {client_ip} - Username: {username}, Password: {password}\n")
    print(f"[INFO] Logging attempt from {client_ip}: {username}:{password}")

def handle_connection(client, address):
    transport = paramiko.Transport(client)
    transport.add_server_key(SSH_KEY)
    server = SSHemulation()

    try:
        transport.start_server(server=server)
        channel = transport.accept(20)
        if channel is None:
            raise Exception("Kanał połączenia nie został zaakceptowany.")
        channel.close()
    except Exception as e:
        print(f"[ERROR] Błąd podczas obsługi połączenia: {str(e)}")

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
