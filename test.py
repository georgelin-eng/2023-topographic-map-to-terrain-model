cols = 4
rows = 100

data = [[0]*cols for _ in range(rows)]

for index in range(100):
    data[index][0] = index
    data[index][1] = index
    data[index][2] = index

print(data)