# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 15:34:44 2018

@author: Sofiascope
"""



import pygame
import sys
from pygame.locals import QUIT
import numpy as np
import time
import utils

pygame.init()


display_width = 1000
display_height = 800
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (227, 27, 27)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RCB = (27, 27, 27)
crashed = False


DISPSURF = pygame.display.set_mode((display_width, display_height), 0, 32)
pygame.display.set_caption("Easy Traffic")

numberVertices=100
distSecur=50
listCars, listLanes, listStart, listStartEnd, flatten, \
            listPassingLine, listPassingLine2, listPassingLine3, \
            listPassingLine4, whereEnd = \
                utils.prepareMap(numberVertices, DISPSURF, distSecur)

print(len(listPassingLine))
while not crashed:

    for c in listCars.get_listCars():
        for l in [0,1,2]:
            if(c.x==len(listLanes.get_path_lane(l)[0])):
                    c.x=0
                    c.j=0

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            crashed = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x0, x1 = pygame.mouse.get_pos()
            whichLane, corner = utils.closest(listLanes.get_listLanes(),\
                    [x0,x1], numberVertices)
        elif event.type == pygame.MOUSEBUTTONUP:
            DISPSURF.fill(WHITE)
            x0, x1 = pygame.mouse.get_pos()
            newListCar, flatten = listLanes.update(x0,x1, flatten, whichLane, \
                                    corner, listCars.get_listCars(),\
                                    listStartEnd)

            listCars.update_cars(newListCar)


    for l in range(len(listCars.get_listCars())):
        listStart, listCars, listLanes, flatten =\
                    utils.updatePosition(l, listStart, listCars, \
                                listLanes, distSecur, \
                                flatten, [listPassingLine, listPassingLine2,\
                                        listPassingLine3, listPassingLine4],\
                                        whereEnd)

    DISPSURF.fill(WHITE)

    pygame.draw.polygon(DISPSURF, RED, listLanes.get_lane(0)\
                                            .get_positions(), 2)
    pygame.draw.polygon(DISPSURF, RED, listLanes.get_lane(1)\
                                            .get_positions(), 2)
    pygame.draw.polygon(DISPSURF, RED, listLanes.get_lane(2)\
                                            .get_positions(), 2)

    for c in listCars.get_listCars():
        c.carPrint()

    pygame.display.update()

pygame.quit()
quit()
