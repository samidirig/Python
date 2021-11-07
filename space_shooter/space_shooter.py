import pygame
from pygame import mixer
import random

pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
# define fps
clock = pygame.time.Clock()
fps = 60  # add fps time to limit screen frame rate

# define game variables
screen_width = 500
screen_height = 700
rows = 5
cols = 5
boss_health = 50
boss_spawn = False
meteor_times = 9
meteor_killed_counter = 0
alien_killed_counter = 0
power_speed_delay = 10000
speed_power_times = 2
countdown = 3
last_countdown = pygame.time.get_ticks()
game_over = 0  # 0 zero is game is working, 1 is player has won, -1 is player has lost
# spaceship variables
shoot_delay = 370
meteor_shoot_delay = 250
spaceship_health = 5
# alien time variables
alien_delay = 700
last_alien_shot = pygame.time.get_ticks()
# define colours
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)

# define screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Space Shooter')

# load background choose on file
background_image = pygame.image.load("images/bg2.jpg")

# load sounds
explosion_sound = pygame.mixer.Sound("sounds/img_explosion.wav")
explosion_sound.set_volume(0.2)

explosion_sound2 = pygame.mixer.Sound("sounds/spaceship_exp.wav")
explosion_sound2.set_volume(0.3)

laser_sound = pygame.mixer.Sound("sounds/img_laser.wav")
laser_sound.set_volume(0.1)

boss_death_sound = pygame.mixer.Sound("sounds/boss_death.wav")
boss_death_sound.set_volume(0.4)

game_sound = pygame.mixer.Sound("sounds/game_music2.wav")
game_sound.set_volume(0.1)
game_sound.play()

# fonts
font30 = pygame.font.SysFont('constantia', 30)
font40 = pygame.font.SysFont('constantia', 40)

# print(pygame.font.get_fonts())   # if we want to see available fonts in packs

# get time
time_font = pygame.font.SysFont("BebasNeue-Regular.ttf", 30)
start_time = pygame.time.get_ticks()
static_time = 0
minute_counter = 0
second_counter = 0


def get_time():
    counting_time = pygame.time.get_ticks() - start_time
    global static_time, second_counter, minute_counter, counting_string
    counting_minute = int(counting_time / 60000)  # 1 minute is 60000 milliseconds
    counting_second = int((counting_time - static_time) / 1000)  # 1 second is 1000 milliseconds
    second_counter = int(counting_time / 1000)
    minute_counter = int(counting_time / 60000)
    if counting_second < 10:
        counting_string = "%s : %s" % (counting_minute, ('0' + str(counting_second)))
    elif counting_second == 59:  # when time passed a minute, second will be again 0
        static_time = pygame.time.get_ticks()
        minute_counter += 1
    else:
        counting_string = "%s : %s" % (counting_minute, counting_second)

    counting_text = time_font.render(str(counting_string), True, (255, 255, 255))
    counting_rect = counting_text.get_rect()
    counting_rect.center = [35, 50]
    screen.blit(counting_text, counting_rect)


if second_counter == 110:
    game_sound.play()


# set background
def define_bg():
    screen.blit(background_image, (0, 0))


# set text
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


# draw score
score_value = 0
score_font = pygame.font.SysFont("BebasNeue-Regular.ttf", 30)
score_x = 10
score_y = 10


def calculate_score():
    global score_value, second_counter
    if 110 >= second_counter > 90:
        score_value += 300
    elif 90 >= second_counter > 60:
        score_value += 600
    elif 60 >= second_counter:
        score_value += 1000
    # health remaining
    elif 5 >= spaceship_health > 3:
        score_value += 1000
    elif 3 >= spaceship_health > 1:
        score_value += 300


def show_score(x, y):
    score = score_font.render("Score : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))


# create a class for spaceship
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        global spaceship_health
        self.image = pygame.image.load("images/spaceship2.png")
        self.image = pygame.transform.scale(self.image, (65, 58))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = spaceship_health
        self.health_remaining = spaceship_health
        self.last_shot = pygame.time.get_ticks()

    def movement_spaceship(self):
        speed = 5
        delay = shoot_delay  # ms
        if len(alien_group) == 0:
            delay = meteor_shoot_delay  # if meteor came up, shoot delay will increase
            if boss_spawn:  # if boss came up shoot delay will decrease
                delay = shoot_delay

        # key_state (press and control ship movements)
        key_state = pygame.key.get_pressed()
        if key_state[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key_state[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed
        if key_state[pygame.K_UP] and self.rect.top > 450:
            self.rect.y -= speed
        if key_state[pygame.K_DOWN] and self.rect.bottom < screen_height - 22:
            self.rect.y += speed

        # shoot bullets
        current_time = pygame.time.get_ticks()
        if key_state[pygame.K_SPACE] and current_time - self.last_shot > delay:
            laser_sound.play()
            bullet = Bullets(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = current_time

    # draw health bar and explosions on ship
    def draw_health(self):
        global game_over
        game_over = 0
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 8))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10),
                                             int(self.rect.width * (self.health_remaining / self.health_start)), 8))
        elif self.health_remaining <= 0:
            # spaceship big explosion
            explosion = Exp_spaceship(self.rect.centerx, self.rect.centery)
            exp_spaceship_group.add(explosion)
            self.kill()
            game_over = -1
        return game_over


