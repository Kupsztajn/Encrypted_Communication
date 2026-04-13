import socket
import ssl
import sys


class SecureClient:
    def __init__(self, host='127.0.0.1', port=0):
        self.host = host
        self.port = port
        
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.context.load_verify_locations(cafile="ca-cert.pem")
        self.context.load_cert_chain(certfile="client-cert.pem", keyfile="client-key.pem")
        self.context.check_hostname = False 

    def connect_and_send(self, message):
        # Tworzenie standardowego gniazda TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # "Owijanie" gniazda warstwą TLS ZANIM połączymy się z serwerem
        # server_hostname jest potrzebne dla SNI (Server Name Indication)
        conn = self.context.wrap_socket(sock, server_hostname="localhost")
        
        try:
            conn.connect((self.host, self.port))
            print("[+] Połączono i zweryfikowano serwer pomyślnie.")
            
            conn.sendall(message.encode())
            data = conn.recv(1024)
            print(f"Odpowiedź z serwera: {data.decode()}")
        except ssl.SSLError as e:
            print(f"[!] Błąd weryfikacji SSL: {e}")
        finally:
            conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Użycie: python client.py <NUMER_PORTU_SERWERA>")
        sys.exit(1)
        
    port_serwera = int(sys.argv[1])
    
    client = SecureClient(port=port_serwera)
    client.connect_and_send("Tajne dane do przeslania")