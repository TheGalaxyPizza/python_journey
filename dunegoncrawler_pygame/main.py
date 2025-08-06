import pygame
import constants
import csv
from pygame import mixer
from weapon import Weapon
from items import Item
from world import World
from button import Button

mixer.init()
pygame.init()


screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Dungeon Crawler")

#clock for maintaining frame rate
clock = pygame.time.Clock()

#define game variables
level = 1
start_game = False
pause_game = False
start_intro = False
screen_scroll = [0, 0]

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

#load music and sounds
pygame.mixer.music.load("Assets/Audio/game_music.wav")
pygame.mixer.music.set_volume(1)
pygame.mixer.music.play(-1, 0.0, 5000)
pause_music = pygame.mixer.Sound("Assets/Audio/pause_music.mp3")
pygame.mixer.music.set_volume(0.3)
shot_fx = pygame.mixer.Sound("assets/audio/arrow_shot.mp3")
shot_fx.set_volume(0.5)
hit_fx = pygame.mixer.Sound("assets/audio/arrow_hit.wav")
hit_fx.set_volume(0.5)
coin_fx = pygame.mixer.Sound("assets/audio/coin.wav")
coin_fx.set_volume(0.5)
heal_fx = pygame.mixer.Sound("assets/audio/heal.wav")
heal_fx.set_volume(0.5)


#load button images
restart_img = scale_img(pygame.image.load("assets/images/buttons/button_restart.png").convert_alpha(), constants.BUTTON_SCALE)
start_img = scale_img(pygame.image.load("assets/images/buttons/button_start.png").convert_alpha(), constants.BUTTON_SCALE)
resume_img = scale_img(pygame.image.load("assets/images/buttons/button_resume.png").convert_alpha(), constants.BUTTON_SCALE)
exit_img = scale_img(pygame.image.load("assets/images/buttons/button_exit.png").convert_alpha(), constants.BUTTON_SCALE)

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

item_images = [coin_images, red_potion]

#load weapon images
bow_image = scale_img(pygame.image.load("assets/images/weapons/bow.png").convert_alpha(), constants.WEAPON_SCALE)
arrow_image = scale_img(pygame.image.load("assets/images/weapons/arrow.png").convert_alpha(), constants.WEAPON_SCALE)
fireball_image = scale_img(pygame.image.load("assets/images/weapons/fireball.png").convert_alpha(), constants.FIREBALL_SCALE)

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

    #level
    draw_text("LEVEL:" + str(level), font, constants.WHITE, constants.SCREEN_WIDTH / 2, 15)

    #Show Score
    draw_text(f"x{player.score}", font, constants.WHITE, constants.SCREEN_WIDTH - 97, 15)

#function to reset level
def reset_level():
    damage_text_group.empty()
    arrow_group.empty()
    item_group.empty()
    fireball_group.empty()

    #create empty tile list
    data = []
    for r in range(constants.ROWS):
        r = [-1] * constants.COLS
        data.append(r)

    return data

#damage text class
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos, damage, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x_pos, y_pos)
        self.counter = 0

    def update(self):
        #reposition based on screen scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]
        #move damage text up
        self.rect.y -= 1
        #delete the counter
        self.counter += 1
        #delete the counter after a few seconds
        if self.counter > 30:
            self.kill()

