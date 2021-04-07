import random
import numpy as np
import pygame
from pygame import *
import sys
import os

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
GREEN = (50, 150, 50)
PURPLE = (130, 0, 130)
GREY = (230, 230, 230)
HORRIBLE_YELLOW = (190, 175, 50)
RED = (240, 0, 0)
BACKGROUND = GREY
CHOCOLATE_BROWN = (210, 105, 30)


class Dot(pygame.sprite.Sprite):
    def __init__(
            self,
            x,
            y,
            width,
            height,
            color=BLACK,
            radius=5,
            velocity=[0, 0],
            randomize=False,
    ):
        super().__init__()
        self.image = pygame.Surface([radius * 2, radius * 2])
        self.image.fill(BACKGROUND)
        pygame.draw.circle(
            self.image, color, (radius, radius), radius
        )

        self.rect = self.image.get_rect()
        self.pos = np.array([x, y], dtype=np.float64)
        self.vel = np.asarray(velocity, dtype=np.float64)

        self.killswitch_on = False
        self.recovered = False
        self.randomize = randomize

        self.WIDTH = width
        self.HEIGHT = height

    def update(self):

        self.pos += self.vel

        x, y = self.pos

        # Periodic boundary conditions
        if x < 0:
            self.pos[0] = self.WIDTH
            x = self.WIDTH
        if x > self.WIDTH:
            self.pos[0] = 0
            x = 0
        if y < 0:
            self.pos[1] = self.HEIGHT
            y = self.HEIGHT
        if y > self.HEIGHT:
            self.pos[1] = 0
            y = 0

        self.rect.x = x
        self.rect.y = y

        vel_norm = np.linalg.norm(self.vel)
        if vel_norm > 3:
            self.vel /= vel_norm

        if self.randomize:
            self.vel += np.random.rand(2) * 2 - 1

        if self.killswitch_on:
            self.cycles_to_fate -= 1

            if self.cycles_to_fate <= 0:
                self.killswitch_on = False
                some_number = np.random.rand()
                if self.mortality_rate > some_number:
                    self.kill()
                else:
                    self.recovered = True

    def respawn(self, color, radius=5):
        return Dot(
            self.rect.x,
            self.rect.y,
            self.WIDTH,
            self.HEIGHT,
            color=color,
            velocity = self.vel,
        )

    def killswitch(self, cycles_to_fate=20, mortality_rate=0.2):
        self.killswitch_on = True
        self.cycles_to_fate = cycles_to_fate
        self.mortality_rate = mortality_rate


