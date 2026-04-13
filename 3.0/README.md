***

# Dokumentacja: Klient i Serwer TCP z szyfrowaniem TLS (Self-signed) - Ocena 3.0

Poniższy projekt realizuje bezpieczną komunikację w architekturze klient-serwer z wykorzystaniem protokołu TCP oraz warstwy szyfrowania TLS, opierając się na certyfikacie wygenerowanym samodzielnie (self-signed).

## 1. Generowanie certyfikatów i kluczy

Przed uruchomieniem kodu, za pomocą narzędzia OpenSSL generowane są niezbędne pliki kryptograficzne:

```bash
openssl req -x509 -newkey rsa:4096 -keyout server-key.pem -out server-cert.pem -days 365 -nodes -subj "//CN=localhost"
```

**Co dokładnie robi ten skrypt?**
* **`-x509`**: Wskazuje, że chcemy wygenerować od razu certyfikat z podpisem własnym (self-signed), a nie tylko żądanie podpisania certyfikatu (CSR).
* **`-newkey rsa:4096`**: Tworzy nowy klucz prywatny używając algorytmu RSA o długości 4096 bitów.
* **`-keyout server-key.pem`**: Zapisuje wygenerowany klucz prywatny do tego pliku (serwer używa go do odszyfrowywania danych i udowadniania swojej tożsamości).
* **`-out server-cert.pem`**: Zapisuje publiczny certyfikat (klucz publiczny + dane tożsamości) do tego pliku.
* **`-nodes`**: Oznacza "No DES" – klucz prywatny nie będzie zabezpieczony dodatkowym hasłem, co ułatwia automatyczne uruchamianie serwera.
* **`-subj "//CN=localhost"`**: Automatycznie wypełnia dane certyfikatu, ustawiając Common Name (CN) na `localhost`, co odpowiada nazwie hosta, z którym będzie łączył się klient.

## 2. Przygotowanie kontekstu TLS w kodzie

Zanim nastąpi jakakolwiek wymiana danych, obie strony muszą skonfigurować zasady szyfrowania (kontekst SSL/TLS).

* **Serwer (`server.py`)**: 
    W metodzie `__init__` serwer ładuje swój certyfikat oraz klucz prywatny:
    `self.context.load_cert_chain(certfile="server-cert.pem", keyfile="server-key.pem")`. 
    Dzięki temu, gdy klient się połączy, serwer będzie mógł przedstawić mu swój certyfikat.
* **Klient (`client.py`)**: 
    W metodzie `__init__` klient ładuje certyfikat serwera jako zaufany punkt odniesienia (pełni rolę lokalnego Root CA dla tego konkretnego połączenia):
    `self.context.load_verify_locations(cafile="server-cert.pem")`.
    Wyłącza również restrykcyjne sprawdzanie nazwy hosta (`check_hostname = False`), co ułatwia testowanie na środowisku lokalnym.

## 3. Przebieg komunikacji (krok po kroku)

Komunikacja przebiega warstwowo: najpierw nawiązywane jest zwykłe połączenie TCP, które następnie zostaje "podniesione" (upgraded) do szyfrowanego połączenia TLS.

### Krok A: Zwykły Handshake TCP
1.  **Serwer** otwiera gniazdo i czeka na połączenie: `server_socket.accept()`
2.  **Klient** inicjuje standardowe połączenie TCP z adresem i portem serwera: `conn.connect((self.host, self.port))`

### Krok B: Handshake TLS (Wymiana certyfikatów i kluczy)
W tym momencie gniazda TCP są "owijane" w warstwę SSL. Zwykły strumień bajtów zamienia się w strumień szyfrowany.
* **Klient** wykonuje to natychmiast przy tworzeniu gniazda: 
    `conn = self.context.wrap_socket(sock, server_hostname="localhost")`
* **Serwer** robi to zaraz po zaakceptowaniu połączenia z klientem: 
    `conn = self.context.wrap_socket(conn_socket, server_side=True)`
* **Co się dzieje pod spodem?** Strony uzgadniają algorytmy szyfrujące, serwer wysyła klientowi plik `server-cert.pem`, klient weryfikuje go ze swoim załadowanym plikiem (czy są zgodne), po czym generowany jest symetryczny klucz sesji, którym będą szyfrowane dalsze wiadomości.

### Krok C: Szyfrowana wymiana danych
Po udanym Handshake'u TLS, przesyłanie danych wygląda w kodzie identycznie jak w zwykłym TCP (metody `sendall` i `recv`), ale biblioteka `ssl` w locie szyfruje i odszyfrowuje dane w tle.
1.  **Klient** wysyła zaszyfrowaną wiadomość: 
    `conn.sendall(message.encode())`
2.  **Serwer** odbiera i automatycznie odszyfrowuje dane: 
    `data = conn.recv(1024)`
3.  **Serwer** odsyła zaszyfrowaną odpowiedź: 
    `conn.sendall(b"Witaj Kliencie!...")`
4.  **Klient** odbiera i odszyfrowuje odpowiedź: 
    `data = conn.recv(1024)`

### Krok D: Zakończenie
Po wymianie danych (lub w przypadku błędu weryfikacji przechwyconego w bloku `except ssl.SSLError`), połączenie jest zamykane poprzez `conn.close()`.