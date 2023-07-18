from datetime import datetime

from flask import Flask, request


app = Flask(__name__)


def handle_request():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"Received audio at {timestamp}")

    # Get the uploaded file
    audio_file = request.files["file"]
    if audio_file:
        filename = "out.wav"
        audio_file.save(filename)
        print(f"File saved.")


@app.route("/audio", methods=["PUT", "POST"])
def audio_endpoint():
    handle_request()
    return "200"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
