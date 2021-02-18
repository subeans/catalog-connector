from chalice import Chalice
from chalice import Chalice ,AuthResponse  , Response
from jinja2 import Environment, PackageLoader, select_autoescape
from chalicelib import select
import os 

app = Chalice(app_name='catalog-connector-front')

"""
수정 필요한 부분 : token 처리 방식 
"""
token = os.environ['FACEBOOK_TOKEN']

env = Environment(
    loader=PackageLoader(__name__, 'chalicelib/templates'),
    autoescape=select_autoescape(['html', 'xml']))


@app.route('/',cors = True)
def index():   
    return render_template('main.html')


def render_template(template_name, status_code=200, content_type='text/html', headers=None):
    template = env.get_template(template_name)
    body = template.render()

    if headers is None:
        headers = {}

    headers.update({
        'Content-Type': content_type,
        'Access-Control-Allow-Origin': '*' 
    })

    return Response(body=body, status_code=status_code, headers=headers)


@app.authorizer()
def demo_auth(auth_request):
    if token == 'allow':
        return AuthResponse(routes=['/'], principal_id='user')
    else:
        return AuthResponse(routes=[''], principal_id='user')

# @app.route('/top/{name}',authorizer=demo_auth)
@app.route('/top/{name}')
def selectN(name):
    """
    default 
    """
    pick_option = "all"
    N = 3

    params = app.current_request.query_params
    try:
        if 'pick_option' in params:
            pick_option = params['pick_option']
        if N in params :
            N = params['N']
    except:
        pass
    show_info = select.select_act(name,N,pick_option)

    return show_info


@app.route('/top/test/{name}',cors = True)
def test(name):
    
    show_info=selectN(name)

    return {'Test': show_info}
