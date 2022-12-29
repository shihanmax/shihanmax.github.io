import os
import sys
import re
import logging


logging.basicConfig(level=logging.INFO)

from flask import Flask

app = Flask(__name__)


@app.route("/hook", methods=['POST'])
def hook():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(debug=True, port=8082)
