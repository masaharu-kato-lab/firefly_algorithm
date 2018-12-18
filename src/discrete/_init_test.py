import numpy as np
import matplotlib.pyplot as plt
import distance
import init




def main():
    print('hogehoge')

    # 乱数を生成
    pts = []
    for _ in range(100):
        pts.append(np.array([np.random.rand(), np.random.rand()]))

    nodes = list(range(100))

    base_nodes = np.random.choice(nodes, 6, replace=False)

    nodes_in_class = init.cluster(
        base_nodes,
        nodes,
        lambda n1, n2: np.linalg.norm(pts[n1] - pts[n2])
    )

    classes = [None] * len(pts)

    for class_id, nodes in enumerate(nodes_in_class):
        for node in nodes:
            classes[int(node)] = class_id


    plt.scatter(
        [pt[0] for pt in pts],
        [pt[1] for pt in pts],
        c=classes,
    )

    plt.scatter(
        [pts[node][0] for node in base_nodes],
        [pts[node][1] for node in base_nodes],
        s = 100,
        marker='+'
    )

    # 散布図を描画
    plt.title("This is a title")
    plt.xlabel("x axis")
    plt.ylabel("y axis")
    plt.grid(True)
    plt.show()





if __name__ == '__main__':
	main()