#screen fade class
class ScreenFade:
    def __init__(self, direction, color, speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:
            pygame.draw.rect(screen, self.color, (0 - self.fade_counter, 0, constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (constants.SCREEN_WIDTH // 2 + self.fade_counter, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color,(0, 0 - self.fade_counter, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT//2))
            pygame.draw.rect(screen, self.color,(0, constants.SCREEN_HEIGHT //2 + self.fade_counter, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))

        elif self.direction == 2:
            pygame.draw.rect(screen, self.color, (0, 0, constants.SCREEN_WIDTH, 0 + self.fade_counter))


        if self.fade_counter >= constants.SCREEN_WIDTH:
            fade_complete = True

        return fade_complete

#create empty tile list
world_data = []
for row in range(constants.ROWS):
    r = [-1] * constants.COLS
    world_data.append(r)

#load in level data and create world
with open(f"levels/level{level}_data.csv", newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter = ",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
world.process_data(world_data, tile_list, item_images, mob_animations)


#create player properties
player = world.player

#create player's weapon
bow = Weapon(bow_image, arrow_image)

#extract enemies from world data
enemy_list = world.character_list

#create sprite groups
damage_text_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()
item_group =  pygame.sprite.Group()
fireball_group = pygame.sprite.Group()


#make coin counter coin
score_coin = Item(constants.SCREEN_WIDTH - 111, 23, 0, coin_images, True)
item_group.add(score_coin)

#add the items from level data
for item in world.item_list:
    item_group.add(item)

#create screen fades
intro_fade = ScreenFade(1, constants.BLACK, 4)
death_fade = ScreenFade(2, constants.PINK, 4)

#create button
restart_button = Button(constants.SCREEN_WIDTH // 2 - 175, constants.SCREEN_HEIGHT // 2 - 50, restart_img)
start_button = Button(constants.SCREEN_WIDTH // 2 - 145, constants.SCREEN_HEIGHT // 2 - 150, start_img)
exit_button = Button(constants.SCREEN_WIDTH // 2 - 110, constants.SCREEN_HEIGHT // 2 + 50, exit_img)
resume_button = Button(constants.SCREEN_WIDTH // 2 - 175, constants.SCREEN_HEIGHT // 2 - 150, resume_img)

#main game loop
run = True
while run:

    #control frame rate
    clock.tick(constants.FPS)

    if not start_game:
        screen.fill(constants.MENU_BG)
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
                run = False
    else:
        if pause_game:
            screen.fill(constants.MENU_BG)
            if resume_button.draw(screen):
                pause_game = False
                pygame.mixer.music.unpause()
                pause_music.stop()

            if exit_button.draw(screen):
                run = False
        else:
            screen.fill(constants.BG)


            if player.alive:
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
                screen_scroll, level_complete = player.move(dx, dy, world.obstacle_tiles, world.exit_tile)


                #update world
                world.update(screen_scroll)

                #update player
                player.update()
                arrow = bow.update(player)

                #update arrows
                if arrow:
                    arrow_group.add(arrow)
                    shot_fx.play()
                for arrow in arrow_group:
                    damage, damage_pos = arrow.update(screen_scroll, enemy_list, world.obstacle_tiles)
                    if damage:
                        damage_text = DamageText(damage_pos.centerx, damage_pos.centery - 30, str(damage), constants.RED)
                        damage_text_group.add(damage_text)
                        hit_fx.play()
                damage_text_group.update()

                #update enemy
                for enemy in enemy_list:
                    fireball = enemy.ai(player, world.obstacle_tiles, screen_scroll, fireball_image)
                    if fireball:
                        fireball_group.add(fireball)

                    if enemy.alive:
                        enemy.update()

                    damage_text_group.update()

                    #update fireballs
                    fireball_group.update(screen_scroll, player)


                #update items
                item_group.update(screen_scroll, player, coin_fx, heal_fx)

            #draw stuff
            world.draw(screen)
            player.draw(screen)
            bow.draw(screen)
            #draw the arrows
            for arrow in arrow_group:
                arrow.draw(screen)

            #draw fireballs
            for fireball in fireball_group:
                fireball.draw(screen)

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


            #check level complete
            if level_complete:
                start_intro = True
                level += 1
                world_data = reset_level()
                #load in level data and create world
                with open(f"levels/level{level}_data.csv", newline="") as csvfile:
                    reader = csv.reader(csvfile, delimiter = ",")
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                world.process_data(world_data, tile_list, item_images, mob_animations)
                temp_hp = player.health
                temp_score = player.score

                player = world.player
                player.health = temp_hp
                player.score = temp_score
                enemy_list = world.character_list
                score_coin = Item(constants.SCREEN_WIDTH - 111, 23, 0, coin_images, True)
                item_group.add(score_coin)
                #add the items from level data
                for item in world.item_list:
                    item_group.add(item)

            #show intro
            if start_intro:
                if intro_fade.fade():
                    start_intro = False
                    intro_fade.fade_counter = 0

            #show death screen
            if not player.alive:
                if death_fade.fade():
                    if restart_button.draw(screen):
                        death_fade.fade_counter = 0
                        start_intro = True
                        world_data = reset_level()
                        level = 1
                        #load in level data and create world
                        with open(f"levels/level{level}_data.csv", newline="") as csvfile:
                            reader = csv.reader(csvfile, delimiter = ",")
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)
                        world = World()
                        world.process_data(world_data, tile_list, item_images, mob_animations)
                        temp_score = player.score
                        player = world.player
                        player.score = temp_score
                        enemy_list = world.character_list
                        score_coin = Item(constants.SCREEN_WIDTH - 111, 23, 0, coin_images, True)
                        item_group.add(score_coin)
                        #add the items from level data
                        for item in world.item_list:
                            item_group.add(item)




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

            if event.key == pygame.K_ESCAPE:
                pause_game = True
                pygame.mixer.music.pause()
                pause_music.play(-1)
                pause_music.set_volume(0.2)

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