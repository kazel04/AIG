from Globals import *
from GameEntity import *

import pygame

import numpy as np

def is_opponent_in_range(character, opponent):
    
    x = [character.position.x, opponent.position.x]
    y = [character.position.y, opponent.position.y]
    
    equation = np.poly1d(np.polyfit(x, y, 1))
    x_axis = np.linspace(x[0], x[1], 30)
    y_axis = equation(x_axis)
    
    is_position_in_obstacle = False
    # prevent character from attacking opponent through walls
    for i in range(len(x_axis)):
        predicted_pos = Vector2(x_axis[i], y_axis[i])

        dummy_character = GameEntity(character.world, "", pygame.image.load("assets/blue_archer_32_32.png").convert_alpha(), False)
        dummy_character.rect = pygame.Rect(predicted_pos, (10, 10))
        
        if is_stuck(dummy_character):
            is_position_in_obstacle = True
            break
    
    # if character.name == "archer":
    #     print(character.name + " " + str(is_position_in_obstacle))
    
    opponent_distance = (character.position - opponent.position).length()
    if opponent_distance <= character.min_target_distance and not is_position_in_obstacle:
        return opponent
    
def is_stuck(character):
    # obstacles = [obstacle for obstacle in character.world.obstacles if obstacle.name == "obstacle"]
    
    return character.rect.x < 0 or character.rect.x > SCREEN_WIDTH or \
           character.rect.y < 0 or character.rect.y > SCREEN_HEIGHT or \
            len(pygame.sprite.spritecollide(character, character.world.obstacles, False, pygame.sprite.collide_mask)) > 0


def get_second_nearest_opponent(self, char):
    flag = False
    second_nearest_opponent = None
    distance = 0

    for entity in self.world.entities.values():

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
