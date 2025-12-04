import pgzrun
import random
from pygame import Rect

WIDTH = 800
HEIGHT = 400
TITLE = "Run & Jump"
GRAVITY = 1
JUMP_STRENGTH = -18

# Globals
game_state = "menu"
score = 0
music_on = True

# Button Class
class Button:
    def __init__(self, x, y, w, h, text, color="white"):
        self.rect = Rect(x, y, w, h)
        self.text = text
        self.color = color

    def draw(self):
        screen.draw.filled_rect(self.rect, "black")
        screen.draw.rect(self.rect, self.color)
        screen.draw.text(self.text, center=self.rect.center, color=self.color, fontsize=30)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Player Class
class Player:
    def __init__(self, x, y):
        self.actor = Actor('player_idle1', (x, y))
        self.velocity_y = 0
        self.is_jumping = False
        self.anim_timer = 0

        self.run_images = ['player_run1', 'player_run2', 'player_run3', 'player_run4']
        self.idle_images = ['player_idle1', 'player_idle2']

    def update(self):
        # Gravity
        self.velocity_y += GRAVITY
        self.actor.y += self.velocity_y

        # Restrictions
        if self.actor.y >= 330:
            self.actor.y = 330
            self.velocity_y = 0
            self.is_jumping = False

        if keyboard.left:
            self.actor.x -= 5
        if keyboard.right:
            self.actor.x += 5

        # Bounds
        if self.actor.x < 20: self.actor.x = 20
        if self.actor.x > 780: self.actor.x = 780

        # Animation
        self.anim_timer += 0.15

        if self.is_jumping:
            self.actor.image = 'player_run2'
        elif keyboard.left or keyboard.right:
            frame = int(self.anim_timer) % 4
            self.actor.image = self.run_images[frame]
        else:
            frame = int(self.anim_timer) % 2
            self.actor.image = self.idle_images[frame]

    def jump(self):
        if not self.is_jumping:
            self.velocity_y = JUMP_STRENGTH
            self.is_jumping = True
            if music_on: sounds.jump.play()

    def draw(self):
        self.actor.draw()

    def get_hitbox(self):
        return self.actor._rect.inflate(-50, -50)

# Enemy Class
class Enemy:
    def __init__(self, sprite_type, x, y):
        self.actor = Actor(f'{sprite_type}_move1', (x, y))
        self.sprite_type = sprite_type
        self.speed = random.randint(4, 8)
        self.anim_timer = 0
        self.idle_images = [f'{sprite_type}_idle1', f'{sprite_type}_idle2']

    def update(self):
        self.anim_timer += 0.15
        self.actor.x -= self.speed

        # Run Animation
        frame = str(int(self.anim_timer) % 3 + 1)
        self.actor.image = f'{self.sprite_type}_move{frame}'

        # Respawn
        if self.actor.x < -50:
            self.actor.x = random.randint(850, 1200)
            self.speed = random.randint(4, 9)

    def draw(self):
        self.actor.draw()

# Coin Class
class Coin:
    def __init__(self, x, y):
        self.actor = Actor('coin1', (x, y))
        self.anim_timer = 0

    def update(self):
        self.actor.x -= 2
        self.anim_timer += 0.15
        frame = str(int(self.anim_timer) % 4 + 1)
        self.actor.image = f'coin{frame}'

        if self.actor.x < -50:
            self.respawn()

    def respawn(self):
        self.actor.x = random.randint(850, 1200)
        self.actor.y = random.randint(200, 250)

    def draw(self):
        self.actor.draw()

# Setup
btn_start = Button(300, 150, 200, 50, "START GAME", "yellow")
btn_sound = Button(300, 220, 200, 50, "SOUND: ON")
btn_exit = Button(300, 290, 200, 50, "EXIT")

player = Player(100, 330)
enemies = []
coins = []


def reset_game():
    global score, enemies, coins
    score = 0
    player.actor.pos = (100, 330)
    player.velocity_y = 0

    enemies = [
        Enemy('enemy1', 900, 330),
        Enemy('enemy2', 1300, 330)
    ]

    coins = []
    for i in range(5):
        coins.append(Coin(random.randint(300, 800), random.randint(200, 250)))

    if music_on:
        music.play('bg_music')
        music.set_volume(0.5)

# Main Logic
def update():
    global game_state, score
    if game_state == "game":
        player.update()

        for enemy in enemies:
            enemy.update()

            if player.get_hitbox().colliderect(enemy.actor._rect):
                if music_on: sounds.hit.play()
                music.stop()
                game_state = "game_over"

        for coin in coins:
            coin.update()

            if player.get_hitbox().colliderect(coin.actor._rect):
                if music_on: sounds.coin.play()
                score += 2
                coin.respawn()

        if score >= 20:
            music.stop()
            game_state = "win"


def draw():
    screen.clear()
    if game_state == "menu":
        screen.fill((20, 20, 50))
        screen.draw.text("Run & Jump", center=(400, 80), fontsize=60, color="white")
        btn_start.draw()
        btn_sound.draw()
        btn_exit.draw()

    elif game_state == "game":
        screen.fill((30, 30, 70))
        screen.draw.filled_rect(Rect((0, 350), (800, 50)), (50, 50, 50))
        screen.draw.text(f"Score: {score}/20", (20, 20), fontsize=30)
        player.draw()

        for enemy in enemies:
            enemy.draw()

        for coin in coins:
            coin.draw()

    elif game_state == "game_over":
        screen.fill("black")
        screen.draw.text("GAME OVER", center=(400, 150), fontsize=60, color="red")
        screen.draw.text(f"Final Score: {score}", center=(400, 220), fontsize=40, color="white")
        screen.draw.text("Press SPACE to Menu", center=(400, 300), fontsize=30, color="gray")

    elif game_state == "win":
        screen.fill("green")
        screen.draw.text("YOU WIN!", center=(400, 200), fontsize=80, color="white")
        screen.draw.text("Press SPACE to Menu", center=(400, 300), fontsize=30, color="white")


def on_key_down(key):
    global game_state
    if key == keys.SPACE:
        if game_state == "game":
            player.jump()
        elif game_state in ("game_over", "win"):
            game_state = "menu"


def on_mouse_down(pos):
    global game_state, music_on
    if game_state == "menu":
        if btn_start.is_clicked(pos):
            reset_game()
            game_state = "game"

        if btn_sound.is_clicked(pos):
            music_on = not music_on
            if music_on:
                btn_sound.text = "SOUND: ON"
            else:
                btn_sound.text = "SOUND: OFF"
                music.stop()

        if btn_exit.is_clicked(pos):
            quit()


pgzrun.go()