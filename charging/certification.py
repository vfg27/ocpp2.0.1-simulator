import datetime
from hashlib import sha256
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

# Generate a new private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# Create a certificate
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"FR"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"France"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Sophia-Antipolis"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"EURECOM"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"eurecom.fr"),
])

# Create a certificate signing request
csr = x509.CertificateSigningRequestBuilder().subject_name(subject).sign(private_key, hashes.SHA256(), default_backend())

# Self-sign the certificate
cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(csr.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.datetime.utcnow())
    .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365*2))
    .add_extension(
        x509.SubjectAlternativeName([x509.DNSName(u"eurecom.fr")]),
        critical=False,
    )
    .sign(private_key, hashes.SHA256(), default_backend())
)

# Save the private key and certificate to files
with open("private_key.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ))

with open("certificate.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))