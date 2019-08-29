import numpy as np
import settings as sts
import pickle


#Class definition :

class Node:
    def __init__(self,value,point):
        self.value = value
        self.point = point
        self.parent = None
        self.angle = -1
        self.H = 0
        self.G = 0.0
        self.D = 0.0
        self.T = 0


class Final_Path:
    def __init__(self,point,time):
        self.point = point
        self.T = time


#Annex Function to aStar :

def children(point,grid):
    x,y = point.point
	# No diag
	#links = [grid[d[0]][d[1]] for d in [(x-1, y),(x,y - 1),(x,y + 1),(x+1,y)]]
	# With diag
    links = [grid[d[0]][d[1]] for d in [(x-1, y),(x,y - 1),(x,y + 1),(x+1,y),(x+1,y+1),(x+1,y-1),(x-1,y+1),(x-1,y-1)]]
    return [link for link in links if link.value != 1]


#Unused at the moment, function for getting children in function of the angle of the movement
def adaptiveChildren(actualPos, grid, lastPos):
	x,y = actualPos
	a, b = lastPos
	c = x + (x - a)
	d = y + (y - b)
	if(c == x):
		links = [grid[d[0]][d[1]] for d in [(c+1, d),(c-1 ,d),(c, d)]]
	elif(d == y):
		links = [grid[d[0]][d[1]] for d in [(c, d),(c,d - 1),(c,d + 1)]]
	else:
		links = [grid[d[0]][d[1]] for d in [(c, d),(c, y),(c, d)]]
	return [link for link in links if link.value != 1]
        

def calculVector(point1, point2):
	return(point1[0] - point2[0], point1[1] - point2[1])

def absolute(x):
	if x < 0:
		return -x
	else:
		return x

#Determinate the angle of te drone movement with the vector of this movement
def calculAngle(vector):
	switcher = {
		(1,0):0,
		(1,1):45,
		(0,1):90,
		(-1,1):135,
		(-1,0):180,
		(-1,-1):225,
		(0,-1):270,
		(1,-1):315
	}
	return switcher.get(vector, "Invalid vector")

# Unused, this fonction can get the precedent point of the path with the angle
def getOldPoint(angle):
	switcher = {
		0:(-1,0),
		45:(-1,-1),
		90:(0,1),
		135:(-1,1),
		180:(-1,0),
		225:(-1,-1),
		270:(0,-1),
		315:(-1,1)
	}
	return switcher.get(angle, "Invalid Angle")


#Function of an adaptive cost to give a different value of G to return to Astar to get a more realistic movement

def adaptivecost(angle1, angle2, dist, point1, point2):
	if(angle1 != -1):
		res = angle1 - angle2
		res = absolute(res)
		if(res == 0):
			return dist
		elif((res == 45)or(res==315)):
			return sts.ADAPTIVE_45
		elif((res == 90)or(res==270)):
			if((point1.point[0]==point2.point[0])or(point1.point[1]==point2.point[1])):
				return sts.ADAPTIVE_90_1
			else:
				return sts.ADAPTIVE_90_2
		elif((res == 135)or(res==225)):
			return sts.ADAPTIVE_135
		else:
			if((point1.point[0]==point2.point[0])or(point1.point[1]==point2.point[1])):
				return sts.ADAPTIVE_180_1
			else:
				return sts.ADAPTIVE_180_2
	else:
		return dist




def distance(point1, point2, angle1, angle2):
	if(angle1 != -1):
		res = angle1 - angle2
		res = absolute(res)
		if(res == 0):
			if((point1.point[0]==point2.point[0])or(point1.point[1]==point2.point[1])):
				return sts.LENGTH_0_1
			else:
				return sts.LENGTH_0_2
		elif((res == 45)or(res==315)):
			return sts.LENGTH_45
		elif((res == 90)or(res==270)):
			if((point1.point[0]==point2.point[0])or(point1.point[1]==point2.point[1])):
				return sts.LENGTH_90_1
			else:
				return sts.LENGTH_90_2
		elif((res == 135)or(res==225)):
			return sts.LENGTH_135
		else:
			if((point1.point[0]==point2.point[0])or(point1.point[1]==point2.point[1])):
				return sts.LENGTH_180_1
			else:
				return sts.LENGTH_180_2
	else:
		return sts.realDistance(point1, point2)*4.0

