
nodes = {0: [0, [1, 0, 1, 48.5], [0, 1, -1, -1], [-1, 0, -1, -1], [0, -1, -1, -1]], 1: [1, [1, 0, -1, -1], [0, 1, 2, 112.0], [-1, 0, 0, 48.5], [0, -1, -1, -1]], 2: [2, [1, 0, 4, 48.0], [0, 1, -1, -1], [-1, 0, 3, 67.0], [0, -1, 1, 112.0]], 3: [3, [1, 0, 2, 67.0], [0, 1, -1, -1], [-1, 0, -1, -1], [0, -1, -1, -1]], 4: [4, [1, 0, -1, -1], [0, 1, -1, -1], [-1, 0, 2, 48.0], [0, -1, 5, 132.5]], 5: [5, [1, 0, -1, -1], [0, 1, 4, 132.5], [-1, 0, -1, -1], [0, -1, -1, -1]]}

def getLeastTraversedPartnerPosition(nodeid, traversions):
    node = nodes[nodeid]
    res = (-1, -1)
    minTrav = 9999999999
    minDist = 9999999999
    for i in range(1,5):
        edge = node[i]
        destination = edge[2]
        distance = edge[3]
        if  destination != -1:
            if traversions[destination] < minTrav or (traversions[destination] == minTrav and distance < minDist):
                res = (destination ,i)
                minTrav = traversions[destination]
                minDist = distance
    return res




def createPath():
    current = 0
    distance = 0
    traversions = {}
    traversednodes = 0
    path = []
    for n in nodes.keys():
        traversions[n] = 0
    while traversednodes < len(nodes.keys()):
        if traversions[current] == 0:
            traversednodes += 1
        traversions[current] += 1
        nextPosition = getLeastTraversedPartnerPosition(current, traversions)
        distance = nodes[current][nextPosition[1]][3]
        path.append([nextPosition[0],nextPosition[1], distance])
        current = nodes[current][nextPosition[1]][2]
        print(traversions)
    return path

path = createPath()
print(path)