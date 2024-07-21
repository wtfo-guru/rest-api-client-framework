path = "/api/{action}/wtf"
args = {"action": "enable"}
path1 = path.format(**args)

print(path)
print(path1)

