# Czyszczenie starych (niepoprawnych) certyfikatów
rm *.pem *.srl

# 1. Tworzymy poprawione CA (z pełnymi uprawnieniami do podpisywania)
openssl req -x509 -newkey rsa:4096 -keyout ca-key.pem -out ca-cert.pem -days 365 -nodes -subj "//CN=MojeWlasneCA" -addext "basicConstraints=critical,CA:TRUE" -addext "keyUsage=critical,keyCertSign,cRLSign"

# 2. Tworzymy klucz i prośbę o certyfikat (CSR) dla SERWERA
openssl req -newkey rsa:4096 -keyout server-key.pem -out server-req.pem -nodes -subj "//CN=localhost"

# 3. Podpisujemy prośbę serwera naszym nowym, w pełni poprawnym CA
openssl x509 -req -in server-req.pem -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem -days 365