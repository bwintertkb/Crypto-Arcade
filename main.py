import pygame
import pymunk
from market_data import Get_data
import numpy as np
import time
import random
import os
from crypto_arcade import *

pygame.font.init()

WIDTH, HEIGHT = 1080, 700  # 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_BLUE = (68, 85, 128)
LIGHT_LIGHT_BLUE = (85, 105, 158)
pygame.display.set_caption('Crypto Arcade')

BAR_WIDTH = 60
BAR_WIDTH_FIND_DIP = 15

global VEL_STEP, VEL_MAX
VEL_STEP = 15
VEL_MAX = 300
BASE_ROTATION_SPEED = VEL_MAX

FPS = 144

IN_GAME_FONT = pygame.font.SysFont('comicsans', 30)
TITLE_FONT = pygame.font.SysFont('comicsans', 75)
MARKET_CHOICE_FONT = pygame.font.SysFont('comicsans', 55)

space = pymunk.Space()
space.gravity = 0, 460

coll_type = 5


def player_platform(arbiter, space, data):
    print("you reached the goal!")
    return True


# h = space.add_collision_handler(5,5)
# h.pre_solve = goal_reached

NUM_BALLS = 150

COINS_SPACING_MIN = 4
COINS_SPACING_MAX = 18

camera = [0, 0]

BITCOIN_IMAGE = pygame.image.load(os.path.join('assets', 'bitcoin.png')).convert_alpha()
BITCOIN_IMAGE = pygame.transform.scale(BITCOIN_IMAGE, (37, 37))

ETH_IMAGE = pygame.image.load(os.path.join('assets', 'eth.png')).convert_alpha()
ETH_IMAGE = pygame.transform.scale(ETH_IMAGE, (30, 30))

DOGECOIN_IMAGE = pygame.image.load(os.path.join('assets', 'dogecoin.png')).convert_alpha()
DOGECOIN_IMAGE = pygame.transform.scale(DOGECOIN_IMAGE, (int(31), 31))

COIN_INFO = [
    {'image': BITCOIN_IMAGE, 'x offset': 19, 'y offset': 19, 'scale crypto rider': 1, 'scale find the dip': 0.3},
    {'image': ETH_IMAGE, 'x offset': 15, 'y offset': 16, 'scale crypto rider': 0.7e1, 'scale find the dip': 0.3},
    {'image': DOGECOIN_IMAGE, 'x offset': 16, 'y offset': 16, 'scale crypto rider': 0.85e6, 'scale find the dip': 5e4}
]


def clear_all_bodies(space):
    if len(space.bodies) > 0:
        for body in space.bodies:
            space.remove(body)
        return True
    return False


def player_handler(ball, keys_pressed, space_pressed):
    if keys_pressed[pygame.K_a] and ball.body.velocity[0] - VEL_STEP > -VEL_MAX: ball.body.velocity += -VEL_STEP, 0
    if keys_pressed[pygame.K_d] and ball.body.velocity[0] + VEL_STEP < VEL_MAX: ball.body.velocity += VEL_STEP, 0
    if keys_pressed[pygame.K_s]: ball.body.velocity = 0, ball.body.velocity[1]
    if keys_pressed[pygame.K_SPACE] and not space_pressed:
        space_pressed = True
        ball.body.velocity += 0, -VEL_STEP * 10
    elif not keys_pressed[pygame.K_SPACE] and space_pressed:
        space_pressed = False
    return space_pressed

def player_handler_crypto_swinging(player, keys_pressed, space_pressed, start_time) -> bool:
    if keys_pressed[pygame.K_a] and player.body.velocity[0] - VEL_STEP > -VEL_MAX: player.body.velocity += -VEL_STEP, 0
    if keys_pressed[pygame.K_d] and player.body.velocity[0] + VEL_STEP < VEL_MAX: player.body.velocity += VEL_STEP, 0
    if keys_pressed[pygame.K_s]: player.body.velocity = 0, player.body.velocity[1]

    try:
        if player.arbiter_info is not None and player.arbiter_info.shapes[0].collision_type == 5:
            space_pressed = False
        if keys_pressed[pygame.K_SPACE] and not space_pressed and time.time()-start_time[0]>0.2:
            player.body.velocity += 0, -VEL_STEP*10
            space_pressed = True
            start_time[0] = time.time()
            print('Pressed')
    except:
        print('Shape issue')

    return space_pressed


