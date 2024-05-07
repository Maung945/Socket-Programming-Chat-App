import kyber
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
# Server generate keypair and give pk to client
# pk: public key    sk: secret key
pk, sk = kyber.Kyber512.keygen()

# Client using server pk to generate c and key
# give c to server
# c: ciphertext     key: shared key     pk: server public key
c, key = kyber.Kyber512.enc(pk)

# Server decrypt c with server sk to have shared key
# _key: shared key
_key = kyber.Kyber512.dec(c,sk)


data = b'uni is cute'

cipher = AES.new(_key, AES.MODE_CFB)
ciphered_data = cipher.encrypt(data)
iv = cipher.iv

d_cipher = AES.new(key, AES.MODE_CFB, iv = iv)
output = d_cipher.decrypt(ciphered_data)
print(output)


