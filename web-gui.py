import os
import random
import json
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory # type: ignore
from reportlab.pdfgen import canvas # type: ignore
from reportlab.lib.units import cm # type: ignore
from reportlab.pdfbase.ttfonts import TTFont # type: ignore
from reportlab.pdfbase import pdfmetrics # type: ignore
from reportlab.lib.colors import HexColor # type: ignore
import google.generativeai as genai # type: ignore


# Initialize Flask app
app = Flask(__name__)

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyDv6DdxRlx1s9mryMusCtZqSK9LEPI1o3E" # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

# Available Gemini models
GEMINI_MODELS = ["gemini-1.5-flash", "gemini-2.0-pro-exp-02-05"]

# Constants for PDF generation - now defaults, adjustable via GUI
DEFAULT_CONSTANTS = {
    'PAGE_WIDTH_CM': 21.7,
    'PAGE_HEIGHT_CM': 27.8,
    'LEFT_MARGIN_CM': 1.7,
    'RIGHT_MARGIN_CM': 2.0,
    'TOP_MARGIN_CM': 3.9,
    'LINE_HEIGHT_CM': 0.75,
    'MAX_LINES_PER_PAGE': 32,
    'FONT_SIZE': 22,
    'LETTER_SPACING_FACTOR': 0.8,
    'TAB_WIDTH': 4,  # Number of spaces per tab
}

FONTS = ['font-1', 'font-2', 'font-3']
FONT_PATH = "fonts/"

# Chat history file - NOT USED ANYMORE
CHAT_HISTORY_FILE = "chat_history.json"

# Ensure necessary directories exist
os.makedirs("static", exist_ok=True)
os.makedirs(FONT_PATH, exist_ok=True)

def register_fonts():
    """Register the required fonts."""
    for font in FONTS:
        try:
            pdfmetrics.registerFont(TTFont(font, f"{FONT_PATH}{font}.otf"))
        except:
            print(f"Warning: Font {font} not found. Please place it in the {FONT_PATH} directory.")

def get_random_font():
    """Return a random font from the registered fonts."""
    return random.choice(FONTS)

def get_random_black_shade():
    """Generate a random dark shade between #000000 and #191919."""
    shade = random.randint(0, 0x19)  # 0x00 to 0x19 in hex
    hex_color = f'#{shade:02x}{shade:02x}{shade:02x}'
    return HexColor(hex_color)

def text_to_pdf(content, output_file, constants):
    """Convert text content to a formatted PDF with adjustable constants."""
    register_fonts()

    PAGE_WIDTH = constants['PAGE_WIDTH_CM'] * cm
    PAGE_HEIGHT = constants['PAGE_HEIGHT_CM'] * cm
    LEFT_MARGIN = constants['LEFT_MARGIN_CM'] * cm
    RIGHT_MARGIN = constants['RIGHT_MARGIN_CM'] * cm
    TOP_MARGIN = constants['TOP_MARGIN_CM'] * cm
    LINE_HEIGHT = constants['LINE_HEIGHT_CM'] * cm
    MAX_LINES_PER_PAGE = constants['MAX_LINES_PER_PAGE']
    FONT_SIZE = constants['FONT_SIZE']
    LETTER_SPACING_FACTOR = constants['LETTER_SPACING_FACTOR']
    TAB_WIDTH = constants['TAB_WIDTH']

    c = canvas.Canvas(output_file, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    x_start = LEFT_MARGIN
    y_start = PAGE_HEIGHT - TOP_MARGIN

    lines = content.split('\n')

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
    return output_file


# Route for the main page
@app.route('/')
def index():
    # Try to read content.txt if it exists
    content = ""
    try:
        with open('content.txt', 'r', encoding='utf-8') as file:
            content = file.read()
    except:
        # If file doesn't exist, create it with empty content
        with open('content.txt', 'w', encoding='utf-8') as file:
            pass

    # Chat history - NOT USED ANYMORE
    chat_history = [] # load_chat_history() - no loading anymore

    return render_template('index.html',
                           content=content,
                           chat_history=chat_history, # Empty history
                           models=GEMINI_MODELS,
                           constants=DEFAULT_CONSTANTS) # Pass constants to template

# Route to serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Route to get default constants
@app.route('/get_constants')
def get_constants():
    return jsonify(DEFAULT_CONSTANTS)

# Route to reset constants to default
@app.route('/reset_constants', methods=['POST'])
def reset_constants():
    return jsonify(DEFAULT_CONSTANTS)

# Route to save content
@app.route('/save_content', methods=['POST'])
def save_content():
    content = request.form.get('content', '')

    with open('content.txt', 'w', encoding='utf-8') as file:
        file.write(content)

    return jsonify({"status": "success", "message": "Content saved successfully"})

# Route to generate PDF
@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    content = request.form.get('content', '')
    constants_from_gui = request.form.to_dict() # Get all form data as constants

    # Use default constants and override with GUI values if provided
    constants = DEFAULT_CONSTANTS.copy()
    for key in constants:
        gui_key = key # Assuming keys are the same in GUI and backend
        if gui_key in constants_from_gui and constants_from_gui[gui_key]: # check if value is not empty string
            try:
                constants[key] = type(DEFAULT_CONSTANTS[key])(constants_from_gui[gui_key]) # Convert to correct type
            except ValueError:
                print(f"Warning: Invalid value for {key} from GUI. Using default.")

    # Save content to file
    with open('content.txt', 'w', encoding='utf-8') as file:
        file.write(content)

    # Generate PDF
    pdf_path = 'static/content.pdf'
    text_to_pdf(content, pdf_path, constants)

    return jsonify({"status": "success", "pdf_url": "/static/content.pdf"})


# Route to download PDF
@app.route('/download_pdf')
def download_pdf():
    return send_file('static/content.pdf', as_attachment=True)


# Route to chat with Gemini
@app.route('/chat', methods=['POST'])
def chat():
    message = request.form.get('message', '')
    model_name = request.form.get('model', GEMINI_MODELS[0])

    # Validate model selection
    if model_name not in GEMINI_MODELS:
        model_name = GEMINI_MODELS[0]

    try:
        # Initialize Gemini model
        model = genai.GenerativeModel(model_name)


        # Get response from Gemini - stateless now, no history
        response = model.generate_content(message) # Simple stateless call
        response_text = response.text

        # Chat history - NOT SAVING ANYMORE

        return jsonify({
            "status": "success",
            "response": response_text
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error communicating with Gemini: {str(e)}"
        })

# Route to clear chat history - NOT USED ANYMORE
@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    # save_chat_history([]) - No saving anymore
    return jsonify({"status": "success", "message": "Chat history cleared"}) # Still return success for frontend compatibility in case button is not fully removed


if __name__ == "__main__":
    app.run(debug=True)