def manhattan(point1,point2):
    return abs(point1.point[0] - point2.point[0]) + abs(point1.point[1]-point2.point[1])










#aStar :

def aStar(start, goal, grid, angleStart):
    #The open and closed sets
    k=0
    openset = set()
    closedset = set()
    #angleAct = -1

    #Current point is the starting point
    current = start
    current.angle = angleStart
    #print("angleStart = ",angleStart)
    #Add the starting point to the open set
    openset.add(current)

    #While the open set is not empty
    while openset:

        #Find the item in the open set with the lowest G + H score
        current = min(openset, key=lambda o:o.G + o.H)

        #If it is the item we want, retrace the path and return it
        if current == goal:
            path = []
            times = []
            TotalTime = current.T
            Totaldistance = current.D
            angleStart = current.angle
            while current.parent:
                path.append(Final_Path(current.point, current.T))
                current = current.parent
                TotalTime += current.T
                Totaldistance += current.D
            path.append(current.point)
            path.pop()
            return (path[::-1], TotalTime, angleStart, Totaldistance)

        #Remove the item from the open set
        openset.remove(current)

        #Add it to the closed set
        closedset.add(current)

        #Loop through the node's children/siblings

        for node in children(current, grid):

            #If it is already in the closed set, skip it
            if node in closedset:
                continue

            #Otherwise if it is already in the open set
            if node in openset:
                #Check if we beat the G score
                angleAct = calculAngle(calculVector(node.point, current.point))
                dist = distance(current, node,current.angle, angleAct)
                new_g = current.G + adaptivecost(current.angle, angleAct, dist, current, node)
                if node.G > new_g:
                    #If so, update the node to have a new parent
                    node.G = new_g
                    node.D = current.D + dist
                    node.parent = current
                    node.angle = angleAct
                    node.T = sts.getTime(dist,5)
            else:
                #If it isn't in the open set, calculate the Angle, G, D and H score for the node
                node.angle = calculAngle(calculVector(node.point, current.point))
                dist = distance(current, node, current.angle, node.angle)
                node.G = current.G + adaptivecost(current.angle, node.angle, dist, current, node)
                #node.G = current.G + current.move_cost(node)
                node.H = manhattan(node, goal)
                node.D = current.D + dist
                node.T = sts.getTime(dist,sts.SPEED)
                #Set the parent to our current item
                node.parent = current
                #Add it to the set
                openset.add(node)

    #Throw an exception if there is no path
    raise ValueError('No Path Found')








#Function for Optimizer:

def checkAll(checkpoints,grid,gridInit):
	dic = {}
	for i in checkpoints:
		for j in checkpoints:
			k = 0
			while(k <= 315):
				angleStart = k
				grid = grid_constructor(gridInit)
				dic[(i,j,k)]=aStar(grid[i[0]][i[1]],grid[j[0]][j[1]],grid,angleStart)
				k = k+45
	start = checkpoints[0] 
	for i in checkpoints:
		angleStart = -1
		dic[(start,i,-1)]=aStar(grid[start[0]][start[1]],grid[i[0]][i[1]],grid,angleStart)
	print(dic)	
	pickle_out = open("ways.pickle","wb")
	pickle.dump(dic, pickle_out)
	pickle_out.close()		





#Function for Java application :

