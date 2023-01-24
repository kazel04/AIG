import pygame

from random import randint, random
from Graph import *

from Character import *
from State import *

from Utlis_ZhugeLiang import *

from Base import Base

class Archer_ZhugeLiang(Character):

    def __init__(self, world, image, projectile_image, base, position):

        Character.__init__(self, world, "archer", image)

        self.projectile_image = projectile_image
        
        # all the incoming projectiles
        self.projectiles = []
        
        # keep track of opponent count in the map
        # (path graph id, count)
        self.opponents = {}

        self.dodge_distance = self.min_target_distance + 20

        self.base = base
        self.position = position
        self.move_target = GameEntity(world, "archer_move_target", None)
        self.target = None

        self.maxSpeed = 50
        self.min_target_distance = 100
        self.projectile_range = 100
        self.projectile_speed = 100
        
        seeking_state = ArcherStateSeeking_ZhugeLiang(self)
        attacking_state = ArcherStateAttacking_ZhugeLiang(self)
        dodging_state = ArcherStateDodging_ZhugeLiang(self)
        unstuck_state = ArcherStateUnstuck_ZhugeLiang(self)
        ko_state = ArcherStateKO_ZhugeLiang(self)

        self.brain.add_state(seeking_state)
        self.brain.add_state(attacking_state)
        self.brain.add_state(dodging_state)
        self.brain.add_state(unstuck_state)
        self.brain.add_state(ko_state)

        self.brain.set_state("seeking")

    def render(self, surface):

        Character.render(self, surface)


    def process(self, time_passed):
        
        opponents = [v for (k,v) in self.world.entities.items() if issubclass(type(v), Character) \
                        and v.team_id != self.team_id and v.team_id != 2]
        
        self.opponents = {}
        
        for opponent in opponents:
            if not hasattr(opponent, "path_graph"):
                continue
            
            path_graph_index = self.world.paths.index(opponent.path_graph)
            
            if path_graph_index not in self.opponents:
                self.opponents[path_graph_index] = 0
                
            self.opponents[path_graph_index] += 1
        
        self.dodge_distance = self.min_target_distance + 20
        
        # get all projectiles in the range
        self.projectiles = [v for (k,v) in self.world.entities.items() if issubclass(type(v), Projectile)
            and v.team_id != self.team_id and (v.position - self.position).length() < self.dodge_distance]
        
        Character.process(self, time_passed)
        
        level_up_stats = ["hp", "speed", "ranged damage", "ranged cooldown", "projectile range"]
        if self.can_level_up():
            choice = 3#randint(0, len(level_up_stats) - 1)
            self.level_up(level_up_stats[choice])   


class ArcherStateUnstuck_ZhugeLiang(State):
    def __init__(self, archer):

        State.__init__(self, "unstuck")
        self.archer = archer
        self.starting_time = None
        self.move_time = 0.2 / SPEED_MULTIPLIER
        
    def do_actions(self):
        
        if self.archer.velocity.length() > 0:
            self.archer.velocity.normalize_ip();
            self.archer.velocity *= self.archer.maxSpeed
            
    def check_conditions(self):
        current_time = pygame.time.get_ticks()
    
        if current_time - self.starting_time > self.move_time * 1000:
            return "seeking"
    
    def entry_actions(self):
        
        move_degree = randint(0, 360)
        
        # dummy_character = GameEntity(self.archer.world, "", pygame.image.load("assets/blue_archer_32_32.png").convert_alpha(), False)
        
        # while self.archer.velocity.length() > 0 and is_stuck(dummy_character):
        #     move_degree = randint(0, 360)
            
        #     predicted_pos = self.archer.position + self.archer.velocity.rotate(move_degree).normalize() * self.archer.maxSpeed * self.move_time
        
        #     dummy_character.rect = pygame.Rect(predicted_pos, (1, 1))
    
        self.starting_time = pygame.time.get_ticks()
        
        self.archer.velocity = Vector2(1, 0).rotate(move_degree)
            

