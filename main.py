import random
from reportlab.pdfgen import canvas # type: ignore
from reportlab.lib.units import cm # type: ignore
from reportlab.pdfbase.ttfonts import TTFont # type: ignore
from reportlab.pdfbase import pdfmetrics # type: ignore
from reportlab.lib.colors import HexColor # type: ignore

# Constants
PAGE_WIDTH, PAGE_HEIGHT = 21.7 * cm, 27.8 * cm
LEFT_MARGIN, RIGHT_MARGIN = 1.7 * cm, 2 * cm
TOP_MARGIN = 3.9 * cm
LINE_HEIGHT = 0.75 * cm
MAX_LINES_PER_PAGE = 32
FONT_SIZE = 22
LETTER_SPACING_FACTOR = 0.8
TAB_WIDTH = 4  # Number of spaces per tab

FONTS = ['font-1', 'font-2', 'font-3']
FONT_PATH = "fonts/"


def register_fonts():
    """Register the required fonts."""
    for font in FONTS:
        pdfmetrics.registerFont(TTFont(font, f"{FONT_PATH}{font}.otf"))


def get_random_font():
    """Return a random font from the registered fonts."""
    return random.choice(FONTS)


def get_random_black_shade():
    """Generate a random dark shade between #000000 and #191919."""
    shade = random.randint(0, 0x19)  # 0x00 to 0x19 in hex
    hex_color = f'#{shade:02x}{shade:02x}{shade:02x}'
    return HexColor(hex_color)


def text_to_pdf(input_file, output_file):
    """Convert a text file to a formatted PDF."""
    register_fonts()
    
    c = canvas.Canvas(output_file, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    x_start = LEFT_MARGIN
    y_start = PAGE_HEIGHT - TOP_MARGIN
    
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    x, y = x_start, y_start
    line_count = 0
    
    for line in lines:
        line = line.rstrip()  # Remove trailing whitespace
        
        if not line:  # Handle empty lines
            y -= LINE_HEIGHT
            line_count += 1
        else:
            words = line.split(' ')
            for word in words:
                if '\t' in word:
                    x += pdfmetrics.stringWidth(' ', get_random_font(), FONT_SIZE) * TAB_WIDTH
                
                word_width = sum(pdfmetrics.stringWidth(char, get_random_font(), FONT_SIZE) * LETTER_SPACING_FACTOR for char in word)
                
                if x + word_width > (PAGE_WIDTH - RIGHT_MARGIN):
                    x = x_start
                    y -= LINE_HEIGHT
                    line_count += 1

                for char in word:
                    font = get_random_font()
                    color = get_random_black_shade()
                    c.setFont(font, FONT_SIZE)
                    c.setFillColor(color)
                    c.drawString(x, y, char)
                    x += pdfmetrics.stringWidth(char, font, FONT_SIZE) * LETTER_SPACING_FACTOR
                
                x += pdfmetrics.stringWidth(' ', get_random_font(), FONT_SIZE)  # Space after word
        
        x = x_start
        y -= LINE_HEIGHT
        line_count += 1

        if line_count >= MAX_LINES_PER_PAGE:
            c.showPage()
            x, y = x_start, y_start
            line_count = 0
    
    c.save()

    print('Updated content.pdf')


# Convert content.txt to content.pdf
if __name__ == "__main__":
    text_to_pdf('content.txt', 'content.pdf')