class Simulation:
    def __init__(self, width=600, height=480):
        pygame.init()
        self.WIDTH = width
        self.HEIGHT = height

        self.susceptible_container = pygame.sprite.Group()
        self.infected_container = pygame.sprite.Group()
        self.recovered_container = pygame.sprite.Group()
        self.all_container = pygame.sprite.Group()
        self.clock = pygame.time.Clock()
        self.n_susceptible = 20
        self.n_infected = 1
        self.n_quarantined = 0
        self.T = 10000
        self.cycles_to_fate = 20
        self.mortality_rate = 0.2
        self.transmission_rate = 0.6
        self.screen = pygame.display.set_mode([self.WIDTH, self.HEIGHT])
        self.font_name = pygame.font.match_font("Arial")
        self.base_font = pygame.font.Font(None, 32)

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def intro_screen(self):
        self.screen.fill(BACKGROUND)
        self.draw_text("Virus Simulator by Chirag", 48, GREEN, self.WIDTH // 2, 40)
        pygame.draw.rect(self.screen, BLACK, (800, 900, 200, 52), 1)
        pygame.draw.rect(self.screen, WHITE, (802, 902, 196, 48), 0)
        self.draw_text("PRESS SPACE TO START", 18, BLACK, 900, 915)

        self.draw_text("About my Project", 32, BLACK, self.WIDTH // 2, 300)
        self.draw_text("My project is my first attempt at creating a fairly complex program after recently learning "
                       "the Programming Language; Python.", 32, BLACK, 900, 400)
        self.draw_text("In order to keep my product relevant to todays time, I thought of creating a Virus Simulation "
                       "which allows you to model your own virus.", 32, BLACK, 900, 500)
        self.draw_text("Letting you model your virus can let you understand how different parameters effect a virus "
                       "scenario.", 32, BLACK, 900, 600)
        self.draw_text("With that being said, Have Fun!", 32, BLACK, 900, 700)


        pygame.display.flip()
        self.wait_for_button()

    def text_input_1(self):
        self.screen.fill(BACKGROUND)
        self.draw_text("Enter your Susceptible Population: ", 48, GREEN, self.WIDTH // 2, 40)
        pygame.draw.rect(self.screen, BLACK, (800, 900, 200, 52), 1)
        pygame.draw.rect(self.screen, WHITE, (802, 902, 196, 48), 0)
        self.draw_text("PRESS SPACE TO START", 18, BLACK, 900, 915)
        self.draw_text("Enter the Initial Susceptible Population: ", 40, BLACK, 325, 300)
        self.draw_text("The susceptible population is the population which is susceptible to the virus at the start "
                       "of the simulation. Enter an integer less than 500", 32, BLACK, 833, 350)
        pygame.draw.rect(self.screen, BLACK, ((self.WIDTH // 2) - 2, self.HEIGHT // 2, 150, 52), 1)
        pygame.draw.rect(self.screen, WHITE, ((self.WIDTH // 2), (self.HEIGHT // 2) + 2, 146, 48), 0)
        user_text = ""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == K_SPACE:
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.type == pygame.K_BACKSPACE:
                        user_text = user_text[0:-1]
                    else:
                        user_text += event.unicode

            text_input_1_surface = self.base_font.render(user_text, True, BLACK)
            self.screen.blit(text_input_1_surface, (self.WIDTH // 2, self.HEIGHT // 2 + 10))
            pygame.display.flip()
        sus_input = int(user_text)
        return sus_input

    def text_input_2(self):
        self.screen.fill(BACKGROUND)
        self.draw_text("Enter your Infected Population: ", 48, GREEN, self.WIDTH // 2, 40)
        pygame.draw.rect(self.screen, BLACK, (800, 900, 200, 52), 1)
        pygame.draw.rect(self.screen, WHITE, (802, 902, 196, 48), 0)
        self.draw_text("PRESS SPACE TO START", 18, BLACK, 900, 915)
        self.draw_text("Enter the Initial Infected Population: ", 40, BLACK, 325, 300)
        self.draw_text("The infected population is the population which is infected to the virus at the start "
                       "of the simulation. Enter an integer less than 500", 32, BLACK, 833, 350)
        pygame.draw.rect(self.screen, BLACK, (self.WIDTH // 2, self.HEIGHT // 2, 150, 52), 1)
        pygame.draw.rect(self.screen, WHITE, ((self.WIDTH // 2) + 2, (self.HEIGHT // 2) + 2, 146, 48), 0)
        user_text = ""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == K_SPACE:
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.type == pygame.K_BACKSPACE:
                        user_text = user_text[0:-1]
                    else:
                        user_text += event.unicode

            text_input_1_surface = self.base_font.render(user_text, True, BLACK)
            self.screen.blit(text_input_1_surface, (self.WIDTH // 2, self.HEIGHT // 2 + 10))
            pygame.display.flip()
        inf_input = int(user_text)
        return inf_input

    def text_input_3(self):
        self.screen.fill(BACKGROUND)
        self.draw_text("Enter your Quarantined Population: ", 48, GREEN, self.WIDTH // 2, 40)
        pygame.draw.rect(self.screen, BLACK, (800, 900, 200, 52), 1)
        pygame.draw.rect(self.screen, WHITE, (802, 902, 196, 48), 0)
        self.draw_text("PRESS SPACE TO START", 18, BLACK, 900, 915)
        self.draw_text("Enter the Initial Quarantined Population: ", 40, BLACK, 325, 300)
        self.draw_text("The Quarantined population is the population which is Quarantined, which means they are not "
                       "moving of the simulation. Enter an integer less than 500", 32, BLACK, 833, 350)
        pygame.draw.rect(self.screen, BLACK, (self.WIDTH // 2, self.HEIGHT // 2, 150, 52), 1)
        pygame.draw.rect(self.screen, WHITE, ((self.WIDTH // 2) + 2, (self.HEIGHT // 2) + 2, 146, 48), 0)
        user_text = ""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == K_SPACE:
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.type == pygame.K_BACKSPACE:
                        user_text = user_text[0:-1]
                    else:
                        user_text += event.unicode

            text_input_1_surface = self.base_font.render(user_text, True, BLACK)
            self.screen.blit(text_input_1_surface, (self.WIDTH // 2, self.HEIGHT // 2 + 10))
            pygame.display.flip()
        qua_input = int(user_text)
        return qua_input

    def text_input_4(self):
        self.screen.fill(BACKGROUND)
        self.draw_text("Enter your Recovery Time: ", 48, GREEN, self.WIDTH // 2, 40)
        pygame.draw.rect(self.screen, BLACK, (800, 900, 200, 52), 1)
        pygame.draw.rect(self.screen, WHITE, (802, 902, 196, 48), 0)
        self.draw_text("PRESS SPACE TO START", 18, BLACK, 900, 915)
        self.draw_text("Enter the Recovery Time: ", 40, BLACK, 325, 300)
        self.draw_text("The Recovery time is time that it takes for an Infected person to recover from the virus, "
                       "Enter the recovery time in days.", 32, BLACK, 833, 350)
        pygame.draw.rect(self.screen, BLACK, (self.WIDTH // 2, self.HEIGHT // 2, 150, 52), 1)
        pygame.draw.rect(self.screen, WHITE, ((self.WIDTH // 2) + 2, (self.HEIGHT // 2) + 2, 146, 48), 0)
        user_text = ""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == K_SPACE:
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.type == pygame.K_BACKSPACE:
                        user_text = user_text[0:-1]
                    else:
                        user_text += event.unicode

            text_input_1_surface = self.base_font.render(user_text, True, BLACK)
            self.screen.blit(text_input_1_surface, (self.WIDTH // 2, self.HEIGHT // 2 + 10))
            pygame.display.flip()
        rec_input = int(user_text) * 100
        return rec_input

    def text_input_5(self):
        self.screen.fill(BACKGROUND)
        self.draw_text("Enter your Transmission Rate: ", 48, GREEN, self.WIDTH // 2, 40)
        pygame.draw.rect(self.screen, BLACK, (800, 900, 200, 52), 1)
        pygame.draw.rect(self.screen, WHITE, (802, 902, 196, 48), 0)
        self.draw_text("PRESS SPACE TO START", 18, BLACK, 900, 915)
        self.draw_text("Enter the Transmission", 40, BLACK, 325, 300)
        self.draw_text("The transmission rate is the rate at which people get infected, enter a decimal value like; "
                       "0.9. ", 32, BLACK, 833, 350)
        pygame.draw.rect(self.screen, BLACK, (self.WIDTH // 2, self.HEIGHT // 2, 150, 52), 1)
        pygame.draw.rect(self.screen, WHITE, ((self.WIDTH // 2) + 2, (self.HEIGHT // 2) + 2, 146, 48), 0)
        user_text = ""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == K_SPACE:
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.type == pygame.K_BACKSPACE:
                        user_text = user_text[0:-1]
                    else:
                        user_text += event.unicode

            text_input_1_surface = self.base_font.render(user_text, True, BLACK)
            self.screen.blit(text_input_1_surface, (self.WIDTH // 2, self.HEIGHT // 2 + 10))
            pygame.display.flip()
        tra_input = float(user_text)

    def text_input_6(self):
        self.screen.fill(BACKGROUND)
        self.draw_text("Enter your Death Rate: ", 48, GREEN, self.WIDTH // 2, 40)
        pygame.draw.rect(self.screen, BLACK, (800, 900, 200, 52), 1)
        pygame.draw.rect(self.screen, WHITE, (802, 902, 196, 48), 0)
        self.draw_text("PRESS SPACE TO START", 18, BLACK, 900, 915)
        self.draw_text("Enter the Death Rate: ", 40, BLACK, 325, 300)
        self.draw_text("The Death Rate is the rate at which the infected population dies, enter a decimal value "
                       "like; 0.02", 32, BLACK, 833, 350)
        pygame.draw.rect(self.screen, BLACK, (self.WIDTH // 2, self.HEIGHT // 2, 150, 52), 1)
        pygame.draw.rect(self.screen, WHITE, ((self.WIDTH // 2) + 2, (self.HEIGHT // 2) + 2, 146, 48), 0)
        user_text = ""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == K_SPACE:
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.type == pygame.K_BACKSPACE:
                        user_text = user_text[0:-1]
                    else:
                        user_text += event.unicode

            text_input_1_surface = self.base_font.render(user_text, True, BLACK)
            self.screen.blit(text_input_1_surface, (self.WIDTH // 2, self.HEIGHT // 2 + 10))
            pygame.display.flip()
        dea_input = float(user_text)

    def show_final_start_screen(self):
        self.screen.fill(BACKGROUND)
        self.draw_text("Virus Simulator by Chirag", 48, GREEN, self.WIDTH // 2, 40)
        self.draw_text("Your Virus Parameters:", 40, BLACK, 250, 200)
        self.draw_text("The Initial Susceptible Population: ", 40, BLACK, 325, 300)
        self.draw_text("The susceptible population is the population which is susceptible to the virus at the start "
                       "of the simulation. Enter an integer less than 500", 12, BLACK, 325, 350)
        self.draw_text("The Initial Infected Population: ", 40, BLACK, 290, 400)
        self.draw_text("The infected population is the population which is infected with the virus at the start of "
                       "the simulation. Enter an integer less than 500.", 12, BLACK, 325, 450)
        self.draw_text("The quarantined population: ", 40, BLACK, 280, 500)
        self.draw_text("The Quarantined Population is population which is not moving in the simulation, "
                       "which decreases the risk them getting infected.", 12, BLACK, 310, 550)
        self.draw_text("The recovery time: ", 40, BLACK, 210, 600)
        self.draw_text("The time is time that it takes for an Infected person to recover from the virus, "
                       "Enter the recovery time in days.", 12, BLACK, 290, 650)
        self.draw_text("The Mortality Rate: ", 40, BLACK, 210, 700)
        self.draw_text("The Mortality Rate is the rate at which the infected population dies, enter a decimal value "
                       "like; 0.02", 12, BLACK, 240, 750)
        self.draw_text("The Transmission Rate: ", 40, BLACK, 240, 800)
        self.draw_text("The transmission rate is the rate at which people get infected, enter a decimal value like; "
                       "0.9. ", 12, BLACK, 220, 850)

        pygame.draw.rect(self.screen, BLACK, (900, 900, 184, 52), 1)
        pygame.draw.rect(self.screen, WHITE, (902, 902, 180, 48), 0)
        self.draw_text("PRESS SPACE TO START", 18, BLACK, 900 + 92, 915)

        pygame.display.flip()
        self.wait_for_button()

    def wait_for_button(self):
        waiting = True
        while waiting:
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == K_SPACE:
                    waiting = False

    def start(self, randomize=False):
        self.N = (self.n_susceptible + self.n_infected + self.n_quarantined)
        pygame.init()
        screen = pygame.display.set_mode([self.WIDTH, self.HEIGHT])

        for i in range(self.n_susceptible):
            x = np.random.randint(0, self.WIDTH + 1)
            y = np.random.randint(0, self.HEIGHT + 1)
            vel = np.random.rand(2) * 2 - 1
            guy = Dot(
                x,
                y,
                self.WIDTH,
                self.HEIGHT,
                color=BLUE,
                velocity=vel,
                randomize=randomize,
            )
            self.susceptible_container.add(guy)
            self.all_container.add(guy)

        for i in range(self.n_quarantined):
            x = np.random.randint(0, self.WIDTH + 1)
            y = np.random.randint(0, self.HEIGHT + 1)
            vel = [0, 0]
            guy = Dot(
                x,
                y,
                self.WIDTH,
                self.HEIGHT,
                color=BLUE,
                velocity=vel,
                randomize=False,
            )
            self.susceptible_container.add(guy)
            self.all_container.add(guy)

        for i in range(self.n_infected):
            x = np.random.randint(0, self.WIDTH + 1)
            y = np.random.randint(0, self.HEIGHT + 1)
            vel = np.random.rand(2) * 2 - 1
            guy = Dot(
                x,
                y,
                self.WIDTH,
                self.HEIGHT,
                color=GREEN,
                velocity=vel,
                randomize=randomize,
            )
            self.infected_container.add(guy)
            self.all_container.add(guy)

        stats = pygame.Surface((self.WIDTH - (self.WIDTH // 2), self.HEIGHT // 8))
        stats.fill(WHITE)
        stats.set_alpha(230)
        stats_pos = (self.WIDTH // 40, self.HEIGHT // 40)

        num_stats = pygame.Surface(((self.WIDTH // 4) - 200, self.HEIGHT // 4))
        num_stats.fill(WHITE)
        num_stats.set_alpha(230)
        num_stats_pos = ((self.WIDTH // 40), self.HEIGHT - (self.HEIGHT // 3))

        init_stats = pygame.Surface(((self.WIDTH // 4) - 200, self.HEIGHT // 4))
        init_stats.fill(WHITE)
        init_stats.set_alpha(230)
        init_stats_pos = (1600, self.HEIGHT - (self.HEIGHT // 3))

        clock = pygame.time.Clock()

        for i in range(self.T):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            self.all_container.update()

            screen.fill(BACKGROUND)

            # Update stats
            stats_height = stats.get_height()
            stats_width = stats.get_width()
            n_inf_now = len(self.infected_container)
            n_pop_now = len(self.all_container)
            n_rec_now = len(self.recovered_container)
            t = int((i / self.T) * stats_width)
            y_infect = int(
                stats_height - (n_inf_now / n_pop_now) * stats_height
            )
            y_dead = int(
                ((self.N - n_pop_now) / self.N) * stats_height
            )
            y_recovered = int((n_rec_now / n_pop_now) * stats_height)
            stats_graph = pygame.PixelArray(stats)
            stats_graph[t, y_infect:] = pygame.Color(*RED)
            stats_graph[t, :y_dead] = pygame.Color(*CHOCOLATE_BROWN)
            stats_graph[
            t, y_dead: y_dead + y_recovered
            ] = pygame.Color(*GREEN)

            total_population_string = "Total Population: " + str(n_pop_now)

            total_infected_string = "Infected Population: " + str(n_inf_now)
            total_susceptible_string = "Susceptible Population: " + str(n_pop_now - (n_inf_now + n_rec_now))

            total_recovered_string = "Recovered Population: " + str(n_rec_now)
            total_deaths_string = "Deceased Population: " + str((self.N - n_pop_now))

            pygame.font.init()
            myFont = pygame.font.SysFont('Comic Sans MS', 19)
            t_population_suf = myFont.render(total_population_string, False, (0, 0, 0))
            t_population_suf_pos = ((self.WIDTH // 40) + 5, self.HEIGHT - (self.HEIGHT // 3) + 5)

            t_infected_suf = myFont.render(total_infected_string, False, (0, 0, 0))
            t_infected_suf_pos = (self.WIDTH // 40 + 5, self.HEIGHT - (self.HEIGHT // 3) + 55)

            t_susceptible_suf = myFont.render(total_susceptible_string, False, (0, 0, 0))
            t_susceptible_suf_pos = (self.WIDTH // 40 + 5, self.HEIGHT - (self.HEIGHT // 3) + 105)

            t_recovered_suf = myFont.render(total_recovered_string, False, (0, 0, 0))
            t_recovered_suf_pos = (self.WIDTH // 40 + 5, self.HEIGHT - (self.HEIGHT // 3) + 155)

            t_deaths_suf = myFont.render(total_deaths_string, False, (0, 0, 0))
            t_deaths_suf_pos = (self.WIDTH // 40 + 5, self.HEIGHT - (self.HEIGHT // 3) + 205)

            # New infections?
            collision_group = pygame.sprite.groupcollide(
                self.susceptible_container,
                self.infected_container,
                True,
                False,
            )

            for guy in collision_group:
                random_number = np.random.rand()
                if self.transmission_rate > random_number:
                    new_guy = guy.respawn(RED)
                    new_guy.vel *= -1
                    new_guy.killswitch(
                        self.cycles_to_fate, self.mortality_rate)
                    self.infected_container.add(new_guy)
                    self.all_container.add(new_guy)

                else:
                    new_guy = guy.respawn(BLUE)
                    new_guy.vel *= -1
                    self.susceptible_container.add(new_guy)
                    self.all_container.add(new_guy)

            # Any recoveries?
            recovered = []
            for guy in self.infected_container:
                if guy.recovered:
                    new_guy = guy.respawn(GREEN)
                    self.recovered_container.add(new_guy)
                    self.all_container.add(new_guy)
                    recovered.append(guy)

            if len(recovered) > 0:
                self.infected_container.remove(*recovered)
                self.all_container.remove(*recovered)

            self.all_container.draw(screen)

            del stats_graph
            stats.unlock()

            screen.blit(stats, stats_pos)
            # screen.blit(init_stats, init_stats_pos)
            # screen.blit(inputted_variables_suf, inputted_variables_suf_pos)
            num_stats.unlock()

            screen.blit(num_stats, num_stats_pos)
            screen.blit(t_population_suf, t_population_suf_pos)
            screen.blit(t_infected_suf, t_infected_suf_pos)
            screen.blit(t_susceptible_suf, t_susceptible_suf_pos)
            screen.blit(t_recovered_suf, t_recovered_suf_pos)
            screen.blit(t_deaths_suf, t_deaths_suf_pos)

            pygame.display.flip()

            clock.tick(30)

        pygame.quit()


covid = Simulation(1800, 1000)

covid.show_final_start_screen()
covid.n_susceptible = 500
covid.n_quarantined = 50
covid.n_infected = 10
covid.cycles_to_fate = 1200
covid.mortality_rate = 0.03
covid.transmission_rate = 0.8
covid.start(randomize=True)