# create a class for bullets
class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/bullet2.png")
        self.image = pygame.transform.scale(self.image, (8, 40))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    # control collides between bullets and enemies
    def update(self):
        global score_value
        self.rect.y -= 10
        if self.rect.bottom < 0:
            self.kill()
        # destroy aliens
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            global alien_killed_counter
            alien_killed_counter += 1
            # explosion sound
            explosion_sound.play()
            score_value += 1
            # explosion alien
            explosion = Explosions(self.rect.centerx, self.rect.centery, 2)
            exp_enemies_group.add(explosion)
        # destroy meteors
        if pygame.sprite.spritecollide(self, meteor_group, True):
            self.kill()
            global meteor_killed_counter
            meteor_killed_counter += 1
            # explosion sound
            explosion_sound.play()
            score_value += 5
            # explosion meteor
            explosion = Explosions(self.rect.centerx, self.rect.centery, 2)
            exp_enemies_group.add(explosion)
        # destroy big_boss
        if pygame.sprite.spritecollide(self, big_boss_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion_sound2.play()
            # animating health
            big_boss.boss_health -= 1
            score_value += 1
            # spaceship mini explosion
            explosion = Explosions(self.rect.centerx, self.rect.centery, 1)
            exp_enemies_group.add(explosion)


class Speed_power(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/bolt_gold.png")
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, screen_width - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randint(1, 5)

    # if speed power disappeared, they will be shown again
    def spawn_again(self):
        self.rect.x = random.randrange(0, screen_width - self.rect.width)
        self.rect.y = random.randrange(-150, -30)
        self.speedy = random.randint(1, 2)

    def update(self):
        global shoot_delay
        self.rect.y += self.speedy
        # set the frequency of appearance
        if len(alien_group) <= 5 and self.rect.top > screen_height:
            self.spawn_again()
        if len(speed_power_group) < 2:
            create_speed_power()
        #control using speed power
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            # if spaceship health below 3, speed power will increase it to 3
            if spaceship.health_remaining < 3:
                spaceship.health_remaining += 1
            # increase shoot delay
            shoot_delay -= 10


# create a class for meteors
class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.num = random.randint(1, 3)
        self.image = pygame.image.load(f"images/others/meteor{self.num}.png")
        self.image.set_colorkey((0, 0, 0))
        # self.image = pygame.transform.scale(self.image, (35, 35))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, screen_width - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speed_y = random.randint(1, 2)
        self.speed_x = random.randint(-2, 2)

    def spawn_again(self):
        self.rect.x = random.randrange(0, screen_width - self.rect.width)
        self.rect.y = random.randrange(-150, -20)
        self.speed_y = random.randint(1, 2)
        self.speed_x = random.randint(-2, 2)

    # movements meteors
    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        # respawn meteors
        if self.rect.left > screen_width or self.rect.right < 0 or self.rect.top > screen_height + 1:
            self.spawn_again()
        if len(meteor_group) < 8:
            create_meteor()
        # control collide spaceship
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion_sound2.play()
            # animating health
            spaceship.health_remaining -= 1
            # spaceship mini explosion
            explosion = Explosions(self.rect.centerx, self.rect.centery, 1)
            exp_enemies_group.add(explosion)


# create a class for aliens
class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/alien" + str(random.randint(1, 5)) + ".png").convert()
        self.image.set_colorkey((0, 0, 0))  # remove black pixels
        self.image = pygame.transform.scale(self.image, (35, 35))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move = 1
        self.move_counter = 0

    # movements aliens
    def update(self):
        self.rect.x += self.move
        self.move_counter += 1
        if abs(self.move_counter) > 30:
            self.move *= -1
            self.move_counter *= self.move
            self.rect.y += 2


# create a class for alien bullets
class Aliens_bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/alien_bullet.png")
        self.image = pygame.transform.scale(self.image, (8, 8))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    # alien shoots and control spaceship explosion
    def update(self):
        self.rect.y += 5
        if self.rect.bottom > screen_height:
            self.kill()
        # masking spaceship rectangle
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion_sound2.play()
            # animating health
            spaceship.health_remaining -= 1
            # spaceship mini explosion
            explosion = Explosions(self.rect.centerx, self.rect.centery, 1)
            exp_enemies_group.add(explosion)


# create a class for big alien
class Big_boss(pygame.sprite.Sprite):
    def __init__(self, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/alien_boss.png")
        self.image = pygame.transform.scale(self.image, (250, 90))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width / 2, -250)
        self.boss_health = health
        self.move = 1
        self.move_counter = 0

    def update(self):
        global score_value
        self.rect.x += self.move
        self.move_counter += 4
        if self.rect.y < 100:
            self.rect.y += 50
        elif abs(self.move_counter) > 450:
            self.move *= -1
            self.move_counter *= self.move
        elif self.boss_health <= 0:
            # big_boss explosion
            explosion = Exp_spaceship(self.rect.centerx, self.rect.centery)
            laser_sound.stop()
            boss_death_sound.play()
            calculate_score()
            score_value += 1000
            exp_spaceship_group.add(explosion)
            self.kill()


# creating a class for explosions
class Explosions(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        # create list for images
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"images/exp{num}.png")
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            # adding images to list
            self.images.append(img)
        self.index = 0
        self.counter = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        # creating animation to show an explosion using images' index
        exp_speed = 3
        self.counter += 1
        if self.counter >= exp_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]
        if self.index >= len(self.images) - 1 and self.counter >= exp_speed:
            self.kill()


# a class for spaceship explosions
class Exp_spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(9):
            img = pygame.image.load(f"images/others/exp0{num}.png")
            img.set_colorkey((0, 0, 0))
            img = pygame.transform.scale(img, (110, 110))
            self.images.append(img)
        self.index = 0
        self.counter = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        exp_speed = 3
        self.counter += 1
        if self.counter >= exp_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]
        if self.index >= len(self.images) - 1 and self.counter >= exp_speed:
            self.kill()


