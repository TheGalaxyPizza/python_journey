import pygame
import constants
from character import Character
from weapon import Weapon

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

#load weapon images
bow_image = scale_img(pygame.image.load("assets/images/weapons/bow.png").convert_alpha(), constants.WEAPON_SCALE)
arrow_image = scale_img(pygame.image.load("assets/images/weapons/arrow.png").convert_alpha(), constants.WEAPON_SCALE)

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



#create player
player = Character(100, 100, 100, mob_animations, 0)

#create enemy
enemy = Character(200, 300, 100, mob_animations, 1)

#create player's weapon
bow = Weapon(bow_image, arrow_image)

#create empty enemy list
enemy_list = [enemy]

#create sprite groups
damage_text_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()



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

    print(enemy.health)

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