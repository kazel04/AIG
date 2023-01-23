from Globals import *
from GameEntity import *

import pygame

import numpy as np

def is_opponent_in_range(character, opponent):
    
    x = [character.position.x, opponent.position.x]
    y = [character.position.y, opponent.position.y]
    
    equation = np.poly1d(np.polyfit(x, y, 1))
    x_axis = np.linspace(x[0], x[1], 10)
    y_axis = equation(x_axis)
    
    is_position_in_obstacle = False
    
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
    if opponent_distance <= character.min_target_distance: #and not is_position_in_obstacle:
        return opponent
    
def is_stuck(character):
    # obstacles = [obstacle for obstacle in character.world.obstacles if obstacle.name == "obstacle"]
    
    return character.rect.x < 0 or character.rect.x > SCREEN_WIDTH or \
           character.rect.y < 0 or character.rect.y > SCREEN_HEIGHT or \
            len(pygame.sprite.spritecollide(character, character.world.obstacles, False, pygame.sprite.collide_mask)) > 0
