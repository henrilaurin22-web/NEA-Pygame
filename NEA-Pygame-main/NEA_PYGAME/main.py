import random, pygame, math, time, heapq, json, sys
from operator import add
#---CLASSES---#

class Queue:
   def __init__(self):
       self.Queue = []
       self.Counter = 0

   def enqueue(self, Element, Priority):
       heapq.heappush(self.Queue, (Priority, self.Counter, Element))
       self.Counter +=1 

   def dequeue(self):
       return heapq.heappop(self.Queue)[2]

   def peek(self):
       if self.isEmpty():
           return "Queue is empty"
       return self.Queue[0]

   def Megapeek(self):
       if self.isEmpty():
           return "Queue is empty"
       return self.Queue

   def isEmpty(self):
       return len(self.Queue) == 0

   def size(self):
       return len(self.Queue)

   def display(self):
       print(self.Queue)

   def Destroy(self):
       self.Queue.clear()
       self.Counter = 0

class Cell:
   def __init__(self):
       self.Weight = int(0)
       self.Coordinates = ()
       self.Previousvertex = (0,0)
       self.ObjType = None

   def SetCoordinates(self, Tup):
       self.Coordinates = (Tup)

   def SetWeight(self, W):
       self.Weight = int(W)

   def SetPrevious(self, Vertex):
       self.Previousvertex = Vertex

   def SetType(self, NewType):
       self.ObjType = NewType

   def GetCoordinates(self):
       return self.Coordinates

   def GetPosition(self):
       return ConvertNumCoord(self.Coordinates, 0)

   def GetWeight(self):
       return self.Weight #The cell object that gets put into a grd of width x height

   def GetType(self):
       return self.ObjType

   def GetPrevious(self):
       return self.Previousvertex

class Person:
    def __init__(self):
        self.Speed = 2  # blocks per tick
        self.Age = 10
        self.ObjType = PERSON
        self.Colour = PERSON
        self.Location = tuple()
        self.DistanceTraveled = 0
        self.ColourMultiplier = (0, 0, 0)
        self.WaitTime = 0
        self.WaitTicker = 0

    def __del__(self):
        return

    def GetType(self):
        return self.ObjType

    def SetType(self, NewType):
        if NewType not in [FLOORCOLOUR, PATH, STARTCOLOUR, DESTINATION, CONNECTOR]:
            self.ObjType = NewType

    def SetPosition(self, NPos):
        self.Location = NPos

    def GetPosition(self):
        return self.Location

    def GetPrevious(self):
        return self.Location  # When asked for previous just return itself

    def SetPrevious(self, v):
        return

    def GetWeight(self):
        return 0

    def SetWeight(self, w):
        return

    def GetSpeed(self):
        return self.Speed

    def SetSpeed(self, NSpeed):
        self.Speed = NSpeed

    def GetDistance(self):
        return self.DistanceTraveled

    def AddToDistance(self, ND):
        self.DistanceTraveled += ND

    def Destroy(self):
        if self in PeopleList:
            PeopleList.remove(self)
            PeoplePositions.discard(self.GetPosition())
        del self

    def SetMultiplier(self, Nm):
        self.ColourMultiplier = Nm

    def GetNewColour(self):
        return tuple(map(add, self.ObjType, self.ColourMultiplier))

    def GetWaitTime(self):
        return self.WaitTime

    def SetWaitTime(self, NT):
        self.WaitTime = NT

    def GetWaitTicker(self):
        return self.WaitTicker

    def SetWaitTicker(self, NWT):
        self.WaitTicker = NWT

    def CanPersonMove(self):
        if self.WaitTicker >= self.WaitTime:
            self.WaitTicker = 0
            self.WaitTime = 0
            return True
        return False



#--INITIALISE ALL GRIDS, BOARDS, DICTIONARIES--#

def LoadValues():
    with open("config.json", "r") as f:
        return json.load(f)

Config = LoadValues()

#The size of the board:
GRIDWIDTH = Config["GWIDTH"]
GRIDHEIGHT = Config["GHEIGHT"]

AREA = GRIDWIDTH*GRIDHEIGHT

#Box scales
SQUAREWIDTH = 60 
SQUAREHEIGHT = 0.4 * SQUAREWIDTH #Should be 40% of SQUAREWIDTH

OFFSET = SQUAREWIDTH//15 # distance between "Pixels" AKA border thickness

#Types - just rgbs for now
BGCOLOUR = (133, 199, 222)
FLOORCOLOUR = (180, 134, 159)
STARTCOLOUR = (44, 81, 76)
DESTINATION = (44, 81, 76)
PATH = (219, 173, 106)
WALL = (128, 128, 128)
FIRE = (241, 136, 5)
PERSON = (232, 204, 191)
CONNECTOR = (75, 63, 114)
CONSTANTTILE = [FIRE, WALL, CONNECTOR, PERSON]#List of tiles i dont want to be overwritten

#The weights of all the types
FLOORWEIGHT = 1
WALLWEIGHT = 4
FIREWEIGHT = 2
CONNECTORWEIGHT = 2
PEOPLEWEIGHT = 10

#For drawing:
BORDER = 2* math.sqrt(2*OFFSET**2) # The first 2* is just a bigger Offset

#Game settings
TICKRATE = 60
GAMESPEED = Config["GSPEED"] #How many seconds before it updates
#PEOPLEAMOUNT = Config["PEOPLE"]

CurrentDrawState = 0
STATES = [WALL, CONNECTOR, PERSON, FIRE]
HIGHLIGHTED = tuple(map(add, STATES[CurrentDrawState], (-10,-10,-10)))

GameRunning = False
Count = 0

PeopleList = []
TotalPeopleAmount = 0
DeadPeople = []
PeoplePositions = set()
NewPeoplePositions = set()

#Statistics varibles - to be used at the end for stats
PeopleWhoMadeIt = []
PeopleWhoDidNotMakeIt = []
TimePassed = 0

DJQ = Queue() #Create a queue

#Level variables
MAXBoardLevels = Config["MLevels"] #How many board layers??
BoardLevels = [None] + [[] for _ in range(MAXBoardLevels)] #Array of availiable BoardLevels
CurrentLevel = 1

