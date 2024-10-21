import pygame
import math


def draw_rounded_rect(surface, color, rect, corner_radius):
    """
    Draws a rectangle with rounded corners.
    
    :param surface: The surface to draw on.
    :param color: The color of the rectangle.
    :param rect: The rect representing the position and size of the rectangle.
    :param corner_radius: The radius of the corners.
    """
    if corner_radius > 0:
        # Top-left corner
        pygame.draw.circle(surface, color, (rect.x + corner_radius, rect.y + corner_radius), corner_radius)
        # Top-right corner
        pygame.draw.circle(surface, color, (rect.x + rect.width - corner_radius, rect.y + corner_radius), corner_radius)
        # Bottom-left corner
        pygame.draw.circle(surface, color, (rect.x + corner_radius, rect.y + rect.height - corner_radius), corner_radius)
        # Bottom-right corner
        pygame.draw.circle(surface, color, (rect.x + rect.width - corner_radius, rect.y + rect.height - corner_radius), corner_radius)

        # Draw the rectangle without corners
        pygame.draw.rect(surface, color, (rect.x + corner_radius, rect.y, rect.width - 2 * corner_radius, rect.height))
        pygame.draw.rect(surface, color, (rect.x, rect.y + corner_radius, rect.width, rect.height - 2 * corner_radius))

        # Draw the edge rectangles to fill in the gaps
        pygame.draw.rect(surface, color, (rect.x + corner_radius, rect.y, rect.width - 2 * corner_radius, rect.height))
        pygame.draw.rect(surface, color, (rect.x, rect.y + corner_radius, rect.width, rect.height - 2 * corner_radius))
    else:
        pygame.draw.rect(surface, color, rect)

# Function to create a gradient surface
def create_gradient_surface(size, start_color, end_color):
    gradient = pygame.Surface(size)
    for y in range(size[1]):
        # Calculate the blend ratio
        ratio = y / size[1]
        # Interpolate the color between start_color and end_color
        color = (
            start_color[0] + (end_color[0] - start_color[0]) * ratio,
            start_color[1] + (end_color[1] - start_color[1]) * ratio,
            start_color[2] + (end_color[2] - start_color[2]) * ratio
        )
        pygame.draw.line(gradient, color, (0, y), (size[0], y))
    return gradient

