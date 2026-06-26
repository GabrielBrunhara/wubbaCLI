import requests
import random
from PIL import Image
from io import BytesIO
import warnings
from pyfiglet import Figlet

warnings.filterwarnings("ignore", category=DeprecationWarning)

# ASCII chars do mais escuro pro mais claro
# ASCII_CHARS = "@%#*+=-:. "
ASCII_CHARS = "@%#W$9876543210?!abc;:+=-,._ "
WIDTH = 200

def resize_image(image, new_width=100):
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio * 0.55)
    return image.resize((new_width, new_height))

def grayscale(image):
    return image.convert("L")

def pixels_to_ascii(image):
    pixels = image.getdata()
    scale = len(ASCII_CHARS) - 1
    chars = "".join([ASCII_CHARS[pixel * scale // 255] for pixel in pixels])
    return chars

def image_to_ascii(url, width=100):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))

    image = resize_image(image, width)
    image = grayscale(image)

    ascii_str = pixels_to_ascii(image)

    ascii_img = "\n".join(
        ascii_str[i:i+width] for i in range(0, len(ascii_str), width)
    )

    return ascii_img

def get_random_character():
    # pega total de personagens
    base = requests.get("https://rickandmortyapi.com/api/character").json()
    total = base["info"]["count"]

    random_id = random.randint(1, total)

    url = f"https://rickandmortyapi.com/api/character/{random_id}"
    data = requests.get(url).json()

    return data

def main():
    char = get_random_character()

    name = char["name"]
    image_url = char["image"]

    ascii_art = image_to_ascii(image_url, width=WIDTH)
    fig = Figlet(font="colossal")
    print(fig.renderText(name))
    print(ascii_art)

if __name__ == "__main__":
    main()