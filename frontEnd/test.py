import re

dms_string = ' -01deg 41\' 55.5""'

test_string = dms_string.split()

res = int(re.sub("\D", "", test_string[0]))
res1 = float(re.sub("\D", "", test_string[1]))
res2 = test_string[2][:len(test_string[2])-1]

print(res)
print(res1)
print(res2)

print(type(res))
print(res1)
print(res2)