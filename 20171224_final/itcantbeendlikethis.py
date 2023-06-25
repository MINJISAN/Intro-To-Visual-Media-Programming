# KidsCanCode - Game Development with Pygame video series
# Shmup game - part 10
# Video link: https://www.youtube.com/watch?v=AdG_ITCFHDI
# Explosions
# Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3
# Art from Kenney.nl
import pygame
import random
from os import path

img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

WIDTH = 320
HEIGHT = 640
FPS = 60

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# initialize pygame and create window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shmup!")
clock = pygame.time.Clock()

font_name = pygame.font.match_font('arial')
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def play_opening_animation():
    for img in opening_images:
        screen.blit(img, (0, 0))
        pygame.display.flip()
        pygame.time.wait(500)  # 이미지 간의 딜레이 조정    

def play_ending_animation():
    while True:  # 무한 루프로 이미지를 계속 그립니다
        screen.blit(ending_image, (0, 0))
        pygame.display.flip()
        pygame.time.wait(500)  # 이미지 간의 딜레이 조정

def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

def draw_shield_bar(surf, x, y, pct, color):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, 310, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, color, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

# 상수 정의
LASER_SPEED = 5
LASER_COOLDOWN = 2000  # 레이저 발사 간격 (밀리초)

class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(img_dir, 'ackdang_lasor.png')).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = LASER_SPEED

    def update(self):
        self.rect.y += self.speedy
        # 화면에서 벗어나면 삭제
        if self.rect.bottom < 0:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (46, 66))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 130
        self.speedx = 0
        self.speedy = 0
        self.shield = 310
        self.shoot_delay = 500
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.speedx = 0
        self.speedy = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_UP]:
            self.speedy = -8
        if keystate[pygame.K_DOWN]:
            self.speedy = 8            
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top+40)
            all_sprites.add(bullet)
            bullets.add(bullet)
            shoot_sound.play()

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.bottom = random.randrange(200, 220)
        self.speedy = random.randrange(1, 3)
        self.speedx = 0  # 초기값은 가로로 이동하지 않음
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()
        self.last_speed_change = pygame.time.get_ticks()  # 속도 변경을 위한 변수 추가
        self.speed_change_interval = 1000  # 속도 변경 주기 (밀리초)


    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        # 일정 주기마다 가로/세로 이동 방향 변경
        if self.last_update - self.last_speed_change > self.speed_change_interval:
            self.last_speed_change = self.last_update
            self.speedx = random.choice([-1, 0, 1])
            self.speedy = random.randrange(1, 3)

        # 화면 밖으로 나갈 경우 재생성
        if self.rect.top > HEIGHT - 30 or self.rect.left < 30 or self.rect.right > WIDTH - 30:
            self.rect.x = random.randrange(WIDTH - self.rect.width - 1)
            self.rect.y = random.randrange(200, 300)
            self.speedy = random.randrange(1, 4)


    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

# 보스몹 클래스 생성
class Boss(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(boss1_img, (160, 134))
        self.image.set_colorkey(BLACK)        
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)  # 초기 위치 설정
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 440
        self.shield = 310

    def update(self):
        # 보스몹의 위치, 애니메이션 등을 업데이트하는 로직
        if self.shield < 150:
            self.image = pygame.transform.scale(boss2_img, (160, 134))
            self.image.set_colorkey(BLACK)
        if self.shield < 50:
            self.image = pygame.transform.scale(boss3_img, (160, 134))
            self.image.set_colorkey(BLACK)
        if self.shield <= 0:
            self.kill()



class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -5

    def update(self):
        self.rect.y += self.speedy
        # kill if it moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

# Load all game graphics
opening_images = []
for i in range(9):
    img = pygame.image.load(path.join(img_dir, f"scene_intro{i}.png")).convert()
    img = pygame.transform.scale(img, (320, 640))
    opening_images.append(img)
