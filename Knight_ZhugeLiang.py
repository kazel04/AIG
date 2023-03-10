import pygame
from random import randint, random
from Graph import *

from Character import *
from State import *

from Utlis_ZhugeLiang import *

class Knight_ZhugeLiang(Character):

    def __init__(self, world, image, base, position):

        Character.__init__(self, world, "knight", image)

        self.base = base
        self.position = position
        self.move_target = GameEntity(world, "knight_move_target", None)
        self.target = None

        self.maxSpeed = 80
        self.min_target_distance = 100
        self.melee_damage = 20
        self.melee_cooldown = 2.

        seeking_state = KnightStateSeeking_ZhugeLiang(self)
        attacking_state = KnightStateAttacking_ZhugeLiang(self)
        defending_state = KnightStateDefending_ZhugeLiang(self)
        ko_state = KnightStateKO_ZhugeLiang(self)

        self.brain.add_state(seeking_state)
        self.brain.add_state(attacking_state)
        self.brain.add_state(defending_state)
        self.brain.add_state(ko_state)

        self.brain.set_state("seeking")
        

    def render(self, surface):

        Character.render(self, surface)


    def process(self, time_passed):
        
        Character.process(self, time_passed)

        level_up_stats = ["hp", "speed", "melee damage", "melee cooldown"]
        if self.can_level_up():
            choice = 0 #always choose to increase hp!
            self.level_up(level_up_stats[choice])

class KnightStateSeeking_ZhugeLiang(State):

    def __init__(self, knight):

        State.__init__(self, "seeking")
        self.knight = knight

        self.knight.path_graph = self.knight.world.paths[randint(2,3)] #always attack mid first, then switch to bott


    def do_actions(self):

        self.knight.velocity = self.knight.move_target.position - self.knight.position
        if self.knight.velocity.length() > 0:

            self.knight.velocity.normalize_ip();
            self.knight.velocity *= self.knight.maxSpeed


    def check_conditions(self):
        # add priority system incl tower & orcs! Cos now can only target heroes
        # check if opponent is in range TBD: ADD PRIORITY FOR THIS STATE(archer first, then wizard, then knight)
        nearest_opponent = self.knight.world.get_nearest_opponent(self.knight)
        #add switch to defence state if the last tower is down
        
        #&also defend allied wizard
        if nearest_opponent is not None and nearest_opponent.team_id is not self.knight.team_id:
            if is_opponent_in_range(self.knight, nearest_opponent):
                if nearest_opponent.name == "archer":
                    opponent_distance = (self.knight.position - nearest_opponent.position).length()
                    if opponent_distance <= self.knight.min_target_distance:
                            self.knight.target = nearest_opponent
                            return "attacking"
                elif nearest_opponent.name == "wizard":
                    second_nearest = get_second_nearest_opponent(self.knight, self.knight) #checking if there is a wizard in the vicinity
                    if second_nearest is not None:
                        if second_nearest.name == "archer" and is_opponent_in_range(self.knight, second_nearest):
                            opponent_distance = (self.knight.position - second_nearest.position).length()
                            if opponent_distance <= self.knight.min_target_distance:
                                    self.knight.target = second_nearest
                                    return "attacking"
                        else:
                            opponent_distance = (self.knight.position - second_nearest.position).length()
                            if opponent_distance <= self.knight.min_target_distance:
                                    self.knight.target = nearest_opponent
                                    return "attacking"
                         
                elif nearest_opponent.name == "knight":
                    second_nearest = get_second_nearest_opponent(self.knight, self.knight)
                    if second_nearest is not None:
                        if second_nearest.name == "archer" and is_opponent_in_range(self.knight, second_nearest):
                            opponent_distance = (self.knight.position - second_nearest.position).length()
                            if opponent_distance <= self.knight.min_target_distance:
                                    self.knight.target = second_nearest
                                    return "attacking"
                        elif second_nearest.name == "wizard" and is_opponent_in_range(self.knight, second_nearest):
                            opponent_distance = (self.knight.position - second_nearest.position).length()
                            if opponent_distance <= self.knight.min_target_distance:
                                    self.knight.target = second_nearest
                                    return "attacking"
                        else:
                            opponent_distance = (self.knight.position - nearest_opponent.position).length()
                            if opponent_distance <= self.knight.min_target_distance:
                                    self.knight.target = nearest_opponent
                                    return "attacking"
                else:
                    opponent_distance = (self.knight.position - nearest_opponent.position).length()
                    if opponent_distance <= self.knight.min_target_distance:
                            self.knight.target = nearest_opponent
                            return "attacking"
                         
        #heal if out of range of nearest opponent OR when health is low 
        opponent_distance = (self.knight.position - nearest_opponent.position).length()
        if self.knight.current_hp < self.knight.max_hp and \
            opponent_distance > self.knight.healing_cooldown * self.knight.maxSpeed + self.knight.min_target_distance:
            print("Heal")
            self.knight.heal()
        elif self.knight.current_hp < self.knight.max_hp * 0.2:
            print("Heal")
            self.knight.heal()
                
        
        if (self.knight.position - self.knight.move_target.position).length() < 8:
            if self.current_connection < self.path_length:
                self.knight.move_target.position = self.path[self.current_connection].toNode.position
                self.current_connection += 1
            
            #test case to collect node positions:
