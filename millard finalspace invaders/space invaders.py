import pygame
from pygame import mixer
from pygame.locals import *
import random


pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()


#define fps
clock = pygame.time.Clock()
fps = 60


screen_width = 600
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Cat Terminator')


#define fonts
font30 = pygame.font.SysFont('Constantia', 30)
font40 = pygame.font.SysFont('Constantia', 40)


#load sounds
meow_fx = pygame.mixer.Sound("img/meow.wav")
meow_fx.set_volume(0.25)

rawr_fx = pygame.mixer.Sound("img/rawr.wav")
rawr_fx.set_volume(0.25)

droplet_fx = pygame.mixer.Sound("img/droplet.wav")
droplet_fx.set_volume(0.25)

shield_fx = pygame.mixer.Sound("img/shield.wav")
shield_fx.set_volume(0.25)

# define game variables
rows = 5
cols = 5
cat_cooldown = 200  # droplet cooldown in milliseconds
last_cat_drop = pygame.time.get_ticks()
countdown = 3
last_count = pygame.time.get_ticks()
game_over = 0  # 0 is no game over, 1 means player has won, -1 means player has lost

# define colours
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)



# load image
bg = pygame.image.load("img/bg.png")

def draw_bg():
    screen.blit(bg, (0, 0))


# define function for creating text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# create bottle class
class bottle(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/bottle.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_drop = pygame.time.get_ticks()


    def update(self):
        # set movement speed
        speed = 8
        # set a cooldown variable
        cooldown = 250  # milliseconds
        game_over = 0


        # get key press
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed

            
        # record current time
        time_now = pygame.time.get_ticks()
        # shoot
        if key[pygame.K_SPACE] and time_now - self.last_drop > cooldown:
            droplet_fx.play()
            droplet = droplets(self.rect.centerx, self.rect.top)
            droplet_group.add(droplet)
            self.last_drop = time_now


        # update mask
        self.mask = pygame.mask.from_surface(self.image)


        # draw health bar
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 15))
        elif self.health_remaining <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            game_over = -1
        return game_over



# create droplets class
class droplets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/droplet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, cat_group, True):
            self.kill()
            rawr_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)



class Shield(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 50))
        pygame.draw.rect(self.image, (255, 0, 200), (0, 0, self.image.get_width(), self.image.get_height()))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health = 3

    def update(self):
        if pygame.sprite.spritecollide(self, cat_droplet_group, True):
            self.health -= 1
            meow_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
            # change the shield color to signify that it has been hit
            pygame.draw.rect(self.image, (0, 0, 0), (0, 0, self.image.get_width(), self.image.get_height()))
            pygame.draw.rect(self.image, (0, 255, 60 * (4 - self.health)), (0, 0, self.image.get_width(), self.image.get_height()))

        if self.health <= 0:
            self.kill()
        if pygame.sprite.spritecollide(self, droplet_group, True):
            self.health -= 1
            meow_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
            # change the shield color to signify that it has been hit
            pygame.draw.rect(self.image, (0, 0, 0), (0, 0, self.image.get_width(), self.image.get_height()))
            pygame.draw.rect(self.image, (0, 255, 60 * (4 - self.health)), (0, 0, self.image.get_width(), self.image.get_height()))

        if self.health <= 0:
            self.kill()

# create cats class
class cats(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/cat" + str(random.randint(1, 5)) + ".png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction


# create cat droplets class
class cat_droplets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/cat_poo.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 5
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, bottle_group, False, pygame.sprite.collide_mask):
            self.kill()
            shield_fx.play()
            # reduce bottle health
            bottle.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)


# create Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"img/exp{num}.png")
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            # add the image to the list
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0


    def update(self):
        explosion_speed = 3
        # update explosion animation
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        # if the animation is complete, delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()


# create sprite groups
bottle_group = pygame.sprite.Group()
droplet_group = pygame.sprite.Group()
cat_group = pygame.sprite.Group()
cat_droplet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
shield_group = pygame.sprite.Group()

def create_shields():
    for i in range(8):
        shield = Shield(i * 100, screen_height - 200)
        shield_group.add(shield)

def create_cats():
    # generate cats
    for row in range(rows):
        for item in range(cols):
            cat = cats(100 + item * 100, 100 + row * 70)
            cat_group.add(cat)

create_cats()
create_shields()

# create player
bottle = bottle(int(screen_width / 2), screen_height - 100, 3)
bottle_group.add(bottle)

run = True
while run:
    clock.tick(fps)

    # draw background
    draw_bg()


    if countdown == 0:
        # create random cat droplets
        # record current time
        time_now = pygame.time.get_ticks()
        # shoot
        if time_now - last_cat_drop > cat_cooldown and len(cat_droplet_group) < 5 and len(cat_group) > 0:
            attacking_cat = random.choice(cat_group.sprites())
            cat_droplet = cat_droplets(attacking_cat.rect.centerx, attacking_cat.rect.bottom)
            cat_droplet_group.add(cat_droplet)
            last_cat_drop = time_now

        # check if all the cats have been killed
        if len(cat_group) == 0:
            game_over = 1

        if game_over == 0:
            # update bottle
            game_over = bottle.update()

            # update sprite groups
            droplet_group.update()
            cat_group.update()
            cat_droplet_group.update()
        else:
            if game_over == -1:
                draw_text('YOU LOSE!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))
            if game_over == 1:
                draw_text('YOU ROCK!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))

    if countdown > 0:
        draw_text('WIPE ALL THE CATS!', font40, white, int(screen_width / 2 - 200), int(screen_height / 2 + 50))
        draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100))
        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000:
            countdown -= 1
            last_count = count_timer


    # update explosion group    
    explosion_group.update()
    shield_group.update()

    # draw sprite groups
    bottle_group.draw(screen)
    droplet_group.draw(screen)
    cat_group.draw(screen)
    cat_droplet_group.draw(screen)
    shield_group.draw(screen)
    explosion_group.draw(screen)

    # event handlers
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False


    pygame.display.update()

pygame.quit()