####################################
# create sprite groups
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
exp_enemies_group = pygame.sprite.Group()
exp_spaceship_group = pygame.sprite.Group()
meteor_group = pygame.sprite.Group()
big_boss_group = pygame.sprite.Group()
speed_power_group = pygame.sprite.Group()


# create meteors
def create_meteor():
    for i in range(meteor_times):
        meteor = Meteor()
        meteor_group.add(meteor)


create_meteor()


# create aliens
def create_aliens():
    # create an alien
    for row in range(rows):
        for item in range(cols):
            alien = Aliens(50 + item * 100, 100 + row * 70)
            alien_group.add(alien)


create_aliens()
# create boss
big_boss = Big_boss(boss_health)
big_boss_group.add(big_boss)

# create spaceship
spaceship = Spaceship(int(screen_width / 2), screen_height - 100)
spaceship_group.add(spaceship)


# create speed power
def create_speed_power():
    for i in range(speed_power_times):
        speed_power = Speed_power()
        speed_power_group.add(speed_power)


create_speed_power()
####################################
####################################
# run
running = True

while running:
    clock.tick(fps)

    # draw background
    define_bg()
    if countdown == 0:

        # create alien and boss shots
        time_now = pygame.time.get_ticks()
        if time_now - last_alien_shot > alien_delay and len(alien_bullet_group) < 10 and len(alien_group) > 0:
            attack = random.choice(alien_group.sprites())
            alien_bullet = Aliens_bullets(attack.rect.centerx, attack.rect.bottom)
            alien_bullet_group.add(alien_bullet)
            last_alien_shot = time_now
        # big boss shot
        elif time_now - last_alien_shot > alien_delay and len(alien_group) <= 0 and len(
                big_boss_group) > 0 and boss_spawn:
            attack2 = big_boss
            alien_bullet = Aliens_bullets(attack2.rect.centerx, attack2.rect.bottom)
            alien_bullet_group.add(alien_bullet)
            last_alien_shot = time_now
        # check all aliens been killed
        if len(big_boss_group) == 0:
            game_over = 1
        if game_over == 0:
            get_time()
            # spaceship
            spaceship.movement_spaceship()
            game_over = spaceship.draw_health()

            # update sprite groups
            bullet_group.update()
            alien_group.update()
            alien_bullet_group.update()
            speed_power_group.update()
            if len(alien_group) <= 1:
                speed_power_group.update()
            if meteor_killed_counter > 50:
                big_boss_group.update()
                boss_spawn = True
                meteor_times = 0
            # when aliens has destroyed, meteors come
            if len(alien_group) <= 0:
                meteor_group.update()
        else:
            if game_over == -1:
                get_time()
                draw_text('YOU LOST! GAME OVER!', font40, white, int(screen_width / 2 - 220), int(screen_height / 2 + 100))
                draw_text(str(score_value), font40, white, int(screen_width / 2 - 10),
                          int(screen_height + 100))

            if game_over == 1:
                get_time()
                draw_text('YOU WİN!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 70))
                draw_text("YOUR SCORE: " + str(score_value), font40, white, int(screen_width / 2 - 10),
                          int(screen_height + 100))

    if countdown > 0:
        draw_text('GET READY!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 70))
        draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100))
        count_timer = pygame.time.get_ticks()
        if count_timer - last_countdown > 1000:
            countdown -= 1
            last_countdown = count_timer
    # update explosion group
    exp_enemies_group.update()
    exp_spaceship_group.update()
    # draw all sprites
    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    alien_group.draw(screen)
    alien_bullet_group.draw(screen)
    exp_enemies_group.draw(screen)
    exp_spaceship_group.draw(screen)
    meteor_group.draw(screen)
    big_boss_group.draw(screen)
    speed_power_group.draw(screen)

    # show score
    show_score(score_x, score_y)
    # event handlers
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #################################
    pygame.display.update()
# print(meteor_killed_counter)
pygame.quit()
