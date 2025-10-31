import pygame
import pygame.gfxdraw
import sys
import math
import random
from typing import List

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
ZOOM_FACTOR = 1.1
DT_NORM = 1 / FPS

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

KEY_HELP = {
    'SPACE': 'Pause/Play',
    'R': 'Create Bounding Box',
    'C': 'Reset to Default',
    'W': 'Toggle Following Massive Body',
    'G': 'Toggle Grid',
    'RIGHT': 'Increase Time Acceleration',
    'LEFT': 'Decrease Time Acceleration',
    'UP': 'Increase G',
    'DOWN': 'Decrease G',
    ']': 'Increase Explosion Count',
    '[': 'Decrease Explosion Count',
    'S': 'Spawn Grid of Particles',
    'N': 'Toggle Particle Labels',
    'B': 'Create Star System',
    'A': 'Add Particle',
    'Z': 'Delete Mode',
    '3': 'Create Three-Body System',
    '/': 'Show/Hide Key Help'
}


class TextInput:
    def __init__(self, x, y, width, height, default_text=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = default_text
        self.active = False
        self.color = WHITE
        self.font = pygame.font.Font(None, 24)
        self.rendered_text = self.font.render(self.text, True, self.color)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = GREEN if self.active else WHITE
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.rendered_text = self.font.render(self.text, True, self.color)
        return False

    def draw(self, screen, label=""):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        if label:
            label_surface = self.font.render(label, True, self.color)
            screen.blit(label_surface, (self.rect.x - 100, self.rect.y + 5))
        screen.blit(self.rendered_text, (self.rect.x + 5, self.rect.y + 5))


class ParticleCreationMenu:
    def __init__(self, screen_width, screen_height):
        self.active = False
        menu_width = 400
        menu_height = 450
        self.rect = pygame.Rect((screen_width - menu_width) // 2,
                                (screen_height - menu_height) // 2,
                                menu_width, menu_height)

        # Create input fields
        base_x = self.rect.x + 120
        self.inputs = {
            "Name: ": TextInput(base_x, self.rect.y + 50, 200, 30, "P1"),
            "X Position: ": TextInput(base_x, self.rect.y + 100, 200, 30, "0"),
            "Y Position: ": TextInput(base_x, self.rect.y + 150, 200, 30, "0"),
            "X Velocity: ": TextInput(base_x, self.rect.y + 200, 200, 30, "0"),
            "Y Velocity: ": TextInput(base_x, self.rect.y + 250, 200, 30, "0"),
            "Mass: ": TextInput(base_x, self.rect.y + 300, 200, 30, "1000"),
        }

        # Create color selection buttons
        button_width = 60
        button_height = 30
        self.color_buttons = [
            (pygame.Rect(self.rect.x + 50 + i * (button_width + 10),
                         self.rect.y + 350, button_width, button_height), color)
            for i, color in enumerate([RED, GREEN, BLUE, WHITE, YELLOW])
        ]
        self.selected_color = WHITE

        # Create submit button
        self.submit_button = pygame.Rect(self.rect.centerx - 50,
                                         self.rect.bottom - 40, 100, 30)

        self.font = pygame.font.Font(None, 24)
        self.error_message = ""
        self.error_timer = 0

    def handle_event(self, event):
        if not self.active:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check color buttons
            for button, color in self.color_buttons:
                if button.collidepoint(event.pos):
                    self.selected_color = color
                    return None

            # Check submit button
            if self.submit_button.collidepoint(event.pos):
                return self.create_particle()

        # Handle text input fields
        for input_field in self.inputs.values():
            if input_field.handle_event(event):
                return self.create_particle()

        return None

    def create_particle(self):
        try:
            particle = PointMass(
                name=self.inputs["Name: "].text,
                x=float(self.inputs["X Position: "].text),
                y=float(self.inputs["Y Position: "].text),
                vx=float(self.inputs["X Velocity: "].text),
                vy=float(self.inputs["Y Velocity: "].text),
                mass=float(self.inputs["Mass: "].text),
                color=self.selected_color
            )
            self.active = False
            return particle
        except ValueError:
            self.error_message = "Please enter valid numerical values"
            self.error_timer = 60
            return None

    def draw(self, screen):
        if not self.active:
            return

        # Draw menu background
        pygame.draw.rect(screen, BLACK, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)

        # Draw title
        title = self.font.render("Add New Particle", True, WHITE)
        screen.blit(title, (self.rect.centerx - title.get_width() // 2,
                            self.rect.y + 20))

        # Draw input fields
        for label, input_field in self.inputs.items():
            input_field.draw(screen, label)

        # Draw color buttons
        color_text = self.font.render("Color:", True, WHITE)
        screen.blit(color_text, (self.rect.x + 50, self.rect.y + 330))
        for button, color in self.color_buttons:
            pygame.draw.rect(screen, color, button)
            pygame.draw.rect(screen, WHITE, button, 2)
            if color == self.selected_color:
                pygame.draw.rect(screen, GREEN, button, 4)

        # Draw submit button
        pygame.draw.rect(screen, WHITE, self.submit_button, 2)
        submit_text = self.font.render("Create", True, WHITE)
        screen.blit(submit_text, (self.submit_button.centerx - submit_text.get_width() // 2,
                                  self.submit_button.centery - submit_text.get_height() // 2))

        # Draw error message if any
        if self.error_timer > 0:
            error_surface = self.font.render(self.error_message, True, RED)
            screen.blit(error_surface, (self.rect.centerx - error_surface.get_width() // 2,
                                        self.rect.bottom - 80))
            self.error_timer -= 1


class PointMass:
    def __init__(self, name, x, y, vx, vy, mass, color):
        self.name = name
        self.x = x
        self.y = y
        self.xi = x
        self.yi = y
        self.vx = vx
        self.vy = vy
        self.vxi = vx
        self.vyi = vy
        self.ax = 0
        self.ay = 0
        self.mass = mass
        self.color = color
        self.radius = math.cbrt(mass)

    def reset(self):
        self.vx = self.vxi
        self.vy = self.vyi
        self.x = self.xi
        self.y = self.yi


class KeyHelpMenu:
    def __init__(self, screen_width, screen_height):
        self.active = False
        self.menu_width = 500
        self.menu_height = 435
        self.rect = pygame.Rect((screen_width - self.menu_width) // 2,
                                (screen_height - self.menu_height) // 2,
                                self.menu_width, self.menu_height)
        self.font = pygame.font.Font(None, 24)
        self.current_page = 0
        self.keys_per_page = 12
        self.total_pages = (len(KEY_HELP) + self.keys_per_page - 1) // self.keys_per_page

    def update_dimensions(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.rect = pygame.Rect((screen_width - self.menu_width) // 2,
                                (screen_height - self.menu_height) // 2,
                                self.menu_width, self.menu_height)

    def handle_event(self, event):
        if not self.active:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Cycle to next page
            self.current_page = (self.current_page + 1) % self.total_pages

        return False

    def draw(self, screen):
        if not self.active:
            return

        # Draw menu background
        pygame.draw.rect(screen, BLACK, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)

        # Draw title with page number
        title = self.font.render(f"Keyboard Controls (Page {self.current_page + 1}/{self.total_pages})", True, WHITE)
        screen.blit(title, (self.rect.centerx - title.get_width() // 2,
                            self.rect.y + 20))

        # Draw keys for current page
        start_index = self.current_page * self.keys_per_page
        end_index = min(start_index + self.keys_per_page, len(KEY_HELP))

        y_offset = 60
        for key, description in list(KEY_HELP.items())[start_index:end_index]:
            key_text = self.font.render(key, True, GREEN)
            desc_text = self.font.render(description, True, WHITE)
            screen.blit(key_text, (self.rect.x + 50, self.rect.y + y_offset))
            screen.blit(desc_text, (self.rect.x + 200, self.rect.y + y_offset))
            y_offset += 30


class PhysicsSimulation:
    def __init__(self):
        # Get display info and set up fullscreen
        display_info = pygame.display.Info()
        self.SCREEN_WIDTH = display_info.current_w
        self.SCREEN_HEIGHT = display_info.current_h

        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
                                              pygame.FULLSCREEN)
        pygame.display.set_caption("Gravity Simulator")
        self.clock = pygame.time.Clock()

        # Simulation properties
        self.particles: List[PointMass] = []
        self.show_axes = False
        self.zoom = 1.0
        self.offset_x = self.SCREEN_WIDTH // 2
        self.offset_y = self.SCREEN_HEIGHT // 2
        self.time = 0
        self.dragging = False
        self.last_mouse_pos = None

        # UI elements
        self.font = pygame.font.Font(None, 24)
        self.particle_menu = ParticleCreationMenu(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        self.delete_button_rect = pygame.Rect(10, 170, 100, 30)
        self.delete_mode = False
        self.paused = False

        self.windowed_size = (1024, 768)  # Default windowed size
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = self.windowed_size
        self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)

        self.following_massive = False
        self.time_accel = 1
        self.show_labels = True

        self.toCollide = []
        self.bounding_box = None
        self.explosion = 0
        self.G = 20
        self.key_help_menu = KeyHelpMenu(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

    def getAccelVector(self, pointMass):
        ax = 0
        ay = 0
        for particle in self.particles:
            if particle is pointMass:
                continue
            self.checkCollision(particle, pointMass)

            # Calculate distance vector components
            dx = particle.x - pointMass.x
            dy = particle.y - pointMass.y
            r = math.sqrt(dx * dx + dy * dy)

            # Calculate gravitational force magnitude
            if r != 0:
                gmag = self.G * particle.mass / (r * r)  # Note: using r² for inverse square law
                # Add acceleration components using normalized direction vector
                ax += gmag * dx / r
                ay += gmag * dy / r
            else:
                self.toCollide.append((pointMass, particle))

        return (ax, ay)

    def advance(self, time_accel):  # Using leapfrog approach
        dt = DT_NORM * time_accel
        for particle in self.particles:
            particle.ax, particle.ay = self.getAccelVector(particle)
            particle.vx = particle.vx + 0.5 * particle.ax * dt
            particle.vy = particle.vy + 0.5 * particle.ay * dt
            particle.x = particle.x + particle.vx * dt
            particle.y = particle.y + particle.vy * dt

            particle.ax, particle.ay = self.getAccelVector(particle)
            particle.vx = particle.vx + 0.5 * particle.ax * dt
            particle.vy = particle.vy + 0.5 * particle.ay * dt

            if self.bounding_box:
                left, top, right, bottom = self.bounding_box
                vmag = math.sqrt(particle.vx ** 2 + particle.vy ** 2)
                # Elastic bounce conditions
                if particle.x < left:
                    particle.x = left
                    particle.vx = abs(particle.vx)
                    for _ in range(self.explosion):
                        self.particles.append(PointMass(particle.name, right, random.random() * (bottom - top) + top,
                                                        -abs(vmag * math.cos(random.random() * 2 * math.pi)),
                                                        vmag * math.sin(random.random() * 2 * math.pi), particle.mass,
                                                        particle.color))
                elif particle.x > right:
                    particle.x = right
                    particle.vx = -abs(particle.vx)
                    for _ in range(self.explosion):
                        self.particles.append(PointMass(particle.name, left, random.random() * (bottom - top) + top,
                                                        abs(vmag * math.cos(random.random() * 2 * math.pi)),
                                                        vmag * math.sin(random.random() * 2 * math.pi), particle.mass,
                                                        particle.color))
                if particle.y > bottom:
                    particle.y = bottom
                    particle.vy = -abs(particle.vy)
                    for _ in range(self.explosion):
                        self.particles.append(PointMass(particle.name, random.random() * (right - left) + left, top,
                                                        vmag * math.cos(random.random() * 2 * math.pi),
                                                        abs(vmag * math.sin(random.random() * 2 * math.pi)),
                                                        particle.mass, particle.color))
                elif particle.y < top:
                    particle.y = top
                    particle.vy = abs(particle.vy)
                    for _ in range(self.explosion):
                        self.particles.append(PointMass(particle.name, random.random() * (right - left) + left, bottom,
                                                        vmag * math.cos(random.random() * 2 * math.pi),
                                                        -abs(vmag * math.sin(random.random() * 2 * math.pi)),
                                                        particle.mass, particle.color))

        self.collide(self.particles)

    def checkCollision(self, particle0, particle1):
        if particle0.mass >= particle1.mass and math.sqrt((particle0.x - particle1.x) ** 2 + (
                particle0.y - particle1.y) ** 2) < particle0.radius + particle1.radius:
            self.toCollide.append((particle0, particle1))

    def collide(self, particlesArray):
        for pair in self.toCollide:
            if pair[0] in particlesArray and pair[1] in particlesArray:
                particle0 = pair[0]
                particle1 = pair[1]
                px = particle0.mass * particle0.vx + particle1.mass * particle1.vx
                py = particle0.mass * particle0.vy + particle1.mass * particle1.vy
                particlesArray.remove(particle1)
                particle0.mass += particle1.mass
                particle0.vx = px / particle0.mass
                particle0.vy = py / particle0.mass
                particle0.radius = math.cbrt(particle0.mass)
                particle0.x = (particle0.mass * particle0.x + particle1.mass * particle1.x) / (
                            particle0.mass + particle1.mass)
                particle0.y = (particle0.mass * particle0.y + particle1.mass * particle1.y) / (
                            particle0.mass + particle1.mass)
        self.toCollide = []

    def center_on_massive(self):
        if not self.particles:
            return
        # Find most massive particle
        massive = max(self.particles, key=lambda p: p.mass)
        # Center view on it
        self.offset_x = self.SCREEN_WIDTH // 2 - massive.x * self.zoom
        self.offset_y = self.SCREEN_HEIGHT // 2 + massive.y * self.zoom

    def world_to_screen(self, x, y):
        screen_x = self.offset_x + x * self.zoom
        screen_y = self.offset_y - y * self.zoom  # Flip y-axis
        return int(screen_x), int(screen_y)

    def screen_to_world(self, screen_x, screen_y):
        world_x = (screen_x - self.offset_x) / self.zoom
        world_y = (self.offset_y - screen_y) / self.zoom  # Flip y-axis
        return world_x, world_y

    def add_particle(self, particle: PointMass):
        self.particles.append(particle)

    def draw_grid(self):
        if not self.show_axes:
            return

        # Calculate grid spacing based on zoom level
        grid_spacing = 100  # Base grid spacing in world units

        # Calculate visible area in world coordinates
        left, top = self.screen_to_world(0, 0)
        right, bottom = self.screen_to_world(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        # Draw vertical lines
        x = math.floor(left / grid_spacing) * grid_spacing
        while x <= right:
            start_x, start_y = self.world_to_screen(x, top)
            end_x, end_y = self.world_to_screen(x, bottom)
            alpha = max(0, min(255, 128 - abs(x) / 10))
            if 0 <= start_x <= self.SCREEN_WIDTH:
                pygame.draw.line(self.screen, GRAY, (start_x, 0),
                                 (end_x, self.SCREEN_HEIGHT))
            x += grid_spacing

        # Draw horizontal lines
        y = math.floor(bottom / grid_spacing) * grid_spacing
        while y <= top:
            start_x, start_y = self.world_to_screen(left, y)
            end_x, end_y = self.world_to_screen(right, y)
            alpha = max(0, min(255, 128 - abs(y) / 10))
            if 0 <= start_y <= self.SCREEN_HEIGHT:
                pygame.draw.line(self.screen, GRAY, (0, start_y),
                                 (self.SCREEN_WIDTH, end_y))
            y += grid_spacing

        # Draw bold main axes
        if 0 >= left and 0 <= right:  # Draw Y axis
            start_x, start_y = self.world_to_screen(0, top)
            end_x, end_y = self.world_to_screen(0, bottom)
            pygame.draw.line(self.screen, WHITE, (start_x, 0), (end_x, self.SCREEN_HEIGHT), 3)

        if 0 >= bottom and 0 <= top:  # Draw X axis
            start_x, start_y = self.world_to_screen(left, 0)
            end_x, end_y = self.world_to_screen(right, 0)
            pygame.draw.line(self.screen, WHITE, (0, start_y), (self.SCREEN_WIDTH, end_y), 3)

        if self.bounding_box:
            l, t, r, b = self.bounding_box
            top_left = self.world_to_screen(l, t)
            bottom_right = self.world_to_screen(r, b)
            pygame.draw.rect(self.screen, GREEN,
                             (top_left[0], bottom_right[1],
                              bottom_right[0] - top_left[0],
                              top_left[1] - bottom_right[1]), 2)

        # Draw grid numbers
        number_spacing = grid_spacing  # or multiply by some factor for sparser numbers
        x = math.floor(left / number_spacing) * number_spacing
        while x <= right:
            screen_x, screen_y = self.world_to_screen(x, 0)
            if x != 0 and 0 <= screen_x <= self.SCREEN_WIDTH:  # Don't draw 0
                text = self.font.render(str(int(x)), True, GRAY)
                self.screen.blit(text, (screen_x - text.get_width() // 2, self.offset_y + 5))
            x += number_spacing

        y = math.floor(bottom / number_spacing) * number_spacing
        while y <= top:
            screen_x, screen_y = self.world_to_screen(0, y)
            if y != 0 and 0 <= screen_y <= self.SCREEN_HEIGHT:  # Don't draw 0
                text = self.font.render(str(int(y)), True, GRAY)
                self.screen.blit(text, (self.offset_x + 5, screen_y - text.get_height() // 2))
            y += number_spacing

    def draw_ui(self):
        particle_text = self.font.render("Particle count: " + str(len(self.particles)), True, WHITE)
        self.screen.blit(particle_text, (10, 10))

        # Draw time
        time_text = self.font.render(f"Time: {self.time:.2f}" + " (" + str(self.time_accel) + "x)", True, WHITE)
        self.screen.blit(time_text, (10, 40))

        G_text = self.font.render("G = " + " " + str(self.G), True, WHITE)
        self.screen.blit(G_text, (10, 70))

        if self.bounding_box:
            explosion_text = self.font.render("Explosion count: " + " " + str(self.explosion), True, WHITE)
            self.screen.blit(explosion_text, (10, 100))

        if self.delete_mode:
            pygame.draw.rect(self.screen, WHITE, self.delete_button_rect, 2)
            text = self.font.render("Delete Mode", True, WHITE if not self.delete_mode else RED)
            text_rect = text.get_rect(center=self.delete_button_rect.center)
            self.screen.blit(text, text_rect)

        # Draw particle creation menu if active
        self.particle_menu.draw(self.screen)
        self.key_help_menu.draw(self.screen)

        play_status = "PAUSED" if self.paused else "PLAYING"
        status_text = self.font.render(play_status, True, RED if self.paused else GREEN)
        self.screen.blit(status_text, (10, 130))  # Position below other UI elements

    def draw_particles(self):
        for particle in self.particles:
            screen_x, screen_y = self.world_to_screen(particle.x, particle.y)

            # Draw particle
            pygame.gfxdraw.filled_circle(self.screen, screen_x, screen_y,
                                         int(particle.radius * self.zoom), particle.color)
            pygame.gfxdraw.aacircle(self.screen, screen_x, screen_y,
                                    int(particle.radius * self.zoom), particle.color)

            # Draw label with offset outside particle radius
            if self.show_labels:
                text = self.font.render(particle.name + " (" + str(round(particle.mass)) + ")", True, particle.color)
                offset = int(particle.radius * self.zoom) + 5  # Offset from particle edge
                self.screen.blit(text, (screen_x + offset, screen_y - offset))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return False
            # Handle particle creation menu events
            new_particle = self.particle_menu.handle_event(event)
            self.key_help_menu.handle_event(event)
            if new_particle:
                self.add_particle(new_particle)
                continue
            # if self.key_help_menu.active:
            # self.key_help_menu.handle_event(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.delete_mode:  # Check if clicked on a particle
                        for particle in self.particles[:]:  # Create copy of list to avoid modification issues
                            screen_x, screen_y = self.world_to_screen(particle.x, particle.y)
                            if math.sqrt((event.pos[0] - screen_x) ** 2 + (
                                    event.pos[1] - screen_y) ** 2) < particle.radius * self.zoom:
                                self.particles.remove(particle)
                                self.delete_mode = False
                                break
                    # Handle dragging (only if not clicking on UI)
                    elif not self.particle_menu.active:
                        self.dragging = True
                        self.last_mouse_pos = event.pos

                elif event.button == 4:  # Mouse wheel up
                    # Get world position of mouse before zoom
                    mouse_world_x, mouse_world_y = self.screen_to_world(*event.pos)
                    self.zoom *= ZOOM_FACTOR
                    # Get new screen position of the same world point
                    new_mouse_screen_x = self.offset_x + mouse_world_x * self.zoom
                    new_mouse_screen_y = self.offset_y - mouse_world_y * self.zoom
                    # Adjust offset to keep mouse position fixed
                    self.offset_x += event.pos[0] - new_mouse_screen_x
                    self.offset_y += event.pos[1] - new_mouse_screen_y

                elif event.button == 5:  # Mouse wheel down
                    # Same logic for zooming out
                    mouse_world_x, mouse_world_y = self.screen_to_world(*event.pos)
                    self.zoom /= ZOOM_FACTOR
                    new_mouse_screen_x = self.offset_x + mouse_world_x * self.zoom
                    new_mouse_screen_y = self.offset_y - mouse_world_y * self.zoom
                    self.offset_x += event.pos[0] - new_mouse_screen_x
                    self.offset_y += event.pos[1] - new_mouse_screen_y

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    self.dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if self.dragging and not self.particle_menu.active:
                    current_pos = event.pos
                    dx = current_pos[0] - self.last_mouse_pos[0]
                    dy = current_pos[1] - self.last_mouse_pos[1]
                    self.offset_x += dx
                    self.offset_y += dy
                    self.last_mouse_pos = current_pos

            elif event.type == pygame.KEYDOWN and not self.particle_menu.active:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_q:
                    self.particles = []
                    for i in range(math.floor(random.random() * 9 + 2)):
                        self.particles.append(PointMass(
                            "P" + str(i),
                            random.random() * 1000 - 500,
                            random.random() * 1000 - 500,
                            random.random() * 300 - 150,
                            random.random() * 300 - 150,
                            10 ** (random.random() * 7),
                            (math.floor(random.random() * 256), math.floor(random.random() * 256),
                             math.floor(random.random() * 256))
                        ))
                elif event.key == pygame.K_c:
                    self.particles = []
                    self.time_accel = 1
                    self.bounding_box = None
                    self.G = 20
                elif event.key == pygame.K_w:
                    self.following_massive = not self.following_massive
                    if not self.following_massive:
                        # Return to origin
                        self.offset_x = self.SCREEN_WIDTH // 2
                        self.offset_y = self.SCREEN_HEIGHT // 2
                elif event.key == pygame.K_g:
                    self.show_axes = not self.show_axes
                elif event.key == pygame.K_RIGHT:
                    self.time_accel *= 2
                elif event.key == pygame.K_LEFT:
                    self.time_accel /= 2
                elif event.key == pygame.K_s:
                    self.particles = []
                    self.show_labels = False
                    for i in range(-500, 550, 50):
                        for j in range(-500, 550, 50):
                            if random.random() < 1 / 3:
                                mass = 1
                            else:
                                mass = 100
                            self.particles.append(PointMass("P" + str(i) + "," + str(j), i, j, 0, 0, mass,
                                                            (math.floor(random.random() * 256),
                                                             math.floor(random.random() * 256),
                                                             math.floor(random.random() * 256))))
                elif event.key == pygame.K_n:
                    self.show_labels = not self.show_labels
                elif event.key == pygame.K_b:
                    self.particles = []
                    self.show_labels = False
                    self.particles.append(PointMass("Star", 0, 0, 0, 0, 1000000, WHITE))
                    for r in range(200, 1000, 3):
                        self.create_circular_orbit(r, 100)
                elif event.key == pygame.K_a:
                    self.particle_menu.active = True
                elif event.key == pygame.K_z:
                    self.delete_mode = not self.delete_mode
                elif event.key == pygame.K_r:
                    # Create bounding box from origin to current mouse position
                    mouse_world_x, mouse_world_y = self.screen_to_world(*pygame.mouse.get_pos())
                    self.bounding_box = (min(mouse_world_x, -mouse_world_x), min(-mouse_world_y, mouse_world_y),
                                         max(-mouse_world_x, mouse_world_x), max(-mouse_world_y, mouse_world_y))
                elif event.key == pygame.K_RIGHTBRACKET:
                    self.explosion += 1
                elif event.key == pygame.K_LEFTBRACKET and self.explosion > 0:
                    self.explosion -= 1
                elif event.key == pygame.K_3:
                    self.create_three_body_system()
                elif event.key == pygame.K_UP:
                    self.G += 1
                elif event.key == pygame.K_DOWN and self.G > 0:
                    self.G -= 1
                elif event.key == pygame.K_SLASH:
                    self.key_help_menu.active = not self.key_help_menu.active

        return True

    def create_circular_orbit(self, r, mass):
        theta = random.random() * 2 * math.pi
        vmag = math.sqrt(20 * 1000000 / r)
        self.particles.append(PointMass(
            "C" + str(r),
            r * math.cos(theta),
            r * math.sin(theta),
            vmag * math.cos(theta + math.pi / 2),
            vmag * math.sin(theta + math.pi / 2),
            mass,
            (math.floor(random.random() * 256), math.floor(random.random() * 256), math.floor(random.random() * 256))
        ))

    def create_three_body_system(self):
        self.particles = []
        mass = 10000
        radius = 100

        # Calculate velocities for stable configuration
        orbital_velocity = math.sqrt(self.G * mass * 3 / (2 * radius))

        self.particles.append(PointMass("Body1",
                                        radius * math.cos(0),
                                        radius * math.sin(0),
                                        orbital_velocity * math.cos(math.pi / 2),
                                        orbital_velocity * math.sin(math.pi / 2),
                                        mass, RED))

        self.particles.append(PointMass("Body2",
                                        radius * math.cos(2 * math.pi / 3),
                                        radius * math.sin(2 * math.pi / 3),
                                        orbital_velocity * math.cos(7 * math.pi / 6),
                                        orbital_velocity * math.sin(7 * math.pi / 6),
                                        mass, GREEN))

        self.particles.append(PointMass("Body3",
                                        radius * math.cos(4 * math.pi / 3),
                                        radius * math.sin(4 * math.pi / 3),
                                        orbital_velocity * math.cos(11 * math.pi / 6),
                                        orbital_velocity * math.sin(11 * math.pi / 6),
                                        mass, BLUE))

    def run(self):
        running = True
        while running:
            running = self.handle_events()

            display_info = pygame.display.Info()
            self.SCREEN_WIDTH = display_info.current_w
            self.SCREEN_HEIGHT = display_info.current_h
            self.key_help_menu.update_dimensions(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

            # Clear screen
            self.screen.fill(BLACK)

            # Draw everything
            self.draw_grid()
            self.draw_particles()
            self.draw_ui()

            # Only advance if not paused and not in menu
            if not self.particle_menu.active and not self.paused and not self.key_help_menu.active:
                self.advance(self.time_accel)
                self.time += 1 / FPS * self.time_accel

            if self.following_massive:
                self.center_on_massive()

            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    s = PhysicsSimulation()
    s.run()