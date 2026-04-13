import socket
import ssl

class SecureServer:
    def __init__(self, host='127.0.0.1', port=0):
        self.host = host
        self.port = port
        
        # Konfiguracja kontekstu SSL dla SERWERA
        # Purpose.CLIENT_AUTH oznacza, że serwer będzie weryfikował klienta
        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        
        # Wymagaj certyfikatu od klienta (mTLS)
        self.context.verify_mode = ssl.CERT_REQUIRED
        
        # Załaduj certyfikat naszego CA, aby móc zweryfikować certyfikat klienta
        self.context.load_verify_locations(cafile="ca-cert.pem")
        
        # Załaduj certyfikat i klucz prywatny samego serwera
        self.context.load_cert_chain(certfile="server-cert.pem", keyfile="server-key.pem")

    def start(self):
        # Tworzenie standardowego gniazda TCP
        bindsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bindsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        bindsocket.bind((self.host, self.port))
        bindsocket.listen(5)
        
        assigned_port = bindsocket.getsockname()[1]
        self.port = assigned_port

        print(f"[*] Serwer nasłuchuje na {self.host}:{self.port} (mTLS)", flush=True)

        while True:
            # Akceptacja połączenia TCP
            newsocket, fromaddr = bindsocket.accept()
            print(f"[*] Połączenie TCP od: {fromaddr}")
            
            try:
                # "Owijanie" gniazda TCP warstwą TLS
                conn = self.context.wrap_socket(newsocket, server_side=True)
                print("[+] Zestawiono bezpieczne połączenie TLS.")
                
                data = conn.recv(1024)
                if data:
                    print(f"Wiadomość od klienta: {data.decode()}")
                    conn.sendall(b"Witaj Kliencie! Tu bezpieczny serwer.")
            except ssl.SSLError as e:
                print(f"[!] Błąd SSL (np. brak certyfikatu klienta): {e}")
            finally:
                if conn:
                    conn.close()
                else:
                    newsocket.close()

if __name__ == "__main__":
    server = SecureServer()
    server.start()