# =============================================================================
#                 self.knight.move_target.position = self.path[self.current_connection].toNode.position
#                 print(self.knight.move_target.position)
# =============================================================================

            # continue on path (first movement strategy, tried & moved onto a faster strategy
# =============================================================================
#                 if self.knight.position[0] < 345: #check if x-axis of unit is past first checkpoint
#                     self.knight.move_target.position = (345, 290) # (900, 640)this node position forces the knight to always go centre, now need to program out the moving aside from the tower (nudging left or right till velo not zero?)
#                     
#                 elif self.knight.position[0] < 362:
#                     self.knight.move_target.position = (362,482)
#                     
#                 elif self.knight.position[0] < 671:
#                     #calculate halfway point between previous node & next node to form another shortcut
#                      self.knight.move_target.position = (671,477)
# =============================================================================
            #alternate movement strategy (faster) + MUST INCLUDE ALT PATHS IF SENT TO TOP OR BOTT LANES, problem is the knight will draw fire from the middle tower and cause an initial death especially if engaged with an enemy hero
# =============================================================================
#                 if self.knight.position[0] < 345: #check if x-axis of unit is past first checkpoint
#                     self.knight.move_target.position = (345, 290) # (900, 640)this node position forces the knight to always go centre, now need to program out the moving aside from the tower (nudging left or right till velo not zero?)
#                     
#                 elif self.knight.position[0] < 487:
#                     self.knight.move_target.position = (487,545)
#                     
#                 elif self.knight.position[0] < 900:
#                     #calculate halfway point between previous node & next node to form another shortcut
#                      self.knight.move_target.position = (900,640)
#                 else:
#                     self.knight.move_target.position = self.path[self.current_connection].toNode.position
#                     print(self.knight.move_target.position)
#                 self.current_connection += 1
# =============================================================================
               
        return None


    def entry_actions(self):

        nearest_node = self.knight.path_graph.get_nearest_node(self.knight.position)

        self.path = pathFindAStar(self.knight.path_graph, \
                                  nearest_node, \
                                  self.knight.path_graph.nodes[self.knight.base.target_node_index])
         
        self.path_length = len(self.path)

        if (self.path_length > 0):
           self.current_connection = 0
           self.knight.move_target.position = self.path[0].fromNode.position
        else:
            self.knight.move_target.position = self.knight.path_graph.nodes[self.knight.base.target_node_index].position


class KnightStateAttacking_ZhugeLiang(State):

    def __init__(self, knight):

        State.__init__(self, "attacking")
        self.knight = knight

    def do_actions(self):

        # colliding with target
        if pygame.sprite.collide_rect(self.knight, self.knight.target):
            self.knight.velocity = Vector2(0, 0)
            self.knight.melee_attack(self.knight.target)

        else:
            self.knight.velocity = self.knight.target.position - self.knight.position
            if self.knight.velocity.length() > 0:
                self.knight.velocity.normalize_ip();
                self.knight.velocity *= self.knight.maxSpeed


    def check_conditions(self):

        # target is gone or if target is on a different lane from the Knight if target is a hero & not at either ends of the map where there are no mountains in between, 
        if self.knight.world.get(self.knight.target.id) is None or self.knight.target.ko:
            self.knight.target = None
            return "seeking"
        elif (self.knight.target.name == "knight" or self.knight.target.name == "wizard" or self.knight.target.name == "archer")  and self.knight.target.path_graph is not self.knight.path_graph and (self.knight.position[0] < 345 or self.knight.position[0] > 671):
            self.knight.target = self.knight.target.world.get_nearest_opponent(self.knight.target)
            return "seeking"
            
        return None

    def entry_actions(self):

        return None


class KnightStateKO_ZhugeLiang(State):

    def __init__(self, knight):

        State.__init__(self, "ko")
        self.knight = knight

    def do_actions(self):

        return None


    def check_conditions(self):

        # respawned
        if self.knight.current_respawn_time <= 0:
            self.knight.current_respawn_time = self.knight.respawn_time
            self.knight.ko = False
            self.knight.path_graph = self.knight.world.paths[randint(2,3)]
            #if self.knight.base.current_hp < self.knight.base.max_hp/2: #if base is less than half health, knight will return back to base to protect
                #return "defending"
            return "seeking"
            
        return None

    def entry_actions(self):

        self.knight.current_hp = self.knight.max_hp
        self.knight.position = Vector2(self.knight.base.spawn_position)
        self.knight.velocity = Vector2(0, 0)
        self.knight.target = None

        return None