# Function to render gradient text
def render_gradient_text(text, font, start_color, end_color):
    text_surface = font.render(text, True, (255, 255, 255))
    gradient_surface = create_gradient_surface(text_surface.get_size(), start_color, end_color)
    text_surface.blit(gradient_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return text_surface

# Function to draw a surface with a drop shadow
def draw_surface_with_shadow(screen, surface, position, shadow_color, shadow_offset):
    # Create a shadow surface
    shadow_surface = surface.copy()
    shadow_surface.fill(shadow_color, special_flags=pygame.BLEND_RGBA_MULT)
    
    # Calculate shadow position
    shadow_position = (position[0] + shadow_offset[0], position[1] + shadow_offset[1])
    
    # Draw the shadow surface
    screen.blit(shadow_surface, shadow_position)
    # Draw the main surface on top of the shadow
    screen.blit(surface, position)

# Function to render text with an outline
def render_text_with_outline(text, font, text_color, outline_color, outline_width):
    # Create a surface to hold the text and its outline
    text_surface = font.render(text, True, text_color)
    width, height = text_surface.get_size()

    # Create a larger surface to accommodate the outline
    outline_surface = pygame.Surface((width + 2 * outline_width, height + 2 * outline_width), pygame.SRCALPHA)

    # Render the outline by drawing the text slightly offset in all directions
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:  # Skip the center position
                font.render_to(outline_surface, (dx + outline_width, dy + outline_width), text, outline_color)

    # Render the main text in the center
    font.render_to(outline_surface, (outline_width, outline_width), text, text_color)

    return outline_surface

# Function to render text with gradient, drop shadow, and outline
def renderText(text, font, start_color, end_color, shadow_color, shadow_offset, outline_color=(0, 0, 0), outline_width=0):
    # Render text surface
    text_surface = font.render(text, True, (255, 255, 255))
    width, height = text_surface.get_size()

    # Create a surface for the effects
    effect_surface = pygame.Surface((width + 2 * outline_width + shadow_offset[0], 
                                     height + 2 * outline_width + shadow_offset[1]), pygame.SRCALPHA)

    # Draw the drop shadow
    shadow_surface = text_surface.copy()
    shadow_surface.fill(shadow_color, special_flags=pygame.BLEND_RGBA_MULT)
    effect_surface.blit(shadow_surface, (outline_width + shadow_offset[0], outline_width + shadow_offset[1]))

    # Draw the outline
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:  # Skip the center position
                outline_surface = font.render(text, True, outline_color)
                effect_surface.blit(outline_surface, (dx + outline_width, dy + outline_width))

    # Apply the gradient to the text
    gradient_surface = create_gradient_surface(text_surface.get_size(), start_color, end_color)
    text_surface.blit(gradient_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Draw the main text
    effect_surface.blit(text_surface, (outline_width, outline_width))

    return effect_surface

def draw_player(surface, color, innercolor, center, size, player, width=0):
    for part in player.playerShape:
        # Calculate the coordinates of the player
        points = []
        for vec in part:
            x = math.cos(vec[0] + math.pi * 1.5) * vec[1] * size + center[0]
            y = math.sin(vec[0] + math.pi * 1.5) * vec[1] * size + center[1]
            points.append((x, y))

        # Draw the part
        pygame.draw.polygon(surface, innercolor, points, width=0)
        pygame.draw.polygon(surface, color, points, width=width)

def draw_wrapped_text(surface, text, font, rect, startColor, endColor, shadowColor, shadowOffset=(3, 3), outlineColor=(0, 0, 0), outlineSize=1):
    paragraphs = text.split('\n')
    y = rect.top

    for paragraph in paragraphs:
        words = paragraph.split(' ')
        lines = []
        current_line = []

        for word in words:
            # Test the line with the new word
            current_line.append(word)
            test_line = ' '.join(current_line)
            test_width, test_height = font.size(test_line)

            if test_width <= rect.width:
                # The word fits in the line
                continue
            else:
                # The word doesn't fit, start a new line
                current_line.pop()  # Remove the word
                lines.append(' '.join(current_line))  # Add the current line to the lines list
                current_line = [word]  # Start a new line with the word

        # Add the last line to the lines list
        lines.append(' '.join(current_line))

        for line in lines:
            line_surf = renderText(line, font, startColor, endColor, shadowColor, shadowOffset, outlineColor, outlineSize)
            surface.blit(line_surf, (rect.left, y))
            if line:
                y += font.get_linesize()

        # Add a newline space
        if current_line:
            y += font.get_linesize()

# Function to create a surface with a vignette effect
def create_vignette_surface(size, edge_color, internal_radius, max_alpha=255, sharpness=1.0):
    width, height = size
    vignette_surface = pygame.Surface(size, pygame.SRCALPHA)
    
    # Calculate the center of the surface
    center_x, center_y = width // 2, height // 2
    
    # Create the vignette effect
    for y in range(height):
        for x in range(width):
            # Calculate the distance from the center
            distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            max_distance = math.sqrt(center_x ** 2 + center_y ** 2)
            
            if distance < internal_radius:
                # Fully transparent inside the internal radius
                alpha = 0
            else:
                # Sharpen the gradient by applying a power function
                ratio = (distance - internal_radius) / (max_distance - internal_radius)
                ratio = ratio ** sharpness
                alpha = int(max_alpha * (ratio))
            
            # Color with calculated alpha
            color = (
                edge_color[0],
                edge_color[1],
                edge_color[2],
                alpha  # Fade alpha to have transparency in the center
            )
            
            # Set the pixel color on the surface
            vignette_surface.set_at((x, y), color)
    
    return vignette_surface

# Function to create a new surface with a gradient circle
def create_gradient_circle(radius, inner_color, outer_color):
    # Create a new surface with per-pixel alpha
    surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    
    # The center of the circle
    center = (radius, radius)
    
    # Draw the gradient circle
    for i in range(radius):
        # Calculate the blend factor
        blend_factor = i / radius
        
        # Interpolate between the outer and inner colors
        color = (
            int(outer_color[0] + (inner_color[0] - outer_color[0]) * blend_factor),
            int(outer_color[1] + (inner_color[1] - outer_color[1]) * blend_factor),
            int(outer_color[2] + (inner_color[2] - outer_color[2]) * blend_factor),
            int(outer_color[3] + (inner_color[3] - outer_color[3]) * blend_factor)
        )
        
        # Draw a circle for each step, from the outer edge to the center
        pygame.draw.circle(surface, color, center, radius - i)

    return surface