import jsonmap

temp = {}
for x in jsonmap.match:
    if x in jsonmap.names:
        temp[x] = jsonmap.names[x]
        
print(temp)