from flask import render_templates
from app import create_app

app = create_app()

@app.route('/')
def home():
    return render_template('base.html')

