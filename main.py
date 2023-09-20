import pygame

import math


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

    def explode(self):
        self.sprites = []
        for i in range(1, 10):
            self.image = pygame.image.load(f'Graphics/Explosion/frame_{i}.png')
            self.sprites.append(self.image)
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
        self.angle_velocity *= 0.98

    def apply_thrust(self):
        self.thrust_force = 0.01
        self.velocity_x += self.cosine * self.thrust_force
        self.velocity_y -= self.sine * self.thrust_force

    def apply_vector(self):
        self.gravity_direction = self.gravity_point - pygame.math.Vector2(self.x, self.y)
        self.gravity_direction.normalize_ip()
        self.velocity_x += self.gravity_direction.x * self.gravitational_force * 0.1
        self.velocity_y += self.gravity_direction.y * self.gravitational_force * 0.1

    def update_location(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        if self.x > WIDTH:
            self.x = 0
        elif self.x < 0 - self.w:
            self.x = WIDTH
        elif self.y < 0:
            self.y = HEIGHT
        elif self.y > HEIGHT:
            self.y = 0

    def update(self):
        self.update_rotation()
        if self.health > 0:
            self.apply_vector()
            self.update_location()


class Bullet:
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
            self.velocity_x = (math.cos(math.radians(angle + 90)) * 2) + player.velocity_x
            self.velocity_y = (-math.sin(math.radians(angle + 90)) * 2) + player.velocity_y
        else:
            self.velocity_x = 0
            self.velocity_y = 0
        self.gravity_point = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
        self.gravitational_force = 0

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.apply_vector()

    def apply_vector(self):
        self.gravity_direction = self.gravity_point - pygame.math.Vector2(self.x, self.y)
        self.gravity_direction.normalize_ip()
        self.velocity_x += self.gravity_direction.x * self.gravitational_force
        self.velocity_y += self.gravity_direction.y * self.gravitational_force

    def draw(self, window):
        pygame.draw.circle(window, self.color, (int(self.x), int(self.y)), self.radius)

    def check_ship_collision(self, object):
        distance = math.sqrt((self.x - object.centerx) ** 2 + (self.y - object.centery) ** 2)
        return distance < object.width / 2

    def check_bullet_collision(self, other_bullet, hitbox_size):
        distance = math.sqrt((self.x - other_bullet.x) ** 2 + (self.y - other_bullet.y) ** 2)
        return distance < (self.radius * hitbox_size) + (other_bullet.radius * hitbox_size)


def display_text(name, variable, height):
    font = pygame.font.Font(None, 36)
    variable_text = font.render(f"{name}: {variable: .0f}", True, (255, 255, 255))
    screen.blit(variable_text, (10, height))


def mouse_bullet_spawn():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()
    if mouse_buttons[0] == 1:
        bullet_mouse.bullet_list.append(Bullet(mouse_x, mouse_y, 0, False, player1))


def draw_bullet(name, player):
    for i in name.bullet_list:
        i.draw(screen)
        i.update()
        if i.x < 0 or i.x > WIDTH or i.y < 0 or i.y > HEIGHT:
            name.bullet_list.remove(i)
        if i.check_ship_collision(player.rotated_rect):
            name.bullet_list.remove(i)
            player.health -= 1
            if player.health <= 0:
                pygame.time.set_timer(event_1, 3000, 1)
                pygame.mixer.Channel(3).play(player1.sound_explode)
                player.explode()


def bullet_collisions():
    for i in player1_bullet.bullet_list:
        for j in player2_bullet.bullet_list:
            if i != j:
                if i.check_bullet_collision(j, 6):
                    player1_bullet.bullet_list.remove(i)
                    player2_bullet.bullet_list.remove(j)


def restart_game():
    # Player 1 reset settings
    player1.angle = 270
    player1.x = 633
    player1.y = 500
    player1.health = 1
    player1.velocity_x = 0
    player1.velocity_y = 0
    player1.current_sprite = 0

    # Player 2 reset settings
    player2.angle = 90
    player2.x = 1266
    player2.y = 500
    player2.health = 1
    player2.velocity_x = 0
    player2.velocity_y = 0
    player2.current_sprite = 0

    # Clear all bullets
    player1_bullet.bullet_list.clear()
    player2_bullet.bullet_list.clear()
    bullet_mouse.bullet_list.clear()


pygame.init()
WIDTH = 1900
HEIGHT = 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spacewar")
mouse_x, mouse_y = pygame.mouse.get_pos()
player1 = Player(633, 500, 270, 'Player_1')
player2 = Player(1266, 500, 90, 'Player_2')
player1_bullet = Bullet(player1.x, player1.y, player1.angle, True, player1)
player2_bullet = Bullet(player2.x, player2.y, player2.angle, True, player2)
bullet_mouse = Bullet(mouse_x, mouse_y, 0, False)
player1_last_bullet_time = 0
player2_last_bullet_time = 0
bullet_cooldown = 1000
clock = pygame.time.Clock()
pygame.mixer.set_num_channels(4)
game_active = True
running = True

# Custom events
event_1 = pygame.USEREVENT + 1

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == event_1:
            restart_game()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                if start_ticks - player1_last_bullet_time > bullet_cooldown:
                    if player1.health > 0:
                        player1_bullet.bullet_list.append(Bullet(player1.x, player1.y, player1.angle, True, player1))
                        pygame.mixer.Channel(2).play(player1_bullet.sound)
                        player1_last_bullet_time = start_ticks
            if event.key == pygame.K_s:
                if start_ticks - player2_last_bullet_time > bullet_cooldown:
                    if player2.health > 0:
                        player2_bullet.bullet_list.append(Bullet(player2.x, player2.y, player2.angle, True, player2))
                        pygame.mixer.Channel(2).play(player2_bullet.sound)
                        player2_last_bullet_time = start_ticks
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                if player1.health > 0:
                    player1.sound_boost_loop.stop()
                    pygame.mixer.Channel(1).play(player1.sound_boost_end)
            if event.key == pygame.K_w:
                if player2.health > 0:
                    player2.sound_boost_loop.stop()
                    pygame.mixer.Channel(1).play(player2.sound_boost_end)
    if game_active:
        start_ticks = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player1.turn_left()
        if keys[pygame.K_RIGHT]:
            player1.turn_right()
        if keys[pygame.K_UP]:
            if player1.health > 0:
                player1.apply_thrust()
                player1.sound_boost_loop.play(1)
                player1.img = player1.img_thrust
        elif player1.health <= 0:
            player1.explode()
        else:
            player1.img = pygame.image.load(f'Graphics/Player_1.png').convert_alpha()
        if keys[pygame.K_a]:
            player2.turn_left()
        if keys[pygame.K_d]:
            player2.turn_right()
        if keys[pygame.K_w]:
            if player2.health > 0:
                player2.apply_thrust()
                player2.sound_boost_loop.play(1)
                player2.img = player2.img_thrust
        elif player2.health <= 0:
            player2.explode()
        else:
            player2.img = pygame.image.load(f'Graphics/Player_2.png').convert_alpha()

        player1.update()
        player2.update()
        screen.fill('black')

        # Center circle
        pygame.draw.circle(screen, (255, 255, 255), (WIDTH // 2, HEIGHT // 2), 8)
        pygame.draw.circle(screen, (0, 0, 0), (WIDTH // 2, HEIGHT // 2), 7)

        # Stop drawing when explosion animation ends
        if player1.current_sprite < 9:
            player1.draw()
        if player2.current_sprite < 9:
            player2.draw()

        draw_bullet(player1_bullet, player2)
        draw_bullet(player2_bullet, player1)
        draw_bullet(bullet_mouse, player1)
        fps = clock.get_fps()
        display_text('FPS', fps, 10)
        display_text('velocity', player1.angle_velocity, 40)
        display_text('bullets', len(player1_bullet.bullet_list + bullet_mouse.bullet_list), 70)
        display_text('angle', player1.angle, 100)
        display_text('p1_health', player1.health, 130)
        display_text('p2_health', player2.health, 160)
        display_text('time', player1_last_bullet_time, 190)
        bullet_collisions()
        mouse_bullet_spawn()
        pygame.display.update()
    clock.tick(60)
pygame.quit()