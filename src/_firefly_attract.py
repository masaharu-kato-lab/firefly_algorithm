import discrete_firefly as df

nodes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

n = 5
x = df.sample(nodes, n)
for cx in x:
    print(cx)

for i in range(len(x)):
    for j in range(i):
        print('{:} & {:} : '.format(i, j))
        a = df.beta_step(x[i], x[j], 0.3)
        a = df.alpha_step(a, 2)
        #print('{:} & {:} = '.format(i, j), end='')
        #print(a)
