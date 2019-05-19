import pygame
from .mode import Mode
from .state import State
from data import config
from core.car.car import Car
from core.map.map import Map


class Game:
    # ----- INITIALIZATION -----
    def __init__(self, mode):
        self.mode = mode
        self.init_game_state()
        self.init_game_window()
        self.init_game_objects()

    def init_game_state(self):
        self.state = State.DRIVING
        self.active = True

    def init_game_window(self):
        pygame.init()
        self.screen = pygame.display.set_mode(config.SCREEN_SIZE)
        self.text_font = pygame.font.SysFont("Courier", 30)
        self.clock = pygame.time.Clock()

    def init_game_objects(self):
        self.car = Car(config.CAR_STARTING_X, config.CAR_STARTING_Y, config.CAR_SIZE)
        self.map = Map()


    # ----- MAIN GAME LOOP -----
    def run(self):
        while self.active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.shutdown()

            self.update_internal_game_data()
            self.update_objects()
            self.handle_input()
            self.draw()

    def shutdown(self):
        self.active = False


    # ----- INTERNAL GAME STATE -----
    def update_internal_game_data(self):
        self.delta_time = self.get_time_since_last_frame()

    def get_time_since_last_frame(self):
        return self.clock.get_time() / 1000


    # ----- OBJECT MANIPULATION -----
    def update_objects(self):
        self.car.update(self.delta_time)
        self.handle_collisions()

    def handle_collisions(self):
        if self.map.collided_wall(self.car):
            self.car.crash()
        elif self.map.entered_finish_line(self.car):
            self.car.finish()

    def add_wall_at_mouse_pos(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.map.add_wall(mouse_x, mouse_y)

    def add_finish_line_at_mouse_pos(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.map.add_finish_line(mouse_x, mouse_y)

    def reset_car(self):
        self.car = Car(config.CAR_STARTING_X, config.CAR_STARTING_Y, config.CAR_SIZE)

    def reset_map(self):
        self.map = Map()


    # ----- HANDLING INPUT -----
    def handle_input(self):
        if self.mode == Mode.USER:
            self.handle_user_input()
        elif self.mode == Mode.AI:
            self.handle_ai_input()

    def handle_user_input(self):
        self.handle_user_input_for_game_state()
        self.handle_user_input_for_map()
        self.handle_user_input_for_car()

    def handle_user_input_for_game_state(self):
        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_r]:
            self.reset_car()
        elif pressed[pygame.K_p]:
            self.reset_map()

    def handle_user_input_for_map(self):
        # left click
        if pygame.mouse.get_pressed()[0]:
            self.add_wall_at_mouse_pos()

        # middle mouse btn
        if pygame.mouse.get_pressed()[1]:
            self.add_finish_line_at_mouse_pos()

    def handle_user_input_for_car(self):
        if self.car.has_crashed():
            return

        pressed = pygame.key.get_pressed()
        dt = self.delta_time

        if pressed[pygame.K_w]:
            self.car.accelerate(dt)
        elif pressed[pygame.K_s]:
            self.car.decelerate(dt)
        else:
            self.car.no_acceleration()

        if pressed[pygame.K_d]:
            self.car.steer_right(dt)
        elif pressed[pygame.K_a]:
            self.car.steer_left(dt)
        else:
            self.car.no_steering()

        if pressed[pygame.K_SPACE]:
            self.car.brake(dt)

    def handle_ai_input(self):
        pass

    # ----- DRAWING -----
    def draw(self):
        self.draw_background()
        self.draw_map()
        self.draw_car()

        self.display_text("Car Velocity: %s" % self.car.velocity, (5, 10))
        self.display_text("Car has crashed: %s" % self.car.has_crashed(), (5, 40))
        self.display_text("Car has finished: %s" % self.car.has_finished(), (5, 70))

        self.render_ui()
        self.limit_fps(config.FPS)

    def draw_map(self):
        for wall in self.map.get_walls():
            pygame.draw.rect(self.screen, config.WHITE, wall.get_rect())

        for finish_line in self.map.get_finish_lines():
            pygame.draw.rect(self.screen, config.BLUE, finish_line.get_rect())

    def draw_car(self):
        self.screen.blit(self.car.get_image(), self.car.get_rect())

    def draw_background(self):
        self.screen.fill(config.GREY)

    def display_text(self, text, position):
        text = self.text_font.render(text, True, config.WHITE)
        self.screen.blit(text, position)

    @staticmethod
    def render_ui():
        pygame.display.flip()

    def limit_fps(self, fps):
        self.clock.tick(fps)
