from flask import Blueprint, request

cart_controller = Blueprint("cart", __name__)


@cart_controller.route("/cart", methods=["POST"])
def add_cart():
    print(request.json)
    return []
