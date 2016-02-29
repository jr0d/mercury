import os
import bottle


app = bottle.Bottle()
root = os.path.abspath(os.path.dirname(__file__))
bottle.TEMPLATE_PATH.append(os.path.join(root, "templates"))


# noinspection PyUnresolvedReferences
@app.route('/static/<filepath:path>')
def static_javascript(filepath):
    return bottle.static_file(filepath, root=os.path.join(root, 'static'))


@app.route('/', method='GET')
@bottle.view('index')
def index_page():
    return {}


bottle.run(app, host='localhost', port=9006)