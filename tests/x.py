import subprocess

r = subprocess.run(["echo", "100"], text=True, capture_output=True)
print(r)
