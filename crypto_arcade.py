import random
import pygame
import pymunk
import time
from operator import sub
import numpy as np

class TimeFunction():
    import time
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs) -> None:
        t1 = time.time()
        self.func(*args, **kwargs)
        t2 = time.time()-t1
        print('Function {} run time {}'.format(self.func.__name__,t2-t2))


class Button():
    def __init__(self, surface, pos: tuple, width: int, height: int,
                 shape_color: tuple = (200, 200, 200),
                 shape_highlight_color: tuple = (200, 200, 200),
                 text: str = '', font: str = 'comicsans', font_size: int = 30,
                 font_color: tuple = (255, 255, 255)):
        self.surface = surface
        self.pos = pos
        self.width = width
        self.height = height
        self.shape_color = shape_color
        self.shape_highlight_color = shape_highlight_color
        self.font = font
        self.font_size = font_size
        self.font_color = font_color
        self.text = text
        self.click_delay = 0.2  # delay between clicks
        self.click_time = time.time()

        self.create_shape()
        self.in_game_font = pygame.font.SysFont(self.font, self.font_size)

    def create_shape(self):
        self.button = pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)

    def add_text(self):
        text_font = self.in_game_font.render(self.text, 1, self.font_color)
        self.surface.blit(text_font,
                          (self.pos[0] + self.width // 2 - text_font.get_width() // 2,
                           self.pos[1] + self.height // 2 - text_font.get_height() // 2))

    def draw(self):
        mousex, mousey = pygame.mouse.get_pos()
        if mousex < self.button.x or mousex > self.button.x + self.button.width or mousey < self.button.y or mousey > self.button.y + self.button.height:
            pygame.draw.rect(self.surface, self.shape_color, self.button)
        else:
            pygame.draw.rect(self.surface, self.shape_highlight_color, self.button)
        self.add_text()

    def click(self, func, *args, **kwargs):
        mousex, mousey = pygame.mouse.get_pos()
        (leftclick, _, _) = pygame.mouse.get_pressed()
        if self.button.x <= mousex <= self.button.x + self.button.width and \
                self.button.y <= mousey <= self.button.y + self.button.height and \
                leftclick and \
                time.time() - self.click_time > self.click_delay:
            self.click_time = time.time()
            func(*args, **kwargs)

    def is_clicked(self):
        mousex, mousey = pygame.mouse.get_pos()
        (leftclick, _, _) = pygame.mouse.get_pressed()
        if self.button.x <= mousex <= self.button.x + self.button.width and \
                self.button.y <= mousey <= self.button.y + self.button.height and \
                leftclick:
            return True


class Ball():
    def __init__(self, space, surface, start_coords: tuple, start_velocity: tuple = (0, 0),
                 rad: int = 15,
                 texture=None) -> None:
        self.body = pymunk.Body(body_type=pymunk.Body.DYNAMIC)
        self.body.position = start_coords
        self.body.velocity = start_velocity
        self.shape = pymunk.Circle(self.body, 15)
        self.shape.density = 1
        self.shape.elasticity = 0.5
        space.add(self.body, self.shape)
        self.surface = surface
        self.rad = rad
        self.rect_shape = pygame.Rect(self.body.position[0], self.body.position[1], self.rad, self.rad)
        self.texture = texture['image']
        self.coin_offset_x = texture['x offset']
        self.coin_offset_y = texture['y offset']
        if self.texture is not None:
            self.rect = self.texture.get_rect()
            self.centrex, self.centrey = self.rect_shape.center

    def remove(self, space):
        space.remove(self.shape, self.body)

    def rot_center(self, angle):
        """rotate an image while keeping its center and size"""
        orig_rect = self.texture.get_rect()
        rot_texture = pygame.transform.rotate(self.texture, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_texture.get_rect().center
        rot_texture = rot_texture.subsurface(rot_rect).copy()
        return rot_texture

    def draw(self, camera):
        x, y = self.body.position
        self.rect_shape = pygame.Rect(x, y, self.rad, self.rad)
        camerax = camera[0]
        cameray = camera[1]
        pygame.draw.circle(self.surface, (255, 255, 255), (int(x - camerax), int(y - cameray)), self.rad)
        if self.texture is not None:
            self.surface.blit(self.texture, (x - camerax - self.coin_offset_x, y - cameray - self.coin_offset_y))


class Player(Ball):

    arbiter_info = None

    def __init__(self, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)
        self.score = 0
        self.power_up = None
        self.shape.filter = pymunk.ShapeFilter(categories=0b1)
        self.shape.collision_type = 5
        self.jumped = False

    def super_jump(self):
        if self.score >= 1:
            self.body.velocity += 30, -800
            self.score -= 1

    def bouncy(self):
        if self.score >= 5:
            self.shape.elasticity = 1
            self.score -= 5

    def mega_jump(self):
        if self.score >= 10:
            self.body.velocity += 60, -7000
            self.score -= 10

    def launch(self, window_width, window_height, delx, dely):
        max_speed = 5e1

        abs_delx = np.abs(delx)
        abs_dely = np.abs(dely)

        xscale = (max_speed / window_width / 2) * abs_delx
        yscale = (max_speed / window_height / 2) * abs_dely

        self.body.velocity += delx * xscale, dely * yscale

    @staticmethod
    def coll_begin(arbiter, space, data) -> bool:
        Player.get_contact_info(arbiter)
        return True

    @classmethod
    def get_contact_info(cls, arbiter) -> None:
        cls.arbiter_info = arbiter

    def add_collision_handler(self, space, collision_type1: int = 5, collision_type2: int = 5) -> None:
        self.col_handler = space.add_collision_handler(collision_type1, collision_type2)
        self.col_handler.pre_solve = Player.coll_begin

class NoStringObjectError(Exception):
    def __init__(self):
        self.message = 'Platform needs a string object before creation'
        super().__init__(self.message)

class Box(Ball):

    arbiter_info = None

    def __init__(self, surface, position: tuple, width: int, height: int, colour=(100, 255, 100), index: int=0):
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = (position[0] + width // 2, position[1] + height // 2)
        self.shape = pymunk.Poly.create_box(self.body, (width, height))
        self.shape.filter = pymunk.ShapeFilter(categories=1)
        self.shape.elasticity = 1
        self.width = width
        self.height = height
        self.surface = surface
        self.colour = colour
        self.position = position
        self.index = index

        details = {
            'type': 'box',
            'body': self.body,
            'segment': self.shape,
            'pivot joint': None,
            'colour': self.colour
        }

        self.object_details = [details]

    def add_string(self, length: int = 5, num_elements: int = 5, thickness: float = 5,
                   colour: tuple = (100, 255, 100)) -> None:
        self.length = length
        self.num_elements = num_elements if num_elements < length else length
        self.length_per_element = self.length / self.num_elements
        self.thickness = thickness
        self.string_colour = colour

        self.box_x = self.body.position.x
        self.box_y = self.body.position.y
        self.box_height = self.height

        element_y = self.box_y + self.box_height / 2
        self.y_coords = []
        first_body = self.body
        for i in range(self.num_elements):
            self.y_coords.append(element_y)

            body = pymunk.Body(100000, 10000000)
            body.position = (self.box_x, element_y + self.length_per_element / 2)
            segment = pymunk.Poly.create_box(body, (self.thickness, self.length_per_element))
            segment.filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS() ^ 0b1)
            # segment = pymunk.Segment(body,(self.box_x-self.thickness/2, element_y),(self.box_x+self.thickness/2, element_y+self.length_per_element), self.thickness/2)
            pivot_point = pymunk.PivotJoint(first_body, body, (self.box_x - self.thickness / 2, element_y))

            details = {
                'type': 'string',
                'body': body,
                'segment': segment,
                'pivot joint': pivot_point,
                'colour': self.string_colour
            }
            self.object_details.append(details)
            element_y += self.length_per_element
            first_body = body

    def get_string_objects(self) -> list:
        string_objects = []
        for object in self.object_details:
            if object['type'] == 'string': string_objects.append(object)
        return string_objects

    def get_platform_objects(self) -> list:
        platform_objects = []
        for object in self.object_details:
            if object['type'] == 'platform': platform_objects.append(object)
        return platform_objects

    @staticmethod
    def coll_pre_solve(arbiter, space, data) -> bool:
        Box.get_contact_info(arbiter)
        return True

    @classmethod
    def get_contact_info(cls,arbiter) -> None:
        cls.arbiter_info = arbiter

    def add_collision_handler(self, space, collision_type1: int = 5, collision_type2: int = 5) -> None:
        self.col_handler = space.add_collision_handler(collision_type1, collision_type2)
        self.col_handler.pre_solve = Box.coll_pre_solve

    def add_platform(self, length: int = 30, thickness: float = 5,
                     colour: tuple = (100, 255, 100)) -> None:
        if not any([object['type'] == 'string' for object in self.object_details]):
            raise NoStringObjectError()

        self.platform_length = length
        self.platform_thickness = thickness
        self.platform_colour = colour

        body = pymunk.Body(1e5, 1e11)
        body.position = (self.box_x, self.box_y + self.box_height / 2 + self.length)
        velocity = [(750, 0),(-750, 0)]
        body.velocity = random.choice(velocity)
        segment = pymunk.Poly.create_box(body, (self.platform_length, self.thickness))
        segment.filter = pymunk.ShapeFilter(categories=1)
        segment.collision_type = 5
        segment.friction = 1e200
        string_objects = self.get_string_objects()
        pivot_point = pymunk.PivotJoint(string_objects[-1]['body'], body,
                                        (self.box_x, self.box_y + self.box_height / 2 + self.length))

        details = {
            'type': 'platform',
            'body': body,
            'segment': segment,
            'pivot joint': pivot_point,
            'colour': self.platform_colour
        }
        self.object_details.append(details)

    def draw(self, camera) -> None:
        camerax = camera[0]
        cameray = camera[1]
        for object in self.object_details:
            if object['type'] == 'box':
                self.rect = pygame.Rect(self.position[0] - camerax, self.position[1] - cameray, self.width, self.height)
            elif object['type'] == 'string':
                self.rect = pygame.Rect(object['body'].position.x - self.thickness / 2 - camerax,
                                        object['body'].position.y - self.length_per_element / 2 - cameray,
                                        self.thickness,
                                        self.length_per_element)
            elif object['type'] == 'platform':
                self.rect = pygame.Rect(object['body'].position.x - self.platform_length / 2 - camerax,
                                        object['body'].position.y - self.platform_thickness / 2 - cameray,
                                        self.platform_length,
                                        self.platform_thickness)
            pygame.draw.rect(self.surface, object['colour'], self.rect)

    def add2space(self, space) -> None:
        for object in self.object_details:
            if not object['pivot joint']:
                space.add(object['body'], object['segment'])
            else:
                space.add(object['body'], object['segment'], object['pivot joint'])

    def remove(self, space) -> None:
        for object in self.object_details:
            if not object['pivot joint']:
                space.remove(object['body'], object['segment'])
            else:
                space.remove(object['body'], object['segment'], object['pivot joint'])


class Floor(Ball):
    def __init__(self, space, surface, p1: tuple, p2: tuple, collision_number=None,
                 colour=(255, 0, 0)):
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.shape = pymunk.Segment(self.body, p1, p2, 1)
        self.shape.elasticity = 1
        self.surface = surface
        if collision_number:
            self.shape.collision_type = collision_number
        space.add(self.body, self.shape)
        self.colour = colour

    def draw(self, camera):
        camerax = camera[0]
        cameray = camera[1]
        pygame.draw.line(self.surface, self.colour, tuple(map(sub, self.shape.a, camera)),
                         tuple(map(sub, self.shape.b, camera)),
                         width=5)


class StartWall(Ball):
    def __init__(self, space, p1: tuple, p2: tuple, collision_number=None):
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.shape = pymunk.Segment(self.body, p1, p2, 1)
        self.shape.elasticity = 1
        if collision_number:
            self.shape.collision_type = collision_number
        space.add(self.body, self.shape)


class Coin():
    def __init__(self, surface, pos: tuple = (0, 0), rad: int = 15, texture=None, colour=(255, 255, 255)):
        self.surface = surface
        self.pos = pos
        self.rad = rad
        self.texture = texture
        self.colour = colour
        self.collided = False
        self.rect_shape = pygame.Rect(self.pos[0], self.pos[1], self.rad, self.rad)

    def check_collision(self, ball_position: tuple):
        if self.pos[0] <= ball_position[0] <= self.pos[0] + self.rad and \
                self.pos[1] <= ball_position[1] <= self.pos[1] + self.rad:
            self.collided = True
            return True
        return False

    def draw(self, camera):
        x, y = self.pos
        camerax = camera[0]
        cameray = camera[1]
        pygame.draw.circle(self.surface, self.colour, (int(x - camerax), int(y - cameray)), self.rad)
        if self.texture is not None:
            self.surface.blit(self.texture, (x - camerax, y - cameray))
