import sys
from PIL import Image

def process_image(input_path, output_path):
    img = Image.open(input_path)
    img = img.convert("RGBA")
    data = img.getdata()
    
    new_data = []
    for item in data:
        # Check if white (or very close to white)
        # R, G, B, A
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    img.save(output_path, "PNG")

if __name__ == "__main__":
    input_path = "C:/Users/yagol/.gemini/antigravity/brain/865ead90-80bc-4dc9-82d3-5c742bbe1d26/.user_uploaded/media_1790564598337.png"
    output_path = "y:/dev/Kakuja/EtoApp/eto_bg.png"
    process_image(input_path, output_path)
    print("done")
