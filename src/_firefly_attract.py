import discrete_firefly as df
import permutation as perm

nodes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

n = 5
x = df.sample(nodes, n)
for cx in x:
    print(cx)

for i in range(len(x)):
    for j in range(i):
        a = df.attract(x[i], x[j], 0.3)
        print('{:} & {:} = '.format(i, j), end='')
        print(a)
