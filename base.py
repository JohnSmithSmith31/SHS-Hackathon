# Genai key: AIzaSyDuJ3wxFUFDIl3td6V4COYVW2SrZAuio7U

# PLAN:
# Revert to basic functionality
# Clean up code
# Then add flask support
# Make a simple GUI with to edit text and generate AI first
# Also add other settings
# Then ask DeepSeek to make it look 

# ALSO ADD:
# Different AI APIs
# More font variety
# OCR to font feature
# Night mode
# And other settings

import random
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor

# Register the .otf font files
def register_fonts():
    pdfmetrics.registerFont(TTFont('MyFont1', 'MyFont1.otf'))
    pdfmetrics.registerFont(TTFont('MyFont2', 'MyFont2.otf'))
    pdfmetrics.registerFont(TTFont('MyFont3', 'MyFont3.otf'))

# Randomly choose font
def get_random_font():
    fonts = ['MyFont1', 'MyFont2', 'MyFont3']
    return random.choice(fonts)

# Get a random shade of black between #000000 and #191919
def get_random_black_shade():
    shade = random.randint(0, 40)  # 0x00 to 0x19 in hex (40 possible shades)
    hex_color = f'#{shade:02x}{shade:02x}{shade:02x}'
    return HexColor(hex_color)

# Create the PDF from text
def text_to_pdf(input_file, output_file):
    register_fonts()

    # Page and margin dimensions in cm
    page_width, page_height = 21.7 * cm, 27.8 * cm
    left_margin, right_margin = 1.6 * cm, 2 * cm  # Adjusted left margin to 1.7 cm
    top_margin = 3.9 * cm
    line_height = 0.78 * cm  # Adjusted line height to 0.75 cm
    max_lines_per_page = 31
    font_size = 22  # Increased font size to 22
    letter_spacing_factor = 0.8  # Adjusted letter spacing factor

    # Create a PDF canvas
    c = canvas.Canvas(output_file, pagesize=(page_width, page_height))
    x_start = left_margin
    y_start = page_height - top_margin

    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    x, y = x_start, y_start
    line_count = 0

    for line in lines:
        # Handle line skips
        if line.strip() == '':
            x = x_start
            y -= line_height
            line_count += 1
            if line_count >= max_lines_per_page:
                c.showPage()
                x, y = x_start, y_start
                line_count = 0
            continue

        words = line.split(' ')  # Split by space to handle tabs separately

        for word in words:
            # Handle tab characters
            if '\t' in word:
                tab_space = pdfmetrics.stringWidth(' ', get_random_font(), font_size) * 4
                x += tab_space  # Add tab space

            # Calculate the width of the word
            word_width = sum(pdfmetrics.stringWidth(char, get_random_font(), font_size) * letter_spacing_factor for char in word)

            # If word would exceed the right margin, move to the next line
            if x + word_width > (page_width - right_margin):
                x = x_start
                y -= line_height
                line_count += 1

                if line_count >= max_lines_per_page:
                    c.showPage()
                    x, y = x_start, y_start
                    line_count = 0

            # Draw each character of the word with random fonts and colors
            for char in word:
                font = get_random_font()
                color = get_random_black_shade()  # Random shade of black
                c.setFont(font, font_size)
                c.setFillColor(color)
                c.drawString(x, y, char)
                x += pdfmetrics.stringWidth(char, font, font_size) * letter_spacing_factor

            # Add increased space after the word
            x += pdfmetrics.stringWidth(' ', get_random_font(), font_size)

        # Move to the next line for the newline character
        x = x_start
        y -= line_height
        line_count += 1

        if line_count >= max_lines_per_page:
            c.showPage()
            x, y = x_start, y_start
            line_count = 0

    c.save()

# Convert text.txt to text.pdf
text_to_pdf('text.txt', 'text.pdf')