def route_builder2(route,grid,gridInit):
	j = 0
	angleStart = -1
	time = 0.0
	final_route = []
	start = route[0]
	final_route.append(Final_Path(start,0))
	newDronePosition = []
	length = len(route)
	for i in range(length-1):
		angleSave = angleStart
		drone = route[i]
		checkpoint = route[i+1]
		print('Way :', drone, '   ',checkpoint)
		grid = grid_constructor(gridInit)
		temp = aStar(grid[drone[0]][drone[1]],grid[checkpoint[0]][checkpoint[1]],grid,angleStart)
		angleStart = temp[2]
		print("done")
		if(time>650):
			angleTemp = angleStart
			grid = grid_constructor(gridInit)
			temp2 = aStar(grid[checkpoint[0]][checkpoint[1]],grid[start[0]][start[1]],grid, angleStart)
			angleStart = temp2[2]
			if(temp[1] + temp2[1] + time > 1200):
				angleStart = angleSave
				grid = grid_constructor(gridInit)
				path = aStar(grid[drone[0]][drone[1]],grid[start[0]][start[1]],grid, angleStart)
				final_route = final_route + path[0]
				angleStart = path[2]
				time = 0
				final_route.append(Final_Path((-1,-1),-1))
				final_route.append(Final_Path(start,0))
				newDronePosition.append(i + j + 1)
				j += 1
				grid = grid_constructor(gridInit)
				retur = aStar(grid[start[0]][start[1]],grid[checkpoint[0]][checkpoint[1]],grid,angleStart)
				time = retur[1]
				final_route = final_route + retur[0]
			else:
				final_route = final_route + temp[0]
				time += temp[1]
				angleStart = angleTemp
		else:
			final_route = final_route + temp[0]
			time += temp[1]
	print('Finary way :',checkpoint, '   ',start)
	grid = grid_constructor(gridInit)
	final_route = final_route + aStar(grid[checkpoint[0]][checkpoint[1]],grid[start[0]][start[1]],grid,angleStart)[0]
	for i in newDronePosition:
		route.insert(i, (-1,-1))
	return final_route, route

#def get_best_angle():

def route_builder(route,ways):
	totalTime = 0
	totalLength = 0
	#print(example_dict)
	#print(ways[((42, 162), (165, 40), 180)])
	j = 0 
	angleStart = -1
	angleSave = -1
	time = 0.0
	length = 0.0
	final_route = []
	start = route[0]
	final_route.append(Final_Path(start,0))
	newDronePosition = []
	length = len(route)
	#print(route)
	for i in range(length-1):
		drone = route[i]
		checkpoint = route[i+1]
		# print("Angle =",angleStart)
		path = ways[(drone, checkpoint, angleStart)]
		back_to_reload = ways[(checkpoint, start, path[2])]
		if (time + back_to_reload[1] + path[1] < sts.BATTERY_LIMIT_SEC):
			final_route = final_route + path[0]
			time += path[1]
			length += path[3]
			angleStart = path[2]
		else:
			angleStart = angleSave
			path = ways[(drone, start, angleStart)]
			final_route = final_route + path[0]
			totalTime += time
			totalLength += length
			final_route.append(Final_Path((-1,-1),-1))
			final_route.append(Final_Path(start,0))
			newDronePosition.append(i + j + 1)
			j += 1
			path = ways[(start, checkpoint, -1)]
			time = path[1]
			length = path[3]
			final_route = final_route + path[0]
		angleSave = angleStart
		angleStart = path[2]
	path = ways[(checkpoint, start, angleStart)]
	final_route = final_route + path[0]
	totalTime += time + path[1]
	totalLength += length + path[3]
	for i in newDronePosition:
		route.insert(i, (-1,-1))
	return final_route, route, totalTime, totalLength


# Initiallise the Grid to use the aStar algorithm, reset all nodes
def grid_constructor(gridInit):
	grid = []
	for x in range(len(gridInit)):
		line = []
		for y in range(len(gridInit[0])):
			line.append(Node(gridInit[x][y],(x,y)))
		grid.append(line)
	return grid

def big_move(route,grid,gridInit):
	#Get the route
	#route = route_builder(route,ways)
	route = route_builder2(route, grid, gridInit)
	#Output the path
	print(len(route[0]))
	map_printer(grid, route[0], gridInit)
	#Get the file name for the new file to write
	return(route)

def map_constructor(grid):
	A = np.zeros((len(grid),len(grid[0])))
	for x in range(len(grid)):
		for y in range(len(grid[0])):
			A[x][y] = grid[x][y].value
	return A


def map_printer(grid, path, gridInit):
	grid = grid_constructor(gridInit)
	A = map_constructor(grid)
	for points in path:
		x, y = points.point
		A[x][y]=2
	for x in range(len(A)):
		for y in range(len(A[0])):
			if(A[x][y]==0):
				print(" -", end = '')
			elif(A[x][y]==1):
				print("X-", end = '')
			else:
				print("O-", end = '')
		print()

