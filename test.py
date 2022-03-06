import rsa

pu,pr = rsa.newkeys(512)

msg = b'hola'
new_key =  rsa.PublicKey.load_pkcs1(pu.save_pkcs1().decode('utf-8').encode('utf-8'))
signature = rsa.sign(msg,pr,'SHA-256').hex()
print(signature)
print(pu.save_pkcs1())
print(new_key.save_pkcs1())

rsa.verify(msg,bytes.fromhex(signature),new_key)
