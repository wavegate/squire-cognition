import json

file = open("somefile.txt", "r")
string = file.read()
parsed = json.loads(string)


def search(x):
	if 'test_part' in x:
		return True
	else:
		return False

result = filter(search, parsed)
for e in result:
	print(e)
#print(json.dumps(parsed, indent=4, sort_keys=True))