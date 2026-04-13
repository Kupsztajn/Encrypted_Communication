rm *.pem *.srl
openssl req -x509 -newkey rsa:4096 -keyout ca-key.pem -out ca-cert.pem -days 365 -nodes -subj "//CN=MojeWlasneCA" -addext "basicConstraints=critical,CA:TRUE" -addext "keyUsage=critical,keyCertSign,cRLSign"
openssl req -newkey rsa:4096 -keyout server-key.pem -out server-req.pem -nodes -subj "//CN=localhost"
openssl x509 -req -in server-req.pem -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem -days 365