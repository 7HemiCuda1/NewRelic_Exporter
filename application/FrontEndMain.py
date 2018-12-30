from flask import request, render_template, jsonify, g
from index import app


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
