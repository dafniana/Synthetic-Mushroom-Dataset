import decimal

decimal.getcontext().prec = 3

# h = 75
# w = 122
# h = 115
# w = 143
h = 100
w = 100
textures = []
for i in range(1, h):
    for j in range(1, w):
        textures.append([float(decimal.Decimal(i) / decimal.Decimal(h + 1)),
                        float(decimal.Decimal(j) / decimal.Decimal(w + 1))])
print(textures)
print(len(textures))


with open('textureless_mushroom.obj', 'r') as file1:
    context = []
    for line in file1:
        context.append(line)
print(len(context))
print(context[0], context[-1])

number = 241463
with open('mushroom.obj', 'w') as file2:
    for line in context:
        if line[0] == 'f':
            parts = line.split(' ')
            file2.write('f ')
            for part in parts[1:]:
                numbers = part.split('//')
                file2.write(numbers[0])
                file2.write('/')
                file2.write(numbers[0])
                file2.write('/')
                file2.write(numbers[0])
                file2.write(' ')
            file2.write('\n')
        elif line[:6] == 'usemtl':
            for i in range(0, number):
                file2.write('vt ')
                file2.write(str(textures[i % 8954][0]))
                file2.write(' ')
                file2.write(str(textures[i % 8954][1]))
                file2.write('\n')
            file2.write(line)
        else:
            file2.write(line)
