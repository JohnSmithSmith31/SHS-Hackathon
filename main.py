from flask import Flask, render_template, request, send_file, url_for
import random
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor
import os

app = Flask(__name__)

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
    shade = random.randint(0, 40)
    hex_color = f'#{shade:02x}{shade:02x}{shade:02x}'
    return HexColor(hex_color)

# Create the PDF from text
def text_to_pdf(input_file, output_file):
    register_fonts()
    page_width, page_height = 21.7 * cm, 27.8 * cm
    left_margin, right_margin = 1.6 * cm, 2 * cm
    top_margin = 3.9 * cm
    line_height = 0.78 * cm
    max_lines_per_page = 31
    font_size = 22
    letter_spacing_factor = 0.8

    c = canvas.Canvas(output_file, pagesize=(page_width, page_height))
    x_start = left_margin
    y_start = page_height - top_margin

    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    x, y = x_start, y_start
    line_count = 0

    for line in lines:
        if line.strip() == '':
            x = x_start
            y -= line_height
            line_count += 1
            if line_count >= max_lines_per_page:
                c.showPage()
                x, y = x_start, y_start
                line_count = 0
            continue

        words = line.split(' ')

        for word in words:
            if '\t' in word:
                tab_space = pdfmetrics.stringWidth(' ', get_random_font(), font_size) * 4
                x += tab_space

            word_width = sum(pdfmetrics.stringWidth(char, get_random_font(), font_size) * letter_spacing_factor for char in word)

            if x + word_width > (page_width - right_margin):
                x = x_start
                y -= line_height
                line_count += 1

                if line_count >= max_lines_per_page:
                    c.showPage()
                    x, y = x_start, y_start
                    line_count = 0

            for char in word:
                font = get_random_font()
                color = get_random_black_shade()
                c.setFont(font, font_size)
                c.setFillColor(color)
                c.drawString(x, y, char)
                x += pdfmetrics.stringWidth(char, font, font_size) * letter_spacing_factor

            x += pdfmetrics.stringWidth(' ', get_random_font(), font_size)

        x = x_start
        y -= line_height
        line_count += 1

        if line_count >= max_lines_per_page:
            c.showPage()
            x, y = x_start, y_start
            line_count = 0

    c.save()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text_content = request.form['text']
        with open('text.txt', 'w', encoding='utf-8') as f:
            f.write(text_content)
        text_to_pdf('text.txt', 'static/text.pdf')
        return render_template('index.html', pdf_url=url_for('static', filename='text.pdf'))

    return render_template('index.html', pdf_url=None)

if __name__ == '__main__':
    app.run(debug=True)