import socket
import ssl


class CAServer:
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

        print(f"[*] Serwer (CA Mode 3.5) nasłuchuje na {self.host}:{assigned_port}")

        while True:
            newsocket, fromaddr = server_socket.accept()
            conn = None
            try:
                conn = self.context.wrap_socket(newsocket, server_side=True)
                print(f"[+] Bezpieczne połączenie z {fromaddr}")
                conn.sendall("Witaj! Twoje połączenie zostało zweryfikowane przez moje CA.".encode())
            except Exception as e:
                print(f"[!] Błąd: {e}")
            finally:
                if conn: conn.close()
                else: newsocket.close()


if __name__ == "__main__":
    CAServer().start()