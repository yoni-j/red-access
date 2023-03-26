from flask import Flask
from flask import request
from service import ConfigurationService

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def configuration():
    if request.method == 'GET':
        return ConfigurationService.get_configuration()
    data = request.get_json()
    ConfigurationService.update_configuration(data)
    return {"status": "updated"}


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
