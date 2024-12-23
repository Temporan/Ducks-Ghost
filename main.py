import pyautogui
import os
import time
from PIL import Image, ImageDraw
import math

def take_screenshot(region):
    """Captures a screenshot of a specific region and returns it as an Image object."""
    screenshot = pyautogui.screenshot(region=region)
    return screenshot


def distance(coord1, coord2):
    """Calculates the Euclidean distance between two coordinates (x, y)."""
    return math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)


def filter_close_detections(detections, min_distance=10):
    """Filters closely spaced coordinates (duplicates)."""
    filtered = []
    for coord in detections:
        if all(distance(coord, other) >= min_distance for other in filtered):
            filtered.append(coord)
    return filtered


time.sleep(4)
ducks_centers = []
haystack = take_screenshot([444, 222, 1121, 304])

# Convert haystack to RGB mode just in case it's not in that mode
haystack = haystack.convert("RGB")

needles = [
    os.path.join("images/needles", image)
    for image in os.listdir("images/needles")
    if image.endswith((".png", ".jpg"))
]

# Search for each needle image in the haystack
for needle in needles:
    print(f"Searching for: {needle}")
    time.sleep(1)
    try:
        raw_locations = list(pyautogui.locateAll(needle, haystack, confidence=0.8))  # Convert to list

        if raw_locations:  # Check if there are any matches
            locations = [
                (box.left, box.top, box.width, box.height)
                for box in raw_locations
                if box is not None
            ]

            # Calculate the center coordinates for each box and store in ducks_centers
            for loc in locations:
                center = pyautogui.center(loc)
                ducks_centers.append([int(center.x), int(center.y)])

            # Filter the ducks_centers list to remove near-duplicates based on the distance threshold
            unique_ducks_centers = filter_close_detections(ducks_centers, min_distance=10)

            print(f"Found {len(unique_ducks_centers)} unique matches for {needle}")
            print(f"Unique Ducks Centers: {unique_ducks_centers}")

            # Draw rectangles around the filtered locations
            draw = ImageDraw.Draw(haystack)

            # Check if unique_ducks_centers list is valid and draw the rectangles
            image_width, image_height = haystack.size
            for loc in unique_ducks_centers:
                # Find the bounding box for the center coordinates
                for original_loc in locations:
                    # Check if the coordinates in the filtered list match the original locations
                    x, y, w, h = original_loc
                    if distance([x + w / 2, y + h / 2], loc) < 10:  # Match the center of the box
                        # Ensure coordinates are within the bounds of the image
                        if x >= 0 and y >= 0 and x + w <= image_width and y + h <= image_height:
                            draw.rectangle((x, y, x + w, y + h), outline=(255, 0, 0), width=2)
                        break

            haystack.show()
        else:
            print(f"No matches found for {needle}")

    except pyautogui.ImageNotFoundException as e:
        print(f"Warning: {str(e)}. Skipping {needle}.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

print("Finished searching all needles.")
print()
print(len(unique_ducks_centers))
print(unique_ducks_centers)