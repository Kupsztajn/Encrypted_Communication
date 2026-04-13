import socket
import ssl


class SecureServer:
    def __init__(self, host='127.0.0.1', port=0):
        self.host = host
        self.port = port

        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.context.load_cert_chain(certfile="server-cert.pem", keyfile="server-key.pem")

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)

        assigned_port = server_socket.getsockname()[1]
        self.port = assigned_port

        print(f"[*] Serwer nasłuchuje na {self.host}:{assigned_port} (Tylko TLS - Ocena 3.0)", flush=True)

        while True:
            conn_socket, fromaddr = server_socket.accept()
            print(f"\n[*] [Warstwa Transportowa] Połączenie TCP od: {fromaddr}", flush=True) 
            conn = None

            try:
                conn = self.context.wrap_socket(conn_socket, server_side=True)
                print("Zestawiono szyfrowane połączenie TLS.", flush=True)

                data = conn.recv(1024)

                if data:
                    print(f"Odszyfrowana wiadomość od klienta: {data.decode()}", flush=True)
                    conn.sendall(b"Witaj Kliencie! Tu bezpieczny serwer")
            
            except ssl.SSLError as e:
                print(f"Błąd TLS (prawdopodobnie klient odrzucił certyfikat): {e}", flush=True)

                if conn:
                    conn.close()
                else:
                    server_socket.close()



if __name__ == "__main__":
    server = SecureServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n Serwer został zatrzymany ręcznie.")