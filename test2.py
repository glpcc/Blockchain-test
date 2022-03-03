import rsa
pb_key,pr_key = rsa.newkeys(512)

mess = 'holaaa'
signed1 = rsa.sign(mess.encode('utf-8'),pr_key,'SHA-256')
signed2 = rsa.sign(signed1,pr_key,'SHA-256')
print(signed2.hex())

