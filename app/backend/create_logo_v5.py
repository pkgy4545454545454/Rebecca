from PIL import Image, ImageDraw
import math

size = 1024
center = size // 2
img = Image.new('RGBA', (size, size), (248, 250, 252, 255))
draw = ImageDraw.Draw(img)

blue = (0, 128, 255, 255)
black = (0, 0, 0, 255)

outer_radius = 240
inner_radius = 120
pupil_radius = 80

# Gap: ~60 degrees on the LEFT side (like original but smaller)
gap_start_deg = 170
gap_end_deg = 230

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
            if not (gap_start_deg <= angle <= gap_end_deg):
                img.putpixel((x, y), blue)

# Draw pupil
draw.ellipse([center - pupil_radius, center - pupil_radius, 
              center + pupil_radius, center + pupil_radius], fill=black)

# HOUR HAND - 12 o'clock, LONG and touching blue ring
# The hand should extend from center, through the pupil, to touch the blue ring
hour_tip_y = center - inner_radius + 5  # Touch inner edge of blue

draw.polygon([
    (center - 5, center + 15),      # Base left
    (center + 5, center + 15),      # Base right  
    (center + 3, hour_tip_y + 25),  # Narrow
    (center, hour_tip_y - 15),      # Pointed tip (touches blue)
    (center - 3, hour_tip_y + 25),  # Narrow
], fill=black)

# MINUTE HAND - ~2 o'clock, touching blue ring
minute_angle = -25  # degrees
minute_rad = math.radians(minute_angle)
minute_tip_dist = inner_radius - 5  # Touch inner edge of blue

tip_x = center + minute_tip_dist * math.cos(minute_rad)
tip_y = center + minute_tip_dist * math.sin(minute_rad)

# Perpendicular for hand width
perp = minute_rad + math.pi/2
w = 4

draw.polygon([
    (center + w*math.cos(perp), center + w*math.sin(perp)),
    (center - w*math.cos(perp), center - w*math.sin(perp)),
    (tip_x + 8*math.cos(minute_rad), tip_y + 8*math.sin(minute_rad)),  # Extended tip
], fill=black)

# Center cap
draw.ellipse([center-10, center-10, center+10, center+10], fill=black)

img.save('/app/backend/uploads/logo_v5.png', 'PNG')
print("Done!")
