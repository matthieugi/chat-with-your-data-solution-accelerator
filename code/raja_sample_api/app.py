import os

from controller.cart import cart_controller
from controller.pack import pack_controller
from flask import Flask


DEBUG = os.getenv("DEBUG", "False") == "True"
URL_PREFIX = os.getenv("URL_PREFIX", "/api")
APPINSIGHTS_CONNECTION_STRING = os.getenv("APPINSIGHTS_CONNECTION_STRING")

app = Flask(__name__, static_folder="public")

app.register_blueprint(pack_controller, url_prefix=URL_PREFIX)
app.register_blueprint(cart_controller, url_prefix=URL_PREFIX)

# Run the app
if __name__ == "__main__":
    print("Starting Flask app")
    app.run(debug=DEBUG, host="127.0.0.1", port="5001")