class ArcherStateDodging_ZhugeLiang(State):
    def __init__(self, archer):

        State.__init__(self, "dodging")
        self.archer = archer
        self.starting_time = None
        self.dodge_time = 0.6 / SPEED_MULTIPLIER
        
    def do_actions(self):
        
        if self.archer.current_ranged_cooldown <= 0 and self.archer.target is not None:
            self.archer.ranged_attack(self.archer.target.position)
        
        if self.archer.velocity.length() > 0:
            self.archer.velocity.normalize_ip();
            self.archer.velocity *= self.archer.maxSpeed
        
    
    def check_conditions(self):
        current_time = pygame.time.get_ticks()
    
        if current_time - self.starting_time > self.dodge_time * 1000:
            return "seeking"
        
        if len(self.archer.projectiles) <= 0:
            return "seeking"
    
    def entry_actions(self):
        self.starting_time = pygame.time.get_ticks()
        
        cloest_projectile = self.archer.projectiles[0]
        for projectile in self.archer.projectiles:
            if (cloest_projectile.position - self.archer.position).length() > (projectile.position - self.archer.position).length():
                cloest_projectile = projectile
        
        predicted_pos_90deg = self.archer.position + cloest_projectile.velocity.rotate(90).normalize() * self.archer.maxSpeed * self.dodge_time
        
        dummy_character = GameEntity(self.archer.world, "", pygame.image.load("assets/blue_archer_32_32.png").convert_alpha(), False)
        dummy_character.rect = pygame.Rect(predicted_pos_90deg, (1, 1))
                 
        if is_stuck(dummy_character):
            self.archer.velocity = cloest_projectile.velocity.rotate(-90)
        else:
            self.archer.velocity = cloest_projectile.velocity.rotate(90)
            
        if self.archer.velocity.length() > 0:
            self.archer.velocity.normalize_ip();
            self.archer.velocity *= self.archer.maxSpeed

class ArcherStateSeeking_ZhugeLiang(State):

    def __init__(self, archer):

        State.__init__(self, "seeking")
        self.archer = archer

        self.archer.path_graph = self.archer.world.paths[randint(0, 1)] #randint(0, len(self.archer.world.paths)-1)]


    def do_actions(self):
            
        self.archer.velocity = self.archer.move_target.position - self.archer.position
        
        if self.archer.velocity.length() > 0:
            self.archer.velocity.normalize_ip();
            self.archer.velocity *= self.archer.maxSpeed


    def check_conditions(self):
        
        if len(self.archer.projectiles) > 0:
            return "dodging"

        # check if opponent is in range
        nearest_opponent = self.archer.world.get_nearest_opponent(self.archer)
        if nearest_opponent is not None:
            if is_opponent_in_range(self.archer, nearest_opponent):
                self.archer.target = nearest_opponent
                return "attacking"
            
            opponent_distance = (self.archer.position - nearest_opponent.position).length()
                
            if self.archer.current_hp < self.archer.max_hp and \
                opponent_distance > self.archer.healing_cooldown * self.archer.maxSpeed + self.archer.min_target_distance:
                
                self.archer.heal()
        
        if (self.archer.position - self.archer.move_target.position).length() < 8:

            # continue on path
            if self.current_connection < self.path_length:
                self.archer.move_target.position = self.path[self.current_connection].toNode.position
                self.current_connection += 1
                
        
        if is_stuck(self.archer):
            return "unstuck"
            
        return None

    def entry_actions(self):

        nearest_node = self.archer.path_graph.get_nearest_node(self.archer.position)
        
        self.path = pathFindAStar(self.archer.path_graph, \
                                  nearest_node, \
                                  self.archer.path_graph.nodes[self.archer.base.target_node_index])
        
        self.path_length = len(self.path)

        if self.path_length > 1:
            
            # will not go back to node before continuing
            distance_from_node_to_base = (Vector2(self.path[0].fromNode.position) - Vector2(self.archer.base.position)).length()
            distance_from_archer_to_base = (Vector2(self.archer.position) - Vector2(self.archer.base.position)).length()

            if distance_from_archer_to_base > distance_from_node_to_base:
                self.path.pop(0)
                self.path_length -= 1
                
            self.archer.move_target.position = self.path[0].fromNode.position

        else:
            self.archer.move_target.position = self.archer.path_graph.nodes[self.archer.base.target_node_index].position
            
        # print([x.fromNode.id for x in self.path])
        
        self.current_connection = 0

