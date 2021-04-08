import pygame
import pymunk
import time
from operator import sub



class Button():
    def __init__(self, surface, pos: tuple[int, int], width: int, height: int,
                 shape_color: tuple[int, int, int] = (200, 200, 200),
                 shape_highlight_color: tuple[int, int, int] = (200, 200, 200),
                 text: str = '', font: str = 'comicsans', font_size: int = 30,
                 font_color: tuple[int, int, int] = (255, 255, 255)):
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

    def click(self, func, *args):
        mousex, mousey = pygame.mouse.get_pos()
        (leftclick, _, _) = pygame.mouse.get_pressed()
        if self.button.x <= mousex <= self.button.x + self.button.width and \
                self.button.y <= mousey <= self.button.y + self.button.height and \
                leftclick and \
                time.time() - self.click_time > self.click_delay:
            self.click_time = time.time()
            func(*args)

    def is_clicked(self):
        mousex, mousey = pygame.mouse.get_pos()
        (leftclick, _, _) = pygame.mouse.get_pressed()
        if self.button.x <= mousex <= self.button.x + self.button.width and \
                self.button.y <= mousey <= self.button.y + self.button.height and \
                leftclick:
            return True


class Ball():
    def __init__(self, space, surface, start_coords: tuple[int, int], start_velocity: tuple[int, int] = (0, 0), rad: int = 15,
                 texture=None):
        self.body = pymunk.Body(body_type=pymunk.Body.DYNAMIC)
        self.body.position = start_coords
        self.body.velocity = start_velocity
        self.shape = pymunk.Circle(self.body, 15)
        self.shape.density = 1
        self.shape.elasticity = 0.5
        space.add(self.body, self.shape)
        # self.shape.collision_type = 2
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
        space.remove(self.body, self.shape)

    def rot_center(self, angle):
        """rotate an image while keeping its center and size"""
        orig_rect = self.texture.get_rect()
        rot_texture = pygame.transform.rotate(self.texture, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_texture.get_rect().center
        rot_texture = rot_texture.subsurface(rot_rect).copy()
        return rot_texture

    def draw(self,camera):
        x, y = self.body.position
        self.rect_shape = pygame.Rect(x, y, self.rad, self.rad)
        camerax = camera[0]
        cameray = camera[1]
        pygame.draw.circle(self.surface, (255, 255, 255), (int(x - camerax), int(y - cameray)), self.rad)
        if self.texture is not None:
            self.surface.blit(self.texture, (x - camerax - self.coin_offset_x, y - cameray - self.coin_offset_y))


class Player(Ball):
    def __init__(self, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)
        self.score = 0
        self.power_up = None

    def super_jump(self):
        if self.score >= 1:
            self.body.velocity += 30, -800
            self.score -= 1

    def bouncy(self):
        if self.score >= 5:
            self.shape.elasticity = 1
            self.score -= 5

    def low_g(self,space):
        if self.score >= 10:
            space.gravity = 0, 700
            self.score -= 10


class Floor(Ball):
    def __init__(self, space, surface, p1: tuple[int, int], p2: tuple[int, int], collision_number=None):
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.shape = pymunk.Segment(self.body, p1, p2, 1)
        self.shape.elasticity = 1
        self.surface = surface
        if collision_number:
            self.shape.collision_type = collision_number
        space.add(self.body, self.shape)

    def draw(self,camera):
        camerax = camera[0]
        cameray = camera[1]
        pygame.draw.line(self.surface, (255, 0, 0), tuple(map(sub, self.shape.a, camera)), tuple(map(sub, self.shape.b, camera)),
                         width=5)


class StartWall(Ball):
    def __init__(self, space, p1: tuple[int, int], p2: tuple[int, int], collision_number=None):
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.shape = pymunk.Segment(self.body, p1, p2, 1)
        self.shape.elasticity = 1
        if collision_number:
            self.shape.collision_type = collision_number
        space.add(self.body, self.shape)


class Coin():
    def __init__(self, surface, pos: tuple[int, int] = (0, 0), rad: int = 15, texture=None, colour=(255, 255, 255)):
        self.surface = surface
        self.pos = pos
        self.rad = rad
        self.texture = texture
        self.colour = colour
        self.collided = False
        self.rect_shape = pygame.Rect(self.pos[0], self.pos[1], self.rad, self.rad)

    def check_collision(self, ball_position: tuple[int, int]):
        if self.pos[0] <= ball_position[0] <= self.pos[0] + self.rad and \
                self.pos[1] <= ball_position[1] <= self.pos[1] + self.rad:
            self.collided = True
            return True
        return False

    def draw(self,camera):
        x, y = self.pos
        camerax = camera[0]
        cameray = camera[1]
        pygame.draw.circle(self.surface, self.colour, (int(x - camerax), int(y - cameray)), self.rad)
        if self.texture is not None:
            self.surface.blit(self.texture, (x - camerax, y - cameray))