
nodes = {0: [0, [1, 0, 1, 48.5], [0, 1, -1, -1], [-1, 0, -1, -1], [0, -1, -1, -1]], 1: [1, [1, 0, -1, -1], [0, 1, 2, 112.0], [-1, 0, 0, 48.5], [0, -1, -1, -1]], 2: [2, [1, 0, 4, 48.0], [0, 1, -1, -1], [-1, 0, 3, 67.0], [0, -1, 1, 112.0]], 3: [3, [1, 0, 2, 67.0], [0, 1, -1, -1], [-1, 0, -1, -1], [0, -1, -1, -1]], 4: [4, [1, 0, -1, -1], [0, 1, -1, -1], [-1, 0, 2, 48.0], [0, -1, 5, 132.5]], 5: [5, [1, 0, -1, -1], [0, 1, 4, 132.5], [-1, 0, -1, -1], [0, -1, -1, -1]]}
distance = {}
predecesour = {}

#res = (Zielknoten, Kantennumer)
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



#Path Bestandteil = (Zielknoten, Kantennumer, Distanz)
def createPathTroughAllNodes():
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

def initDistanceDict():
    global distance
    global predecesour
    for i in range(0, len(nodes)):
        distance[i] = []
        predecesour[i] = {}
        for j in range(0, len(nodes)):
            if j != i:
                distance[i].append(9999999999)
                predecesour[i][j] = -1
            else:
                distance[i].append(0)
                predecesour[i][j] = i
                
#Path Bestandteil = (Zielknoten, Kantennumer, Distanz)              
def createPath(start, goal):
    global distance
    global predecesour
    q = []
    for i in range(0, len(nodes)):
        q.append(i)
    
    while len(q) > 0:
        v = q[0]
        for j in q:
            if(distance[start][j] < distance[start][v]):
                v = j
        q.remove(v)
        for w in range(1, len(nodes[v])):
            edgew = nodes[v][w]
            nodew = edgew[2]
            if(q.count(nodew) > 0):
                if (distance[start][v] + edgew[3]) < distance[start][nodew]:
                    distance[start][nodew] = distance[start][v] + edgew[3]
                    predecesour[start][nodew] = v
      
    #print(distance)
    #print(predecesour)              
    res = []
    v = goal
    while v != start:
        vgoal = v
        v = predecesour[start][vgoal]
        for k in range(1, len(nodes[v])):
            if nodes[v][k][2] == vgoal:
                distance = nodes[v][k][3]
                res.insert(0, [vgoal, k, distance])
                break
    return res
                
        
initDistanceDict()
path = createPath(0, 4)
print(path)