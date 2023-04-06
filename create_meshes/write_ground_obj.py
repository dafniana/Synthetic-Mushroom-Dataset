import decimal

decimal.getcontext().prec = 3

# n = 494
# n2 = 241463
n = 201
n2 = 40000
textures = []
for i in range(1, n, 2):
    for j in range(1, n):
        textures.append([float(decimal.Decimal(i) / decimal.Decimal(n)),
                        float(decimal.Decimal(j) / decimal.Decimal(n))])
    for j in range(n, 1, -1):
        textures.append([float(decimal.Decimal(i+1) / decimal.Decimal(n)),
                        float(decimal.Decimal(j) / decimal.Decimal(n))])

initial = 'simple_ground_mesh.obj'
with open(initial, 'r') as file1:
    context = []
    for line in file1:
        context.append(line)
print(len(context))
print(context[0], context[-1])

# new = '/home/dafnianagno/Documents/blender_mushrooms/dafni/mushroom_new3.obj'
new = 'ground_mesh_1.obj'
with open(new, 'w') as file2:
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
            for i in range(0, n2):
                file2.write('vt ')
                file2.write(str(textures[i][0]))
                file2.write(' ')
                file2.write(str(textures[i][1]))
                file2.write('\n')
            file2.write(line)
        else:
            file2.write(line)
