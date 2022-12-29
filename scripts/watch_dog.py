import logging
import os
import time


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from flask import Flask

app = Flask(__name__)


@app.route("/hook", methods=['POST'])
def hook():
    os.system("git pull")
    logger.info(f"Update at {time.ctime()}")
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082)
