Raport projektu – Bezpieczna komunikacja klient–serwer (mTLS)
Opis ogólny

Projekt implementuje bezpieczny model komunikacji sieciowej w architekturze klient–serwer z wykorzystaniem protokołu TLS oraz mechanizmu mutual TLS (mTLS). W rozwiązaniu obie strony połączenia – klient i serwer – uwierzytelniają się wzajemnie przy użyciu certyfikatów X.509 podpisanych przez własne centrum certyfikacji (CA). Transmisja danych jest szyfrowana.

Struktura projektu

1. Plik server.py
Serwer realizuje połączenia TCP zabezpieczone warstwą TLS. Konfiguracja obejmuje:

utworzenie kontekstu SSL w trybie wymagającym uwierzytelnienia klienta
załadowanie certyfikatu CA (ca-cert.pem)
załadowanie certyfikatu i klucza serwera (server-cert.pem, server-key.pem)
wymuszenie przedstawienia certyfikatu przez klienta (CERT_REQUIRED)

Po zestawieniu połączenia serwer odbiera dane od klienta i odsyła odpowiedź w ramach szyfrowanego kanału.

2. Plik client.py
Klient inicjuje połączenie TLS z serwerem:

weryfikuje certyfikat serwera na podstawie CA
przedstawia własny certyfikat (client-cert.pem, client-key.pem)
nawiązuje połączenie i przesyła wiadomość tekstową

Po stronie klienta wyłączono sprawdzanie hostname (check_hostname = False), co upraszcza testy lokalne, ale obniża poziom bezpieczeństwa w środowisku produkcyjnym.

3. Plik skrypt.sh
Skrypt automatyzuje tworzenie infrastruktury certyfikatów:

generuje własne centrum certyfikacji (CA)
tworzy żądania podpisania certyfikatów (CSR) dla serwera i klienta
podpisuje certyfikaty przy użyciu CA

W efekcie powstaje zamknięty system zaufania umożliwiający wzajemną weryfikację tożsamości.