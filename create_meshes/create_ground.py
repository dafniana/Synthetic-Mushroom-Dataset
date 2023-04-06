import random
import decimal
import open3d as o3d

decimal.getcontext().prec = 3

ground = o3d.geometry.TriangleMesh()
vertices = []
n = 200
N = n * n
noise = 0.1
for i in range(n):
    for j in range(n):
        vertices.append([i + round(random.uniform(-noise, noise), 2),
                         j + round(random.uniform(-noise, noise), 2),
                         round(random.uniform(-noise, noise), 2)])

faces_1 = []
for i in range(N - n - 1):
    if (i + 1) % n != 0:
        faces_1.append([i, i + n + 1, i + 1])
        faces_1.append([i, i + n, i + n + 1])

faces_2 = []
for i in range(1, N - n):
    if i % n != 0:
        faces_2.append([i, i - 1, i + n - 1])
        faces_2.append([i, i + n - 1, i + n])


faces = []
for j in range(0, int(len(faces_1) / 2)):
    if j % 2 == 0:
        faces.append(faces_1[2 * j])
        faces.append(faces_1[2 * j + 1])
    else:
        faces.append(faces_2[2 * j])
        faces.append(faces_2[2 * j + 1])
n2 = N
textures = []
for i in range(1, n, 2):
    for j in range(1, n):
        textures.append([float(decimal.Decimal(i) / decimal.Decimal(n)),
                        float(decimal.Decimal(j) / decimal.Decimal(n))])
    for j in range(n, 1, -1):
        textures.append([float(decimal.Decimal(i+1) / decimal.Decimal(n)),
                        float(decimal.Decimal(j) / decimal.Decimal(n))])

ground.vertices = o3d.utility.Vector3dVector(vertices)
ground.triangles = o3d.utility.Vector3iVector(faces)
ground.triangle_uvs = o3d.utility.Vector2dVector(textures)
ground.compute_vertex_normals()
ground.compute_triangle_normals()
image = o3d.io.read_image('../data/ground/ground_textures/brown_mud_02_diff_8k.jpg')
ground.textures = [image]
ground.translate((0, 0, 0), relative=False)

o3d.visualization.draw_geometries([ground])
o3d.io.write_triangle_mesh('simple_ground_mesh.obj', ground, write_triangle_uvs=True, print_progress=True)
