***

# Dokumentacja: Klient i Serwer TCP z obustronnym uwierzytelnianiem TLS (mTLS) - Ocena 4.0

W tej wersji projektu wprowadzamy architekturę **Mutual TLS (mTLS)**, co oznacza, że weryfikacja tożsamości działa w obu kierunkach. Nie tylko klient weryfikuje, czy połączył się z właściwym serwerem, ale również serwer wymaga od klienta przedstawienia ważnego certyfikatu, zanim pozwoli mu na przesłanie jakichkolwiek danych.

## 1. Architektura Kluczy i Certyfikatów (Skrypt Bash)

Skrypt generuje pełną infrastrukturę klucza publicznego (PKI) niezbędną do uwierzytelniania obu stron:

1.  **Utworzenie Urzędu Certyfikacji (CA):** Podobnie jak w wersji 3.5, generujemy nadrzędne CA (`ca-key.pem` i `ca-cert.pem`), które posiada jawne uprawnienia do podpisywania.
2.  **Generowanie certyfikatu SERWERA:** Tworzony jest klucz prywatny serwera oraz żądanie (CSR), które zostaje podpisane przez nasze CA. Powstaje plik `server-cert.pem`.
3.  **Generowanie certyfikatu KLIENTA:** **(Nowość)** Tworzony jest odrębny klucz prywatny dla klienta (`client-key.pem`) oraz żądanie certyfikatu dla użytkownika `Client1`. Nasze CA podpisuje ten wniosek, tworząc plik `client-cert.pem`.

Dzięki temu *obie strony* posiadają własne "dowody tożsamości" wystawione przez ten sam, zaufany urząd (MyCustomCA).

## 2. Przygotowanie kontekstu TLS w kodzie (mTLS)

Konfiguracja w kodzie musi teraz uwzględniać wymianę certyfikatów w obu kierunkach.

* **Serwer (`server.py`):** * Ładuje swój własny certyfikat i klucz (`load_cert_chain`), aby móc przedstawić się klientowi.
    * Wymusza na kliencie przesłanie certyfikatu za pomocą flagi: `self.context.verify_mode = ssl.CERT_REQUIRED`.
    * Ładuje certyfikat CA (`load_verify_locations`), aby móc kryptograficznie zweryfikować poprawność "dowodu tożsamości" nadesłanego przez klienta.
* **Klient (`client.py`):** * Ładuje certyfikat CA (`load_verify_locations`), aby zweryfikować tożsamość serwera.
    * **Kluczowa zmiana:** Ładuje własny klucz prywatny i certyfikat (`load_cert_chain`), aby w odpowiedzi na żądanie serwera móc udowodnić swoją tożsamość.

## 3. Przebieg komunikacji i podwójnej weryfikacji

Proces nawiązywania połączenia jest w tej wersji najbardziej rygorystyczny:

1.  **Zwykłe połączenie TCP:** Następuje standardowy handshake protokołu TCP (`conn.connect(...)`).
2.  **Handshake TLS i Obustronna Weryfikacja (mTLS):**
    * Podczas wywołania metody `wrap_socket` strony rozpoczynają negocjacje.
    * **Weryfikacja Serwera:** Serwer wysyła swój certyfikat do klienta. Klient weryfikuje jego podpis przy użyciu załadowanego `ca-cert.pem`.
    * **Weryfikacja Klienta:** Ponieważ serwer ma ustawioną flagę `CERT_REQUIRED`, żąda on od klienta przesłania certyfikatu. Klient wysyła `client-cert.pem`. Serwer weryfikuje jego podpis za pomocą swojego załadowanego `ca-cert.pem`.
    * Jeśli którakolwiek ze stron przedstawi nieważny, niepodpisany przez właściwe CA certyfikat (lub klient w ogóle go nie wyśle), biblioteka podniesie wyjątek `ssl.SSLError` i połączenie zostanie natychmiast odrzucone.
3.  **Zabezpieczony transfer danych:**
    Dopiero gdy obie strony pomyślnie udowodnią sobie nawzajem swoją tożsamość, ustanawiany jest bezpieczny, szyfrowany kanał. Klient wysyła swoją tajną wiadomość, a serwer bezpiecznie na nią odpowiada.