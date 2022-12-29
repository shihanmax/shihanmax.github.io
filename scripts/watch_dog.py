import os
import sys
import re
import time
import logging


logging.basicConfig(level=logging.INFO)

from flask import Flask

app = Flask(__name__)


@app.route("/hook", methods=['POST'])
def hook():
    os.system("git pull")
    print(f"Update at {time.ctime()}")
    
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8082)
