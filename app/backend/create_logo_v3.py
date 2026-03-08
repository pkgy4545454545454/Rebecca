from PIL import Image, ImageDraw
import math

# Create a high-res image with white background
size = 1024
center = size // 2
img = Image.new('RGBA', (size, size), (255, 255, 255, 255))
draw = ImageDraw.Draw(img)

# Colors matching original exactly
blue = (0, 128, 255, 255)  # Bright blue iris
black = (0, 0, 0, 255)

# Dimensions matching original
outer_radius = 250
inner_radius = 130
pupil_radius = 85

# Gap - SMALLER (about 60 degrees instead of 120)
# Original gap was roughly from 7 o'clock going to 5 o'clock (lower left)
# New gap: smaller, roughly 60 degrees in the lower-right area
gap_center = 335  # Center of gap at roughly 2 o'clock area (where the minute hand points)
gap_half = 30     # Half of gap = 30 degrees, so total gap = 60 degrees

# Draw the blue iris as a thick arc
# Fill the ring area pixel by pixel for smooth result
for y in range(size):
    for x in range(size):
        dx = x - center
        dy = y - center
        dist = math.sqrt(dx*dx + dy*dy)
        
        if inner_radius <= dist <= outer_radius:
            # Check if in gap
            angle = math.degrees(math.atan2(dy, dx))
            if angle < 0:
                angle += 360
            
            # Gap from (gap_center - gap_half) to (gap_center + gap_half)
            gap_start = (gap_center - gap_half) % 360
            gap_end = (gap_center + gap_half) % 360
            
            in_gap = False
            if gap_start < gap_end:
                in_gap = gap_start <= angle <= gap_end
            else:
                in_gap = angle >= gap_start or angle <= gap_end
            
            if not in_gap:
                img.putpixel((x, y), blue)

# Draw black pupil (center circle)
draw.ellipse(
    [center - pupil_radius, center - pupil_radius, center + pupil_radius, center + pupil_radius],
    fill=black
)

# Clock hands - TOUCHING the inner edge of blue ring
# Hour hand: pointing straight UP (12 o'clock)
hour_length = inner_radius - 2  # Almost touching the blue
hour_tip_extra = 8  # Tip extends slightly

# Hour hand shape (elegant pointed)
hour_base_width = 6
hour_points = [
    (center - hour_base_width//2, center + 5),  # Base left
    (center + hour_base_width//2, center + 5),  # Base right
    (center + 3, center - hour_length + 20),     # Narrow before tip
    (center, center - hour_length - hour_tip_extra),  # Pointed tip
    (center - 3, center - hour_length + 20),     # Narrow before tip
]
draw.polygon(hour_points, fill=black)

# Minute hand: pointing to roughly 2-3 o'clock, touching the edge
minute_angle = -25  # degrees from horizontal (pointing to ~2 o'clock)
minute_length = inner_radius - 2
minute_rad = math.radians(minute_angle)

minute_end_x = center + int(minute_length * math.cos(minute_rad))
minute_end_y = center + int(minute_length * math.sin(minute_rad))

# Calculate perpendicular for hand width
perp_rad = minute_rad + math.pi/2
base_offset = 4

minute_points = [
    (center + int(base_offset * math.cos(perp_rad)), center + int(base_offset * math.sin(perp_rad))),
    (center - int(base_offset * math.cos(perp_rad)), center - int(base_offset * math.sin(perp_rad))),
    (minute_end_x, minute_end_y),  # Pointed tip
]
draw.polygon(minute_points, fill=black)

# Center cap
draw.ellipse([center - 10, center - 10, center + 10, center + 10], fill=black)

# Save
img.save('/app/backend/uploads/logo_eye_clock_fixed.png', 'PNG')
print("Logo saved!")
