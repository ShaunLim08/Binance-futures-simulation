import hmac
import hashlib

api_secret = 'NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j'
query_string = 'symbol=LTCBTC&side=BUY&type=LIMIT&timeInForce=GTC&quantity=1&price=0.1&recvWindow=5000&timestamp=1499827319559'
expected_signature = 'c8db56825ae71d6d79447849e617115f4a920fa2acdc98b0693acfa8b29257e9'

signature = hmac.new(
    api_secret.encode('utf-8'),
    query_string.encode('utf-8'),
    hashlib.sha256
).hexdigest()

print(f"Generated: {signature}")
print(f"Expected:  {expected_signature}")
print(f"Match: {signature == expected_signature}")