class ArcherStateAttacking_ZhugeLiang(State):

    def __init__(self, archer):

        State.__init__(self, "attacking")
        self.archer = archer

    def do_actions(self):
        
        if self.archer.current_ranged_cooldown <= 0:
            self.archer.ranged_attack(self.archer.target.position)
            
        enemy_base = [entity for entity_id, entity in self.archer.world.entities.items() if issubclass(type(entity), Base) \
            and entity.team_id != self.archer.team_id][0]
        
        distance_to_enemy_base = (self.archer.position - enemy_base.position).length() - 40

        nearest_opponent = self.archer.world.get_nearest_opponent(self.archer)
        if nearest_opponent is not None and is_opponent_in_range(self.archer, nearest_opponent):
            self.archer.target = nearest_opponent

        opponent_distance = (self.archer.position - self.archer.target.position).length()
        
        if distance_to_enemy_base < self.archer.min_target_distance and opponent_distance > self.archer.min_target_distance * 0.5:
            self.archer.target = enemy_base
            opponent_distance = distance_to_enemy_base
        
        if opponent_distance - self.archer.min_target_distance > 10:
            #move towards target
            self.archer.velocity = self.archer.target.position - self.archer.position
        elif opponent_distance - self.archer.min_target_distance < -5:
            #retreat to base
            
            if self.current_connection < self.path_length:
                self.archer.velocity = self.archer.move_target.position - self.archer.position
            else:
                self.archer.velocity = self.archer.position - self.archer.target.position
        else:
            self.archer.velocity = Vector2(0, 0)
            
        if (self.archer.position - self.archer.move_target.position).length() < 32:
            # continue on path
            if self.current_connection < self.path_length:
                self.archer.move_target.position = self.path[self.current_connection].toNode.position
                self.current_connection += 1

        if self.archer.velocity.length() > 0:
            self.archer.velocity.normalize_ip();
            self.archer.velocity *= self.archer.maxSpeed


    def check_conditions(self):

        # target is gone
        if self.archer.world.get(self.archer.target.id) is None or self.archer.target.ko:
            self.archer.target = None
            return "seeking"
        
        nearest_opponent = self.archer.world.get_nearest_opponent(self.archer)
        opponent_distance = (self.archer.position - nearest_opponent.position).length()
        
        if len(self.archer.projectiles) > 0 and opponent_distance > self.archer.min_target_distance * 0.5:
            return "dodging"
        
        if is_stuck(self.archer):
            return "unstuck"

        return None

    def entry_actions(self):

        nearest_node = self.archer.path_graph.get_nearest_node(self.archer.position)

        self.path = pathFindAStar(self.archer.path_graph, \
                                  nearest_node, \
                                  self.archer.path_graph.nodes[self.archer.base.spawn_node_index])
        
        
        self.path_length = len(self.path)

        if (self.path_length > 1):
            # will not go back to node before continuing
            distance_from_node_to_base = (Vector2(self.path[0].fromNode.position) - Vector2(self.archer.base.position)).length()
            distance_from_archer_to_base = (Vector2(self.archer.position) - Vector2(self.archer.base.position)).length()

            if distance_from_archer_to_base < distance_from_node_to_base:
                self.path.pop(0)
                self.path_length -= 1
                
            self.archer.move_target.position = self.path[0].fromNode.position

        else:
            self.archer.move_target.position = self.archer.path_graph.nodes[self.archer.base.spawn_node_index].position

        self.current_connection = 0


class ArcherStateKO_ZhugeLiang(State):

    def __init__(self, archer):

        State.__init__(self, "ko")
        self.archer = archer

    def do_actions(self):

        return None


    def check_conditions(self):

        # respawned
        if self.archer.current_respawn_time <= 0:
            self.archer.current_respawn_time = self.archer.respawn_time
            self.archer.ko = False
            
            path_graph_id = max(self.archer.opponents, key=self.archer.opponents.get)
            
            if path_graph_id != 0 or path_graph_id != 1:
                path_graph_id = randint(0, 1)
            
            self.archer.path_graph = self.archer.world.paths[path_graph_id]
            return "seeking"
            
        return None

    def entry_actions(self):

        self.archer.current_hp = self.archer.max_hp
        self.archer.position = Vector2(self.archer.base.spawn_position)
        self.archer.velocity = Vector2(0, 0)
        self.archer.target = None

        return None