ending_images = pygame.image.load(path.join(img_dir, "Scene_Ending.png")).convert()
ending_images = pygame.transform.scale(img, (320, 640))
background = pygame.image.load(path.join(img_dir, "Scene_Bossphase_withoutAckdang.png")).convert()
background = pygame.transform.scale(background, (320, 640))
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir, "zooingong.png")).convert()
bullet_img = pygame.image.load(path.join(img_dir, "zooingong_projectile.png")).convert()
boss1_img = pygame.image.load(path.join(img_dir, "ackdang_phase1.png")).convert()
boss2_img = pygame.image.load(path.join(img_dir, "ackdang_phase2.png")).convert()
boss3_img = pygame.image.load(path.join(img_dir, "ackdang_phase3.png")).convert()
meteor_images = []
meteor_list = ['ackdang_projectile1.png', 'ackdang_projectile2.png', 'ackdang_projectile3.png']
for img in meteor_list:
    pnt_img = pygame.image.load(path.join(img_dir, img)).convert()
    # width = pnt_img.get_rect().width
    # height = pnt_img.get_rect().height
    # pnt_img = pygame.transform.scale(pnt_img, (int(width*0.5), int(height*0.5)))
    meteor_images.append(pnt_img.convert())


explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
for i in range(2):
    filename = 'ackdang_projectile{}_brkn.png'.format(i+1)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (150, 150))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (64, 64))
    explosion_anim['sm'].append(img_sm)
# Load all game sounds
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'shot.wav'))
shoot_sound.set_volume(0.3)
expl_sounds = []
for snd in ['explode1.wav', 'explode2.wav']:
    exp = pygame.mixer.Sound(path.join(snd_dir, snd))
    exp.set_volume(0.3)
    expl_sounds.append(exp)
pygame.mixer.music.load(path.join(snd_dir, 'HUBO2.wav'))
pygame.mixer.music.set_volume(0.4)

lasers = pygame.sprite.Group()
last_laser_time = pygame.time.get_ticks()

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
boss = Boss()
all_sprites.add(player)
all_sprites.add(boss)
spawn_mobs = True  # Mob 생성 여부를 저장하는 변수

score = 0
end_flag = 0
spawn_delay = 4000  # Mob 생성 딜레이 (4초)
last_spawn_time = pygame.time.get_ticks()  # 마지막으로 Mob이 생성된 시간을 기록

pygame.mixer.music.play(loops=-1)
# Game loop
play_opening_animation()
running = True
while running:
    # keep loop running at the right speed
    clock.tick(FPS)
    # Process input (events)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False

    now = pygame.time.get_ticks()
    if now - last_laser_time > LASER_COOLDOWN and spawn_mobs :
        last_laser_time = now
        laser_x = random.randint(50, boss.rect.centerx*2-50)
        laser = Laser(laser_x, boss.rect.bottom)
        all_sprites.add(laser)
        lasers.add(laser)

    # Update
    all_sprites.update()
    lasers.update()
    # check to see if a bullet hit a mob
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)

    # check to see if a mob hit the player
    hits = pygame.sprite.spritecollide(boss, bullets, True, pygame.sprite.collide_circle)
    for hit in hits:
        boss.shield -= 50
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if boss.shield <= 0:
            background = pygame.image.load(path.join(img_dir, "Scene_Ending.png")).convert()
            background = pygame.transform.scale(background, (320, 640))
            background_rect = background.get_rect()
            spawn_mobs = False  # 보스의 체력이 다 닳으면 Mob 생성
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path.join(snd_dir, 'dawn2.mp3'))  # 두 번째 음악 파일 로드
            pygame.mixer.music.play(loops=-1)  # 두 번째 음악 재생

    hits = pygame.sprite.spritecollide(player, lasers, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= 20  # 레이저에 맞았을 때의 피해량
        random.choice(expl_sounds).play()
        if player.shield <= 0:
            running = False

    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        if player.shield <= 0:
            running = False

    current_time = pygame.time.get_ticks()
    if spawn_mobs and current_time - last_spawn_time >= spawn_delay:
        for i in range(3):
            newmob()
        last_spawn_time = current_time

    # Draw / render
    lasers.draw(screen)
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    # draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, boss.shield, RED)
    draw_shield_bar(screen, 5, 605, player.shield, GREEN)
    # *after* drawing everything, flip the display
    pygame.display.flip()

pygame.quit()
