import pygame
import pymunk
from record_data import Historical_data
import numpy as np
from operator import sub
import time
import random
import os

pygame.font.init()

WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
WIN_GAME = pygame.display.set_mode((WIDTH, HEIGHT))
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_BLUE = (68, 85, 128)
LIGHT_LIGHT_BLUE = (85, 105, 158)
pygame.display.set_caption('Crypto Games')

BAR_WIDTH = 60

VEL_STEP = 15
VEL_MAX = 300
BASE_ROTATION_SPEED = VEL_MAX

FPS = 144

IN_GAME_FONT = pygame.font.SysFont('comicsans', 30)
TITLE_FONT = pygame.font.SysFont('comicsans', 75)
MARKET_CHOICE_FONT = pygame.font.SysFont('comicsans', 55)

space = pymunk.Space()
space.gravity = 0, 460

NUM_BALLS = 100

COINS_SPACING_MIN = 4
COINS_SPACING_MAX = 18

global camerax, cameray
camerax = 0
cameray = 0

BITCOIN_IMAGE = pygame.image.load(os.path.join('assets', 'bitcoin.png')).convert_alpha()
BITCOIN_IMAGE = pygame.transform.scale(BITCOIN_IMAGE, (37, 37))

ETH_IMAGE = pygame.image.load(os.path.join('assets', 'eth.png')).convert_alpha()
ETH_IMAGE = pygame.transform.scale(ETH_IMAGE, (30, 30))

DOGECOIN_IMAGE = pygame.image.load(os.path.join('assets', 'dogecoin.png')).convert_alpha()
DOGECOIN_IMAGE = pygame.transform.scale(DOGECOIN_IMAGE, (int(31), 31))

COIN_INFO = [
    {'image': BITCOIN_IMAGE, 'x offset': 19, 'y offset': 19, 'scale': 1},
    {'image': ETH_IMAGE, 'x offset': 15, 'y offset': 16, 'scale': 0.7e1},
    {'image': DOGECOIN_IMAGE, 'x offset': 16, 'y offset': 16, 'scale': 0.85e6}
]


