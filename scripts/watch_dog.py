import os
import sys
import re
import logging


logging.basicConfig(level=logging.INFO)

from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route("/deploy", methods=['POST'])
def add():
    print(request.form) 
    query = request.form["params"].strip()
    print("is ok now")
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True, port=8082)
