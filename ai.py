import math
import pymunk
from pymunk import Vec2d
import gameobjects
from collections import defaultdict, deque

# NOTE: use only 'map0' during development!

MIN_ANGLE_DIF = math.radians(3) # 3 degrees, a bit more than we can turn each tick


def angle_between_vectors(vec1, vec2):
    """ Since Vec2d operates in a cartesian coordinate space we have to
        convert the resulting vector to get the correct angle for our space.
    """
    vec = vec1 - vec2 
    vec = vec.perpendicular()
    return vec.angle

def periodic_difference_of_angles(angle1, angle2): 
    return  (angle1% (2*math.pi)) - (angle2% (2*math.pi))


class Ai:
    """ A simple ai that finds the shortest path to the target using 
    a breadth first search. Also capable of shooting other tanks and or wooden
    boxes. """

    def __init__(self, tank,  game_objects_list, tanks_list, space, currentmap):
        self.tank               = tank
        self.game_objects_list  = game_objects_list
        self.tanks_list         = tanks_list
        self.space              = space
        self.currentmap         = currentmap
        self.flag               = None
        self.MAX_X              = currentmap.width - 1 
        self.MAX_Y              = currentmap.height - 1
        self.last_distance      = math.inf
        self.allow_iron_box     = False
        self.next_coord         = Vec2d()

        self.path = deque()
        self.move_cycle = self.move_cycle_gen()
        self.update_grid_pos()

    def update_grid_pos(self):
        """ This should only be called in the beginning, or at the end of a move_cycle. """
        self.grid_pos = self.get_tile_of_position(self.tank.body.position)

    def decide(self):
        """ Main decision function that gets called on every tick of the game. """
        self.maybe_shoot()
        if self.tank.body.position == self.tank.start_position:
            self.next_coord = self.find_shortest_path().popleft()
        next(self.move_cycle)

    def maybe_shoot(self):
        """ Makes a raycast query in front of the tank. If another tank
            or a wooden box is found, then we shoot. 
        """

        
        tank_x = (self.tank.body.position[0] - (math.sin(self.tank.body.angle)))
        tank_y = (self.tank.body.position[1] + (math.cos(self.tank.body.angle)))
        map_end_x = (self.tank.body.position[0] - (math.sin(self.tank.body.angle))*(self.MAX_X + 1))
        map_end_y = (self.tank.body.position[1] + (math.cos(self.tank.body.angle))*(self.MAX_Y + 1))

        ray = self.space.segment_query_first((tank_x, tank_y), (map_end_x, map_end_y), 0, pymunk.ShapeFilter())
        if hasattr(ray, "shape"):
            # print("has shape")
            if isinstance(ray.shape.parent, gameobjects.Tank) and self.tank.shoot_time > 50:
                # print("sees tank")
                self.game_objects_list.append((self.tank.shoot(self.space)))
            elif isinstance(ray.shape.parent, gameobjects.Box) and self.tank.shoot_time > 50:
                # print("is box")
                if ray.shape.parent.destructable:
                    self.game_objects_list.append(self.tank.shoot(self.space))

    def correct_position(self, next_coord, distance):
        current_distance = self.tank.body.position.get_distance(next_coord) #+ Vec2d(0.5, 0.5))
        if current_distance > self.last_distance:
            self.last_distance = 1000
            return True
        self.last_distance = current_distance
        return False

    
    def correct_angle(self, coord):
        # if self.tank.body.angle / math.pi == 0 or self.tank.body.angle / math.pi == 1:
            # print("tank: ", self.tank, "is calling: correct_angle, with angle:", self.tank.body.angle, ", and is searching for coord:", coord)
        angle = angle_between_vectors(self.tank.body.position, coord)
        if abs(periodic_difference_of_angles(self.tank.body.angle, angle)) <= MIN_ANGLE_DIF:
            self.tank.accelerate()
            self.tank.stop_turning()
            return True
        else:
            return False


    def turn(self, next_coord):
        wanted_angle = angle_between_vectors(self.tank.body.position, next_coord)
        difference = periodic_difference_of_angles(self.tank.body.angle, wanted_angle)
        self.tank.stop_moving()

        if difference >= 0:
            if difference < math.pi:
                self.tank.turn_left()
            else:
                self.tank.turn_right()
        else:
            if abs(difference) < math.pi:
                self.tank.turn_right()
            else:
                self.tank.turn_left()

        return False

    def move_cycle_gen(self):
        """ A generator that iteratively goes through all the required steps
            to move to our goal.
        """ 
        while True:

            self.update_grid_pos()
            shortest_path = self.find_shortest_path()
            if shortest_path == deque([]):
                print("empty shortest path")
                yield
                continue
            self.next_coord = shortest_path.popleft()
            self.next_coord += (0.5, 0.5)

            yield
            
            self.turn(self.next_coord)

            while not self.correct_angle(self.next_coord):
                yield
            
            self.tank.accelerate()

            while not self.correct_position(self.next_coord, self.last_distance):
                yield

            self.update_grid_pos()
            yield
        
    def find_shortest_path(self):
        """ A simple Breadth First Search using integer coordinates as our nodes.
            Edges are calculated as we go, using an external function.
        """
        self.update_grid_pos()
        self.path = deque([])
        visited = set()
        self.path.append(self.grid_pos.int_tuple)
        visited.add(self.grid_pos.int_tuple)
        pathes = {}
        shortest_path = []


        while self.path != deque([]):
            

            if self.grid_pos.int_tuple == self.get_target_tile():
                shortest_path = [self.grid_pos]
                break

            node = self.path.popleft()

            tile_neighbor = self.get_tile_neighbors(Vec2d(node))

            for element in tile_neighbor:
                if not element.int_tuple in visited:
                    self.path.append(element.int_tuple)
                    visited.add(element.int_tuple)
                
                    if not node in pathes:
                        pathes[element.int_tuple] = [element]
                    else:
                        new_path = pathes[node].copy()
                        new_path.append(element)
                        if not element.int_tuple in pathes:
                            pathes[element.int_tuple] = new_path
                  
                if node == self.get_target_tile():
                    shortest_path = pathes[node]
                    break
        
        if shortest_path == []:
            self.allow_iron_box = True
            temporary = self.find_shortest_path()
            self.allow_iron_box = False
            return deque(temporary)
        else:
            return deque(shortest_path)

            
    def get_target_tile(self):
        """ Returns position of the flag if we don't have it. If we do have the flag,
            return the position of our home base.
        """
        # print(self.tank.flag)
        if self.tank.flag != None:
            x, y = self.tank.start_position
        else:
            self.get_flag() # Ensure that we have initialized it.
            x, y = self.flag.x, self.flag.y
        return Vec2d(int(x), int(y))

    def get_flag(self):
        """ This has to be called to get the flag, since we don't know
            where it is when the Ai object is initialized.
        """
        if self.flag == None:
        # Find the flag in the game objects list
            for obj in self.game_objects_list:
                if isinstance(obj, gameobjects.Flag):
                    self.flag = obj
                    break
        return self.flag

    def get_tile_of_position(self, position_vector):
        """ Converts and returns the float position of our tank to an integer position. """
        x, y = position_vector
        return Vec2d(int(x), int(y))

    def get_tile_neighbors(self, coord_vec):
        """ Returns all bordering grid squares of the input coordinate.
            A bordering square is only considered accessible if it is grass
            or a wooden box.
        """
        #TODO: Should it round down?
        above = coord_vec + (0, 1)
        below = coord_vec + (0,-1)
        right_side = coord_vec + (1, 0)
        left_side = coord_vec + (-1, 0)
        neighbors = [above, below, right_side, left_side] # Find the coordinates of the tiles' four neighbors
        # print(filter(self.filter_tile_neighbors, neighbors)) 
        return filter(self.filter_tile_neighbors, neighbors)

    def filter_tile_neighbors (self, coord):
        if 0 <= coord[0] < self.MAX_X + 1 and 0 <= coord[1] < self.MAX_Y + 1:
            coord_is_grass = self.currentmap.boxAt(coord[0], coord[1]) == 0
            coord_is_wood = self.currentmap.boxAt(coord[0], coord[1]) == 2
            coord_is_iron = self.currentmap.boxAt(coord[0], coord[1]) == 3
            if not self.allow_iron_box:
                if (coord_is_grass or coord_is_wood):
                    return True
                else:
                    return False
            else:
                if (coord_is_grass or coord_is_wood or coord_is_iron):
                    return True
                else:
                    return False
SimpleAi = Ai # Legacy