def clear_all_bodies(space):
    if len(space.bodies) > 0:
        for body in space.bodies:
            space.remove(body)
        return True
    return False


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
        text_font = self.in_game_font.render(self.text, 1, WHITE)
        self.surface.blit(text_font,
                          (self.pos[0] + self.width // 2 - text_font.get_width() // 2,
                           self.pos[1] + self.height // 2 - text_font.get_height() // 2))

    def draw(self, text=''):
        if text != '':
            self.text = text
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
    def __init__(self, surface, start_coords: tuple[int, int], start_velocity: tuple[int, int] = (0, 0), rad: int = 15,
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

    def remove(self):
        space.remove(self.body, self.shape)

    def rot_center(self, angle):
        """rotate an image while keeping its center and size"""
        orig_rect = self.texture.get_rect()
        rot_texture = pygame.transform.rotate(self.texture, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_texture.get_rect().center
        rot_texture = rot_texture.subsurface(rot_rect).copy()
        return rot_texture

    def draw(self):
        x, y = self.body.position
        self.rect_shape = pygame.Rect(x, y, self.rad, self.rad)
        global camerax, cameray
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

    def low_g(self):
        if self.score >= 10:
            space.gravity = 0, 700
            self.score -= 10


class Floor(Ball):
    def __init__(self, p1: tuple[int, int], p2: tuple[int, int], collision_number=None):
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.shape = pymunk.Segment(self.body, p1, p2, 1)
        self.shape.elasticity = 1
        if collision_number:
            self.shape.collision_type = collision_number
        space.add(self.body, self.shape)

    def draw(self):
        global camerax, cameray
        camera = camerax, cameray
        pygame.draw.line(WIN, (255, 0, 0), tuple(map(sub, self.shape.a, camera)), tuple(map(sub, self.shape.b, camera)),
                         width=5)


class StartWall(Ball):
    def __init__(self, p1: tuple[int, int], p2: tuple[int, int], collision_number=None):
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

    def draw(self):
        x, y = self.pos
        global camerax, cameray
        pygame.draw.circle(self.surface, self.colour, (int(x - camerax), int(y - cameray)), self.rad)
        if self.texture is not None:
            self.surface.blit(self.texture, (x - camerax, y - cameray))


def player_handler(ball, keys_pressed, space_pressed):
    if keys_pressed[pygame.K_a] and ball.body.velocity[0] - VEL_STEP > -VEL_MAX: ball.body.velocity += -VEL_STEP, 0
    if keys_pressed[pygame.K_d] and ball.body.velocity[0] + VEL_STEP < VEL_MAX: ball.body.velocity += VEL_STEP, 0
    if keys_pressed[pygame.K_SPACE] and not space_pressed:
        space_pressed = True
        ball.body.velocity += 0, -VEL_STEP * 10
    elif not keys_pressed[pygame.K_SPACE] and space_pressed:
        space_pressed = False
    return space_pressed


def draw_falling_balls(balls, texture):
    for ball in balls:
        ball.draw()
        if ball.body.position[1] > HEIGHT + 15:
            ball.remove()
            balls.remove(ball)
            balls.append(Ball(WIN, (random.randint(15, WIDTH - 15), random.randint(-2000, -15)), texture=texture))


def display_start_menu(buttons, balls):
    WIN.fill(BLACK)
    texture = random.choice(COIN_INFO)
    draw_falling_balls(balls, texture)

    game_title = TITLE_FONT.render('CRYPTO GAMES', 1, WHITE)
    WIN.blit(game_title, ((WIDTH - game_title.get_width()) // 2, HEIGHT // 4 - game_title.get_height()))

    buttons[0].draw('Start game')

    space.step(1 / FPS)
    pygame.display.update()


def start_menu():
    global camerax, cameray
    camerax = 0
    cameray = 0

    clock = pygame.time.Clock()
    run = True

    space.gravity = 0, 100

    start_button = Button(WIN, pos=(WIDTH // 2 - 300 // 2, HEIGHT // 2 - 150 // 2), width=300, height=150,
                          shape_color=(200, 200, 200),
                          shape_highlight_color=(255, 200, 200))

    buttons = [start_button]

    clear_all_bodies(space)

    balls = []
    for i in range(NUM_BALLS):
        balls.append(
            Ball(WIN, (random.randint(15, WIDTH - 15), random.randint(-3000, -15)), texture=random.choice(COIN_INFO)))

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        if start_button.is_clicked():
            start_button.click(choose_market_option, balls)
            run = False

        display_start_menu(buttons, balls)


def choose_market_display(buttons):
    WIN.fill(BLACK)

    buttons[0].draw('BTC / USD')
    buttons[1].draw('ETH / USD')
    buttons[2].draw('DOGE / USD')

    pygame.display.update()


def choose_market_option(balls):
    for ball in balls:
        ball.remove()

    clock = pygame.time.Clock()
    run = True

    market_choice_BTCUSD = Button(WIN, pos=(WIDTH // 2 - 200 // 2, HEIGHT // 2 - 150 // 2), width=200, height=75,
                                  shape_color=(200, 200, 200),
                                  shape_highlight_color=(255, 200, 200))
    market_choice_ETHUSD = Button(WIN, pos=(WIDTH // 2 - 400 // 2 - 150, HEIGHT // 2 - 150 // 2), width=200, height=75,
                                  shape_color=(200, 200, 200),
                                  shape_highlight_color=(255, 200, 200))
    market_choice_DOGEUSD = Button(WIN, pos=(WIDTH // 2 + 150, HEIGHT // 2 - 150 // 2), width=200, height=75,
                                   shape_color=(200, 200, 200),
                                   shape_highlight_color=(255, 200, 200))

    buttons = [market_choice_BTCUSD, market_choice_ETHUSD, market_choice_DOGEUSD]
    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        buttons[0].click(loading_screen, 'BTCUSDT')
        buttons[1].click(loading_screen, 'ETHUSDT')
        buttons[2].click(loading_screen, 'DOGEUSDT')

        choose_market_display(buttons)


def loading_screen(symbol='BTCUSDT'):
    WIN.fill(BLACK)
    loading_text = TITLE_FONT.render('Getting data...', 1, WHITE)
    WIN.blit(loading_text, (WIDTH // 2 - loading_text.get_width() // 2, HEIGHT // 2 - loading_text.get_height() // 2))
    pygame.display.update()

    # Record market data
    timeframe = '1D'

    # date format d-m-y
    start_date = '01-1-1990'
    end_date = '01-1-9999'

    data = Historical_data(symbol, timeframe, start_date, end_date)
    close_prices = data.formated_data['Close'][:].to_numpy()

    main(close_prices, symbol)


def get_coin_info(symbol):
    try:
        if symbol == 'BTCUSDT':
            return COIN_INFO[0]
        elif symbol == 'ETHUSDT':
            return COIN_INFO[1]
        elif symbol == 'DOGEUSDT':
            return COIN_INFO[2]
    except:
        print('Market does not exist')
        return False


def get_bar_coords(bar_width, close_prices, symbol):
    coin_info = get_coin_info(symbol)
    x_coords = [i * bar_width for i in range(close_prices.__len__())]
    return list(zip(x_coords, close_prices * coin_info['scale']))


def check_coin_collisions(coins, ball):
    for coin in coins:
        coin.check_collision(ball.body.position)


def display(symbol, player, floors, coins, buttons, start_time, pct_complete):
    WIN.fill(BLACK)

    market_name_text = IN_GAME_FONT.render('SYMBOL: {}'.format(symbol), 1, WHITE)
    WIN.blit(market_name_text, (5, IN_GAME_FONT.get_height() + 2))
    pct_complete_text = IN_GAME_FONT.render('{}%'.format(pct_complete), 1, WHITE)
    WIN.blit(pct_complete_text, (5, IN_GAME_FONT.get_height() * 2 + 4))

    time_elapsed_text = IN_GAME_FONT.render('TIME ELAPSED (s): {}'.format(int(time.time() - start_time)), 1, WHITE)
    WIN.blit(time_elapsed_text, (WIDTH - time_elapsed_text.get_width() - 10, IN_GAME_FONT.get_height() + 2))

    player_points_text = IN_GAME_FONT.render('COINS: {}'.format(player.score), 1, WHITE)
    WIN.blit(player_points_text, (5, IN_GAME_FONT.get_height() * 3 + 4))

    for button in buttons:
        button.draw()

    player.draw()

    for floor in floors:
        floor.draw()

    for coin in coins:
        if not coin.collided and coin.rect_shape.colliderect(player.rect_shape) == 1:
            coin.collided = True
            player.score += 1
        elif not coin.collided:
            coin.draw()
    pygame.display.update()


def player_abilities(buttons, player):
    buttons[0].click(player.super_jump)
    buttons[1].click(player.bouncy)
    buttons[2].click(player.low_g)


def main(close_prices, symbol):
    clock = pygame.time.Clock()
    run = True
    space_pressed = False

    space.gravity = 0, 1200

    bar_coords = get_bar_coords(BAR_WIDTH, -close_prices, symbol)

    coin_image = get_coin_info(symbol)
    player = Player(surface=WIN, start_coords=(bar_coords[1][0], bar_coords[1][1] - 50), texture=coin_image)

    start_wall = StartWall((-20, 1e10), (-5, -1e10))

    floors = []
    for idx in range(1, bar_coords.__len__()):
        floors.append(Floor(bar_coords[idx - 1], bar_coords[idx]))

    sum_coins = 0
    coins_loc = []
    rand_int = 0
    while rand_int < close_prices.__len__():
        rand_int = random.randint(COINS_SPACING_MIN + rand_int, COINS_SPACING_MAX + rand_int)
        if rand_int < close_prices.__len__():
            coins_loc.append(rand_int)

    coins = []
    for loc in coins_loc:
        coin = Coin(WIN, pos=(bar_coords[loc][0], bar_coords[loc][1] - 28), rad=10, colour=(255, 215, 0))
        coins.append(coin)

    # button_speed_super_jump = Button(WIN,)
    width = 150
    height = 30
    button_bouncy = Button(surface=WIN, pos=(WIDTH // 2 - width // 2, HEIGHT - height - 30), width=width, height=height,
                           text='Bouncy (5 coins)',
                           font_size=20, shape_highlight_color=(255, 200, 200))

    button_super_jump = Button(surface=WIN, pos=(WIDTH // 2 - width // 2 - width - 50, HEIGHT - height - 30), width=width,
                         height=height,
                         text='Super jump (1 coin)',
                         font_size=20, shape_highlight_color=(255, 200, 200))
    button_low_gravity = Button(surface=WIN, pos=(WIDTH // 2 - width // 2 + width + 50, HEIGHT - height - 30),
                                width=width, height=height,
                                text='Low G (10 coins)',
                                font_size=20, shape_highlight_color=(255, 200, 200))

    buttons = [button_super_jump, button_bouncy, button_low_gravity]
    start_time = time.time()
    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        global camerax, cameray

        camerax = player.body.position[0] - WIDTH // 2
        cameray = player.body.position[1] - HEIGHT // 2
        keys_pressed = pygame.key.get_pressed()
        space_pressed = player_handler(player, keys_pressed, space_pressed)

        pct_complete = round((player.body.position[0] / (BAR_WIDTH * close_prices.__len__())) * 100, 2)
        player_abilities(buttons, player)
        display(symbol, player, floors, coins, buttons, start_time, pct_complete)

        if pct_complete >= 100:
            player.remove()
            start_wall.remove()
            for floor in floors:
                floor.remove()
            end_game_window(start_time, symbol)
            run = False

        space.step(1 / FPS)
        clock.tick(FPS)


def end_game_display(total_time, button, symbol, balls):
    WIN.fill(BLACK)

    coin_image = get_coin_info(symbol)
    draw_falling_balls(balls, coin_image)

    time_display_text = IN_GAME_FONT.render('TIME: {} SECONDS'.format(total_time), 1, WHITE)
    WIN.blit(time_display_text, (WIDTH // 1.7, (HEIGHT // 4)))
    symbol_name_display = IN_GAME_FONT.render('SYMBOL: {}'.format(symbol), 1, WHITE)
    WIN.blit(symbol_name_display, (WIDTH // 4.5, (HEIGHT // 4)))

    button.draw('Restart game')

    space.step(1 / FPS)
    pygame.display.update()


def end_game_window(start_time, symbol):
    total_time = round(time.time() - start_time, 2)
    clock = pygame.time.Clock()

    restart_button = Button(WIN, (WIDTH // 2 - 300 // 2, HEIGHT // 2, 300, 150), width=300, height=150,
                            shape_color=(200, 200, 200),
                            shape_highlight_color=(255, 200, 200))

    global camerax, cameray
    camerax = 0
    cameray = 0

    space.gravity = 0, 2

    balls_end_display = []
    for i in range(NUM_BALLS):
        balls_end_display.append(
            Ball(WIN, (random.randint(15, WIDTH - 15), random.randint(-2000, -15)),
                 texture=get_coin_info(symbol)))

    run = True
    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        end_game_display(total_time, restart_button, symbol, balls_end_display)
        if restart_button.is_clicked():
            for ball in balls_end_display:
                ball.remove()

            restart_button.click(start_menu)

            run = False


if __name__ == '__main__':
    pygame.init()
    start_menu()
