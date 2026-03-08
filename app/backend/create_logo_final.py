from PIL import Image, ImageDraw
import math

size = 1024
center = size // 2
img = Image.new('RGBA', (size, size), (248, 250, 252, 255))  # Light gray background like original
draw = ImageDraw.Draw(img)

# Colors
blue = (0, 128, 255, 255)
black = (0, 0, 0, 255)

# Dimensions
outer_radius = 240
inner_radius = 120
pupil_radius = 80

# Gap position: RIGHT side (like original) but SMALLER
# Original had gap from ~150° to ~270° (about 120°)
# New: gap from ~165° to ~225° (only 60°) - smaller gap
gap_start_deg = 165
gap_end_deg = 225

# Draw blue ring
for y in range(size):
    for x in range(size):
        dx = x - center
        dy = y - center
        dist = math.sqrt(dx*dx + dy*dy)
        
        if inner_radius < dist < outer_radius:
            angle = math.degrees(math.atan2(dy, dx))
            if angle < 0:
                angle += 360
            
            # Not in gap = draw blue
            if not (gap_start_deg <= angle <= gap_end_deg):
                img.putpixel((x, y), blue)

# Draw pupil
draw.ellipse(
    [center - pupil_radius, center - pupil_radius, center + pupil_radius, center + pupil_radius],
    fill=black
)

# HOUR HAND - pointing UP (12 o'clock), touching inner edge of blue ring
hour_length = inner_radius + 5  # Extends to touch blue ring
hour_width = 8

# Draw hour hand as polygon with pointed tip
draw.polygon([
    (center - hour_width//2, center + 10),
    (center + hour_width//2, center + 10),
    (center + 4, center - hour_length + 30),
    (center, center - hour_length - 10),  # Sharp pointed tip above
    (center - 4, center - hour_length + 30),
], fill=black)

# MINUTE HAND - pointing to ~2 o'clock, touching inner edge of blue ring
minute_angle_deg = -20  # Slightly above horizontal toward right
minute_rad = math.radians(minute_angle_deg)
minute_length = inner_radius + 5  # Touch the blue ring

minute_end_x = center + minute_length * math.cos(minute_rad)
minute_end_y = center + minute_length * math.sin(minute_rad)

# Perpendicular for width
perp = minute_rad + math.pi/2
w = 5

# Draw minute hand
draw.polygon([
    (center + w*math.cos(perp), center + w*math.sin(perp)),
    (center - w*math.cos(perp), center - w*math.sin(perp)),
    (minute_end_x, minute_end_y),
], fill=black)

# Center dot
draw.ellipse([center-12, center-12, center+12, center+12], fill=black)

img.save('/app/backend/uploads/logo_final.png', 'PNG')
print("Done!")
