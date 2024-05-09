import kyber
from Crypto.Cipher import AES

"""
1. server generating public and secret key
2. server sending public key to each client whenever they try to connect to server
3. using public key from server, client encrypt, which gives c (cipher text) and key (shared key)
4. then client sends c (cipher text) to server
5. server decrypts c (cipher text) with its secret key to get the shared key

"""

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

d_cipher = AES.new(_key, AES.MODE_CFB, iv = iv)
output = d_cipher.decrypt(ciphered_data)
print(output)


