import pygame
import constants
from character import Character

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

#help function to scale image
def scale_img(image, scale):
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image, (w * scale, h * scale))




#show player (image)
player_image = pygame.image.load("assets/images/characters/elf/idle/0.png").convert_alpha()
player_image = scale_img(player_image, constants.SCALE)

#create player
player = Character(100, 100, player_image)

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

    #draw the player
    player.draw(screen)

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