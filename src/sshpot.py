import paramiko
import socket
import threading



SSH_KEY = paramiko.RSAKey.generate(2048)  #Generating RSA key
SERVER_IP = '0.0.0.0' #Listening on all avaliable network interfaces
SERVER_PORT = 2222 #Listening on port 2222

class SSHHoneypot(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        print(f"[INFO] Próba logowania: {username}:{password}")
        return paramiko.AUTH_FAILED  # Zawsze odrzuca logowanie

def handle_connection(client, address):
    transport = paramiko.Transport(client)
    transport.add_server_key(HOST_KEY)
    server = SSHHoneypot()

    try:
        transport.start_server(server=server)
        chan = transport.accept(20)
        if chan is None:
            raise Exception("Kanał połączenia nie został zaakceptowany.")
        chan.close()
    except Exception as e:
        print(f"[ERROR] Błąd podczas obsługi połączenia: {str(e)}")

def start_honeypot():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((BIND_IP, BIND_PORT))
    server_socket.listen(100)

    print(f"[INFO] SSH Honeypot nasłuchuje na {BIND_IP}:{BIND_PORT}")

    while True:
        client, address = server_socket.accept()
        print(f"[INFO] Połączenie od {address}")
        threading.Thread(target=handle_connection, args=(client, address)).start()

if __name__ == "__main__":
    start_honeypot()