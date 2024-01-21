import pygame

import math

import random



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
        self.gravity_point = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
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

    def apply_thrust(self):
        self.thrust_force = 0.02
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
        if self.x >= WIDTH or self.x <= 0 - self.w or self.y <= 0 or self.y >= HEIGHT:
            self.health -= 100
            pygame.time.set_timer(event_1, 3000, 1)
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
        self.gravity_point = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
        self.gravitational_force = 0


    def update_bullet(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.apply_bullet_vector()

    def check_bullet_collisions(self, player):
        for i in self.bullet_list:
            i.draw_bullet(screen)
            i.update_bullet()
            if i.x < 0 or i.x > WIDTH or i.y < 0 or i.y > HEIGHT:
                self.bullet_list.remove(i)
            if player.health >= 1:
                if i.check_ship_collision(player.rotated_rect):
                    self.bullet_list.remove(i)
                    player.health -= 1
                    if player.health <= 0:
                        pygame.time.set_timer(event_1, 3000, 1)
                        pygame.mixer.Channel(3).play(player1.sound_explode)
                        player.explode()

    def apply_bullet_vector(self):
        # Calculates bullet gravity towards the centre
        self.gravity_direction = self.gravity_point - pygame.math.Vector2(self.x, self.y)
        self.gravity_direction.normalize_ip()
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
    player1.x = 1266
    player1.y = 500
    player1.health = 1
    # Shared settings to reset
    player1.velocity_x, player2.velocity_x = 0, 0
    player1.velocity_y, player2.velocity_y = 0, 0
    player1.current_sprite, player2.current_sprite = 0, 0
    player1.bullet_count, player2.bullet_count = 1, 1
    player1.angle_velocity, player2.angle_velocity = 0, 0
    # Player 2 reset settings
    player2.angle = 270
    player2.x = 633
    player2.y = 500
    player2.health = 1
    # Clear all bullets
    player1_bullet.bullet_list.clear()
    player2_bullet.bullet_list.clear()
    bullet_mouse.bullet_list.clear()


def display_text(text, x, y, colour='gray33', size=30):
    font = pygame.font.Font('Fonts/clacon2.ttf', size)
    menu_text = font.render(f'{text}', False, colour)
    menu_text_rect = menu_text.get_rect()
    menu_text_rect.center = (x, y)
    screen.blit(menu_text, menu_text_rect)


def check_powerup(player):
    global powerup_collected
    if not powerup_collected:
        pygame.draw.circle(screen, 'green', (powerup_x, powerup_y), 5)
        distance = math.sqrt((player.x - powerup_x) ** 2 + (player.y - powerup_y) ** 2)
        if distance < player.w / 2 + 8:
            player.bullet_count += 1
            powerup_collected = True
            pygame.time.set_timer(event_2, 1000, 1)

def menu_screen():
    screen.fill('black')
    logo = pygame.image.load('Graphics/logo.png').convert_alpha()
    resized_logo = pygame.transform.scale(logo, (742, 116))
    screen.blit(resized_logo, (579, 100))
    display_text('alpha-v0.1.1', 1400, 210, 'grey', 20)
    display_text('START', 950, 450)
    display_text('OPTIONS', 950, 500)
    display_text('EXIT', 950, 550)
    if menu_selection == 0:
        display_text('> START <', 950, 448, 'white')
    elif menu_selection == 1:
        display_text('> OPTIONS <', 950, 498, 'white')
    elif menu_selection == 2:
        display_text('> EXIT <', 950, 548, 'white')


def options_screen():
    screen.fill('black')
    display_text('RESOLUTION (SOON)', 950, 450)
    display_text('CONTROLS (SOON)', 950, 500)
    display_text('SAVE & EXIT', 950, 550)
    if options_selection == 0:
        display_text('> RESOLUTION (SOON) <', 950, 448, 'white')
    elif options_selection == 1:
        display_text('> CONTROLS (SOON) <', 950, 498, 'white')
    elif options_selection == 2:
        display_text('> SAVE & EXIT <', 950, 548, 'white')


pygame.init()
WIDTH = 1900
HEIGHT = 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.transform.scale(screen, (800, 600))
pygame.display.set_caption("Spacewar")
icon = pygame.image.load('Graphics/Player_1_Thrust.png')
pygame.display.set_icon(icon)
mouse_x, mouse_y = pygame.mouse.get_pos()
powerup_x, powerup_y = random.randint(10, 1890), random.randint(10, 990)
player1 = Player(1266, 500, 90, 'Player_1')
player2 = Player(633, 500, 270, 'Player_2')
player1_bullet = Bullet(player1.x, player1.y, player1.angle, True, player1)
player2_bullet = Bullet(player2.x, player2.y, player2.angle, True, player2)
bullet_mouse = Bullet(mouse_x, mouse_y, 0, False)
player1_last_bullet_time = 0
player2_last_bullet_time = 0
player1_bullet_count = 1
player2_bullet_count = 1
bullet_cooldown = 3000
clock = pygame.time.Clock()
pygame.mixer.set_num_channels(4)
menu_selection = 0
options_selection = 0
debug = True
game_active = False
main_menu = True
options_menu = False
running = True
powerup_collected = False


# Custom events
event_1 = pygame.USEREVENT + 1
event_2 = pygame.USEREVENT + 2

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == event_1:
            restart_game()
            powerup_x, powerup_y = random.randint(10, 1890), random.randint(10, 990)
        if event.type == event_2:
            powerup_x, powerup_y = random.randint(10, 1890), random.randint(10, 990)
            powerup_collected = False
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
            options_selection = 0
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
                    if menu_selection == 1:
                        main_menu = False
                        options_menu = True
                    if menu_selection == 2:
                        running = False
        elif options_menu:
            menu_selection = 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    options_selection -= 1
                    if options_selection <= 0:
                        options_selection = 0
                if event.key == pygame.K_DOWN:
                    options_selection += 1
                    if options_selection >= 2:
                        options_selection = 2
                if event.key == pygame.K_RETURN:
                    if options_selection == 2:
                        options_menu = False
                        main_menu = True
                if event.key == pygame.K_ESCAPE:
                    restart_game()
                    options_menu = False
                    main_menu = True


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

        # Center gravity point
        pygame.draw.circle(screen, (255, 255, 255), (WIDTH // 2, HEIGHT // 2), 8)
        pygame.draw.circle(screen, (0, 0, 0), (WIDTH // 2, HEIGHT // 2), 7)

        # Stop drawing when explosion animation ends
        if player1.current_sprite < 9:
            player1.draw()
        if player2.current_sprite < 9:
            player2.draw()

        fps = clock.get_fps()
        player1_bullet.check_bullet_collisions(player2)
        player1_bullet.check_bullet_collisions(player1)
        player2_bullet.check_bullet_collisions(player1)
        player2_bullet.check_bullet_collisions(player2)
        bullet_mouse.check_bullet_collisions(player1)

        if debug:
            debug_text('FPS', 10, 10, 24, fps)
            debug_text('ticks', 40, 10, 24, start_ticks)
            debug_text('p1_bullets', 70, 10, 24, len(player1_bullet.bullet_list + bullet_mouse.bullet_list))
            debug_text('p1_angle', 100, 10, 24, player1.angle)
            debug_text('p1_health', 130, 10, 24, player1.health)
            debug_text('p2_health', 160, 10, 24, player2.health)
            debug_text('p1_bullet_count', 190, 10, 24, player1.bullet_count)
            debug_text('p2_bullet_count', 220, 10, 24, player2.bullet_count)
            debug_text('p1_bullet_count', 250, 10, 24, player1_bullet.velocity_x)
            debug_text('p2_bullet_count', 280, 10, 24, player1_bullet.velocity_y)
        bullets_collide()
        mouse_bullet_spawn()
        check_powerup(player1)
        check_powerup(player2)
        pygame.display.update()

    elif main_menu == True:
        menu_screen()
        pygame.display.update()
        powerup_x, powerup_y = random.randint(10, 1890), random.randint(10, 990)

    elif options_menu == True:
        options_screen()
        pygame.display.update()

    clock.tick(60)
pygame.quit()