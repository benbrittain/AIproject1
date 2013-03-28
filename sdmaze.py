# Program: sdmaze.py
# Author: Ben Brittain
# Solve puzzles using A*

import sys, heapq, copy, math

class Puzzle():
    '''Stores all associated Board Information'''
    __slots__=('puzzle','start','goal','die','parent', 'cost', 'dieO')
    def __init__(self,puzzle,start,goal):
        self.puzzle = puzzle
        self.parent = None
        self.start = start
        self.goal = goal
        #y,x
        self.die = start
        self.dieO = (1,2,3)
        self.cost = 0
    def __str__(self):
        # Modified Puzzle board for enhanced viewing
        # TBA, a way of seeing prior path
        annotated = copy.deepcopy(self.puzzle)
        annotated[self.die[0]][self.die[1]] = "D"
        # Take puzzle output it to screen
        sumstr = ""
        for line in annotated:
            sumstr= sumstr + "\t" + "".join(line) + "\n"
        return sumstr.rstrip()

def goalState(puzzle):
    if (puzzle.goal == puzzle.die) and (puzzle.dieO[0] == 1):
        return True
    else:
        return False

def showSteps(puzzle):
    solution = list()
    while puzzle != None:
        solution.append(puzzle)
        puzzle= puzzle.parent
    solution.reverse()
    for x in solution:
        print x,"\n"
        
def showSolution(puzzle):
    board = copy.deepcopy(puzzle.puzzle)
    count = 0
    while puzzle.parent != None:
        count = count + 1
        board[puzzle.die[0]][puzzle.die[1]] = puzzle.dieO[0]
        puzzle = puzzle.parent
    board[puzzle.die[0]][puzzle.die[1]] = "D"
    board[puzzle.goal[0]][puzzle.goal[1]] = "G"
    sumstr = ""
    for line in board:
        sumstr= sumstr + "\t" + "".join([str(x) for x in line]) + "\n"
    print sumstr
    print str(count) + " moves were made" 

def moveDice(puzzle, direction):
    ''' move the die(Tuple) in a direction along a board'''
    # 0 - North, 1 - South,  2 - East, 3 - West
    ori = puzzle.dieO
    pos = puzzle.die
    npos = None
    card = dict(t=ori[0], e=ori[2], n=ori[1], s=7-ori[1], w= 7-ori[2], b=7-ori[0])
    if direction == 0:
        card['s'], card['n'],card['b'],card['t'] = card['b'],card['t'],card['n'],card['s']
        if pos[0] >= 1:
            npos = (pos[0]-1, pos[1])
    elif direction == 1:
        card['n'], card['s'], card['t'], card['b'] = card['b'], card['t'], card['n'], card['s']
        if pos[0] < (len(puzzle.puzzle)-1):
            npos = (pos[0]+1, pos[1])
    elif direction == 2:
        card['t'], card['b'], card['w'], card['e'] = card['w'], card['e'], card['b'], card['t'] 
        if pos[1] < (len(puzzle.puzzle[0])-1):
            npos = (pos[0], pos[1]+1)
    elif direction == 3:
        card['w'], card['e'], card['b'], card['t'] = card['t'], card['b'], card['w'], card['e']
        if pos[1] >= 1:
            npos = (pos[0], pos[1]-1)
    if npos != None:
        if puzzle.puzzle[npos[0]][npos[1]] == "*":
            npos = None
    return ((card['t'],card['n'],card['e']),npos)

def successors(puzzle):
    ''' generates successors for a dice roll in each cardinal direction, returns puzzle'''
    for cardDirection in range(0,4):
        ori, pos = moveDice(puzzle, cardDirection)
        if pos != None:
            if ori[0] != 6:
                npuzzle = copy.deepcopy(puzzle) 
                npuzzle.cost = npuzzle.cost + 1
                npuzzle.parent = puzzle
                npuzzle.dieO = ori
                npuzzle.die = pos
                yield npuzzle

def aStar(puzzle,heuristic):
    '''A* takes a puzzle & heuristic, return solved puzzle & node generation info'''
    node = (puzzle.cost, puzzle)
    frontier = [node]
    heapq.heapify(frontier) #unecessary, remove?
    explored = list()
    while True:
        if len(frontier) == 0:
            print "Failure"
            return None
        popped = heapq.heappop(frontier)
        node = popped[1]
        cost = popped[0]
        if goalState(node):
            return node, len(explored)
        explored.append((node.die,node.dieO))
        for neighbor in successors(node):
            if (neighbor.die,neighbor.dieO) not in explored:
                cost = heuristic(neighbor) + neighbor.cost
                heapq.heappush(frontier,(cost, neighbor))

def readPuzzle(fin):
    '''Read in the file & create a Puzzle Object'''
    puzzle = []
    start = (-1,-1) 
    goal = (-1,-1)
    rowCount = 0
    for line in open(fin):
        row = list(line.strip())
        #ugly, what is more pythonic?
        try:
            start = (rowCount,row.index("S"))
        except ValueError:
            pass
        try:
            goal = (rowCount,row.index("G"))
        except ValueError:
            pass
        puzzle.append(row)
        rowCount = rowCount + 1
    if start < 0 or goal < 0:
        raise "Invalid File"
    return Puzzle(puzzle,start,goal)

def manhattanCost(puzzle):
    die = puzzle.die
    goal= puzzle.goal
    cost = abs(goal[1] - die[1]) + abs(goal[0] - die[0])
    return cost

def directCost(puzzle):
    die = puzzle.die
    goal= puzzle.goal
    cost = math.sqrt((goal[1] - die[1])**2 + (goal[0] - die[0])**2)
    return cost

def diagManhattan(puzzle):
    ''' try forcing it in the diagonal direction'''
    die = puzzle.die
    goal= puzzle.goal
    x = abs(die[1]-goal[1]);
    y = abs(die[0]-goal[0]);
    if(x > y):
        return (3/2)*y + (x - y)
    else:
        return (3/2)*x + (y - x)

def rowColCost(puzzle):
    die = puzzle.die
    goal= puzzle.goal
    if die[0] == goal[0]:
        return abs(goal[0]-goal[0])
    elif die[1] == goal[1]:
        return abs(goal[1]-goal[1])
    else:
        return 0

def main():
    if len(sys.argv) != 2:
        print("Please specify an input file")        
        return
    fin = sys.argv[1]
    print("\n----- Creating Puzzle from Input -----\n")
    puzzle = readPuzzle(fin)
    print puzzle
    print("\n----- Initializing A* -----\n")
    # UCS
    heuristics={"Manhattan Cost":manhattanCost,"Direct Cost":directCost,"Diagonal Manhattan Cost":diagManhattan}
    for h in heuristics:
        print "Heuristic = "+str(h)
        solved = aStar(puzzle, heuristics[h])
        solved,searched= solved
        if solved != None:
            showSteps(solved)
        print str(searched) + " nodes were generated"
    #    print str(frontier) + " nodes were not expanded"
        print("\n----- Completed A* -----\n")
        if solved == None:
            print "No Solution Found"
            continue
        else:
            showSolution(solved)

main()
