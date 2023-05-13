import pygame
import math
import pygame.mouse
from utils import scale_image, blit_rotate_center, blit_text_colour

pygame.font.init()

grass = scale_image(pygame.image.load("grass.png"), 2.5)
track = scale_image(pygame.image.load("track.png"), 0.9)

track_border = scale_image(pygame.image.load("track_border.png"), 0.9)
track_border_mask = pygame.mask.from_surface(track_border)

flag = scale_image(pygame.image.load("flag.png"), 0.06)
flag_position = (25, 250)
flag_mask = pygame.mask.from_surface(flag)

car1 = scale_image(pygame.image.load("car1.png"), 0.06)
car2 = scale_image(pygame.image.load("car2.png"), 0.06)

win = pygame.display.set_mode((810, 795))
pygame.display.set_caption("CAR RACING")

main_font = pygame.font.SysFont("tahoma", 60)

FPS = 60
Path = [(64, 415), (63, 446), (76, 483), (96, 512), (286, 693), (342, 729), (399, 691), (395, 542), (420, 491),(450,470),
        (509, 467), (570, 483), (618, 546), (612, 667), (623, 711), (659, 727), (704, 721), (726, 679), (728, 426),
        (722, 388), (704, 363), (704, 363), (676, 356), (640, 360), (454, 355), (412, 345), (399, 300), (415, 267),
        (441, 250), (480, 250), (550, 258), (614, 259), (666, 257), (705, 246), (728, 216), (748, 130), (731, 80),
        (678, 62), (619, 66), (551, 66), (480, 66), (413, 63), (361, 63), (302, 68), (274, 102), (264, 145), (262, 336),
        (255, 378), (223, 396), (193, 368), (190, 315), (190, 193), (190, 121), (161, 71), (109, 60), (73, 74),
        (53, 106), (46, 177), (41, 251), (49, 312)]


class gameinfo:

    def __init__(self):
        self.started = False

    def finished(self):
        playercar_finish = player_car.collide(flag_mask, *flag_position)
        if playercar_finish!=None:
                blit_text_colour(win, main_font, "YOU WON!")
                pygame.display.update()
    def start(self):
        self.started = True


class abstarctcar:

    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acc = 4

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acc, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acc, -self.max_vel / 2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel
        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi


class playercar(abstarctcar):
    IMG = car2
    START_POS = (30, 290)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acc / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()


class computercar(abstarctcar):
    IMG = car1
    START_POS = (65, 290)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel

    def draw_points(self, win):
        for point in self.path:
            pygame.draw.circle(win, (255, 0, 0), point, 5)

    def draw(self, win):
        super().draw(win)
        #self.draw_points(win)

    def bounce(self):
        self.vel = -self.vel
        self.move()

    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi / 2
        else:
            desired_radian_angle = math.atan(x_diff / y_diff)

        if target_y > self.y:
            desired_radian_angle += math.pi

        diff_in_angle = self.angle - math.degrees(desired_radian_angle)
        if diff_in_angle >= 180:
            diff_in_angle -= 360

        if diff_in_angle > 0:
            self.angle -= max(self.rotation_vel, abs(diff_in_angle))
        else:
            self.angle += max(self.rotation_vel, abs(diff_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.path):
            return
        self.calculate_angle()
        self.update_path_point()
        super().move()


def draw(win, images, player_car, computer_car):
    for img, pos in images:
        win.blit(img, pos)

    player_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()


def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False
    if keys[pygame.K_LEFT]:
        player_car.rotate(left=True)
    if keys[pygame.K_RIGHT]:
        player_car.rotate(right=True)
    if keys[pygame.K_DOWN]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_UP]:
        moved = True
        player_car.move_backward()
    if not moved:
        player_car.reduce_speed()


def handle_collision(player_car, computer_car):
    if player_car.collide(track_border_mask) != None:
        player_car.bounce()

    if computer_car.collide(track_border_mask) != None:
        computer_car.bounce()

    com_finish_poi_collide = computer_car.collide(flag_mask, *flag_position)
    if com_finish_poi_collide != None:
        blit_text_colour(win, main_font, "YOU LOST!")
        pygame.display.update()

    pl_finish_poi_collide = player_car.collide(flag_mask, *flag_position)
    if pl_finish_poi_collide != None:
        if pl_finish_poi_collide[1] == 32:
            player_car.bounce()


runs = True
clock = pygame.time.Clock()
images = [(grass, (0, 0)), (track, (0, 0)), (flag, flag_position)]
player_car = playercar(6, 2)
computer_car = computercar(2, 5, Path)
game_info = gameinfo()

while runs:
    clock.tick(FPS)

    draw(win, images, player_car, computer_car)

    while not game_info.started:
        blit_text_colour(win, main_font, "  Press any key to start game!")
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            if event.type == pygame.KEYDOWN:
                game_info.start()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            runs = False
            break

    move_player(player_car)
    computer_car.move()

    handle_collision(player_car, computer_car)
    if game_info.finished():
        blit_text_colour(win,main_font,"YOU WON!")


pygame.quit()