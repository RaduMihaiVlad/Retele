import struct
import requests

header = {'Content-Type': 'application/octet-stream'} # vezi in cerinta
data = struct.pack('!LL', 0x123, 0x123) # primii 32 de biti sunt unsigned long restul sunt octetii care reprezinta mesajul
url = 'http://ec2-18-212-174-12.compute-1.amazonaws.com:8001/crc'
response = requests.post(url, headers=header, data=data)
print(response.content)
crc = struct.unpack('!L', response.content) # raspunsul trebuie si el despachetat in funcie de cum a fost calculat
print('CRC calculat: ', crc)