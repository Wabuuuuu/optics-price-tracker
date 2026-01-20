"""
Product Configuration
Add all products you want to track here
"""

PRODUCTS = [
    {
        "id": 1,
        "name": "Vortex Viper PST Gen II 5-25x50",
        "brand": "Vortex",
        "urls": {
            "OpticsPlanet": "https://www.opticsplanet.com/vortex-viper-pst-gen-ii-riflescope.html",
            "Brownells": "https://www.brownells.com/optics-mounting/scopes/rifle-scopes/viper-pst-gen-ii-5-25x50-riflescope-prod105146.aspx",
        }
    },
    {
        "id": 2,
        "name": "Aimpoint PRO",
        "brand": "Aimpoint",
        "urls": {
            "OpticsPlanet": "https://www.opticsplanet.com/aimpoint-pro-patrol-rifle-optic.html",
            "Primary Arms": "https://www.primaryarms.com/aimpoint-patrol-rifle-optic-pro-red-dot-sight-2-moa-with-mount",
        }
    },
]

DATABASE_PATH = "data/price_data.json"
DELAY_BETWEEN_REQUESTS = 3
SCREENSHOT_ENABLED = True
MAX_RETRIES = 2