class KnightStateDefending_ZhugeLiang(State):

    def __init__(self, knight):

        State.__init__(self, "defending")
        self.knight = knight

        self.knight.path_graph = self.knight.world.paths[randint(2,3)] #changed to middle lane
        
    def do_actions(self):

          self.knight.velocity = self.knight.move_target.position - self.knight.position
          if self.knight.velocity.length() > 0:

              self.knight.velocity.normalize_ip();
              self.knight.velocity *= self.knight.maxSpeed
              
    def check_conditions(self):
         # add priority system incl tower & orcs! Cos now can only target heroes
         # check if opponent is in range TBD: ADD PRIORITY FOR THIS STATE(archer first, then wizard, then knight)
         nearest_opponent = self.knight.world.get_nearest_opponent(self.knight)
         #add switch to defence state if the last tower is down
         if nearest_opponent is not None and nearest_opponent.team_id is not self.knight.team_id:
             if is_opponent_in_range(self.knight, nearest_opponent):
                 if nearest_opponent.name == "archer":
                     opponent_distance = (self.knight.position - nearest_opponent.position).length()
                     if opponent_distance <= self.knight.min_target_distance:
                             self.knight.target = nearest_opponent
                             return "attacking"
                 elif nearest_opponent.name == "wizard":
                     second_nearest = get_second_nearest_opponent(self.knight, self.knight) #checking if there is a wizard in the vicinity
                     if second_nearest is not None:
                         if second_nearest.name == "archer" and is_opponent_in_range(self.knight, second_nearest):
                             opponent_distance = (self.knight.position - second_nearest.position).length()
                             if opponent_distance <= self.knight.min_target_distance:
                                     self.knight.target = second_nearest
                                     return "attacking"
                         else:
                             opponent_distance = (self.knight.position - second_nearest.position).length()
                             if opponent_distance <= self.knight.min_target_distance:
                                     self.knight.target = nearest_opponent
                                     return "attacking"
                          
                 elif nearest_opponent.name == "knight":
                     second_nearest = get_second_nearest_opponent(self.knight, self.knight)
                     if second_nearest is not None:
                         if second_nearest.name == "archer" and is_opponent_in_range(self.knight, second_nearest):
                             opponent_distance = (self.knight.position - second_nearest.position).length()
                             if opponent_distance <= self.knight.min_target_distance:
                                     self.knight.target = second_nearest
                                     return "attacking"
                         elif second_nearest.name == "wizard" and is_opponent_in_range(self.knight, second_nearest):
                             opponent_distance = (self.knight.position - second_nearest.position).length()
                             if opponent_distance <= self.knight.min_target_distance:
                                     self.knight.target = second_nearest
                                     return "attacking"
                         else:
                             opponent_distance = (self.knight.position - nearest_opponent.position).length()
                             if opponent_distance <= self.knight.min_target_distance:
                                     self.knight.target = nearest_opponent
                                     return "attacking"
                 else:
                     opponent_distance = (self.knight.position - nearest_opponent.position).length()
                     if opponent_distance <= self.knight.min_target_distance:
                             self.knight.target = nearest_opponent
                             return "attacking"
                          
         #heal if out of range of nearest opponent OR when health is low & lower than opponent
         opponent_distance = (self.knight.position - nearest_opponent.position).length()
         if self.knight.current_hp < self.knight.max_hp and \
             opponent_distance > self.knight.healing_cooldown * self.knight.maxSpeed + self.knight.min_target_distance:
             print("Heal")
             self.knight.heal()
         elif self.knight.current_hp < self.knight.max_hp * 0.2:
             print("Heal")
             self.knight.heal()
                 
         
         if (self.knight.position - self.knight.move_target.position).length() < 8:
             if self.current_connection < self.path_length:
                 if self.knight.move_target.position[0] > 50:
                     self.knight.move_target.position = (150,50)
                 self.current_connection += 1
               
    def entry_actions(self):

        nearest_node = self.knight.path_graph.get_nearest_node(self.knight.position)

        self.path = pathFindAStar(self.knight.path_graph, \
                                  nearest_node, \
                                  self.knight.path_graph.nodes[self.knight.base.target_node_index])
 
        
        self.path_length = len(self.path)

        if (self.path_length > 0):
           self.current_connection = 0
           self.knight.move_target.position = self.path[0].fromNode.position
        else:
            self.knight.move_target.position = self.knight.path_graph.nodes[self.knight.base.target_node_index].position
            
    
    
