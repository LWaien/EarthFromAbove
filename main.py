from flask import Flask, request, render_template
import os
from sat_img import fetch_satellite_image  # Assuming the function is in this file

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        latitude = float(request.form.get("latitude"))
        longitude = float(request.form.get("longitude"))
        fetch_satellite_image(latitude, longitude)
        coordinates_str = f"{latitude:.4f}_{longitude:.4f}"
        image_filename = f"{coordinates_str}.png"
        return render_template("index.html", image_filename=image_filename)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
