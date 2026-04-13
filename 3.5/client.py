import socket
import ssl
import sys


class CAClient:
    def __init__(self, host='127.0.0.1', port=18443):
        self.host = host
        self.port = port
        
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        
        self.context.load_verify_locations(cafile="ca-cert.pem")
    

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn = self.context.wrap_socket(sock, server_hostname="localhost")
        
        try:
            conn.connect((self.host, self.port))
            print("[+] Sukces! Serwer przedstawił certyfikat podpisany przez moje zaufane CA.")
            data = conn.recv(1024)
            print(f"[*] Odpowiedź: {data.decode()}")
        except ssl.SSLError as e:
            print(f"[!] Błąd weryfikacji: Serwer nie ma certyfikatu podpisanego przez nasze CA! {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Użycie: python client.py <NUMER_PORTU_SERWERA>")
        sys.exit(1)
        
    port_serwera = int(sys.argv[1])
    
    client = CAClient(port=port_serwera)
    client.connect()