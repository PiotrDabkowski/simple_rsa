
### Simple RSA module

Supports:
 
 - random public and private key pair generation (any size)
 - asymetric encryption and decryption of arbitrary strings
 - signatures, you can sign, serialize, deserialize and reliably verify claims

Of course, don't use it in production, just read the code to learn how to quickly generate huge prime numbers (1000s digits long),
 or how to solve the linear congruence problem in logarithmic time or about RSA in general. The code is relatively short,
  but its packed with a big number of very interesting algorithms.

#### Key pair generation



```python
import rsa


r = rsa.RSA.get_random_rsa(bits=256) # you can also provide the keys manually, private key (d) is optional
r.modulus, r.exponent, r.d
```




    (176250016774801941160827279259156223243010342842721807630826957004191570731919L,
     78665,
     13572730693948903917010227288808785038086697313751224814125975285859675390426250105L)



#### Encryption/decryption



```python
ciphertext = r.encrypt('hello world')
ciphertext
```




    '\x00\x16S\xcb\x03\xe3F\x91\xa5\x9a\xfaF\xa5j\x02\xf6\r\x85\x8clx\x04\xef\xac\xfa\x8c\xebS\r}\xc6\x1c,\x00\xf2J\x16\xf9"\x8a}\xafkBa\x9b\xad\x1b\xef\xc8\x94\x85\xe5\xa7\x03\xcb\xc2\xc7G\xb9F\x82\xe9\xdeK\x9a\x00D\x85}}\x19\x9c\xd4\xfa\x11\xd9\xa3\xca\x0e74\xf6\x88d\xc7*D^w\x92#\xc8e\xc8\n9z\xc8\x01gzw\xf8\xf3e\x1d<g\xb3;{\xf6\x8ci5?\x9b\x81\x98\xab<\x94\xa9\xdf\xe0::\xaf1]j'




```python
r.decrypt(ciphertext)
```




    'hello world'



#### Claims and signatures


```python
claim = r.sign('Poland is the best')
claim.signature

```




    22344980823786412771627668254706768127981754849555142774287807621995509718288L




```python
claim.verify()
```




    True




```python
claim_str = claim.to_string()
claim_str
```




    '506f6c616e64206973207468652062657374;13349;185a9f96ecc6ecae1dc7caa96e8707466773f389098a88edc3a15d96c4c8a238fL;3166cf9b15f7aca8d8afae20354724ab234c58caee36319dd6be029152021d10L'




```python
claim_recovered = rsa.Claim.from_string(claim_str)
claim_recovered.msg
```




    'Poland is the best'




```python
claim_recovered.verify()
```




    True




```python
claim_recovered.signature += 1
claim_recovered.verify()
```




    False


