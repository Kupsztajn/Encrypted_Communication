***

# Dokumentacja: Klient i Serwer TCP z własnym Urzędem Certyfikacji (CA) - Ocena 3.5

W tej wersji projektu odchodzimy od prostych certyfikatów samopodpisanych (self-signed). Zamiast tego wprowadzamy własny, lokalny Urząd Certyfikacji (Certificate Authority - CA). Serwer legitymuje się certyfikatem podpisanym przez nasze CA, a klient ufa wyłącznie serwerom, które taki podpis posiadają.

## 1. Architektura Kluczy i Certyfikatów (Skrypt Bash)

Zanim nastąpi komunikacja, skrypt automatyzuje proces generowania i podpisywania certyfikatów w trzech krokach:

1.  **Utworzenie głównego Urzędu Certyfikacji (CA):**
    Generowany jest klucz prywatny CA (`ca-key.pem`) oraz główny certyfikat CA (`ca-cert.pem`). Parametry `-addext "basicConstraints=critical,CA:TRUE"` nadają mu specjalne uprawnienia – ten certyfikat może teraz podpisywać inne certyfikaty, działając jak nasz prywatny odpowiednik firm takich jak Let's Encrypt.
2.  **Generowanie żądania dla Serwera (CSR):**
    Tworzony jest klucz prywatny serwera (`server-key.pem`) oraz prośba o wydanie certyfikatu (`server-req.pem`). W tym kroku serwer jeszcze nie posiada certyfikatu, a jedynie "wnioskuje" o jego nadanie dla domeny `localhost`.
3.  **Podpisanie certyfikatu serwera przez CA:**
    Nasze CA bierze wniosek serwera (`server-req.pem`) i przy użyciu swojego klucza głównego (`ca-key.pem`) wystawia i podpisuje ostateczny certyfikat dla serwera (`server-cert.pem`).

## 2. Przygotowanie kontekstu TLS w kodzie

Kluczowa różnica względem oceny 3.0 polega na tym, czym strony się legitymują i komu ufają:

* **Serwer (`server.py`):** Ładuje swój klucz prywatny oraz otrzymany certyfikat podpisany przez CA: 
    `self.context.load_cert_chain(certfile="server-cert.pem", keyfile="server-key.pem")`. 
* **Klient (`client.py`):** **Klient nie zna certyfikatu serwera przed połączeniem.** Ładuje jedynie certyfikat naszego Urzędu Certyfikacji jako zaufany: 
    `self.context.load_verify_locations(cafile="ca-cert.pem")`.
    Oznacza to zasadę: *"Zaufam każdemu serwerowi, pod warunkiem że jego certyfikat wydało MojeWlasneCA"*.

## 3. Przebieg komunikacji i weryfikacji

Komunikacja zaczyna się od warstwy transportowej, a następnie przechodzi w uwierzytelnianie.

1.  **Zwykłe połączenie TCP:** Klient łączy się z dynamicznie przydzielonym portem serwera (`conn.connect(...)`).
2.  **Uzgadnianie TLS (Handshake i Weryfikacja):**
    * Następuje wywołanie `wrap_socket` po obu stronach.
    * Serwer przesyła klientowi swój `server-cert.pem`.
    * **Weryfikacja kryptograficzna:** Biblioteka `ssl` klienta sprawdza podpis kryptograficzny na otrzymanym certyfikacie serwera. Wykorzystuje do tego publiczny klucz znajdujący się w załadowanym wcześniej `ca-cert.pem`. Jeśli matematycznie potwierdzi się, że certyfikat serwera podpisało nasze CA – klient dopuszcza połączenie.
3.  **Zabezpieczony transfer danych:**
    Po pomyślnej weryfikacji nawiązywany jest bezpieczny tunel TLS. Serwer wysyła wiadomość powitalną (`conn.sendall(...)`), a klient ją odbiera i odszyfrowuje w locie (`conn.recv(...)`). W przypadku braku właściwego podpisu CA (np. gdyby serwer użył starego certyfikatu samopodpisanego), u klienta wywołany zostanie wyjątek `ssl.SSLError`, a połączenie zostanie natychmiast zerwane.