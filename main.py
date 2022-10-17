import pygame
import math
import time
from operator import attrgetter
# import astropy
# from astropy import units as u
pygame.init()
# TODO: Use units from astropy
# TODO: True_scale does not affect orbit radius, just object size
WIDTH, HEIGHT = 1200, 1200
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planet Simulator")
FPS = 60

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)

FONT = pygame.font.SysFont("comicsans", 16)


class Planet:
    AU = 1.49597e11
    G = 6.67408e-11
    SCALE = 200 / AU    # 200px/1AU
    TIME_STEP = 3600 * 24

    def __init__(self, x, y, radius, color, mass, TRUE_SIZE, true_scale_radius=0):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass
        self.TRUE_SIZE = TRUE_SIZE
        self.true_scale_radius = true_scale_radius

        self.orbit = []
        self.sun = False
        self.distance_to_sun = 0

        self.x_vel = 0
        self.y_vel = 0

    def draw(self, win, true_scale):
        x = self.x * self.SCALE + WIDTH / 2
        y = self.y * self.SCALE + HEIGHT / 2

        if len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                x, y = point
                x = x * self.SCALE + WIDTH / 2
                y = y * self.SCALE + HEIGHT / 2
                updated_points.append((x, y))

            pygame.draw.lines(win, self.color, False, updated_points)

        # current_rad = (self.true_scale_radius if true_scale else self.radius)
        current_rad = (self.true_scale_radius, self.radius)[true_scale]
        pygame.draw.circle(win, self.color, (x, y), current_rad)

        if not self.sun:
            distance_text = FONT.render(f"{round(self.distance_to_sun / self.AU, 3)}AU", True, WHITE)
            win.blit(distance_text, (x - distance_text.get_width()/2, y - distance_text.get_height()/2))

    def attraction(self, other):
        other_x, other_y = other.x, other.y
        distance_x = other.x - self.x
        distance_y = other.y - self.y
        distance = math.sqrt(distance_x**2 + distance_y**2)

        if other.sun:
            self.distance_to_sun = distance

        force = self.G * self.mass * other.mass / distance**2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    def update_position(self, planets):
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue

            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy
        # Add acceleration * TIME_STEP to total x_velocity
        self.x_vel += total_fx / self.mass * self.TIME_STEP
        self.y_vel += total_fy / self.mass * self.TIME_STEP

        self.x += self.x_vel * self.TIME_STEP
        self.y += self.y_vel * self.TIME_STEP
        if len(self.orbit) > 25:
            del self.orbit[0]
        self.orbit.append((self.x, self.y))


def main():
    true_scale = False
    run = True
    # initialize clock to limit framerate
    clock = pygame.time.Clock()

    sun = Planet(0, 0, 30, YELLOW, 1.98892 * 10**30, 695700)
    sun.sun = True

    mercury = Planet(0.387 * Planet.AU, 0, 8, DARK_GREY, 3.30 * 10 ** 23, 2440)
    mercury.y_vel = -57.4 * 1000

    venus = Planet(0.723 * Planet.AU, 0, 14, WHITE, 4.8685 * 10 ** 24, 6052)
    venus.y_vel = -35.02 * 1000

    earth = Planet(-1 * Planet.AU, 0, 16, BLUE, 5.9742 * 10**24, 6371)
    earth.y_vel = 29.783 * 1000

    mars = Planet(-1.524 * Planet.AU, 0, 12, RED, 6.39 * 10 ** 23, 3390)
    mars.y_vel = 24.077 * 1000

    planets = [sun, earth, mars, mercury, venus]

    maxTRUE_SIZE = max(planets, key=attrgetter('TRUE_SIZE')).TRUE_SIZE
    print(maxTRUE_SIZE)
    for planet in planets:
        planet.true_scale_radius = planet.TRUE_SIZE / maxTRUE_SIZE
    while run:
        # game speed changes based on FPS at the moment
        clock.tick(FPS)
        WIN.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    true_scale = not true_scale

        for planet in planets:
            planet.update_position(planets)
            planet.draw(WIN, true_scale)

        pygame.display.update()

    pygame.quit()


main()
