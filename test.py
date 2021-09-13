ele = {4: {"floors": 2},
	6: {"floors": 2},
	8: {"floors": 2},
	9: {"floors": 3},
	10: {"floors": 2},
	12: {"floors": 3}}
count = 6
if count in ele:
	print()
	width = count / ele[count]['floors']

print(width)