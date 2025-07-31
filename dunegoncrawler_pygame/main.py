import pygame
import constants
from character import Character
from weapon import Weapon
from items import Item
from world import World

pygame.init()

screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Dungeon Crawler")

#clock for maintaining frame rate
clock = pygame.time.Clock()

#define player movement variables
moving_left = False
moving_right = False
moving_up = False
moving_down = False

#define font
font = pygame.font.Font("assets/fonts/AtariClassic.ttf", 20)

#help function to scale image
def scale_img(image, scale):
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image, (w * scale, h * scale))

#load heart images
heart_empty = scale_img(pygame.image.load("assets/images/items/heart_empty.png").convert_alpha(), constants.ITEM_SCALE)
heart_half = scale_img(pygame.image.load("assets/images/items/heart_half.png").convert_alpha(), constants.ITEM_SCALE)
heart_full = scale_img(pygame.image.load("assets/images/items/heart_full.png").convert_alpha(), constants.ITEM_SCALE)

#load coin images
coin_images = []
for a in range(4):
    img = scale_img(pygame.image.load(f"assets/images/items/coin_f{a}.png").convert_alpha(), constants.ITEM_SCALE)
    coin_images.append(img)

#load potion image
red_potion = scale_img(pygame.image.load("assets/images/items/potion_red.png").convert_alpha(), constants.POTION_SCALE)

#load weapon images
bow_image = scale_img(pygame.image.load("assets/images/weapons/bow.png").convert_alpha(), constants.WEAPON_SCALE)
arrow_image = scale_img(pygame.image.load("assets/images/weapons/arrow.png").convert_alpha(), constants.WEAPON_SCALE)

#load tile map images
tile_list = []
for i in range(constants.TILE_TYPES):
    tile_image = pygame.image.load(f"assets/images/tiles/{i}.png").convert_alpha()
    tile_image = pygame.transform.scale(tile_image, (constants.TILE_SIZE, constants.TILE_SIZE))
    tile_list.append(tile_image)


#load character images
mob_animations = []
mob_types = ["elf", "imp", "skeleton", "goblin", "muddy", "tiny_zombie", "big_demon"]
for mob in mob_types:

    animation_types = ["idle", "run"]
    #load images
    animation_list = []
    for animation in animation_types:
        #reset temporary list of images:
        temp_list = []
        for i in range(4):
            img = pygame.image.load(f"assets/images/characters/{mob}/{animation}/{i}.png").convert_alpha()
            img = scale_img(img, constants.SCALE)
            temp_list.append(img)
        animation_list.append(temp_list)
    mob_animations.append(animation_list)

#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


#function for displaying game info
def draw_info():
    #Background Panel
    pygame.draw.rect(screen, constants.PANEL, (0, 0, constants.SCREEN_WIDTH, 50))
    pygame.draw.line(screen, constants.WHITE, (0, 50), (constants.SCREEN_WIDTH,50))

    #Draw Lives
    half_heart_drawn = False
    for t in range(5):
        if player.health >= ((t + 1) * 20):
            screen.blit(heart_full, (10 + t * 50, 0))
        elif (player.health % 20 > 0) and half_heart_drawn == False:
            screen.blit(heart_half, (10 + t * 50, 0))
            half_heart_drawn = True
        else:
            screen.blit(heart_empty, (10 + t * 50, 0))

    #Show Score
    draw_text(f"x{player.score}", font, constants.WHITE, constants.SCREEN_WIDTH - 97, 15)

world_data = [
[7, 7, 7, 7, 7, 7],
[7, 0, 1, 2, 3, 7],
[7, 3, 4, 5, 5, 7],
[7, 6, 6, 6, 6, 7],
[7, 0, 0, 0, 0, 7],
[7, 7, 7, 0, 7, 7],
]

world = World()
world.process_data(world_data, tile_list)






#damage text class
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        #move damage text up
        self.rect.y -= 1
        #delete the counter
        self.counter += 1
        #delete the counter after a few seconds
        if self.counter > 30:
            self.kill()



#create player properties
player = Character(100, 100, 50, mob_animations, 0)

#create enemy properties
enemy = Character(200, 300, 100, mob_animations, 1)

#create player's weapon
bow = Weapon(bow_image, arrow_image)

#create empty enemy list
enemy_list = [enemy]

#create sprite groups
damage_text_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()
item_group =  pygame.sprite.Group()

#define item group constants


#make coin counter coin
score_coin = Item(constants.SCREEN_WIDTH - 115, 23, 0, coin_images)
item_group.add(score_coin)

#display potion
potion_images = [red_potion]
potion = Item(200, 200, 1, potion_images)
item_group.add(potion)

#display coin
coin = Item(400, 400, 0, coin_images)
item_group.add(coin)



#main game loop
run = True
while run:

    #control frame rate
    clock.tick(constants.FPS)

    #Background Color
    screen.fill(constants.BG)



    #player movement management
    dx = 0
    dy = 0
    if moving_right:
        dx = constants.SPEED
    if moving_left:
        dx = -constants.SPEED
    if moving_up:
        dy = -constants.SPEED
    if moving_down:
        dy = constants.SPEED

    #move the player
    player.move(dx, dy)

    #update player
    player.update()
    arrow = bow.update(player)

    #update arrows
    if arrow:
        arrow_group.add(arrow)
    for arrow in arrow_group:
        damage, damage_pos = arrow.update(enemy_list)
        if damage:
            damage_text = DamageText(damage_pos.centerx, damage_pos.centery - 30, str(damage), constants.RED)
            damage_text_group.add(damage_text)
    damage_text_group.update()

    #update enemy
    for enemy in enemy_list:
        enemy.update()
        damage_text_group.update()

    #update items
    item_group.update(player)

    #draw world
    world.draw(screen)

    #draw the player
    player.draw(screen)
    bow.draw(screen)

    #draw the arrows
    for arrow in arrow_group:
        arrow.draw(screen)

    #draw the enemies
    for enemy in enemy_list:
        enemy.draw(screen)

    #draw damage
    damage_text_group.draw(screen)

    #draw info
    draw_info()

    #draw items
    item_group.draw(screen)

    #draw coin counter
    score_coin.draw(screen)



    #event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        #take keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                moving_left = True
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                moving_right = True
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                moving_up = True
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                moving_down = True

        #take keyboard releases
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                moving_right = False
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                moving_up = False
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                moving_down = False


    pygame.display.update()



pygame.quit()