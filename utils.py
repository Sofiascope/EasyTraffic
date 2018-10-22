# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 15:34:44 2018

@author: Sofiascope

Utils contains a list of useful function
The most important one is updatePosition, where the position of cars is
updated
"""


import numpy as np
import time
import operator
import random

import pygame
from Car import Car, CarPool
from Map import Map, Lane, Passing

def mapStruct(radius, numberVertices):
    """ Build a lane
        radius : radius of the circle, integer
        numberVertices : integer"""

    theta=np.linspace(0, 360, numberVertices)
    x=[]
    y=[]
    for i in range(len(theta)):
        x.append(radius*np.sin(theta[i]*2*np.pi/360)+450)
        y.append(radius*np.cos(theta[i]*2*np.pi/360)+400)

    listLines=[]
    for i in range(len(x)-1):
        listLines.append(([x[i],y[i]],[x[i+1],y[i+1]]))

    listPositions=[t[0] for t in listLines]

    # Return the list of vertices and their position
    return listLines, listPositions

def path(listLines):
    """ Return the path of a car in a line
        listLines : list of lines (vertices)"""
    xLines=[]
    yLines=[]
    st=0

    for l in listLines:
        startM, endM = l
        #Compute the slope
        slope=(endM[1]-startM[1])/(endM[0]-startM[0])
        x=np.linspace(startM[0],endM[0],\
                int(distance(listLines[st][0], listLines[st][1])))
        b=startM[1]-slope*startM[0]
        y=[slope*x[i]+b for i in range(len(x))]
        xLines.append(x)
        yLines.append(y)
        st=st+1
    return xLines,yLines

def closest(listLane, point, numberVertices):
    """ Return the point of the map needed to be change
        listLane : List of lane (1,2,3)
        point : Coordinates of the click point
        numberofVertices : integer"""
    distances=[]
    sizes=[]
    for lane in listLane:
        if isinstance(lane,(list,))==False:
            sizes.append(len(lane.get_positions()))
            for l in lane.get_positions():
                distances.append(((l[0]-point[0])**2+(l[1]-point[1])**2)**0.5)

    minimum= np.argmin(distances)
    # Compute the line and the corner from the line
    whichLane=minimum//numberVertices

    corner=minimum%numberVertices
    if(whichLane in [1,2]):
        corner=corner+whichLane
    if(corner==numberVertices-1):
        corner=0
        whichLane+=1


    return whichLane, corner

def closestPassing(passing, point, whichLane, isEnd):
    """ Return the passing line of the map needed to be change
        listLane : List of lane (1,2,3)
        whichLane : Lane where the passing lines belong.
        isEnd : Boolean, True ==> Consider the end of the passing line"""
    segment={}

    for p in passing:
        if(isEnd):
            toTest=p.get_end()
        else:
            toTest=p.get_start()
        p1= ((toTest[0]-point[0])**2+(toTest[1]-point[1])**2)**0.5
        segment[p]=p1
    closeSegment = min(segment, key=lambda key: segment[key])
    return passing.index(closeSegment)

def distance(a,b):
    """ Euclidean distance"""
    return ((a[0]-b[0])**2+(a[1]-b[1])**2)**0.5

def toflatten(pathX, pathY):
    """ Flatten list of paths"""
    flatten=[]
    for i in range(len(pathX)):
        for j in range(len(pathX[i])):
            flatten.append([pathX[i][j], pathY[i][j]])
    return flatten

def okay(flatten, xImg, yImg, listCars, car, distSecur, lane):
    """ Check if there is another car in front of the current one
        flatten : Flatten list
        xImg, yImg : Graphic position of the car
        listCars : List of cars
        car : The current car
        distSecur : The security distance
        lane : The lane where the car is driving"""
    # Consider all the other cars
    listCarToCheck=listCars.copy()
    listCarToCheck.pop(car)
    # Boolean value toReturn
    toReturn=True
    findC=0
    accident=False
    for c in listCarToCheck:
        if c.get_lane()==lane: #Check only car in same lane
            if([xImg, yImg] in flatten):
                posX= flatten.index([xImg, yImg])
                # Check if there is a car in the interval between
                # the current position and the security distance

                # Be careful because car are looping
                if(posX+distSecur>len(flatten)-1):
                    toCheckP1 = posX+distSecur-len(flatten)+1
                    toCheckP2 = distSecur-toCheckP1
                    positionToCheck1=\
                        [i for i in range(0,toCheckP1)]
                    positiontoCheck2=\
                    [i for i in range(len(flatten)-toCheckP2, len(flatten))]
                    positionToCheck=positiontoCheck2+positionToCheck1

                else:
                    toCheck=posX+distSecur
                    positionToCheck=[i for i in range(toCheck-distSecur,toCheck)]

                find=False
                # We modify the boolean value
                for t in positionToCheck:
                    verifX=abs(flatten[t][0]-c.get_imgx())
                    verifY=abs(flatten[t][1]-c.get_imgy())

                    if(verifX<1 and verifY<1 and find==False):
                        if(abs(t-posX)<int(distSecur*0.9)):
                            accident=True
                        toReturn=False
                        findC=c
    return toReturn, findC, accident

def checkPassing(listCars, passingPoints, listLanes, l, wEnd, k,toTransfer):
    """ Start the passing phase when needed
        listCars : List of cars
        passingPoints : List of passing points
        listLanes : List of lanes
        l : Current car
        wEnd : End of the passing path
        k : kth passing line
        toTransfer : Indicates changes between lines"""

    close=listCars.get_listCars()[l].get_curr_position()
    closeX=abs(passingPoints[0][0]-close[0])
    closeY=abs(passingPoints[0][1]-close[1])
    testReturn=False
    # Check if the car want to pass, to start the process
    if(listCars.get_listCars()[l].wPassingStart()==True and \
            (closeX<1 and closeY<1)):
            pathX, pathY = listLanes.get_path_passing(toTransfer, k)
            listCars.get_listCars()[l].path(pathX, pathY)
            listCars.get_listCars()[l].x=0
            listCars.get_listCars()[l].y=0
            listCars.get_listCars()[l].lane=3+toTransfer
            listCars.get_listCars()[l].setwPassingStart(False)
            listCars.get_listCars()[l].set_isPassing(True)
            listCars.get_listSpeed()[l]=listCars.get_listWantSpeed()[l]
            listCars.get_listCars()[l].update_pos()

    closeX=abs(passingPoints[1][0]-close[0])
    closeY=abs(passingPoints[1][1]-close[1])
    # Once the car choose the passing line, change path
    if(listCars.get_listCars()[l].wPassingStart()==False and \
            (closeX<1 and closeY<1) and \
            listCars.get_listCars()[l].get_isPassing()==True):
            pathX, pathY = listLanes.get_path_lane(1+toTransfer)
            listCars.get_listCars()[l].path(pathX, pathY)
            listCars.get_listCars()[l].x=wEnd
            listCars.get_listCars()[l].y=0
            listCars.get_listCars()[l].lane=1+toTransfer
            listCars.get_listCars()[l].set_isPassing(False)
            listCars.get_listCars()[l].setwPassingStart(True)
            listCars.get_listCars()[l].update_pos()
            listCars.get_listCars()[l].set_goBack(True)
            listCars.get_listCars()[l].set_timeUp()


    return listCars, listLanes

def goBack(listCars, passingPoints, listLanes, l, wEnd, k,toTransfer):
    """ Start the going back phase when needed
        listCars : List of cars
        passingPoints : List of passing points
        listLanes : List of lanes
        l : Current car
        wEnd : End of the passing path
        k : kth passing line
        toTransfer : Indicates changes between lines"""
    close=listCars.get_listCars()[l].get_curr_position()
    closeX=abs(passingPoints[0][0]-close[0])
    closeY=abs(passingPoints[0][1]-close[1])
    testReturn=False

    # A car can only go back after 500ms
    listCars.get_listSpeed()[l]=listCars.get_listWantSpeed()[l]
    if(time.time()-listCars.get_listCars()[l].get_timeUp()>0.5):
        # Check if the car want to pass, to start the process
        if(listCars.get_listCars()[l].wPassingStart()==True and \
                (closeX<1 and closeY<1)):
                pathX, pathY = listLanes.get_path_passing(toTransfer, k)
                listCars.get_listCars()[l].path(pathX, pathY)
                listCars.get_listCars()[l].x=0
                listCars.get_listCars()[l].y=0
                listCars.get_listCars()[l].lane=3+toTransfer
                listCars.get_listCars()[l].setwPassingStart(False)
                listCars.get_listCars()[l].set_isPassing(True)
                listCars.get_listCars()[l].update_pos()

        closeX=abs(passingPoints[1][0]-close[0])
        closeY=abs(passingPoints[1][1]-close[1])
        # Once the car choose the passing line, change path
        if(listCars.get_listCars()[l].wPassingStart()==False and \
                (closeX<1 and closeY<1)):
                if(toTransfer==2):
                    lane=0
                if(toTransfer==3):
                    lane=1
                pathX, pathY = listLanes.get_path_lane(lane)
                listCars.get_listCars()[l].path(pathX, pathY)
                listCars.get_listCars()[l].x=wEnd
                listCars.get_listCars()[l].y=0
                listCars.get_listCars()[l].lane=lane
                listCars.get_listCars()[l].setwPassingStart(True)
                listCars.get_listCars()[l].update_pos()
                testReturn=True
                listCars.get_listCars()[l].set_goBack(True)

    return listCars, listLanes, testReturn

def toBlit(listCars):
    listToBlit=[]
    myfont = pygame.font.SysFont("monospace", 15)

    # POINTS
    values = rankingCarPoint(listCars)
    sortDict = sorted(values.items(), key=lambda x: x[1])
    sortDict=sortDict[::-1]

    label = myfont.render("HIGH SCORE", 30, (0,0,0))
    listToBlit.append((label, (1100, 80)))

    x=0
    for i in range(len(sortDict)):
        text="CAR "+str(sortDict[i][0])+ "         : "+str(sortDict[i][1])
        label = myfont.render(text, 30, (0,0,0))
        listToBlit.append((label, (1050, 160+x)))
        x+=20

    return listToBlit

def decideChangeLane(c):
    """ Decide whether or not a car should change line
        c : car"""
    nbPassing = c.get_countPassing()
    p=0.5
    if(nbPassing>0):
        if(random.random()>p/nbPassing):
            c.setwPassingStart(True)
            c.set_changingLane(1)
    else:
        if(random.random()<p):
            c.set_goBack(True)
            c.setwPassingStart(True)
            c.set_changingLane(2)


    c.resetCountPassing()
    return c

def rankingCar(df):
    values={}
    for i in df.CarId.unique():
        lastLeap = np.max(df[df.CarId==i].Leap)
        values[i]=df[(df.CarId==i) &(df.Leap==lastLeap)].AverageSpeed.values[0]
    return values

def carAccidents(df):
    values={}
    for i in df.CarId.unique():
        lastLeap = np.max(df[df.CarId==i].Leap)
        values[i]=df[(df.CarId==i) &(df.Leap==lastLeap)].Accidents.values[0]
    return values

def rankingCarPoint(listCars):
    values={}
    for i in range(len(listCars.get_listCars())) :
        values[i] = listCars.get_listCars()[i].numberPoints
    return values

def checkSpeedPoint(listCars, df):
    values = rankingCar(df)
    for key in values:
        speed = values[key]
        if(speed>281.25):
            print("Car ",int(key), " has been punished !")
            listCars.get_listCars()[int(key)].numberPoints-=350
        else:
            listCars.get_listCars()[int(key)].numberPoints+=50
    return listCars

def checkAccidentPoint(listCars, df):
    values = carAccidents(df)
    for key in values:
        speed = values[key]
        confidencePassing = listCars.get_listCars()[int(key)].get_confidencePassing()
        if(speed>0):
            print("Car ",int(key), " has been punished !")
            sigma=0.9
            mu=np.log(250)
            penalty=int(np.random.lognormal(mu, sigma)/3)
            listCars.get_listCars()[int(key)].numberPoints-=penalty
            newConfidence=1-np.random.lognormal(mu, sigma)/1000
            newValue=max(confidencePassing*newConfidence, 0.2)
            listCars.get_listCars()[int(key)].set_confidencePassing(newValue)
        else:
            newValue=min(confidencePassing*1.1, 1)
            listCars.get_listCars()[int(key)].set_confidencePassing(newValue)
    return listCars

def rewardPoint(listCars):
    values = rankingCarPoint(listCars)
    sortDict = sorted(values.items(), key=lambda x: x[1])
    rankCar = [sortDict[i][0] for i in range(len(sortDict))]
    print("Car ",int(rankCar[0])," is the fastest !")
    listCars.wantedSpeed[int(rankCar[0])]+=75
    for i in range(len(sortDict)):
        if(sortDict[i][1]<0):
            curr=listCars.wantedSpeed[int(rankCar[i])]
            newValue=curr-80
            if(newValue<0):
                newValue=curr
            listCars.wantedSpeed[int(rankCar[i])]=newValue
    return listCars

def rewardSpeed(listCars, df):
    values = rankingCar(df)
    sortDict = sorted(values.items(), key=lambda x: x[1])
    rankCar = [sortDict[i][0] for i in range(len(sortDict))]

    listCars.wantedSpeed[int(rankCar[0])]+=75

    return listCars


def updatePosition(l, listStart, listCars, listLanes, distSecur, flatten, \
                    listPassingLine, wEnd):
    """ Update the position of the cars :
        l : Current car
        listStart : List of time markers, keeping track of refresh
        listLanes : List of lanes
        distSecur : Security distance
        flatten : Flatten list of paths
        listPassingLine : List of passing/Go back Lines
        wEnd : End of the passing path"""

    # Check time markers to see if we can update position
    if(time.time()-listStart[l]>(1/(listCars.get_listSpeed()[l]))):
        listCars.get_listCars()[l].update_pos()
        # Test to check if there is a car in front of the current car
        toReturn, findC, accident =okay(flatten[listCars.get_listCars()[l].get_lane()], \
                listCars.get_listCars()[l].get_imgx(), \
                listCars.get_listCars()[l].get_imgy(), \
                listCars.get_listCars(), l, distSecur, \
                listCars.get_listCars()[l].get_lane())
        if(accident):
            listCars.get_listCars()[l].update_accident()
        if(toReturn):
            listCars.get_listCars()[l].y=listCars.get_listCars()[l].y+1
            if(listCars.get_listCars()[l].y>=\
                len(listLanes.get_path(listCars.get_listCars()[l].get_lane())[0]\
                [listCars.get_listCars()[l].x])):
                listCars.get_listCars()[l].x=listCars.get_listCars()[l].x+1
                listCars.get_listCars()[l].y=0
        else:
            # If there is one, we update the speed of the car
            m = listCars.get_listCars().index(findC)
            changeSpeed=listCars.get_listSpeed()[m]
            listCars.get_listSpeed()[l]=changeSpeed
            confidencePassing=listCars.get_listCars()[l].get_confidencePassing()
            if(random.random()<confidencePassing):
                listCars.get_listCars()[l].setwPassingStart(True)

        # Check if the car is in a Going Back phase
        if(listCars.get_listCars()[l].get_goBack()==False):
            toTransfer = listCars.get_listCars()[l].get_lane()
            if(toTransfer in [3]):
                toTransfer=0
            if(toTransfer in [2,4]):
                toTransfer=1
            for k in range(len(listPassingLine[toTransfer])):
                    passingPoints = (listPassingLine[toTransfer][k].get_start(),\
                                    listPassingLine[toTransfer][k].get_end())

                    listCars, listLanes, = checkPassing(listCars, passingPoints, \
                                        listLanes, l, wEnd[k], k, toTransfer)

        #Otherwise, we can check if there is a need for passing
        else:
            if(listCars.get_listCars()[l].get_changingLane()%2==0):
                toTransfer = listCars.get_listCars()[l].get_lane()
                if(toTransfer in [6,2]):
                    toTransfer=3
                if(toTransfer in [5,1]):
                    toTransfer=2
                for k in range(len(listPassingLine[toTransfer])):
                        passingPoints = (listPassingLine[toTransfer][k].get_start(),\
                                        listPassingLine[toTransfer][k].get_end())

                        listCars, listLanes, toReturn = goBack(listCars, passingPoints, \
                                            listLanes, l, wEnd[k], k, toTransfer)
                        if(toReturn):
                            if(listCars.get_listCars()[l].get_changingLane()==2):
                                listCars.get_listCars()[l].set_changingLane(0)
                            else:
                                listCars.get_listCars()[l].updateCountPassing()
                            listCars.get_listCars()[l].set_goBack(False)
                            listCars.get_listCars()[l].setwPassingStart(False)
                            listCars.get_listCars()[l].set_isPassing(False)
                            listCars.get_listCars()[l].set_timeUp()


            else:
                listCars.get_listCars()[l].set_changingLane(0)
                listCars.get_listCars()[l].set_goBack(False)
                listCars.get_listCars()[l].setwPassingStart(False)
                listCars.get_listCars()[l].set_isPassing(False)
                listCars.get_listCars()[l].set_timeUp()


        listStart[l]=time.time()
    return listStart, listCars, listLanes, flatten


def computeCars(numberCars, nbLanes,numberVertices,DISPSURF):
    occupied=[]
    speeds=[]
    cars=[]
    for i in range(nbLanes):
        occupied.append([])
    for i in range(numberCars):
        carImg = pygame.image.load('spacestation.png').convert_alpha()
        lane=random.randint(0,2)
        x=random.randint(0,numberVertices)
        while(x in occupied[lane]):
            x=random.randint(0,numberVertices)
        occupied[lane].append(x)
        car=Car(x,0,lane,carImg,DISPSURF)
        cars.append(car)
        speeds.append(random.randint(100, 250))

    listCars=CarPool(cars, speeds)
    return listCars

def prepareMap(numberVertices, DISPSURF, distSecur):
    """ Build the map
        numberVertices : Number of vertices
        DISPSURF : The surface to print on
        distSecur : Security Distance"""

    # Load cars
    listCars = computeCars(24, 3,numberVertices, DISPSURF)
    listLanes=[]
    # Load lanes
    lane0 = Lane(0, 350, numberVertices)
    lane0.path()
    lane1 = Lane(0, 335, numberVertices)
    lane1.path()
    lane2 = Lane(0, 330, numberVertices)
    lane2.path()


    # Load the passing lanes
    listStartEnd, listPassingLine1, listPassingLinePoint1, whereEnd =\
                    computePassingLane(lane0, lane1, numberVertices)
    _, listPassingLine2, listPassingLinePoint2, _ =\
                    computePassingLane(lane1, lane2, numberVertices)
    _, listPassingLine3, listPassingLinePoint3, _ =\
                    computeGetBack(lane1, lane0, numberVertices)
    _, listPassingLine4, listPassingLinePoint4, _ =\
                    computeGetBack(lane2, lane1, numberVertices)

    # Build the map
    listLanes = Map(lane0, lane1, lane2, \
        listPassingLine1, listPassingLine2,listPassingLine3,listPassingLine4,\
        listPassingLinePoint1,listPassingLinePoint2,listPassingLinePoint3,\
            listPassingLinePoint4)


    # Compute the inital paths of the cars
    for c in listCars.get_listCars():
        for l in range(len(listLanes.get_listLanes())):
            if (c.get_lane()==l):
                X, Y = listLanes.get_listLanes()[l].get_path_tuple()
                c.path(X,Y)
                c.update_pos()


    # Compute the flatten array
    flatten=[toflatten(lane0.get_pathX(),lane0.get_pathY()),\
            toflatten(lane1.get_pathX(),lane1.get_pathY()),\
            toflatten(lane2.get_pathX(),lane2.get_pathY())]

    for i in range(len(listPassingLine1)):
        flatten.append(toflatten(\
                        listPassingLine1[i].get_pathX(),\
                        listPassingLine1[i].get_pathY()))
    for i in range(len(listPassingLine2)):
        flatten.append(toflatten(\
                        listPassingLine2[i].get_pathX(),\
                        listPassingLine2[i].get_pathY()))
    for i in range(len(listPassingLine3)):
        flatten.append(toflatten(\
                        listPassingLine3[i].get_pathX(),\
                        listPassingLine3[i].get_pathY()))
    for i in range(len(listPassingLine4)):
        flatten.append(toflatten(\
                        listPassingLine4[i].get_pathX(),\
                        listPassingLine4[i].get_pathY()))
    # Init the time markers
    listStart=[time.time() for c in listCars.get_listCars()]


    return listCars, listLanes, listStart, listStartEnd, flatten,\
            listPassingLine1 , listPassingLine2, listPassingLine3,\
            listPassingLine4, whereEnd

def computePassingLane(laneA, laneB, numberVertices):
    """ Build the passing lanes from laneA to laneB
        laneA : The starting lane
        laneB : The ending lane:
        numberVertices : The number of vertices0"""

    listStartEnd=[]
    listPassingLine=[]
    listPassingLinePoint=[]
    whereEnd=[]

    # Compute list of starting/ending points
    i=0
    while(i<numberVertices-2):
        listStartEnd.append((i, i+2))
        i=i+2

    # Build the passing line objects
    for i in range(len(listStartEnd)):
        a,b=listStartEnd[i]
        start=laneA.get_positions()[a]
        end=laneB.get_positions()[b]
        p=Passing(start, end, 0, a, b)
        p.path()
        listPassingLine.append(p)
        listPassingLinePoint.append((p.get_start(),\
                                    p.get_end()))
        whereEnd.append(b)

    return listStartEnd, listPassingLine, listPassingLinePoint, whereEnd

def computeGetBack(laneA, laneB, numberVertices):
    """ Build the passing lanes from laneA to laneB (Going Back)
        laneA : The starting lane
        laneB : The ending lane:
        numberVertices : The number of vertices0"""

    listStartEnd=[]
    listPassingLine=[]
    listPassingLinePoint=[]
    whereEnd=[]
    i=0
    while(i<numberVertices-2):
        listStartEnd.append((i, i+2))
        i=i+2
    for i in range(len(listStartEnd)):
        a,b=listStartEnd[i]
        start=laneA.get_positions()[a]
        end=laneB.get_positions()[b]
        p=Passing(start, end, 0, a, b)
        p.path()
        listPassingLine.append(p)
        listPassingLinePoint.append((p.get_start(),\
                                    p.get_end()))
        whereEnd.append(b)

    return listStartEnd, listPassingLine, listPassingLinePoint, whereEnd
