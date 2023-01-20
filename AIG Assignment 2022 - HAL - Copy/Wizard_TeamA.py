import pygame

from random import randint, random
from Graph import *

from Character import *
from State import *

import numpy as np

class Wizard_TeamA(Character):

    def __init__(self, world, image, projectile_image, base, position, explosion_image = None):

        Character.__init__(self, world, "wizard", image)

        self.projectile_image = projectile_image
        self.explosion_image = explosion_image

        self.base = base
        self.position = position
        self.move_target = GameEntity(world, "wizard_move_target", None)
        self.target = None

        self.maxSpeed = 50
        self.min_target_distance = 100
        self.projectile_range = 100
        self.projectile_speed = 100

        seeking_state = WizardStateSeeking_TeamA(self)
        attacking_state = WizardStateAttacking_TeamA(self)
        ko_state = WizardStateKO_TeamA(self)

        self.brain.add_state(seeking_state)
        self.brain.add_state(attacking_state)
        self.brain.add_state(ko_state)

        self.brain.set_state("seeking")

    def render(self, surface):

        Character.render(self, surface)


    def process(self, time_passed):
        
        Character.process(self, time_passed)
        
        level_up_stats = ["hp", "speed", "ranged damage", "ranged cooldown", "projectile range"]
        if self.can_level_up():
            choice = 3 #randint(0, len(level_up_stats) - 1)
            self.level_up(level_up_stats[choice])      

def is_opponent_in_range(character, opponent):
    opponent_distance = (character.position - opponent.position).length()
    if opponent_distance <= character.min_target_distance:
        return opponent

class WizardStateSeeking_TeamA(State):

    def __init__(self, wizard):

        State.__init__(self, "seeking")
        self.wizard = wizard

        self.wizard.path_graph = self.wizard.world.paths[3]
        

    def do_actions(self):

        self.wizard.velocity = self.wizard.move_target.position - self.wizard.position
        if self.wizard.velocity.length() > 0:
            self.wizard.velocity.normalize_ip();
            self.wizard.velocity *= self.wizard.maxSpeed

    def check_conditions(self):

        # check if opponent is in range
        nearest_opponent = self.wizard.world.get_nearest_opponent(self.wizard)
        if nearest_opponent is not None:
            if is_opponent_in_range(self.wizard, nearest_opponent):
                self.wizard.target = nearest_opponent
                return "attacking"
            
            
            opponent_distance = (self.wizard.position - nearest_opponent.position).length()
        
            if self.wizard.current_hp < self.wizard.max_hp and \
                opponent_distance > self.wizard.healing_cooldown * self.wizard.maxSpeed + self.wizard.min_target_distance:
                
                self.wizard.heal()
        
        if (self.wizard.position - self.wizard.move_target.position).length() < 8:

            # continue on path
            if self.current_connection < self.path_length:
                self.wizard.move_target.position = self.path[self.current_connection].toNode.position
                self.current_connection += 1
            
        return None

    def entry_actions(self):

        nearest_node = self.wizard.path_graph.get_nearest_node(self.wizard.position)

        self.path = pathFindAStar(self.wizard.path_graph, \
                                  nearest_node, \
                                  self.wizard.path_graph.nodes[self.wizard.base.target_node_index])
        
        self.path_length = len(self.path)

        print(self.wizard.path_graph.nodes[self.wizard.base.target_node_index].position)

        if (self.path_length > 0):
            # will not go back to node before continuing
            distance_from_node_to_base = (Vector2(self.path[0].fromNode.position) - Vector2(self.wizard.base.position)).length()
            distance_from_wizard_to_base = (Vector2(self.wizard.position) - Vector2(self.wizard.base.position)).length()

            if (distance_from_wizard_to_base > distance_from_node_to_base and \
                len(self.path) > 0):

                self.path.pop(0)
                self.path_length -= 1
                        
            if (self.path_length > 0):
                self.current_connection = 0
                self.wizard.move_target.position = self.path[0].fromNode.position

        else:
            self.wizard.move_target.position = self.wizard.path_graph.nodes[self.wizard.base.target_node_index].position


