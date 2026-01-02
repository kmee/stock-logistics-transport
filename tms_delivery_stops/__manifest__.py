{
    "name": "TMS Delivery Stops",
    "version": "18.0.1.0.0",
    "category": "Inventory/Transport",
    "summary": "Support for multiple delivery stops per TMS order",
    "author": "KMEE, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-transport",
    "license": "AGPL-3",
    "depends": [
        "tms",
        "base_geolocalize",
        "uom",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/tms_order_stop.xml",
        "views/tms_order.xml",
    ],
    "demo": [
        "data/demo_data.xml",
    ],
    "installable": True,
    "application": False,
}
