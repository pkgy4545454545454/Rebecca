from PIL import Image, ImageDraw
import math

# Create a high-res image
size = 1024
center = size // 2
img = Image.new('RGBA', (size, size), (255, 255, 255, 255))
draw = ImageDraw.Draw(img)

# Blue color (same as original)
blue = (0, 128, 255, 255)
black = (0, 0, 0, 255)

# Iris dimensions
outer_radius = 280
inner_radius = 160  # White space inside the blue ring
pupil_radius = 100

# Gap angle - REDUCED from ~120° to ~70°
gap_start = 300  # degrees (where gap starts)
gap_end = 370    # degrees (where gap ends) - only 70 degree gap now

# Draw blue iris ring (arc) - gap is smaller now
# We draw from gap_end to gap_start (going around)
draw.arc(
    [center - outer_radius, center - outer_radius, center + outer_radius, center + outer_radius],
    gap_end - 360, gap_start,
    fill=blue, width=int(outer_radius - inner_radius)
)

# Draw filled blue arc (pieslice for thick ring effect)
# Create mask for the ring
for angle in range(int(gap_end - 360), int(gap_start)):
    rad = math.radians(angle)
    for r in range(inner_radius, outer_radius + 1):
        x = center + int(r * math.cos(rad))
        y = center + int(r * math.sin(rad))
        if 0 <= x < size and 0 <= y < size:
            img.putpixel((x, y), blue)

# Draw black pupil (center circle)
draw.ellipse(
    [center - pupil_radius, center - pupil_radius, center + pupil_radius, center + pupil_radius],
    fill=black
)

# Clock hands - touching the inner edge of the blue ring
# Hour hand pointing up (12 o'clock)
hour_length = inner_radius - 5  # Touch the inner edge of blue ring
hour_angle = -90  # 12 o'clock (straight up)
hour_rad = math.radians(hour_angle)
hour_end_x = center + int(hour_length * math.cos(hour_rad))
hour_end_y = center + int(hour_length * math.sin(hour_rad))

# Draw hour hand (thicker, with pointed tip)
draw.polygon([
    (center - 4, center),
    (center + 4, center),
    (hour_end_x + 2, hour_end_y),
    (hour_end_x, hour_end_y - 15),  # Pointed tip
    (hour_end_x - 2, hour_end_y),
], fill=black)

# Minute hand pointing to ~2 o'clock (touching edge)
minute_length = inner_radius - 5  # Touch the inner edge
minute_angle = -30  # Approximately 2 o'clock position
minute_rad = math.radians(minute_angle)
minute_end_x = center + int(minute_length * math.cos(minute_rad))
minute_end_y = center + int(minute_length * math.sin(minute_rad))

# Draw minute hand (thinner, with pointed tip)
draw.polygon([
    (center - 3, center),
    (center + 3, center),
    (minute_end_x, minute_end_y - 8),  # Pointed tip
], fill=black)

# Add small center circle for clock center
draw.ellipse(
    [center - 8, center - 8, center + 8, center + 8],
    fill=black
)

# Save
img.save('/app/backend/uploads/logo_eye_clock_v2.png', 'PNG')
print("Logo saved to /app/backend/uploads/logo_eye_clock_v2.png")