class WizardStateAttacking_TeamA(State):

    def __init__(self, wizard):

        State.__init__(self, "attacking")
        self.wizard = wizard

    def do_actions(self):

        # get all targets in the range
        targets = [v for (k,v) in self.wizard.world.entities.items() if issubclass(type(v), Character) and v.team_id == 1 and (v.position - self.wizard.position).length() < self.wizard.min_target_distance ]
        
        if len(targets) > 0:
        
            # remove the characters that are too far away that will affect the mean
            biggest_cluster = self.get_biggest_cluster(targets, self.wizard.explosion_image.get_size())

            
            target_positions = [target.position for target in biggest_cluster]

            # target the center
            mean_position = None
            if len(target_positions) > 0:
                mean_position = sum(target_positions, start=pygame.Vector2()) / len(target_positions)

            if self.wizard.current_ranged_cooldown <= 0 and mean_position is not None:
                self.wizard.ranged_attack(mean_position, self.wizard.explosion_image)

        nearest_opponent = self.wizard.world.get_nearest_opponent(self.wizard)
        if nearest_opponent is not None and is_opponent_in_range(self.wizard, nearest_opponent):
            self.wizard.target = nearest_opponent
            
        
        opponent_distance = (self.wizard.position - self.wizard.target.position).length()

        if opponent_distance - self.wizard.min_target_distance * 0.5 > 5:
            #move towards target
            self.wizard.velocity = self.wizard.target.position - self.wizard.position
        elif opponent_distance - self.wizard.min_target_distance * 0.5 < -5:
            #move away from target
            self.wizard.velocity = self.wizard.position - self.wizard.target.position
        else:
            self.wizard.velocity = Vector2(0, 0)

        if self.wizard.velocity.length() > 0:
            self.wizard.velocity.normalize_ip();
            self.wizard.velocity *= self.wizard.maxSpeed


    def check_conditions(self):

        # target is gone
        if self.wizard.world.get(self.wizard.target.id) is None or self.wizard.target.ko:
            self.wizard.target = None
            return "seeking"
            
        return None

    def entry_actions(self):

        return None
    
    def get_biggest_cluster(self, targets, perimeter_bound):
        centoid_distances = self.calculate_centoid_distance(targets)
        
        perimeter = self.calculate_perimeter(centoid_distances)
        
        while perimeter[0] > perimeter_bound[0] or perimeter[1] > perimeter_bound[1]:
            
            characters = self.get_furthest_characters(centoid_distances)
            
            if perimeter[0] > perimeter_bound[0] and characters[0] in targets:
                targets.remove(characters[0])
            
            if perimeter[1] > perimeter_bound[1] and characters[1] in targets:
                targets.remove(characters[1])
                
            if len(targets) <= 0:
                return targets
            
            centoid_distances = self.calculate_centoid_distance(targets)
        
            perimeter = self.calculate_perimeter(centoid_distances)

        
        return targets
    
    # calculate the manhattan distance of the cluster from the centoid
    # returns a dict key: target, value: (x distance, y distance)
    def calculate_centoid_distance(self, targets):
        if len(targets) <= 0:
            return {}
        
        centoid_position = sum([x.position for x in targets], start=pygame.Vector2()) / len(targets)
        centoid_distances = {}
        
        for target in targets:
            centoid_distances[target] = ( centoid_position.x - target.position.x, centoid_position.y - target.position.y )
            
        # print(centoid_distances)
        
        return centoid_distances
    
    def calculate_perimeter(self, centoid_distances):
        distance_array = np.array(list(centoid_distances.values()))
        
        return np.sum((np.absolute( distance_array.min(axis=0)), distance_array.max(axis=0)), axis=0)

    # returns the furthest character for the x and y distance
    def get_furthest_characters(self, centoid_distances):
        
        max_x_distance = 0
        max_y_distance = 0
        
        max_x_character = None
        max_y_character = None
        
        for character, centoid_distance in centoid_distances.items():
            if abs(centoid_distance[0]) > max_x_distance:
                max_x_distance = centoid_distance[0]
                max_x_character = character
            
            if abs(centoid_distance[1]) > max_y_distance:
                max_y_distance = centoid_distance[1]
                max_y_character = character
                
        return (max_x_character, max_y_character)


class WizardStateKO_TeamA(State):

    def __init__(self, wizard):

        State.__init__(self, "ko")
        self.wizard = wizard

    def do_actions(self):

        return None


    def check_conditions(self):

        # respawned
        if self.wizard.current_respawn_time <= 0:
            self.wizard.current_respawn_time = self.wizard.respawn_time
            self.wizard.ko = False
            self.wizard.path_graph = self.wizard.world.paths[randint(0, len(self.wizard.world.paths)-1)]
            return "seeking"
            
        return None

    def entry_actions(self):

        self.wizard.current_hp = self.wizard.max_hp
        self.wizard.position = Vector2(self.wizard.base.spawn_position)
        self.wizard.velocity = Vector2(0, 0)
        self.wizard.target = None

        return None