#Resolution calculations
#ScreenWIDTH = math.ceil(GRIDWIDTH * (math.sqrt((SQUAREWIDTH * SQUAREWIDTH) + (SQUAREHEIGHT * SQUAREHEIGHT)) + OFFSET)) #CALCULATES THE DIAGONALWIDTH OF SQUARE AND BASES SCREEN OFF THAT
#ScreenHEIGHT = math.ceil(GRIDHEIGHT * (math.sqrt((SQUAREWIDTH * SQUAREWIDTH) + (SQUAREHEIGHT * SQUAREHEIGHT)) + OFFSET) *0.6) + (SQUAREHEIGHT*(MAXBoardLevels)) #IF ISSUE WITH SCALING TRY REMOVING /2

ScreenWIDTH = int(
    (GRIDWIDTH + GRIDHEIGHT) * (SQUAREWIDTH // 2 + OFFSET)
)

ScreenHEIGHT = int(
    (GRIDWIDTH + GRIDHEIGHT) * (SQUAREHEIGHT // 2 + OFFSET)
    + MAXBoardLevels * SQUAREHEIGHT
)

Graph ={}# Graph variable, stored as num of box (1-range): [num of neighbour box (1-range), weight of relationship]
LayerConnectors = {}#The points at which you can go between the layers

PathWeights = {} #How far is each node from the root

Visited = set() #Array containing order visited by algorithm
Path = [] #Array that shows the nodes visited to get from one point to another

pygame.init()

def ProjISO(Coords):
    x,y = Coords
    return (((x-y) * (SQUAREWIDTH//2 + OFFSET)+ ScreenWIDTH // 2),
            ((x+y) * (SQUAREHEIGHT//2 + OFFSET)+(MAXBoardLevels * SQUAREHEIGHT)))

def DrawFloor(Position):
    Colour = (FLOORCOLOUR[0] - 20, FLOORCOLOUR[1] - 20, FLOORCOLOUR[2] + 20)
    XPos, YPos = ProjISO(Position)
    PolyPoints = [
        (XPos, YPos - 2*OFFSET),
        ((ProjISO((GRIDWIDTH,1))[0] + (SQUAREWIDTH // 2) + BORDER)  , (ProjISO((1,GRIDHEIGHT))[1]) + (SQUAREHEIGHT // 2)), #Right point
        (XPos, ProjISO((GRIDWIDTH, GRIDHEIGHT))[1] + SQUAREHEIGHT + 2*OFFSET),
        ((ProjISO((1,GRIDHEIGHT))[0] - (SQUAREWIDTH // 2) - BORDER) , (ProjISO((1,GRIDHEIGHT))[1]) + (SQUAREHEIGHT // 2)) # left
    ]
    pygame.draw.polygon(Screen, Colour, PolyPoints)

def DrawBase():
    DefaultPosition = (1,1)

    #Draw Floor
    DrawFloor(DefaultPosition)

    #Draw the Left Wall
    Colour = (FLOORCOLOUR[0] - 10, FLOORCOLOUR[1] - 10, FLOORCOLOUR[2] + 10)
    XPos, YPos = ProjISO(DefaultPosition)
    PolyPoints = [
            ((ProjISO((1,GRIDHEIGHT))[0] - (SQUAREWIDTH // 2) - BORDER) , (ProjISO((1,GRIDHEIGHT))[1]) + (SQUAREHEIGHT // 2)), # Top Left
            (XPos, ProjISO((GRIDWIDTH, GRIDHEIGHT))[1] + SQUAREHEIGHT + 2*OFFSET), #Top right
            (XPos, ScreenHEIGHT), #Bottom Right
            ((ProjISO((1,GRIDHEIGHT))[0] - (SQUAREWIDTH // 2) - BORDER) , ScreenHEIGHT) # Bottom Left
        ]
    pygame.draw.polygon(Screen, Colour, PolyPoints)

    #Draw the Right Wall
    Colour = (FLOORCOLOUR[0] - 30, FLOORCOLOUR[1] - 30, FLOORCOLOUR[2] + 30)
    XPos, YPos = ProjISO(DefaultPosition)
    PolyPoints = [
            ((ProjISO((GRIDWIDTH,1))[0] + (SQUAREWIDTH // 2) + BORDER) , (ProjISO((1,GRIDHEIGHT))[1]) + (SQUAREHEIGHT // 2)), # Top Right
            (XPos, ProjISO((GRIDWIDTH, GRIDHEIGHT))[1] + SQUAREHEIGHT + 2*OFFSET), #Top Left
            (XPos, ScreenHEIGHT), #Bottom Left
            ((ProjISO((GRIDWIDTH,1))[0] + (SQUAREWIDTH // 2) + BORDER) , ScreenHEIGHT) # Bottom Right
        ]
    pygame.draw.polygon(Screen, Colour, PolyPoints)    

def DrawCube(Position, Height, Width, Type):
    global CurrentLevel
    Colour = Type
    Height = (1-Height) * SQUAREHEIGHT
    Width = (1-Width) * SQUAREWIDTH//2
    Position = tuple(map(add, Position, (-1,-1)))

    XPos, YPos = ProjISO((Position[0], Position[1]))
    PolyPoints = [
                (XPos, YPos + Height + Width//2), #Top
                (XPos + SQUAREWIDTH // 2 - Width, YPos + SQUAREHEIGHT // 2 + Height), #Right
                (XPos, YPos + SQUAREHEIGHT + Height), #Bottom
                (XPos - SQUAREWIDTH // 2 + Width, YPos + SQUAREHEIGHT // 2 + Height) #Left
            ]
    pygame.draw.polygon(CubeSurface, Colour, PolyPoints) #Draw Top of cube

    Colour = (
    max(0, Colour[0] - 10),
    max(0, Colour[1] - 10),
    min(255, Colour[2] + 10),
    Colour[3]
    )
    XPos, YPos = ProjISO(Position)
    PolyPoints = [
                (XPos - SQUAREWIDTH // 2 + Width, YPos + SQUAREHEIGHT//2 + Height), #Top Left
                (XPos- SQUAREWIDTH // 2 + Width, YPos + 2*SQUAREHEIGHT-OFFSET), #Bottom left
                (XPos, YPos + 2.5*SQUAREHEIGHT - Width//2 - OFFSET), #Bottom Right
                (XPos, YPos + SQUAREHEIGHT + Height-Width//2) #Top Right
            ]
    pygame.draw.polygon(CubeSurface, Colour, PolyPoints) #Draw Left side of cube

    Colour = (
    max(0, Colour[0] - 10),
    max(0, Colour[1] - 10),
    min(255, Colour[2] + 10),
    Colour[3]
    )
    XPos, YPos = ProjISO(Position)
    PolyPoints = [
                (XPos + SQUAREWIDTH // 2 - Width, YPos + SQUAREHEIGHT//2 + Height), #Top Right
                (XPos + SQUAREWIDTH // 2 - Width, YPos + 2*SQUAREHEIGHT-OFFSET), #Bottom right
                (XPos, YPos + 2.5*SQUAREHEIGHT - Width//2 - OFFSET), #Bottom left
                (XPos, YPos + SQUAREHEIGHT + Height-Width//2) #Top Left
            ]
    pygame.draw.polygon(CubeSurface, Colour, PolyPoints) #Draw Right side of cube

#--CONVERSIONS AND MAINTENENCE--#

def ConvertNumCoord(Coord, Choice): #Convert a number to a grid coordinate
   if Choice == 0: #Coord to num
       if Coord[1] == 0:
           return Coord[0]
       else:
           return (Coord[0] + ((Coord[1]-1) * GRIDWIDTH))
   elif Choice == 1: #num to coord
       return (((Coord-1)%GRIDWIDTH) + 1,((Coord-1)//GRIDWIDTH) + 1)

def ConvertMouseToBox(Mouse_Position):
    XPos, YPos = Mouse_Position

    GridXF = (((YPos - (MAXBoardLevels * SQUAREHEIGHT)) / (SQUAREHEIGHT/2 + OFFSET) +
          (XPos - (ScreenWIDTH // 2)) / (SQUAREWIDTH/2 + OFFSET))) / 2

    GridYF = (((YPos - (MAXBoardLevels * SQUAREHEIGHT)) / (SQUAREHEIGHT/2 + OFFSET) -
          (XPos - (ScreenWIDTH // 2)) / (SQUAREWIDTH/2 + OFFSET) )) / 2

    GridX = math.floor(GridXF) + (CurrentLevel-1)
    GridY = math.floor(GridYF) + (CurrentLevel-1) #To realign with inital offset (1 extra up)

    if (GridX) > GRIDWIDTH or GridY > GRIDHEIGHT or GridX <= 0 or GridY <= 0:
        return None

    return ConvertNumCoord(((GridX), GridY), 0 ) #Convert mouse click to grid number

def SetRoot(NewRoot):
    global Root

    Root = NewRoot
    CurrentLevel, CurrentNumber = NewRoot
    BoardLevels[CurrentLevel][CurrentNumber-1].SetWeight(FLOORWEIGHT)
    UpdateWeights(Root)

def SetEnd(NewEnd):
    global End

    End = NewEnd
    CurrentLevel, CurrentNumber = NewEnd
    BoardLevels[CurrentLevel][CurrentNumber-1].SetType(DESTINATION)
    BoardLevels[CurrentLevel][CurrentNumber-1].SetWeight(FLOORWEIGHT)
    UpdateWeights(End)

def RandomPos():
    return (random.randint(1,MAXBoardLevels),random.randint(1, (GRIDWIDTH*GRIDHEIGHT))) #I use this to spawn a fire

def SetVars(RepeatLevel):
    global PathWeights
    global DJQ
    global Visited
    global Path
    global BoardLevels
    global Graph

    BoardLevels[RepeatLevel] = [Cell() for _ in range(AREA)] #Assign a cell object to every number in every level

    for x in range(AREA):
        BoardLevels[RepeatLevel][x].SetCoordinates(ConvertNumCoord(x + 1, 1))
        BoardLevels[RepeatLevel][x].SetWeight(FLOORWEIGHT)
        BoardLevels[RepeatLevel][x].SetType(FLOORCOLOUR)

    for x in range(1, len(BoardLevels[RepeatLevel]) + 1):
        Graph.setdefault((RepeatLevel, x), {})

        # Left Neighbour
        if((x-1) >= 1 and x % GRIDWIDTH != 1):
            Graph[(RepeatLevel, x)][(RepeatLevel, x-1)] = BoardLevels[RepeatLevel][(x-1)-1].GetWeight()

        # Right Neighbour
        if((x+1) <= (AREA) and x % GRIDWIDTH != 0):
            Graph[(RepeatLevel, x)][(RepeatLevel, x+1)] = BoardLevels[RepeatLevel][(x+1)-1].GetWeight()

        # Down Neighbour
        if((x+GRIDWIDTH) <= (AREA)):
            Graph[(RepeatLevel, x)][(RepeatLevel, x+GRIDWIDTH)] = BoardLevels[RepeatLevel][(x+GRIDWIDTH)-1].GetWeight()

        # Up Neighbour
        if((x-GRIDWIDTH) >= 1):
            Graph[(RepeatLevel, x)][(RepeatLevel, x-GRIDWIDTH)] = BoardLevels[RepeatLevel][(x-GRIDWIDTH)-1].GetWeight()

        # LeftUpDiagonal Neighbour
        if((x-1) >= 1 and x % GRIDWIDTH != 1 and (x+GRIDWIDTH) <= (AREA)):
            Graph[(RepeatLevel, x)][(RepeatLevel, x-1+GRIDWIDTH)] = BoardLevels[RepeatLevel][(x-1+GRIDWIDTH)-1].GetWeight() 

        # RightUpDiagonal Neighbour
        if((x+1) <= (AREA) and x % GRIDWIDTH != 0 and (x+GRIDWIDTH) <= (AREA)):
            Graph[(RepeatLevel, x)][(RepeatLevel, x+1+GRIDWIDTH)] = BoardLevels[RepeatLevel][(x+1+GRIDWIDTH)-1].GetWeight()

        # LeftDownDiagonal Neighbour
        if((x-1) >= 1 and x % GRIDWIDTH != 1 and (x-GRIDWIDTH) >= 1):
            Graph[(RepeatLevel, x)][(RepeatLevel, x-1-GRIDWIDTH)] = BoardLevels[RepeatLevel][(x-1-GRIDWIDTH)-1].GetWeight()

        # RightDownDiagonal Neighbour
        if((x+1) <= (AREA) and x % GRIDWIDTH != 0 and (x-GRIDWIDTH) >= 1):
            Graph[(RepeatLevel, x)][(RepeatLevel, x+1-GRIDWIDTH)] = BoardLevels[RepeatLevel][(x+1-GRIDWIDTH)-1].GetWeight()

def RefreshConnections(Cell):
    global Graph, LayerConnectors

    TargetList = LayerConnectors[Cell]
    for Targets in TargetList:
        TargetLevel = Targets[0]
        TargetNumber = Targets[1]
        TargetWeight = Targets[2]

        TargetCell = (TargetLevel,TargetNumber)

        if Cell not in Graph:
            Graph[Cell] = {}

        if TargetCell not in Graph:
            Graph[TargetCell] = {}

        Graph[Cell][TargetCell] = TargetWeight

def ClearPath():
    global PathWeights, DJQ, Visited, Path, BoardLevels

    DJQ.Destroy()
    Visited.clear()
    Path = []

    for Level in range(1, len(BoardLevels)):
        for cell in BoardLevels[Level]:
            if cell.GetType() in [PATH, STARTCOLOUR, DESTINATION]: 
                cell.SetType(FLOORCOLOUR)
                cell.SetWeight(FLOORWEIGHT) #Reset paths starts and destinatoins to floor / pixel
                
            #cell.SetPrevious(0)

def UpdateWeights(GridNumberAndLevel):
    global Graph, BoardLevels
    GridLevel, GridNumber = GridNumberAndLevel

    if BoardLevels[GridLevel][GridNumber-1].GetType() != PERSON:
        NewWeight = BoardLevels[GridLevel][GridNumber-1].GetWeight()

        if GridNumberAndLevel in Graph:
            for neighbour in Graph[GridNumberAndLevel]:
                if BoardLevels[neighbour[0]][neighbour[1]-1].GetType() != PERSON:
                    Graph[GridNumberAndLevel][neighbour] = BoardLevels[neighbour[0]][neighbour[1]-1].GetWeight() #Add weights

        PossibleNeighbors = []
    
        for offset in [-1, 1, -GRIDWIDTH, GRIDWIDTH, -1+GRIDWIDTH, 1+GRIDWIDTH, -1-GRIDWIDTH, 1-GRIDWIDTH]:
            NeighborNum = GridNumber + offset
            if 1 <= NeighborNum <= AREA:
                 PossibleNeighbors.append((GridLevel, NeighborNum))

        if GridNumberAndLevel in LayerConnectors:
            for target in LayerConnectors[GridNumberAndLevel]:
                PossibleNeighbors.append((target[0], target[1]))

        for Node in PossibleNeighbors:
            if Node in Graph and GridNumberAndLevel in Graph[Node]:
                Graph[Node][GridNumberAndLevel] = NewWeight

#--GAME STUFF--#
FirePoints = []
FireFront=[] #The next wave to spread (of fire)
FireStarted = False #Decides whether a fire should be started or updated

Ticker = 0 #This is going to increase by 1 each time the function is called 
Tipper = (TICKRATE) * (GAMESPEED) #When the Ticker = Tipper * GAMESPEED then we know the game should update as it has been enough time

def EndGameAndShowStats():
    global DeadPeople, PeopleWhoDidNotMakeIt, PeopleWhoMadeIt, TimePassed, TotalPeopleAmount, running, GameRunning

    print("The game has ended!")
    print(f"The total amount of people at the start was {TotalPeopleAmount}")
    print(f"The time passed was {TimePassed} and in that time {len(PeopleWhoDidNotMakeIt)} people didnt escape the fire\n and {len(PeopleWhoMadeIt)} who escaped!")

    running = False
    pygame.quit(); sys.exit()

def CreateText(TextToShow, Location, Size):
    global TextSurface, font, TextLocation
    
    TextLocation = (Location)
    font = pygame.font.SysFont(None, Size)
    TextSurface = font.render(TextToShow, True, (255,255,255))

def CreateObject(CurrentCell, Type):
    global FirePoints, FireStarted, FireFront, PeoplePositions, TotalPeopleAmount
    CLevel, CNumber = (CurrentLevel,CurrentCell.GetPosition())

    if Type == WALL:
        Current_Cell = BoardLevels[CellLevel][CellNumber-1]
        Current_Cell.SetType(WALL)
        Current_Cell.SetWeight(WALLWEIGHT)
        UpdateWeights(SelectedCell)
    elif Type == CONNECTOR:
        if CurrentLevel < MAXBoardLevels: 
            LayerConnectors[(CurrentLevel, CNumber)] = [(CurrentLevel+1, CNumber, CONNECTORWEIGHT)]
            BoardLevels[CurrentLevel][CNumber-1].SetType(CONNECTOR)
            LayerConnectors[(CurrentLevel+1, CNumber)] = [(CurrentLevel, CNumber, CONNECTORWEIGHT)]
            BoardLevels[CurrentLevel+1][CNumber-1].SetType(CONNECTOR)
            RefreshConnections((CurrentLevel, CNumber)) #This connects everything together for dijkstras
    elif Type == PERSON:
        NewPerson = Person()
        PeopleList.append(NewPerson)
        NewPerson.SetPosition((CLevel, CNumber))
        NewPerson.SetMultiplier((-random.randint(0,50),-random.randint(0,50),-random.randint(0,50)))
        PeoplePositions.add(NewPerson.GetPosition())
        TotalPeopleAmount += 1
    elif Type == FIRE:
        BoardLevels[CurrentLevel][CNumber-1].SetType(FIRE)
        BoardLevels[CurrentLevel][CNumber-1].SetWeight(FIREWEIGHT)
        UpdateWeights((CurrentLevel,CNumber))
        FireStarted = True
        FirePoints += [(CurrentLevel,CNumber)]
        FireFront += [(CurrentLevel,CNumber)]

def CreateConnectors(AmountOfConnectors):
    global LayerConnectors

    PossibleGridPositions = [1]

    for ThisLevel in range(1,MAXBoardLevels+1):
        #Create an array for the edges of da grid
        GH = list(range(1,GRIDHEIGHT+1))
        for x in (GH):
            CN = random.choice(GH)
            if BoardLevels[ThisLevel][CN*GRIDWIDTH-1].GetType() == FLOORCOLOUR:
                PossibleGridPositions.append(CN*GRIDWIDTH-1)
                continue
            GH.remove(CN)


        GW = list(range(1,GRIDWIDTH+1))
        for x in (GW):
            CN = random.choice(GW)
            if BoardLevels[ThisLevel][GRIDWIDTH + CN].GetType() == FLOORCOLOUR:
                PossibleGridPositions.append(GRIDWIDTH + CN)
                continue
            GW.remove(CN)

        CLevel, CNumber = (ThisLevel, random.choice(PossibleGridPositions))
        if ThisLevel < MAXBoardLevels: 
            LayerConnectors[(ThisLevel, CNumber)] = [(ThisLevel+1, CNumber, CONNECTORWEIGHT)]
            BoardLevels[ThisLevel][CNumber-1].SetType(CONNECTOR)
            LayerConnectors[(ThisLevel+1, CNumber)] = [(ThisLevel, CNumber, CONNECTORWEIGHT)]
            BoardLevels[ThisLevel+1][CNumber-1].SetType(CONNECTOR)

def CreateWalls():
    WallPositions = []
    for CurrentLevel in range(1, MAXBoardLevels+1):
        for CurrentPosition in range(1, GRIDWIDTH+1): #Line the top surface with walls
            WallPositions.append((CurrentLevel, CurrentPosition))
        for CurrentPosition in range(1,GRIDHEIGHT): #Lines the left surface with walls
            WallPositions.append((CurrentLevel, (CurrentPosition*GRIDWIDTH)+1))

        if AREA >= 100: #This creates a bunch of mini cubicles
            for x in range (AREA // 50):
                MiddleNumber = random.randint(1,AREA)

                WallPositions.append((CurrentLevel, MiddleNumber))

                WallPositions.append((CurrentLevel, MiddleNumber-1))
                WallPositions.append((CurrentLevel, MiddleNumber+1))

                MiddleNumber -= GRIDWIDTH

                WallPositions.append((CurrentLevel, MiddleNumber-1))
                WallPositions.append((CurrentLevel, MiddleNumber+1))

                MiddleNumber -= GRIDWIDTH

                WallPositions.append((CurrentLevel, MiddleNumber))

                WallPositions.append((CurrentLevel, MiddleNumber-1))
                WallPositions.append((CurrentLevel, MiddleNumber+1))

                DeleteWall = random.randint(1,5) #Decides where the opening should be for the "Office"
                if DeleteWall == 1:
                    WallPositions.remove((CurrentLevel, MiddleNumber))
                elif DeleteWall == 2:
                    WallPositions.remove((CurrentLevel, MiddleNumber + GRIDWIDTH + 1))
                elif DeleteWall == 3:
                    WallPositions.remove((CurrentLevel, MiddleNumber + GRIDWIDTH -1))
                elif DeleteWall == 2:
                    WallPositions.remove((CurrentLevel, MiddleNumber + GRIDWIDTH + GRIDWIDTH))
    
    for WallCell in WallPositions: #Draw The walls (this should happen at the end of create walls)
        WLevel, WNumber = WallCell
        if WNumber < AREA and WNumber >= 1 and BoardLevels[WLevel][WNumber-1].GetType() not in [STARTCOLOUR, DESTINATION]:
            Current_Cell = BoardLevels[WLevel][WNumber-1]
            Current_Cell.SetType(WALL)
            Current_Cell.SetWeight(WALLWEIGHT)
            UpdateWeights(WallCell)

def CreatePeople(AmountOfPeople):
    global PeopleList
    for x in range(AmountOfPeople):
        CLevel, CNumber = RandomPos()
        if BoardLevels[CLevel][CNumber-1].GetType() == FLOORCOLOUR:#Creates a person on a free box
            NewPerson = Person()
            PeopleList.append(NewPerson)
            NewPerson.SetPosition((CLevel, CNumber))

def UpdateFire(StartPosition): #StartPosition should only be used once
    global FireStarted # yes or no?
    global FirePoints #All the points which have fire
    global FireFront #The front line of fire - where to spread next

    Startlevel, Startbox = (StartPosition[0], StartPosition[1])

    if not FireStarted: #Starts fire if there isnt one already
        BoardLevels[Startlevel][Startbox-1].SetType(FIRE)
        BoardLevels[Startlevel][Startbox-1].SetWeight(FIREWEIGHT)
        UpdateWeights((Startlevel,Startbox))
        FireStarted = True
        FirePoints = [StartPosition]
        FireFront = [StartPosition]
        return

    NewFront = [] #This changes based on the outside of the fire - what is allowed to spread
    
    for Position in FireFront:
        for neighbour in Graph[(Position[0],Position[1])]:
            neighbourLevel, neighbourNumber = neighbour
            neighbour_cell = BoardLevels[neighbourLevel][neighbourNumber-1]
            # Only spread to the right floor tiles
            if neighbour_cell.GetType() in [FLOORCOLOUR]: #Converts a neighbour tile to look, weigh the same as fire
                neighbour_cell.SetType(FIRE)
                neighbour_cell.SetWeight(FIREWEIGHT)
                UpdateWeights(neighbour)
                NewFront.append(neighbour)
                FirePoints.append(neighbour)
            
            elif neighbour_cell.GetType() in [CONNECTOR]: #My attempt at connecting over layers
                NewFireLevel, NewFireNumber, NewFireWeight = LayerConnectors[(neighbourLevel,neighbourNumber)][0]
                NewFireCell = BoardLevels[NewFireLevel][NewFireNumber-1]
                
                NewFireCell.SetType(FIRE)
                NewFireCell.SetWeight(FIREWEIGHT)
                UpdateWeights((NewFireLevel,NewFireNumber))
                NewFront.append((NewFireLevel,NewFireNumber))
                FirePoints.append((NewFireLevel,NewFireNumber))


    FireFront = NewFront

def UpdateDijkstras():
    global PeopleList, End, Path, FirePoints

    for CurrentPerson in PeopleList:
        CurrentPosition = CurrentPerson.GetPosition()
        PeoplePositions.add(CurrentPosition)
        
        CLevel, CNumber = CurrentPosition
        NextStep = BoardLevels[CLevel][CNumber-1].GetPrevious()

        NewPeoplePositions.add(NextStep)

    InitialiseDJ(End)

def UpdatePeople():
    global PeopleList, End, Path, FirePoints, PeoplePositions, NewPeoplePositions, PeopleWhoDidNotMakeIt, PeopleWhoMadeIt, DeadPeople

    PeoplePositions = set(p.GetPosition() for p in PeopleList)
    reserved = set()
    
    for CurrentPerson in PeopleList:
        CurrentPerson.SetWaitTicker(CurrentPerson.GetWaitTicker() + 1)
        CurrentPosition = CurrentPerson.GetPosition()

        if CurrentPosition in FirePoints:#They lwk on sum fire
            DeadPeople.append(CurrentPerson)
            PeopleWhoDidNotMakeIt.append(CurrentPerson)
            continue

        CLevel, CNumber = CurrentPosition
        NextStep = GetNextStep(CurrentPosition)

        if NextStep != (0,0) and NextStep not in PeoplePositions and NextStep not in reserved and NextStep != None:
            reserved.add(NextStep)
            
            NextWeight = BoardLevels[NextStep[0]][NextStep[1]-1].GetWeight()

            CurrentPerson.AddToDistance(NextWeight) #Log the distance

            #Change position
            if CurrentPerson.CanPersonMove() == True:
                CurrentPerson.SetPosition(NextStep)
                CurrentPerson.SetWaitTime(NextWeight)
            
            if NextStep == End:
                #They have arrived at the destination
                PeopleWhoMadeIt.append(CurrentPerson)
                DeadPeople.append(CurrentPerson)
                continue#This updates the person positions so they can refresh faster and look as if they are moving more

    for person in DeadPeople:
        person.Destroy()



#--DIJSKTRAS STUFF--#

def DJ(Cell):
    global BoardLevels
    global StartNode
    global PathWeights
   
    prev = Cell.GetPrevious()
    if prev != 0:
        Current_Node = prev
    else:
        Cell_Position = Cell.GetPosition()
        Current_Node = (CurrentLevel, Cell_Position)
    
    if Current_Node not in Graph:
        return

    Current_Total_Distance = PathWeights[Current_Node]

    for Neighbour_Position in Graph[Current_Node]:
        Neighbour_Level, Neighbour_Number = Neighbour_Position
        Neighbour_Index = Neighbour_Number-1

        if Neighbour_Level > MAXBoardLevels or Neighbour_Index >= len(BoardLevels[Neighbour_Level]):
            continue #This means SKIP (like break)

        Neighbour_Cell = BoardLevels[Neighbour_Level][Neighbour_Index]

        Distance_To = Graph[Current_Node][Neighbour_Position]
        Revised_Weight = Current_Total_Distance + Distance_To

        if Revised_Weight < PathWeights[Neighbour_Position]:
            PathWeights[Neighbour_Position] = Revised_Weight

            Level, Num = Neighbour_Position
            BoardLevels[Level][Num-1].SetPrevious(Current_Node)

            DJQ.enqueue(Neighbour_Cell, Revised_Weight)
    #print(f"Current Node: {Current_Node}, Weight: {PathWeights[Current_Node]}")
    #print(f"Neighbors: {Graph[Current_Node]}")

def InitialiseDJ(TExit):
    global DJQ, PathWeights

    Level, CellNumber = TExit

    # Reset path weights and queue
    for Level in range(1, MAXBoardLevels + 1):
        for cell in range(1, AREA + 1):
            PathWeights[(Level, cell)] = math.inf
            #BoardLevels[Level][cell-1].SetPrevious((0,0))

    PathWeights[TExit] = 0
    DJQ.Destroy()
    DJQ.enqueue(TExit, 0) 
    Visited.clear()

    while not DJQ.isEmpty():
        CurrentNodeNum = DJQ.dequeue() 
        if CurrentNodeNum in Visited:
            continue
        Visited.add(CurrentNodeNum)

        if CurrentNodeNum not in Graph:
            continue
            
        Current_Distance = PathWeights[CurrentNodeNum]
        
        for Neighbour in Graph[CurrentNodeNum]:
            NeighbourLevel, NeighbourNumber = Neighbour

            if NeighbourLevel < 1 or NeighbourLevel > MAXBoardLevels or NeighbourNumber < 1 or NeighbourNumber > AREA or isinstance(BoardLevels[NeighbourLevel][NeighbourNumber-1].GetType(), Person):
                continue
            
            NeighborCell = BoardLevels[NeighbourLevel][NeighbourNumber-1]  

            NeighbourWeight = NeighborCell.GetWeight()

            #if (NeighbourLevel, NeighbourNumber) in PeoplePositions: #If there is a person on a cell, make the cell harder to get through
                #NeighbourWeight += PEOPLEWEIGHT

            NewDistance = Current_Distance + NeighbourWeight

            if NewDistance < PathWeights.get(Neighbour, math.inf):
                PathWeights[Neighbour] = NewDistance
                NeighborCell.SetPrevious(CurrentNodeNum)
                
                DJQ.enqueue(Neighbour, NewDistance)

def GetPrevious(Node):
    global Path
    Path = []
    Current = Node

    while Current != 0 and Current is not None and Current not in Path:
        Path.append(Current)
        Lvl, Num = Current
        Current = BoardLevels[Lvl][Num-1].GetPrevious()
    
    Path.reverse()
    return Path

def GetNextStep(Cell):
    global PathWeights
    BestCell = None
    BestW = PathWeights[Cell]

    if BestW ==  math.inf:
        return None

    for CurrentW in Graph[Cell]:
        if PathWeights.get(CurrentW, math.inf) < BestW:
            BestWeight = PathWeights[CurrentW]
            BestCell = CurrentW
    
    return BestCell

def FindRoute(End, Root):
    if Root is None or End is None:
        return

    global PathWeights
    global Visited
    global DJQ
    global Path

    if len(Path) > 0:
        for Point in Path:
            lvl, num = Point
            cell = BoardLevels[lvl][num-1]
            if Point in LayerConnectors:
                cell.SetType(CONNECTOR)
            if cell.GetType() not in CONSTANTTILE:
                cell.SetType(FLOORCOLOUR)
                cell.SetWeight(FLOORWEIGHT)
            #cell.SetPrevious(0)
    
    if Root:
        r_lvl, r_num = Root
        BoardLevels[r_lvl][r_num-1].SetPrevious(0)
    
    DJQ.Destroy()
    Visited.clear()
    Path = []

    for lvl in range(1, MAXBoardLevels+1):
        for cell in range(1, AREA+1):
            PathWeights[(lvl, cell)] = math.inf

    # set the start node weight
    PathWeights[Root] = 0
    InitialiseDJ(Root)

    Path = GetPrevious(End)
    #print(f"Full path: {Path}")

    #Get path to start from a position
    #print(f"To get from {End} to {Root} you take points: {Path} with weight {PathWeights[End]}")

    if len(Path) > 0:
        if Root in Path:
            rootLevel, rootNumber = Root
            if rootLevel < len(BoardLevels):
                if not isinstance(BoardLevels[rootLevel][rootNumber-1], Person):
                    BoardLevels[rootLevel][rootNumber-1].SetType(STARTCOLOUR)

        if End in Path:
            endLevel, endNumber = End
            if endLevel < len(BoardLevels):
                BoardLevels[endLevel][endNumber -1].SetType(DESTINATION)
        
        for Point in Path:
            Level, CellNumber = Point
            if Point == Root or Point == End:
                continue
            Cell_index = CellNumber - 1

            if Level >= len(BoardLevels) or Level < 1:
                continue
            cell = BoardLevels[Level][Cell_index]

            if cell.GetType() not in CONSTANTTILE:
                cell.SetType(PATH)

#--PYGAME WINDOW-#
#Application window set up
Screen = pygame.display.set_mode((ScreenWIDTH,ScreenHEIGHT))

GridSurface = pygame.Surface((ScreenWIDTH, ScreenHEIGHT), pygame.SRCALPHA)
CubeSurface = pygame.Surface((ScreenWIDTH, ScreenHEIGHT), pygame.SRCALPHA)

font = pygame.font.SysFont(None, 24)
TextLocation = (0,0)
TextSurface = font.render("Hello World", True, (255,255,255))

pygame.display.set_caption("Fire in the Office!")

#Tick speed
Clock = pygame.time.Clock()

#Background set up
Surface_grid = [] #Visual feedback of board
Grid_Colliders = []

def DrawGrid(TopLevel):
    level_alpha = {
        lvl: max(40, int(255 * ((lvl) / TopLevel)))
        for lvl in range(1, TopLevel + 1)} #Calculate all the ranges the transparency can be and puts them in a dictionary

    for RepeatLevel in range (1, TopLevel+1):

        GridSurface.fill((0,0,0,0)) #Clears the surfaces
        CubeSurface.fill((0,0,0,0))

        if RepeatLevel == TopLevel and TopLevel != 1: #We are drawing the top floor
            Offs = (RepeatLevel-1)

            X0, Y0 = ProjISO((1-Offs, 1-Offs))
            X1, Y1 = ProjISO((GRIDWIDTH-Offs, 1-Offs))
            X2, Y2 = ProjISO((GRIDWIDTH-Offs, GRIDHEIGHT-Offs))
            X3, Y3 = ProjISO((1-Offs, GRIDHEIGHT-Offs))

            PolyPoints = [
                (X0, Y0  - 2*OFFSET),                          # Top
                (X1 + (SQUAREWIDTH // 2) + OFFSET + BORDER, Y1 + (SQUAREHEIGHT//2)),                  # Right
                (X2, Y2 + (SQUAREHEIGHT) + 2*OFFSET),                          # Bottom
                (X3 - (SQUAREWIDTH // 2) - OFFSET - BORDER, Y3+ (SQUAREHEIGHT//2))                   # Left
            ]
            pygame.draw.polygon(GridSurface, FLOORCOLOUR, PolyPoints) #ISOMETRIC DRAWING OF EACH CELL

        for x in range(1,GRIDWIDTH+1):
            for y in range(1,GRIDHEIGHT+1):
                Cell_Index = ConvertNumCoord((x,y),0)-1

                XPos, YPos = ProjISO((x - (RepeatLevel-1),y - (RepeatLevel-1))) #-1 because I dont want it to move up on the first level

                BaseColour = BoardLevels[RepeatLevel][Cell_Index].GetType()
                Alpha = level_alpha[RepeatLevel]
                Type = (*BaseColour, Alpha) #Add the transparency of the grid

                FlatTiles = [FLOORCOLOUR, CONNECTOR, HIGHLIGHTED]
                if (Type[:3] in FlatTiles):
                    Type = (
                            max(0, Type[0] - 15),
                            max(0, Type[1] - 15),
                            min(255, Type[2] + 15),
                            Type[3]
                        )
                    PolyPoints = [
                        (XPos, YPos), #Top
                        (XPos + SQUAREWIDTH // 2, YPos + SQUAREHEIGHT // 2), #Right
                        (XPos, YPos + SQUAREHEIGHT), #Bottom
                        (XPos - SQUAREWIDTH // 2, YPos + SQUAREHEIGHT // 2) #Left
                    ]
                    pygame.draw.polygon(GridSurface, Type, PolyPoints) #ISOMETRIC DRAWING OF EACH CELL
                elif Type[:3] == PATH: #Draw a cubed path
                    DrawCube((x - (RepeatLevel-1),y - (RepeatLevel-1)), 0.4, 0.5, Type) #+Current level to offset the y and look like its above the other stuff
                elif Type[:3] != PERSON:
                    DrawCube((x- (RepeatLevel-1),y - (RepeatLevel-1)), 0.6, 0.8, Type)

                for CurPerson in PeopleList: #Iterate and draw each person in this level
                    if CurPerson.GetPosition() == (RepeatLevel, Cell_Index+1):
                        DrawCube((x - (RepeatLevel-1),y - (RepeatLevel-1)), 2, 0.5, (*CurPerson.GetNewColour(), Alpha))

        #This is where the surfaces are "baked" on the screen
        Screen.blit(TextSurface, TextLocation) #Prints text on the screen
        Screen.blit(GridSurface, (0,0)) #Prints the grid blocks onto the screen
        Screen.blit(CubeSurface, (0,0))#Prints the cubes onto the screen
    

#--MAIN CODE--#
for z in range (1, len(BoardLevels)):
    SetVars(z) #Run at start for each grid level

SetEnd((1, GRIDWIDTH+2)) # This is the "Fire exit"

HighlightedCell = None #This is set to none so that I can overwrite it later to show which cell is hovered on

#Stuff that happens first but never again
CreateWalls()
CreateConnectors(1) #Put in the amount per layer
for Cell in LayerConnectors: #For each connector - fresh dijksrtas weights
    RefreshConnections(Cell)

#CreatePeople(PEOPLEAMOUNT) #Create an amount of people

Root = RandomPos()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEWHEEL:#Scrolling to change the layer
            #print(f"Mouse wheel scrolled: x={event.x}, y={event.y}")
            if event.y > 0:
                if CurrentLevel+1 < len(BoardLevels):
                    CurrentLevel += 1
            elif event.y < 0:
                if CurrentLevel > 1:
                    CurrentLevel -= 1
        if not GameRunning:
            Keys = pygame.key.get_pressed()

            CSTATE = STATES[CurrentDrawState]
            if CSTATE == WALL: #Set the text to say what you are placing
                CreateText(f"Place some Walls!", (ScreenWIDTH//15, ScreenHEIGHT//12), 60)
            elif CSTATE == CONNECTOR:
                CreateText(f"Place some inter-layer-connectors!", (ScreenWIDTH//15, ScreenHEIGHT//12), 60)
            elif CSTATE == FIRE:
                CreateText(f"Place some Fire!", (ScreenWIDTH//15, ScreenHEIGHT//12), 60)
            elif CSTATE == PERSON:
                CreateText(f"Place some People!", (ScreenWIDTH//15, ScreenHEIGHT//12), 60)

            Constants = [DESTINATION, STARTCOLOUR] #Things to NOT overwrite when clicking
                
            MousePosition = pygame.mouse.get_pos()
            SelectedCell = (CurrentLevel,ConvertMouseToBox(MousePosition))
            CellLevel, CellNumber = SelectedCell
            if CellNumber != None:
                CurrentType = BoardLevels[CellLevel][CellNumber-1].GetType()
            
                if CurrentType == FLOORCOLOUR: #Show the cell youre currrently hovering over
                    if HighlightedCell != None:
                        OldCellLevel, OldCellNumber = HighlightedCell #The old cell

                        if BoardLevels[OldCellLevel][OldCellNumber-1].GetType() == HIGHLIGHTED: #Replace cells that are just highlighted not cells ive drawn on
                            BoardLevels[OldCellLevel][OldCellNumber-1].SetType(FLOORCOLOUR)

                    BoardLevels[CellLevel][CellNumber-1].SetType(HIGHLIGHTED)
                    HighlightedCell = SelectedCell

            elif CellNumber == None:
                if HighlightedCell != None:
                    OldCellLevel, OldCellNumber = HighlightedCell #The old cell
                    BoardLevels[OldCellLevel][OldCellNumber-1].SetType(FLOORCOLOUR)


            if Keys[pygame.K_w]:        
                if SelectedCell[1] != None:
                    if BoardLevels[CellLevel][CellNumber-1].GetType() not in Constants and BoardLevels[CellLevel][CellNumber-1].GetType() != WALL and ((CellLevel,CellNumber) not in PeoplePositions):
                        CreateObject(BoardLevels[CellLevel][CellNumber-1], STATES[CurrentDrawState])
            elif Keys[pygame.K_d]:
                if CellNumber != None and BoardLevels[CellLevel][CellNumber-1].GetType() not in Constants:
                    Current_Cell = BoardLevels[CellLevel][CellNumber-1]
                    Current_Cell.SetType(FLOORCOLOUR)
                    Current_Cell.SetWeight(FLOORWEIGHT)
                    UpdateWeights(SelectedCell)
                    for CurrentPerson in PeopleList: #This might be laggy - #Also get rid of people in those positions
                        if CurrentPerson.GetPosition() == (CellLevel,CellNumber):
                            CurrentPerson.Destroy()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: # Enter key pressed - move on to what to draw
                    if HighlightedCell != None:
                        OldCellLevel, OldCellNumber = HighlightedCell #The old cell
                        if BoardLevels[OldCellLevel][OldCellNumber-1].GetType() == HIGHLIGHTED:
                            BoardLevels[OldCellLevel][OldCellNumber-1].SetType(FLOORCOLOUR)
                        HighlightedCell = None
                    
                    if CurrentDrawState+1 < len(STATES):
                        CurrentDrawState +=1
                        HIGHLIGHTED = tuple(map(add, STATES[CurrentDrawState], (-10,-10,-10)))

                    elif CurrentDrawState+1 >= len(STATES):
                        GameRunning = True
                        CreateText("Fire is coming, Run!", (ScreenWIDTH//15, ScreenHEIGHT//12), 60)
    
    Screen.fill(BGCOLOUR) #Sets the background 
    
    DrawBase() #Draws the big cube
    DrawGrid(CurrentLevel) #Draws the Grid of the current level we are on and all the levels below it

    if GameRunning: #When the drawning stage is done
        if Ticker >= Tipper: #Anything that gets called here happens at the same time at a set interval
            Count += 1
            if Count == 1:
                UpdateFire((MAXBoardLevels,RandomPos()[1])) # updates / starts a fire

            elif Count == 2:
                UpdateDijkstras()
                UpdatePeople()
                TimePassed += 1
                Count = 0
            
            if len(DeadPeople) == TotalPeopleAmount:
                EndGameAndShowStats()

            Ticker = 0

        Ticker += 1 #increment the ticker so we can see when to update

    pygame.display.flip() #Refresh screen
    Clock.tick(TICKRATE) #Set refresh rate
    

    
pygame.quit()