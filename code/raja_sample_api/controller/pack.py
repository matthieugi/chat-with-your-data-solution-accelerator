import json

from flask import Blueprint

pack_controller = Blueprint("pack", __name__)

catalog = json.load(open("asset/catalog.json"))


@pack_controller.route("/pack", methods=["POST"])
def create_pack():
    item = catalog[0]
    [sku, sku_title, short_description] = [
        item.get("SKU"),
        item.get("SKU Title"),
        item.get("short-description"),
    ]

    return [
        {"sku": sku, "sku_title": sku_title, "short_description": short_description}
    ]
