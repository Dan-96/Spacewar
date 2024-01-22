import pygame
import math
import random
import configparser


class Player:
    def __init__(self, x, y, angle, player):
        self.x = x
        self.y = y
        self.angle = angle
        self.img = pygame.image.load(f'Graphics/{player}.png').convert_alpha()
        self.img_thrust = pygame.image.load(f'Graphics/{player}_Thrust.png').convert_alpha()
        self.sound_boost_loop = pygame.mixer.Sound('Sounds/Boost_loop.wav')
        self.sound_boost_loop.set_volume(0.3)
        self.sound_boost_end = pygame.mixer.Sound('Sounds/Boost_end.wav')
        self.sound_boost_end.set_volume(0.5)
        self.sound_explode = pygame.mixer.Sound('Sounds/Explosion.wav')
        self.sound_explode.set_volume(0.5)
        self.w = self.img.get_width()
        self.h = self.img.get_height()
        self.health = 1
        self.angle_velocity = 0
        self.angle_acceleration = 0.08
        self.rotated_surf = pygame.transform.rotate(self.img, angle)
        self.rotated_rect = self.rotated_surf.get_rect(center=(self.x, self.y))
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity_point = pygame.math.Vector2(width // 2, height // 2)
        self.gravitational_force = 0.02
        self.current_sprite = 0
        self.bullet_count = 1

    def explode(self):
        self.angle = 0
        self.sprites = []
        for i in range(1, 10):
            self.exp_image = pygame.image.load(f'Graphics/Explosion/frame_{i}.png')
            self.sprites.append(self.exp_image)
        self.current_sprite += 0.2
        if self.current_sprite < 9:
            self.img = self.sprites[int(self.current_sprite)]

    def draw(self):
        screen.blit(self.rotated_surf, self.rotated_rect)

    def turn_left(self):
        self.angle_velocity += self.angle_acceleration

    def turn_right(self):
        self.angle_velocity -= self.angle_acceleration

    def update_rotation(self):
        self.angle += self.angle_velocity
        self.angle %= 360
        self.rotated_surf = pygame.transform.rotate(self.img, self.angle)
        self.rotated_rect = self.rotated_surf.get_rect(center=(self.x, self.y))
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.angle_velocity *= 0.96

    def check_ship_collision(self, object):
        distance = math.sqrt((self.x - object.x) ** 2 + (self.y - object.y) ** 2)
        if distance < object.w:
            self.health -= 1
            pygame.time.set_timer(restart_event, 3000, 1)
            pygame.mixer.Channel(3).play(player1.sound_explode)

    def apply_thrust(self):
        self.thrust_force = 0.02 # Default: 0.02
        self.velocity_x += self.cosine * self.thrust_force
        self.velocity_y -= self.sine * self.thrust_force

    def apply_vector(self):
        self.gravity_direction = self.gravity_point - pygame.math.Vector2(self.x, self.y)
        self.gravity_direction.normalize_ip()
        self.velocity_x += self.gravity_direction.x * self.gravitational_force * 0.2
        self.velocity_y += self.gravity_direction.y * self.gravitational_force * 0.2

    def update_location(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        if self.x >= width or self.x <= 0 or self.y <= 0 or self.y >= height:
            self.health -= 1000
            pygame.time.set_timer(restart_event, 3000, 1)
            pygame.mixer.Channel(3).play(player1.sound_explode)

    def update(self):
        self.update_rotation()
        if self.health > 0:
            self.apply_vector()
            self.update_location()



class Bullet(Player):
    def __init__(self, x, y, angle, velocity, player=False):
        self.x = x
        self.y = y
        self.radius = 1
        self.color = (255, 255, 255)
        if player is not False:
            self.offset_x = math.cos(math.radians(angle + 90)) * (player.h / 1.5)
            self.offset_y = -math.sin(math.radians(angle + 90)) * (player.h / 1.5)
            self.x = x + self.offset_x
            self.y = y + self.offset_y
        self.bullet_list = []
        self.sound = pygame.mixer.Sound('Sounds/Shooting.mp3')
        self.sound.set_volume(0.2)
        if velocity:
            self.velocity_x = (math.cos(math.radians(angle + 90)) * 3) + player.velocity_x
            self.velocity_y = (-math.sin(math.radians(angle + 90)) * 3) + player.velocity_y
        else:
            self.velocity_x = 0
            self.velocity_y = 0
        self.gravity_point = pygame.math.Vector2(width // 2, height // 2)
        self.gravitational_force = 0 # How much bullets are attracted towards centre of the screen

    def update_bullet(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.apply_bullet_vector()

    def modify_bullet_list(self, player):
        for i in self.bullet_list:
            i.draw_bullet(screen)
            i.update_bullet()
            if i.x < 0 or i.x > width or i.y < 0 or i.y > height:
                self.bullet_list.remove(i)
            if player.health >= 1:
                if i.check_ship_collision(player.rotated_rect):
                    self.bullet_list.remove(i)
                    player.health -= 1
                    if player.health <= 0:
                        pygame.time.set_timer(restart_event, 3000, 1)
                        pygame.mixer.Channel(3).play(player1.sound_explode)
                        player.explode()

    def apply_bullet_vector(self):
        # If enabled calculates bullet gravity towards the centre
        self.gravity_direction = self.gravity_point - pygame.math.Vector2(self.x, self.y)
        try:
            self.gravity_direction.normalize_ip()
        except ValueError:
            pass
        self.velocity_x += self.gravity_direction.x * self.gravitational_force
        self.velocity_y += self.gravity_direction.y * self.gravitational_force

    def draw_bullet(self, window):
        pygame.draw.circle(window, self.color, (int(self.x), int(self.y)), self.radius)

    def check_ship_collision(self, object):
        distance = math.sqrt((self.x - object.centerx) ** 2 + (self.y - object.centery) ** 2)
        return distance < object.width / 2

    def check_bullet_collision(self, other_bullet, hitbox_size):
        distance = math.sqrt((self.x - other_bullet.x) ** 2 + (self.y - other_bullet.y) ** 2)
        return distance < (self.radius * hitbox_size) + (other_bullet.radius * hitbox_size)



def debug_text(name, x, y, size, variable=False):
    font = pygame.font.Font('Fonts/clacon2.ttf', size)
    if variable:
        text = font.render(f"{name} {variable: .0f}", False, (255, 255, 255))
        screen.blit(text, (y, x))
    else:
        text = font.render(f'{name}', False, (255, 255, 255))
        screen.blit(text, (y, x))


def mouse_bullet_spawn():
    if debug:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] == 1:
            bullet_mouse.bullet_list.append(Bullet(mouse_x, (mouse_y + 17), 0, False, player1))


def bullets_collide():
    # Checks for bullet to bullet collisions
    for i in player1_bullet.bullet_list:
        for j in player2_bullet.bullet_list:
            if i != j:
                if i.check_bullet_collision(j, 6):
                    player1_bullet.bullet_list.remove(i)
                    player2_bullet.bullet_list.remove(j)


def restart_game():
    # Player 1 reset settings
    player1.angle = 90
    player1.x = (width // 1.5)
    player1.y = (height // 2.001)
    player1.health = 1
    # Shared settings to reset
    player1.velocity_x, player2.velocity_x = 0, 0
    player1.velocity_y, player2.velocity_y = 0, 0
    player1.current_sprite, player2.current_sprite = 0, 0
    player1.bullet_count, player2.bullet_count = 1, 1
    player1.angle_velocity, player2.angle_velocity = 0, 0
    # Player 2 reset settings
    player2.angle = 270
    player2.x = (width // 3)
    player2.y = (height // 2.001)
    player2.health = 1
    # Clear all bullets
    player1_bullet.bullet_list.clear()
    player2_bullet.bullet_list.clear()
    bullet_mouse.bullet_list.clear()
    powerups['ammo']['collected'] = True
    powerups['shield']['collected'] = True
    pygame.time.set_timer(ammo_event, 3000, 1)
    pygame.time.set_timer(shield_event, 15000, 1)


def black_hole(player):
    pygame.draw.circle(screen, 'white', (width // 2, height // 2), 62)
    black_hole = pygame.draw.circle(screen, 'black', (width // 2, height // 2), 60)
    black_hole_pos = black_hole.center
    black_hole_radius = black_hole.width // 2
    if player.health >= 1:
        distance = math.sqrt((player.x - black_hole_pos[0]) ** 2 + (player.y - black_hole_pos[1]) ** 2)
        if distance < player.h / 2 + black_hole_radius:
            player.health -= 1
            pygame.time.set_timer(restart_event, 3000, 1)
            pygame.mixer.Channel(3).play(player1.sound_explode)
            player.explode()


def display_text(text, x, y, colour='gray33', size=30):
    font = pygame.font.Font('Fonts/clacon2.ttf', size)
    menu_text = font.render(f'{text}', False, colour)
    menu_text_rect = menu_text.get_rect()
    menu_text_rect.center = (x, y)
    screen.blit(menu_text, menu_text_rect)


def check_powerup(player):
    for powerup_name, powerup_data in powerups.items():
        if not powerup_data["collected"]:
            if powerup_name == 'ammo':
                pygame.draw.circle(screen, powerup_data["color"], (ammo_x, ammo_y), 8)
                distance = math.sqrt((player.x - ammo_x) ** 2 + (player.y - ammo_y) ** 2)
                if distance < player.h - 5:
                    player.bullet_count += 1
                    powerup_data["collected"] = True
                    pygame.time.set_timer(ammo_event, 3000, 1)
            if powerup_name == 'shield':
                pygame.draw.circle(screen, powerup_data["color"], (shield_x, shield_y), 8)
                distance = math.sqrt((player.x - shield_x) ** 2 + (player.y - shield_y) ** 2)
                if distance < player.h - 5:
                    player.health += 1
                    powerup_data["collected"] = True
                    pygame.time.set_timer(shield_event, 15000, 1)
                    pygame.time.set_timer(shield_end_event, 10000, 1)


def resolution_changer():
    config = configparser.ConfigParser()
    config_path = 'Config/Config.ini'
    config.read(config_path)
    def set_res(width, height):
        config['Resolution']['width'] = str(width)
        config['Resolution']['height'] = str(height)
    def save_config():
        with open(config_path, 'w') as config_file:
            config.write(config_file)
    screen_width = int(config.get('Resolution', 'width'))
    screen_height = int(config.get('Resolution', 'height'))
    return screen_width, screen_height, set_res, save_config


def menu_screen():
    screen.fill('black')
    logo = pygame.image.load('Graphics/logo.png').convert_alpha()
    resized_logo = pygame.transform.scale(logo, ((width // 2.56), (height // 8.62)))
    screen.blit(resized_logo, ((width // 3.28), (height // 10)))
    display_text('alpha-v0.1.3', (width // 1.36), (height // 4.76), 'grey', (width // 95))
    display_text('START', w_half, h_half - 50)
    display_text('OPTIONS', w_half, h_half)
    display_text('EXIT', w_half, h_half + 50)
    if menu_selection == 0:
        display_text('> START <', w_half, h_half - 52, 'white')
    elif menu_selection == 1:
        display_text('> OPTIONS <', w_half, h_half - 2, 'white')
    elif menu_selection == 2:
        display_text('> EXIT <', w_half, h_half + 48, 'white')


def options_screen():
    screen.fill('black')
    display_text('RESOLUTION', w_half, h_half - 50)
    display_text('CONTROLS (SOON)', w_half, h_half)
    display_text('EXIT', w_half, h_half + 50)
    if menu_selection == 0:
        display_text('> RESOLUTION <', w_half, h_half - 52, 'white')
    elif menu_selection == 1:
        display_text('> CONTROLS (SOON) <', w_half, h_half - 2, 'white')
    elif menu_selection == 2:
        display_text('> EXIT <', w_half, h_half + 48, 'white')


def resolution_screen():
    screen.fill('black')
    display_text(f'CURRENT RESOLUTION: {width} x {height}', w_half, h_half - 100)
    display_text('1600 x 900', w_half, h_half - 50)
    display_text('1280 x 720', w_half, h_half)
    display_text('854 x 480', w_half, h_half + 50)
    display_text('SAVE & EXIT', w_half, h_half + 100)
    if menu_selection == 0:
        display_text('> 1600 x 900 <', w_half, h_half - 52, 'white')
    elif menu_selection == 1:
        display_text('> 1280 x 720 <', w_half, h_half - 2, 'white')
    elif menu_selection == 2:
        display_text('> 854 x 480 <', w_half, h_half + 48, 'white')
    elif menu_selection == 3:
        display_text('> SAVE & EXIT <', w_half, h_half + 98, 'white')


pygame.init()
width, height = resolution_changer()[:2]
w_half = (width // 2)
h_half = (height // 2)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Spacewar")
icon = pygame.image.load('Graphics/Player_1_Thrust.png')
# background = pygame.image.load('Graphics/Background.png').convert_alpha()
pygame.display.set_icon(icon)
mouse_x, mouse_y = pygame.mouse.get_pos()
ammo_x, ammo_y = random.randint(20, (width - 20)), random.randint(20, (height - 20))
shield_x, shield_y = random.randint(20, (width - 20)), random.randint(20, (height - 20))
player1 = Player((width // 1.5), (height // 2), 90, 'Player_1')
player2 = Player((width // 3), (height // 2), 270, 'Player_2')
player1_bullet = Bullet(player1.x, player1.y, player1.angle, True, player1)
player2_bullet = Bullet(player2.x, player2.y, player2.angle, True, player2)
bullet_mouse = Bullet(mouse_x, mouse_y, 0, False)
width, height, set_res_func, save_config_func = resolution_changer()
player1_last_bullet_time = 0
player2_last_bullet_time = 0
player1_bullet_count = 1
player2_bullet_count = 1
bullet_cooldown = 3000
clock = pygame.time.Clock()
pygame.mixer.set_num_channels(4)
menu_selection = 0
powerups = {
    "ammo": {"collected": True, "color": 'goldenrod3'},
    "shield": {"collected": True, "color": 'dodgerblue3'},
}
debug = False
game_active = False
main_menu = True
options_menu = False
options_res_menu = False
running = True

# Custom events
restart_event = pygame.USEREVENT + 1
ammo_event = pygame.USEREVENT + 2
shield_event = pygame.USEREVENT + 3
shield_end_event = pygame.USEREVENT + 5

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == restart_event:
            restart_game()
        if event.type == ammo_event:
            ammo_x, ammo_y = random.randint(20, (width - 20)), random.randint(20, (height - 20))
            powerups['ammo']['collected'] = False
        if event.type == shield_event:
            shield_x, shield_y = random.randint(20, (width - 20)), random.randint(20, (height - 20))
            powerups['shield']['collected'] = False
        if event.type == shield_end_event:
            if player1.health >= 2:
                player1.health = 1
            if player2.health >= 2:
                player2.health = 1

        if game_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RCTRL:
                    if start_ticks - player1_last_bullet_time > bullet_cooldown:
                        if player1.health > 0 and player1.bullet_count >= 1:
                            player1_bullet.bullet_list.append(Bullet(player1.x, player1.y, player1.angle, True, player1))
                            pygame.mixer.Channel(2).play(player1_bullet.sound)
                            player1_last_bullet_time = start_ticks
                            player1.bullet_count -= 1
                if event.key == pygame.K_SPACE:
                    if start_ticks - player2_last_bullet_time > bullet_cooldown:
                        if player2.health > 0 and player2.bullet_count >= 1:
                            player2_bullet.bullet_list.append(Bullet(player2.x, player2.y, player2.angle, True, player2))
                            pygame.mixer.Channel(2).play(player2_bullet.sound)
                            player2_last_bullet_time = start_ticks
                            player2.bullet_count -= 1
                if event.key == pygame.K_ESCAPE:
                    restart_game()
                    game_active = False
                    main_menu = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    if player1.health > 0:
                        player1.sound_boost_loop.stop()
                        pygame.mixer.Channel(1).play(player1.sound_boost_end)
                if event.key == pygame.K_w:
                    if player2.health > 0:
                        player2.sound_boost_loop.stop()
                        pygame.mixer.Channel(1).play(player2.sound_boost_end)

        elif main_menu:
            powerups['ammo']['collected'] = True
            powerups['shield']['collected'] = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    menu_selection -= 1
                    if menu_selection <= 0:
                        menu_selection = 0
                if event.key == pygame.K_DOWN:
                    menu_selection += 1
                    if menu_selection >= 2:
                        menu_selection = 2
                if event.key == pygame.K_RETURN:
                    if menu_selection == 0:
                        main_menu = False
                        game_active = True
                        pygame.time.set_timer(ammo_event, 3000, 1)
                        pygame.time.set_timer(shield_event, 15000, 1)
                    if menu_selection == 1:
                        main_menu = False
                        options_menu = True
                    if menu_selection == 2:
                        running = False
                    menu_selection = 0

        elif options_menu:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    menu_selection -= 1
                    if menu_selection <= 0:
                        menu_selection = 0
                if event.key == pygame.K_DOWN:
                    menu_selection += 1
                    if menu_selection >= 2:
                        menu_selection = 2
                if event.key == pygame.K_RETURN:
                    if menu_selection == 0:
                        options_menu = False
                        options_res_menu = True
                        menu_selection = 0
                    if menu_selection == 2:
                        options_menu = False
                        main_menu = True
                        menu_selection = 0
                if event.key == pygame.K_ESCAPE:
                    restart_game()
                    options_menu = False
                    main_menu = True

        elif options_res_menu:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    menu_selection -= 1
                    if menu_selection <= 0:
                        menu_selection = 0
                if event.key == pygame.K_DOWN:
                    menu_selection += 1
                    if menu_selection >= 3:
                        menu_selection = 3
                if event.key == pygame.K_RETURN:
                    if menu_selection == 0:
                        set_res_func(1600, 900)
                    if menu_selection == 1:
                        set_res_func(1280, 720)
                    if menu_selection == 2:
                        set_res_func(854, 480)
                    if menu_selection == 3:
                        save_config_func()
                        options_res_menu = False
                        options_menu = True
                        menu_selection = 0
                if event.key == pygame.K_ESCAPE:
                    restart_game()
                    options_menu = False
                    main_menu = True
                    menu_selection = 0

    if game_active:
        start_ticks = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        if player1.health >= 1:
            if keys[pygame.K_LEFT]:
                player1.turn_left()
            if keys[pygame.K_RIGHT]:
                player1.turn_right()
            if keys[pygame.K_UP]:
                player1.apply_thrust()
                player1.sound_boost_loop.play(1)
                player1.img = player1.img_thrust
            else:
                player1.img = pygame.image.load(f'Graphics/Player_1.png').convert_alpha()

        if player1.health <= 0:
            player1.sound_boost_loop.stop()
            player1.explode()
        if player2.health >= 1:
            if keys[pygame.K_a]:
                player2.turn_left()
            if keys[pygame.K_d]:
                player2.turn_right()
            if keys[pygame.K_w]:
                player2.apply_thrust()
                player2.sound_boost_loop.play(1)
                player2.img = player2.img_thrust
            else:
                player2.img = pygame.image.load(f'Graphics/Player_2.png').convert_alpha()
        if player2.health <= 0:
            player2.sound_boost_loop.stop()
            player2.explode()

        player1.update()
        player2.update()
        screen.fill('black')
        black_hole(player1)
        black_hole(player2)
        # Stop drawing when explosion animation ends
        if player1.current_sprite < 9:
            player1.draw()
        if player2.current_sprite < 9:
            player2.draw()
        if player1.health >= 2:
            pygame.draw.arc(screen, 'skyblue', ((player1.x - 15), (player1.y - 15), 30, 30), 0, 360, 1)
        if player2.health >= 2:
            pygame.draw.arc(screen, 'skyblue', ((player2.x - 15), (player2.y - 15), 30, 30), 0, 360, 1)

        fps = clock.get_fps()
        player1_bullet.modify_bullet_list(player2)
        player1_bullet.modify_bullet_list(player1)
        player2_bullet.modify_bullet_list(player1)
        player2_bullet.modify_bullet_list(player2)
        bullet_mouse.modify_bullet_list(player1)
        bullet_mouse.modify_bullet_list(player2)

        if player1.health >= 1 and player2.health >= 1:
            player1.check_ship_collision(player2)
            player2.check_ship_collision(player1)

        if debug:
            debug_text('FPS', 10, 10, 16, fps)
            debug_text('ticks', 40, 10, 16, start_ticks)
            debug_text('p1_bullets', 70, 10, 16, len(player1_bullet.bullet_list + bullet_mouse.bullet_list))
            debug_text('p1_angle', 100, 10, 16, player1.angle)
            debug_text('p1_health', 130, 10, 16, player1.health)
            debug_text('p2_health', 160, 10, 16, player2.health)
            debug_text('p1_bullet_count', 190, 10, 16, player1.bullet_count)
            debug_text('p2_bullet_count', 220, 10, 16, player2.bullet_count)

        bullets_collide()
        mouse_bullet_spawn()
        p1_shield_check = check_powerup(player1)
        p2_shield_check = check_powerup(player2)
        pygame.display.update()

    elif main_menu == True:
        menu_screen()
        pygame.display.update()

    elif options_menu == True:
        options_screen()
        pygame.display.update()

    elif options_res_menu == True:
        resolution_screen()
        pygame.display.update()

    clock.tick(60)
pygame.quit()

# To do:
# -Add a new powerup




