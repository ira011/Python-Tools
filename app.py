from flask import Flask, request, render_template, send_file
from rembg import remove
from pdf2docx import Converter
from PIL import Image
import moviepy as mp
import os
from gtts import gTTS

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

# Remove background tool
@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    file = request.files['image']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    output_path = os.path.join(RESULT_FOLDER, 'no_bg_' + file.filename)
    file.save(input_path)

    inp = Image.open(input_path)
    output = remove(inp)
    output.save(output_path, format="PNG")
    return send_file(output_path, as_attachment=True)

# PDF to DOCX tool
@app.route('/convert-pdf', methods=['POST'])
def convert_pdf():
    try:
        file = request.files['pdf']
        if not file.filename.endswith('.pdf'):
            return "Error: The uploaded file is not a PDF.", 400

        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        output_path = os.path.join(RESULT_FOLDER, os.path.splitext(file.filename)[0] + '.docx')
        file.save(input_path)

        # Convert PDF to DOCX
        cv = Converter(input_path)
        cv.convert(output_path, start=0, end=None)
        cv.close()
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"Error: {e}", 500

# Video compression tool
@app.route('/compress-video', methods=['POST'])
def compress_video():
    file = request.files['video']
    target_size = float(request.form['target_size'])
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    output_path = os.path.join(RESULT_FOLDER, 'compressed_' + file.filename)
    file.save(input_path)

    try:
        video = mp.VideoFileClip(input_path)
        duration = video.duration
        target_size_bytes = target_size * 1024 * 1024
        target_bitrate = (target_size_bytes * 8) / duration

        video.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            bitrate=f"{int(target_bitrate)}"
        )
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"Error: {e}"

# Text-to-Speech tool
@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        text = request.form['text']
        if not text.strip():
            return "Error: No text provided for conversion.", 400

        output_path = os.path.join(RESULT_FOLDER, 'speech.mp3')

        # Convert text to speech
        tts = gTTS(text)
        tts.save(output_path)

        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
