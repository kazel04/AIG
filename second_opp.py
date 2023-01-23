# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 20:59:45 2023

@author: KZ
"""

from Globals import *
from GameEntity import *
from HAL import *

import pygame

import numpy as np


#get second nearest opponent
def get_second_nearest_opponent(self, char):
    flag = False
    second_nearest_opponent = None
    distance = 0

    for entity in self.entities.values():

        # neutral entity
        if entity.team_id == 2:
            continue

        # same team
        if entity.team_id == char.team_id:
            continue

        if entity.name == "projectile" or entity.name == "explosion":
            continue

        if entity.ko:
            continue

        if second_nearest_opponent is None and flag == False: #if no target, set target here
            flag = True
        elif second_nearest_opponent is None and flag == True:
            nearest_opponent = entity
            distance = (char.position - entity.position).length()
        else: #if target 
            if distance > (char.position - entity.position).length():
                distance = (char.position - entity.position).length()
                second_nearest_opponent = entity
    
    return second_nearest_opponent