def draw_falling_balls(space, balls, texture):
    for ball in balls:
        ball.draw(camera)

        if ball.body.position[1] > HEIGHT + 15:
            ball.remove(space)
            balls.remove(ball)
            balls.append(
                Ball(space, WIN, (random.randint(15, WIDTH - 15), random.randint(-2000, -15)), texture=texture))


def display_start_menu(buttons, balls):
    WIN.fill(BLACK)
    texture = random.choice(COIN_INFO)
    draw_falling_balls(space, balls, texture)

    game_title = TITLE_FONT.render('CRYPTO ARCADE', 1, WHITE)
    WIN.blit(game_title, ((WIDTH - game_title.get_width()) // 2, HEIGHT // 4 - game_title.get_height()))

    buttons[0].draw()

    space.step(1 / FPS)
    pygame.display.update()


def start_menu():
    camera[0] = 0
    camera[1] = 0

    clock = pygame.time.Clock()
    run = True

    space.gravity = 0, 100

    start_button = Button(WIN, pos=(WIDTH // 2 - 300 // 2, HEIGHT // 2 - 150 // 2), width=300, height=150,
                          shape_color=(200, 200, 200),
                          shape_highlight_color=(255, 200, 200), text='Choose game')

    buttons = [start_button]

    clear_all_bodies(space)

    balls = []
    for i in range(NUM_BALLS):
        balls.append(
            Ball(space, WIN, (random.randint(15, WIDTH - 15), random.randint(-3000, -15)),
                 texture=random.choice(COIN_INFO)))

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        if start_button.is_clicked():
            for ball in balls:
                ball.remove(space)
            del balls
            start_button.click(game_choice_menu)
            # start_button.click(choose_market_option)
            run = False

        display_start_menu(buttons, balls)


def game_choice_display(buttons):
    WIN.fill(BLACK)

    for button in buttons:
        button.draw()

    pygame.display.update()


def game_choice_menu():
    clock = pygame.time.Clock()
    run = True

    width = 250
    height = 150
    button_crypto_rider = Button(surface=WIN, pos=(WIDTH // 2 - width * 1.5 - 50, HEIGHT // 2 - height // 2),
                                 width=width,
                                 height=height,
                                 shape_highlight_color=(255, 200, 200), text='CRYPTO RIDER', font_size=35)

    button_find_the_dip = Button(surface=WIN, pos=(WIDTH // 2 - width // 2, HEIGHT // 2 - height // 2), width=width,
                                 height=height,
                                 shape_highlight_color=(255, 200, 200), text='FIND THE DIP', font_size=35)

    button_crypto_swinging = Button(surface=WIN, pos=(WIDTH // 2 + width // 2 + 50, HEIGHT // 2 - height // 2),
                                    width=width,
                                    height=height,
                                    shape_highlight_color=(255, 200, 200), text='CRYPTO SWINGING', font_size=35)

    buttons = [button_crypto_rider, button_find_the_dip, button_crypto_swinging]
    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        button_crypto_rider.click(choose_market_option, button_crypto_rider.text)
        button_find_the_dip.click(choose_market_option, button_find_the_dip.text)
        button_crypto_swinging.click(choose_market_option, button_crypto_swinging.text)
        game_choice_display(buttons)


def choose_market_display(buttons):
    WIN.fill(BLACK)

    buttons[0].draw()
    buttons[1].draw()
    buttons[2].draw()

    pygame.display.update()


def choose_market_option(game_name='CRYPTO RIDER'):
    clock = pygame.time.Clock()
    run = True

    if game_name == 'CRYPTO RIDER' or game_name == 'FIND THE DIP':
        text = ['BTC / USD', 'ETH / USD', 'DOGE / USD']
    elif game_name == 'CRYPTO SWINGING':
        text = ['BTC', 'ETH', 'DOGE']

    market_choice_BTCUSD = Button(WIN, pos=(WIDTH // 2 - 200 // 2, HEIGHT // 2 - 150 // 2), width=200, height=75,
                                  shape_color=(200, 200, 200),
                                  shape_highlight_color=(255, 200, 200), text=text[0])
    market_choice_ETHUSD = Button(WIN, pos=(WIDTH // 2 - 400 // 2 - 150, HEIGHT // 2 - 150 // 2), width=200, height=75,
                                  shape_color=(200, 200, 200),
                                  shape_highlight_color=(255, 200, 200), text=text[1])
    market_choice_DOGEUSD = Button(WIN, pos=(WIDTH // 2 + 150, HEIGHT // 2 - 150 // 2), width=200, height=75,
                                   shape_color=(200, 200, 200),
                                   shape_highlight_color=(255, 200, 200), text=text[2])

    buttons = [market_choice_BTCUSD, market_choice_ETHUSD, market_choice_DOGEUSD]
    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        if game_name == 'CRYPTO RIDER' or game_name == 'FIND THE DIP':
            buttons[0].click(loading_screen, symbol='BTCUSDT', game_name=game_name)
            buttons[1].click(loading_screen, symbol='ETHUSDT', game_name=game_name)
            buttons[2].click(loading_screen, symbol='DOGEUSDT', game_name=game_name)
        elif game_name == 'CRYPTO SWINGING':
            buttons[0].click(main_crypto_swinging, symbol='BTCUSDT')
            buttons[1].click(main_crypto_swinging, symbol='ETHUSDT')
            buttons[2].click(main_crypto_swinging, symbol='DOGEUSDT')

        choose_market_display(buttons)


def loading_screen(symbol='BTCUSDT', game_name='CRYPTO RIDER'):
    WIN.fill(BLACK)
    loading_text = TITLE_FONT.render('Getting data...', 1, WHITE)
    WIN.blit(loading_text, (WIDTH // 2 - loading_text.get_width() // 2, HEIGHT // 2 - loading_text.get_height() // 2))
    pygame.display.update()

    # Record market data
    timeframe = '1D'

    # date format d-m-y
    start_date = '01-1-1990'
    end_date = '01-1-9999'

    data = Get_data(symbol, timeframe, start_date, end_date)
    close_prices = np.array(data.close_prices)

    if game_name == 'CRYPTO RIDER':
        main(close_prices, symbol, game_name)
    elif game_name == 'FIND THE DIP':
        main_find_the_dip(close_prices, symbol, game_name)


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


def get_bar_coords(bar_width, close_prices, symbol, game_name):
    coin_info = get_coin_info(symbol)
    x_coords = [i * bar_width for i in range(close_prices.__len__())]

    if game_name == 'CRYPTO RIDER':
        scale = coin_info['scale crypto rider']
    elif game_name == 'FIND THE DIP':
        scale = coin_info['scale find the dip']

    return list(zip(x_coords, close_prices * scale))


def check_coin_collisions(coins, ball):
    for coin in coins:
        coin.check_collision(ball.body.position)


def display(symbol, player, floors, coins, buttons, start_time, pct_complete):
    WIN.fill(BLACK)

    player.draw(camera)

    for floor in floors:
        floor.draw(camera)

    for coin in coins:
        if not coin.collided and coin.rect_shape.colliderect(player.rect_shape) == 1:
            coin.collided = True
            player.score += 1
        elif not coin.collided:
            coin.draw(camera)

    for button in buttons:
        button.draw()

    market_name_text = IN_GAME_FONT.render('SYMBOL: {}'.format(symbol), 1, WHITE)
    WIN.blit(market_name_text, (5, IN_GAME_FONT.get_height() + 2))

    pct_complete_text = IN_GAME_FONT.render('{}%'.format(pct_complete), 1, WHITE)
    WIN.blit(pct_complete_text, (5, IN_GAME_FONT.get_height() * 2 + 4))

    time_elapsed_text = IN_GAME_FONT.render('TIME ELAPSED (s): {}'.format(int(time.time() - start_time)), 1, WHITE)
    WIN.blit(time_elapsed_text, (WIDTH - time_elapsed_text.get_width() - 10, IN_GAME_FONT.get_height() + 2))

    player_points_text = IN_GAME_FONT.render('COINS: {}'.format(player.score), 1, WHITE)
    WIN.blit(player_points_text, (5, IN_GAME_FONT.get_height() * 3 + 4))

    pygame.display.update()


def player_abilities(buttons, player):
    buttons[0].click(player.super_jump)
    buttons[1].click(player.bouncy)
    buttons[2].click(player.mega_jump)


def main(close_prices, symbol, game_name):
    clear_all_bodies(space)
    clock = pygame.time.Clock()
    run = True
    space_pressed = False

    space.gravity = 0, 1200

    bar_coords = get_bar_coords(BAR_WIDTH, -close_prices, symbol, game_name)

    coin_image = get_coin_info(symbol)
    player = Player(space=space, surface=WIN, start_coords=(bar_coords[1][0], bar_coords[1][1] - 50),
                    texture=coin_image)

    start_wall = StartWall(space, (bar_coords[0][0] - 20, 1e10), (bar_coords[0][0] - 5, -1e10))

    floors = []
    for idx in range(1, bar_coords.__len__()):
        floors.append(Floor(space, WIN, bar_coords[idx - 1], bar_coords[idx]))

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
    width = 165
    height = 30
    button_bouncy = Button(surface=WIN, pos=(WIDTH // 2 - width // 2, HEIGHT - height - 30), width=width, height=height,
                           text='Bouncy (5 coins)',
                           font_size=20, shape_highlight_color=(255, 200, 200))

    button_super_jump = Button(surface=WIN, pos=(WIDTH // 2 - width // 2 - width - 50, HEIGHT - height - 30),
                               width=width,
                               height=height,
                               text='Super jump (1 coin)',
                               font_size=20, shape_highlight_color=(255, 200, 200))
    button_mega_jump = Button(surface=WIN, pos=(WIDTH // 2 - width // 2 + width + 50, HEIGHT - height - 30),
                              width=width, height=height,
                              text='Mega jump (10 coins)',
                              font_size=20, shape_highlight_color=(255, 200, 200))

    buttons = [button_super_jump, button_bouncy, button_mega_jump]
    start_time = time.time()
    while run:

        camera[0] = player.body.position[0] - WIDTH // 2
        camera[1] = player.body.position[1] - HEIGHT // 2
        keys_pressed = pygame.key.get_pressed()
        space_pressed = player_handler(player, keys_pressed, space_pressed)

        pct_complete = round((player.body.position[0] / (BAR_WIDTH * close_prices.__len__())) * 100, 2)
        player_abilities(buttons, player)
        display(symbol, player, floors, coins, buttons, start_time, pct_complete)

        if pct_complete >= 100:
            player.remove(space)
            start_wall.remove(space)
            for floor in floors:
                floor.remove(space)
            end_game_window(start_time, symbol)
            run = False

        space.step(1 / FPS)
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()


def main_find_the_dip(close_prices, symbol, game_name):
    clear_all_bodies(space)
    clock = pygame.time.Clock()
    run = True
    FPS = 144

    space.gravity = 0, 1200

    bar_coords = get_bar_coords(BAR_WIDTH_FIND_DIP, -close_prices, symbol, game_name)

    coin_image = get_coin_info(symbol)
    offsetx = 20
    player = Player(space=space, surface=WIN, start_coords=(bar_coords[0][0] - offsetx, bar_coords[0][1] - 50),
                    texture=coin_image)
    player.shape.elasticity = 0.1
    player_base = Floor(space=space, surface=WIN, p1=(bar_coords[0][0] - offsetx - 15, bar_coords[0][1] - 50 + 15),
                        p2=(bar_coords[0][0] - offsetx + 15, bar_coords[0][1] - 50 + 15))
    floors = [player_base]

    for idx in range(1, bar_coords.__len__()):
        floors.append(Floor(space, WIN, bar_coords[idx - 1], bar_coords[idx]))

    left_mouse_down = False
    launched = False

    exit_game_delay = 3  # in seconds
    start_time = time.time()
    points_time = 0
    stop_game = False
    first_run = False

    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        camera[0] = player.body.position[0] - WIDTH // 2
        camera[1] = player.body.position[1] - HEIGHT // 2

        left_mouse_hold, _, _ = pygame.mouse.get_pressed()

        points = int(abs(bar_coords[0][1] - 50) - abs(player.body.position[1]))
        display_find_the_dip(player, floors, points)
        if left_mouse_hold and not launched:
            playerx, playery = player.body.position
            centerx, centery = WIDTH // 2, HEIGHT // 2
            mousex, mousey = pygame.mouse.get_pos()
            delx = centerx - mousex
            dely = centery - mousey
            left_mouse_down = True
            pygame.draw.line(WIN, WHITE, (playerx - camera[0], playery - camera[1]),
                             (playerx - camera[0] - delx, playery - camera[1] - dely), width=5)
            pygame.display.update()

        if not left_mouse_hold and left_mouse_down and not launched:
            player.launch(WIDTH, HEIGHT, delx, dely)
            launched = True

        space.step(1 / FPS)
        clock.tick(FPS)

        if launched and not first_run:
            start_time = time.time()
            first_run = True

        if launched and time.time() - start_time > exit_game_delay and first_run:
            if points == points_time:
                stop_game = True
            else:
                points_time = points
                start_time = time.time()

        if launched and stop_game:
            run = False
            end_game_window_find_the_dip(symbol, points)

    # def get_ball_line(player):


def create_crypto_swinging_course() -> list['box objects']:
    num_boxes = 20
    boxes = []
    coords = 70, -180
    rand_x = 0
    rand_y = 0

    width = 20
    height = 20
    for i in range(num_boxes):
        box = Box(WIN, (coords[0], coords[1]), width, height)
        string_length = random.randint(70, 180)
        box.add_string(length=string_length, num_elements=20)
        platform_length = random.randint(35, 80)
        box.add_platform(length=platform_length, colour=(255, 255, 255))
        box.add2space(space)
        boxes.append(box)
        coords = coords[0] + random.randint(200, 250), coords[1] + random.randint(-50, 50)

    return boxes


def get_course_coordinates() -> list['dictionary']:
    num_swings = 15000

    coords = 70, -180

    swing_info = []
    for i in range(num_swings):
        string_length = random.randint(70, 180)
        platform_length = random.randint(35, 80)
        swing = {
            'coords': coords,
            'string length': string_length,
            'platform length': platform_length,
            'created': False
        }
        swing_info.append(swing)
        coords = coords[0] + random.randint(200, 260), coords[1] + random.randint(-70, 70)

    return swing_info


def create_boxes(space, player, screen_width, swing_info, boxes) -> None:
    width = 20
    height = 20

    min_view = player.body.position.x - screen_width / 2 - width
    max_view = player.body.position.x + screen_width / 2 + width

    for idx, swing in enumerate(swing_info):
        if min_view <= swing['coords'][0] <= max_view and not swing['created']:
            box = Box(WIN, position=swing['coords'], width=width, height=height, index=idx)
            box.add_string(length=swing['string length'], num_elements=20)
            box.add_platform(length=swing['platform length'])
            box.add2space(space)
            swing['created'] = True
            boxes[idx] = box

        if swing['created']:
            if min_view > swing['coords'][0] or max_view < swing['coords'][0]:
                boxes[idx].remove(space)
                boxes[idx] = None
                swing['created'] = False


def main_crypto_swinging(symbol):
    global VEL_STEP, VEL_MAX
    VEL_STEP = 15
    VEL_MAX = 300

    clear_all_bodies(space)
    clock = pygame.time.Clock()

    player = Player(space=space, surface=WIN, start_coords=(0, 0), start_velocity=(0, 0), rad=15,
                    texture=get_coin_info(symbol))
    player.shape.elasticity = 0
    player.shape = pymunk.Poly.create_box(player.body, (15, 15))
    player.add_collision_handler(space)

    floor = Floor(space=space, surface=WIN,
                  p1=(player.body.position.x - player.rad, player.body.position.y + player.rad),
                  p2=(player.body.position.x + player.rad, player.body.position.y + player.rad), collision_number=5)

    swing_info = get_course_coordinates()
    boxes = [None] * swing_info.__len__()

    run = True
    space_pressed = True

    space.gravity = 0, 350
    start_time = [time.time()]

    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        create_boxes(space, player, WIDTH, swing_info, boxes)

        camera[0] = player.body.position[0] - WIDTH // 2
        camera[1] = player.body.position[1] - HEIGHT // 2

        keys_pressed = pygame.key.get_pressed()
        space_pressed = player_handler_crypto_swinging(player, keys_pressed, space_pressed,start_time)

        points = display_crypto_swinging(player, floor, boxes)
        space.step(1 / FPS)
        clock.tick(FPS)

        if player.body.position.y >= 2000:
            end_game_window_find_the_dip(symbol, points)
            clear_all_bodies(space)
            run = False


def display_crypto_swinging(player, floor, boxes) -> int:
    WIN.fill(BLACK)

    floor.draw(camera)
    for box in boxes:
        if box is not None: box.draw(camera)

    player.draw(camera)

    points = int(player.body.position.x // 100)

    points_display_text = IN_GAME_FONT.render('POINTS: {}'.format(points), 1, WHITE)
    WIN.blit(points_display_text, (5, (5 + points_display_text.get_height())))

    pygame.display.update()

    return points


def display_find_the_dip(player, floors, points):
    WIN.fill(BLACK)

    player.draw(camera)

    for floor in floors:
        floor.draw(camera)

    points_display_text = IN_GAME_FONT.render('POINTS: {}'.format(points), 1, WHITE)
    WIN.blit(points_display_text, (5, (5 + points_display_text.get_height())))

    pygame.display.update()


def end_game_window_find_the_dip(symbol, points):
    clear_all_bodies(space)
    clock = pygame.time.Clock()

    restart_button = Button(WIN, (WIDTH // 2 - 300 // 2, HEIGHT // 2, 300, 150), width=300, height=150,
                            shape_color=(200, 200, 200),
                            shape_highlight_color=(255, 200, 200), text='Restart game')
    camera[0] = 0
    camera[1] = 0

    space.gravity = 0, 20

    try:
        del balls
    except Exception:
        print('Balls does not exist')
    balls = []
    for i in range(NUM_BALLS):
        balls.append(
            Ball(space, WIN, (random.randint(15, WIDTH - 15), random.randint(-2000, -15)),
                 texture=get_coin_info(symbol)))

    run = True
    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        end_game_display_find_the_dip(restart_button, symbol, points, balls)
        if restart_button.is_clicked():
            for ball in balls:
                ball.remove(space)

            del balls
            restart_button.click(start_menu)

            run = False

        space.step(1 / FPS)
        clock.tick(FPS)


def end_game_display_find_the_dip(button, symbol, points, balls):
    WIN.fill(BLACK)

    coin_image = get_coin_info(symbol)
    draw_falling_balls(space, balls, coin_image)

    time_display_text = IN_GAME_FONT.render('POINTS: {}'.format(points), 1, WHITE)
    WIN.blit(time_display_text, (WIDTH // 1.7, (HEIGHT // 4)))
    symbol_name_display = IN_GAME_FONT.render('SYMBOL: {}'.format(symbol), 1, WHITE)
    WIN.blit(symbol_name_display, (WIDTH // 4.5, (HEIGHT // 4)))

    button.draw()

    space.step(1 / FPS)
    pygame.display.update()


def end_game_display(total_time, button, symbol, balls):
    WIN.fill(BLACK)

    coin_image = get_coin_info(symbol)
    draw_falling_balls(space, balls, coin_image)

    time_display_text = IN_GAME_FONT.render('TIME: {} SECONDS'.format(total_time), 1, WHITE)
    WIN.blit(time_display_text, (WIDTH // 1.7, (HEIGHT // 4)))
    symbol_name_display = IN_GAME_FONT.render('SYMBOL: {}'.format(symbol), 1, WHITE)
    WIN.blit(symbol_name_display, (WIDTH // 4.5, (HEIGHT // 4)))

    button.text = 'Restart game'
    button.draw()

    space.step(1 / FPS)
    pygame.display.update()


def end_game_window(start_time, symbol):
    clear_all_bodies(space)
    total_time = round(time.time() - start_time, 2)
    clock = pygame.time.Clock()

    restart_button = Button(WIN, (WIDTH // 2 - 300 // 2, HEIGHT // 2, 300, 150), width=300, height=150,
                            shape_color=(200, 200, 200),
                            shape_highlight_color=(255, 200, 200))
    camera[0] = 0
    camera[1] = 0

    space.gravity = 0, 2

    try:
        del balls
    except Exception:
        print('Balls does not exist')
    balls = []
    for i in range(NUM_BALLS):
        balls.append(
            Ball(space, WIN, (random.randint(15, WIDTH - 15), random.randint(-2000, -15)),
                 texture=get_coin_info(symbol)))

    run = True
    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        end_game_display(total_time, restart_button, symbol, balls)
        if restart_button.is_clicked():
            for ball in balls:
                ball.remove(space)
            del balls
            restart_button.click(start_menu)

            run = False


if __name__ == '__main__':
    pygame.init()
    start_menu()
