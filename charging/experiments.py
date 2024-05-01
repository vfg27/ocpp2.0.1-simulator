import os
from db import add_user, remove_user, auth_user, get_events, check_user
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

#connected_clients = [('patata', 32)]

#add_user('E2507-8420-1274', 'patatafrita')
#remove_user('E2507-8420-1274')
#print(auth_user("E2507-8420-1274", "pat' OR '5'='5'"))
#print(auth_user("E2507-8420-1274", "105' OR '1=1"))
#id = 'E2507-8420-1274'
#data = {"type": "ISO15693", "id_token": "1122334455667788"}
#data = {"type": "ISO15693", "id_token": "1' UNION SELECT sqlite_version() as S1, sqlite_version() as S2, sqlite_version() as S3, sqlite_version() as S4, sqlite_version() as S5 --"}
#data = {"type": "ISO15693", "id_token": "1' UNION SELECT id as id, user as user, password as password, user as S4, user as S5 FROM Users --"}
#data = {"type": "1' UNION SELECT sqlite_version() as S1, sqlite_version() as S2, sqlite_version() as S3, sqlite_version() as S4, sqlite_version() as S5 --", "id_token": "1122334455667788"}
#print(get_events(id, data))
#print(type(str(data)))
#"SELECT sqlite_version();"
#remove_user('E2507-8420-127274')
#print(check_user(id)!= None)


CERTIFICATE_PATH = os.path.join(os.getcwd(), 'certificate.pem')
try:
    with open(CERTIFICATE_PATH, "rb") as f:
        cert_data = f.read()
        certificate = x509.load_pem_x509_certificate(cert_data, default_backend())
except Exception as e:
    print("Reading certicate failed:", e)

# DER encode the certificate into binary
print('***************TRANSFORMING 1************************')
der_encoded = certificate.public_bytes(encoding=serialization.Encoding.DER)
print('***************TRANSFORMING 2************************')
# Hex encode the DER encoded binary into a case-insensitive string
hex_encoded = der_encoded.hex().upper()
print(hex_encoded)
            