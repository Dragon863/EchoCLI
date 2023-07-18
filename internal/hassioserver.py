import requests
from flask import Flask

HASS_LOCATION = "homeassistant.example.com"
YOUR_HOME_ASSISTANT_API_KEY = "12345678"
ENTITY_NAME = "text.led_color"


def get_text_entity_value(entity_name, base_url, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    url = f"{base_url}/api/states/{entity_name}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data["state"]
    else:
        return None


app = Flask(__name__)


@app.route("/led")
def led_color():
    base_url = f"http://{HASS_LOCATION}:8123"
    value = get_text_entity_value(ENTITY_NAME, base_url, YOUR_HOME_ASSISTANT_API_KEY)
    if value is not None:
        return value
    else:
        return "Error fetching LED color."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
