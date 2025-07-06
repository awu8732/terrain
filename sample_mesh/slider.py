import pygame 

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, linked_variable, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.value = linked_variable
        self.label = label
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                relative_x = event.pos[0] - self.rect.x
                relative_x = max(0, min(self.rect.w, relative_x))
                self.value = self.min_val + (relative_x / self.rect.w) * (self.max_val - self.min_val)

    def draw(self, surface):
        # Background
        pygame.draw.rect(surface, (180, 180, 180), self.rect)
        # Knob
        knob_x = self.rect.x + ((self.value - self.min_val) / (self.max_val - self.min_val)) * self.rect.w
        pygame.draw.circle(surface, (50, 50, 255), (int(knob_x), self.rect.y + self.rect.h // 2), 8)
        # Label
        font = pygame.font.SysFont(None, 20)
        label_surface = font.render(f"{self.label}: {self.value:.2f}", True, (0, 0, 0))
        surface.blit(label_surface, (self.rect.x, self.rect.y - 20))