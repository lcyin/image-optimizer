from flask import render_template
from flask import current_app as app

# app = create_app()

@app.route('/')
def home():
    print('we got here')
    return render_template('base.html')

# add route to see all registered routes
@app.route('/routes')
def routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f"{rule.endpoint} - {rule.rule}")
    return  "<br>".join(routes)
