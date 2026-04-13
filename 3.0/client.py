import ssl
import socket
import sys


class SecureClient:
    def __init__(self, host='127.0.0.1', port=0):
        self.host = host
        self.port = port
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.context.load_verify_locations(cafile="server-cert.pem")
        self.context.check_hostname = False

    def connect_and_send(self, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn = self.context.wrap_socket(sock, server_hostname="localhost")
        try:
            conn.connect((self.host, self.port))
            print("Zestawiono szyfrowane połączenie TLS z serwerem.")
            conn.sendall(message.encode())
            data = conn.recv(1024)
            print(f"Odszyfrowana odpowiedź od serwera: {data.decode()}")
        except ssl.SSLError as e:
            print(f"Błąd weryfikacji TLS: {e}")
        
        except ConnectionRefusedError:
            print("Blad")
        finally:
            conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Użycie: python client.py <NR PORTU>")
        sys.exit(1)
        
    port_serwera = int(sys.argv[1])
    
    client = SecureClient(port=port_serwera)
    client.connect_and_send("Tajne dane do przeslania")