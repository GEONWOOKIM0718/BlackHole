import math
import random
import pygame

WIDTH, HEIGHT = 900, 700
FPS = 60

BG_COLOR = (5, 5, 20)
PARTICLE_COLOR = (200, 255, 255)
BH_COLOR = (255, 80, 80)
FIELD_COLOR = (120, 180, 255)

G = 50.0
SOFTENING = 10.0
MAX_SPEED = 300


class Body:
    def __init__(self, x, y, vx, vy, mass, radius, color, fixed=False):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.radius = radius
        self.color = color
        self.fixed = fixed
        self.fx = 0.0
        self.fy = 0.0

    def add_force_from(self, other):
        if self is other:
            return
        dx = other.x - self.x
        dy = other.y - self.y
        dist2 = dx * dx + dy * dy + SOFTENING
        dist = math.sqrt(dist2)

        a = G * other.mass / dist2
        self.fx += a * dx / dist
        self.fy += a * dy / dist

    def integrate(self, dt):
        if not self.fixed:
            self.vx += self.fx * dt
            self.vy += self.fy * dt

            speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
            if speed > MAX_SPEED:
                s = MAX_SPEED / speed
                self.vx *= s
                self.vy *= s

            self.x += self.vx * dt
            self.y += self.vy * dt

        self.fx = 0.0
        self.fy = 0.0

        if self.x < 0: self.x += WIDTH
        if self.x > WIDTH: self.x -= WIDTH
        if self.y < 0: self.y += HEIGHT
        if self.y > HEIGHT: self.y -= HEIGHT

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)


def create_world():
    bodies = []

    bodies.append(Body(WIDTH*0.4, HEIGHT*0.5, 0,0, 9000, 35, BH_COLOR, fixed=True))
    bodies.append(Body(WIDTH*0.7, HEIGHT*0.3, 0,0, 8000, 30, BH_COLOR, fixed=True))

    for _ in range(40):
        x = random.uniform(0, WIDTH)
        y = random.uniform(0, HEIGHT)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(5, 20)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed

        mass = random.uniform(5, 15)
        radius = int(3 + mass / 6)
        bodies.append(Body(x, y, vx, vy, mass, radius, PARTICLE_COLOR))

    return bodies


def draw_vector_field(surface, bodies, spacing=35):
    for gx in range(0, WIDTH, spacing):
        for gy in range(0, HEIGHT, spacing):

            fx = 0.0
            fy = 0.0

            for b in bodies:
                dx = b.x - gx
                dy = b.y - gy
                dist2 = dx * dx + dy * dy + SOFTENING
                dist = math.sqrt(dist2)
                a = G * b.mass / dist2
                fx += a * dx / dist
                fy += a * dy / dist

            mag = math.sqrt(fx*fx + fy*fy)
            if mag > 0:
                scale = 0.5 / mag
                vx = fx * scale
                vy = fy * scale

                pygame.draw.line(surface, FIELD_COLOR,
                                 (gx, gy),
                                 (gx + vx * spacing * 1.5,
                                  gy + vy * spacing * 1.5), 1)


def handle_absorption(bodies):
    to_remove = set()

    for i, b in enumerate(bodies):
        if b.fixed:
            continue

        for bh in bodies:
            if not bh.fixed:
                continue

            dx = b.x - bh.x
            dy = b.y - bh.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < bh.radius:
                # 질량 증가
                bh.mass += b.mass

                # 블랙홀 크기 증가 
                bh.radius = int(max(20, 8 + math.sqrt(bh.mass) * 0.5))

                to_remove.add(i)
                break

    if to_remove:
        bodies[:] = [b for idx, b in enumerate(bodies) if idx not in to_remove]


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Gravity with Natural Black Hole Growth")
    clock = pygame.time.Clock()

    bodies = create_world()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(5, 20)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            bodies.append(Body(mx, my, vx, vy, 10, 4, (150, 220, 255)))

        for b in bodies:
            for o in bodies:
                b.add_force_from(o)

        for b in bodies:
            b.integrate(dt)

        # 블랙홀 성장
        handle_absorption(bodies)

        screen.fill(BG_COLOR)
        draw_vector_field(screen, bodies)

        for b in bodies:
            b.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()