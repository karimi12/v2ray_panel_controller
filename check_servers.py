import urllib.request

for i in range(21, 71):
    print(f"server {i}")
    urllib.request.urlopen(f"https://npanel4.karimiblog.ir/shadow/keys/{i}").read()

for i in range(21, 50):
    print(f"server {i}")
    urllib.request.urlopen(f"https://spanel.karimiblog.ir/shadow/keys/{i}").read()