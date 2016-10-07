from paste.deploy import loadapp
from waitress import serve

from opreturnninja.config import config

if __name__ == "__main__":
    app = loadapp('config:production.ini', relative_to='.')
    serve(app, host='0.0.0.0', port=config.PORT)
