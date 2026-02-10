"""Generiert das SmartType Icon."""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Hintergrund: abgerundetes Quadrat
    margin = 10
    radius = 40
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=radius,
        fill="#1e1e2e"
    )

    # Großes "T" in der Mitte
    try:
        font_big = ImageFont.truetype("segoeuib.ttf", 120)
    except:
        font_big = ImageFont.load_default()
    
    draw.text((size // 2 - 15, size // 2), "T", fill="#cdd6f4", font=font_big, anchor="mm")

    # Blitz als Polygon zeichnen (rechts neben T, mittig)
    bolt = [
        (175, 85), (155, 130), (170, 130),
        (148, 175), (195, 120), (178, 120),
        (195, 85),
    ]
    draw.polygon(bolt, fill="#f9e2af")

    # Als .ico speichern (mehrere Größen)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ico_path = os.path.join(script_dir, "smarttype.ico")
    
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, format="ICO", sizes=sizes)
    print(f"Icon erstellt: {ico_path}")
    return ico_path

if __name__ == "__main__":
    create_icon()
