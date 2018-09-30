# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 15:34:44 2018

@author: Sofiascope

Map contains the Lane, Passing and Map classes
Map mostly manages the modification of the map
"""
import utils

class Lane:
    """ Lane class, describing a lane
        nb : Number of the lane
        radius, numberVertices : geomtric parameters of the lane"""

    def __init__(self, nb, radius, numberVertices):
        self.lines, self.positions = utils.mapStruct(radius, numberVertices)
        self.nb=nb
    def path(self):
        self.pathX, self.pathY = utils.path(self.lines)
    def get_path_tuple(self):
        return (self.pathX, self.pathY)
    def get_pathX(self):
        return self.pathX
    def get_pathY(self):
        return self.pathY
    def get_lines(self):
        return self.lines
    def get_positions(self):
        return self.positions
    def updatePath(self, pathX, pathY):
        self.pathX=pathX
        self.pathY=pathY
    def get_nb(self):
        return self.nb

class Passing():
    """ Passing class, describing a passing line
        x = Starting point of the passing line,
        as a position in the list of vertices
        y = Ending point of the passing line,
        as a position in the list of vertices
        startPoint : Starting point, in cartesian coordinates
        endPoint : Ending point, in cartesian coordinates """
    def __init__(self, startPoint, endPoint, startLane, x, y):
        self.startPoint=startPoint
        self.endPoint=endPoint
        self.startLane=startLane
        self.x=x
        self.y=y
    def get_start(self):
        return self.startPoint
    def get_end(self):
        return self.endPoint
    def path(self):
        self.pathX, self.pathY = utils.path([(self.startPoint, \
                        self.endPoint)])
    def get_path_tuple(self):
        return (self.pathX, self.pathY)
    def get_pathX(self):
        return self.pathX
    def get_pathY(self):
        return self.pathY
    def get_positions(self):
        return [self.startPoint, self.endPoint]
    def update_points(self, start, end):
        self.startPoint=start
        self.endPoint=end
        self.path()

class Map():
    """ Map class, list of Passing Lane and Regular Lane
        lane0, lane1, lane2 : Regular lanes
        passing01, passing12, passing10,passing21 : Passing Lines
        passingPoint01, passingPoint12, passingPoint10, passingPoint21 :
            passing lines position points"""

    def __init__(self, lane0, lane1, lane2, \
                passing01, passing12, passing10,passing21,\
                passingPoint01, passingPoint12, passingPoint10, passingPoint21):
        self.lane0=lane0
        self.lane1=lane1
        self.lane2=lane2

        self.passing=passing01
        self.passing12=passing12
        self.passing10=passing10
        self.passing21=passing21

        self.passing01Point=passingPoint01
        self.passing12Point=passingPoint12
        self.passing10Point=passingPoint10
        self.passing21Point=passingPoint21

        self.passingPoint=[self.passing10Point,self.passing12Point,\
            self.passing12Point, self.passing21]

        self.listLanes=[self.lane0, self.lane1, self.lane2, self.passing, \
                        self.passing12, self.passing10,self.passing21]
    def get_listLanes(self):
        return self.listLanes
    def get_lane(self,nb):
        return self.listLanes[nb]
    def get_passing(self, toTransfer, nb):
        return self.listLanes[3+toTransfer]
    def get_path_lane(self, nb):
        return self.listLanes[nb].get_path_tuple()
    def get_path_passing(self, toTransfer, nb):
        return self.listLanes[3+toTransfer][nb].get_path_tuple()
    def get_path(self, nb):
        if(nb<3):
            return self.listLanes[nb].get_path_tuple()
        else:
            return self.listLanes[nb][0].get_path_tuple()
    def update(self, x0,x1, flatten, whichLane, corner, listCars, \
                listStartEnd):
        """ Update the map, trigger by the user click
            x0,x1 : Click coordinates
            flatten : Flatten array
            whichLane : Lane to modify
            corner : Vertex of the lane to modify
            listCars : List of cars
            listStartEnd : list of passing line points"""

        self.listLanes[whichLane].get_positions()[corner]=[x0,x1]
        # Update the lanes
        for k in range(len(self.listLanes[whichLane].get_positions())-1):
            self.listLanes[whichLane].get_lines()[k]=\
            (self.listLanes[whichLane].get_positions()[k],\
                self.listLanes[whichLane].get_positions()[k+1])
        self.listLanes[whichLane].get_lines()[-1]=\
            (self.listLanes[whichLane].get_positions()[-1],\
             self.listLanes[whichLane].get_positions()[0])

        # For each lane, we locate the closest passing line / going back lanes
        # to modify them (graphically and modify their path)
        if(whichLane==0):
            #0 to 1
            idx = utils.closestPassing(self.passing, (x0, x1), whichLane, 0)
            start=self.listLanes[0].get_positions()[listStartEnd[idx][0]]
            end=self.listLanes[1].get_positions()[listStartEnd[idx][1]]
            self.listLanes[3][idx].update_points(start, end)
            self.passing = self.listLanes[3]
            pathX, pathY=self.listLanes[3][idx].get_path_tuple()
            flatten[3+whichLane]=utils.toflatten(pathX, pathY)
            #1 to 0
            idx = utils.closestPassing(self.passing, (x0, x1), whichLane, 1)
            start=self.listLanes[1].get_positions()[listStartEnd[idx][0]]
            end=self.listLanes[0].get_positions()[listStartEnd[idx][1]]
            self.listLanes[5][idx].update_points(start, end)
            self.passing = self.listLanes[5]
            pathX, pathY=self.listLanes[5][idx].get_path_tuple()
            flatten[5+whichLane]=utils.toflatten(pathX, pathY)

        if(whichLane==2):
            #1 to 2
            idx = utils.closestPassing(self.passing, (x0, x1), whichLane, 1)
            start=self.listLanes[1].get_positions()[listStartEnd[idx][0]]
            end=self.listLanes[2].get_positions()[listStartEnd[idx][1]]
            self.listLanes[4][idx].update_points(start, end)
            pathX, pathY=self.listLanes[4][idx].get_path_tuple()
            flatten[3+whichLane]=utils.toflatten(pathX, pathY)
            #2 to 1
            idx = utils.closestPassing(self.passing, (x0, x1), whichLane, 0)
            start=self.listLanes[2].get_positions()[listStartEnd[idx][0]]
            end=self.listLanes[1].get_positions()[listStartEnd[idx][1]]
            self.listLanes[6][idx].update_points(start, end)
            pathX, pathY=self.listLanes[6][idx].get_path_tuple()
            flatten[6+whichLane]=utils.toflatten(pathX, pathY)

        if(whichLane==1):
            #0 to 1
            idx = utils.closestPassing(self.passing, (x0, x1), whichLane,1)
            start=self.listLanes[0].get_positions()[listStartEnd[idx][0]]
            end=self.listLanes[1].get_positions()[listStartEnd[idx][1]]
            self.listLanes[3][idx].update_points(start, end)
            pathX, pathY=self.listLanes[3][idx].get_path_tuple()
            flatten[3+whichLane]=utils.toflatten(pathX, pathY)
            #1 to 0
            idx = utils.closestPassing(self.passing, (x0, x1), whichLane,0)
            start=self.listLanes[1].get_positions()[listStartEnd[idx][0]]
            end=self.listLanes[0].get_positions()[listStartEnd[idx][1]]
            self.listLanes[5][idx].update_points(start, end)
            pathX, pathY=self.listLanes[5][idx].get_path_tuple()
            flatten[5+whichLane]=utils.toflatten(pathX, pathY)
            #1 to 2
            idx = utils.closestPassing(self.passing, (x0, x1), whichLane,0)
            start=self.listLanes[1].get_positions()[listStartEnd[idx][0]]
            end=self.listLanes[2].get_positions()[listStartEnd[idx][1]]
            self.listLanes[4][idx].update_points(start, end)
            pathX, pathY=self.listLanes[4][idx].get_path_tuple()
            flatten[3+whichLane]=utils.toflatten(pathX, pathY)
            #2 to 1
            idx = utils.closestPassing(self.passing, (x0, x1), whichLane, 1)
            start=self.listLanes[2].get_positions()[listStartEnd[idx][0]]
            end=self.listLanes[1].get_positions()[listStartEnd[idx][1]]
            self.listLanes[6][idx].update_points(start, end)
            pathX, pathY=self.listLanes[6][idx].get_path_tuple()
            flatten[6+whichLane]=utils.toflatten(pathX, pathY)


        # Update the position of the car
        if(whichLane in [0,1,2]):
            pathXl, pathYl= utils.path(self.listLanes[whichLane].get_lines())
            self.listLanes[whichLane].updatePath(pathXl, pathYl)
            flatten[whichLane]=utils.toflatten(pathXl, pathYl)
            for c in listCars:
                if(c.get_lane()==whichLane):
                    c.path(pathXl,pathYl)
                    c.update_pos()

        return listCars, flatten
