from Globals import *
from GameEntity import *

import pygame

def is_opponent_in_range(character, opponent):
    
    mean_pos = (character.position + opponent.position) / 2
    
    dummy_character = GameEntity(character.world, "", pygame.image.load("assets/blue_archer_32_32.png").convert_alpha(), False)
    dummy_character.rect = pygame.Rect(mean_pos, (1, 1))
    
    opponent_distance = (character.position - opponent.position).length()
    if opponent_distance <= character.min_target_distance and not is_stuck(dummy_character):
        return opponent
    
def is_stuck(character):
    # obstacles = [obstacle for obstacle in character.world.obstacles if obstacle.name == "obstacle"]
    
    return character.rect.x < 0 or character.rect.x > SCREEN_WIDTH or \
           character.rect.y < 0 or character.rect.y > SCREEN_HEIGHT or \
            len(pygame.sprite.spritecollide(character, character.world.obstacles, False, pygame.sprite.collide_mask)) > 0
