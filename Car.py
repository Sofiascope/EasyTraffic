# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 15:34:44 2018

@author: Sofiascope

Car contains the Car and CarPool class
"""

import time
import utils

class Car:
    """ Car class,
        x : Segment number where the car is currently in
        y : Position in segment where the car is currently in
        lane : Current lane
        img : Image to print
        DIPSURF : Surface to print
        m,n : size of the image to print
        wantPassingStart : Boolean to state if a car want to start passing
        isPassing : Boolean to state if car is in a passing process
        goBack : Boolean to state if a car is in a going back process
        timeUp : Timer to enable a car to go back"""
        
    def __init__(self, x, y, lane, img,DISPSURF):
        self.x=x
        self.y=y
        self.lane=lane
        self.img = img
        self.DISPSURF=DISPSURF
        m,n = img.get_rect().size
        self.m=m
        self.n=n
        self.wantPassingStart=False
        self.isPassing=False
        self.goBack=False
        self.timeUp=time.time()
    def set_goBack(self, value):
        self.goBack=value
    def get_goBack(self):
        return self.goBack
    def set_timeUp(self):
        self.timeUp=time.time()
    def get_timeUp(self):
        return self.timeUp
    def get_isPassing(self):
        return self.isPassing
    def set_isPassing(self, value):
        self.isPassing=value
    def get_lane(self):
        return self.lane
    def carPrint(self):
        self.DISPSURF.blit(self.img, (self.imgx-self.m/2\
                                        ,self.imgy-self.n/2))
    def path(self, pathX, pathY):
        self.pathX=pathX
        self.pathY=pathY
    def get_curr_position(self):
        return (self.imgx,self.imgy)

    def update_pos(self):
        """ Update position of car according to the path"""
        self.imgx=self.pathX[min(self.x,len(self.pathX)-1)]\
                            [min(self.y,len(self.pathX[self.x])-1)]
        self.imgy=self.pathY[min(self.x,len(self.pathY)-1)]\
                            [min(self.y,len(self.pathY[self.x])-1)]

    def get_imgx(self):
        return self.imgx
    def get_imgy(self):
        return self.imgy
    def set_isBlocked(self, value):
        self.isBlocked=value
    def get_isBlocked(self):
        return self.isBlocked
    def wPassingStart(self):
        return self.wantPassingStart
    def setwPassingStart(self, value):
        self.wantPassingStart=value

class CarPool():
    """ Car Pool class, list of cars
        listCars : List of cars in the map
        listSpeed : List of current speeds (can be modified)
        wantedSpeed : List of inital speed (cannot be modified)"""
    def __init__(self, listCars, listSpeed):
        self.listCars=listCars
        self.listSpeed=listSpeed
        self.wantedSpeed=listSpeed.copy()
    def get_listCars(self):
        return self.listCars
    def update_cars(self, newCars):
        self.listCars=newCars
    def get_listSpeed(self):
        return self.listSpeed
    def get_listWantSpeed(self):
        return self.wantedSpeed
