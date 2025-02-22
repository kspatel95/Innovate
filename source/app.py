import dash
from dash import Dash, html, Input, Output, State, callback
import dash_mantine_components as dmc
import os
from flask import Flask, request, redirect, session, url_for
import orjson
from authlib.integrations.flask_client import OAuth
import logging
import secrets_mgr


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Secrets
try:
    gcloud_creds = orjson.loads(secrets_mgr.access_secret_version("gcloud"))
    os.environ["SECRET_KEY"] = gcloud_creds.get("client_secret")
    os.environ["CLIENT_ID"] = gcloud_creds.get("client_id")
    os.environ["CLIENT_SECRET"] = gcloud_creds.get("client_secret")
except:
    gcloud_creds = ""
    os.environ["SECRET_KEY"] = ""
    os.environ["CLIENT_ID"] = ""
    os.environ["CLIENT_SECRET"] = ""
try:
    os.environ["OPENAI_API_KEY"] = secrets_mgr.access_secret_version("openai")
except:
    os.environ["OPENAI_API_KEY"] = ""


server = Flask(__name__)
server.config.update(SECRET_KEY=os.getenv("SECRET_KEY"))

app = Dash(__name__, 
           server=server, 
           use_pages=True)

app.layout = dash.page_container
app._favicon = "assets/favicon.ico"

server = app.server

oauth = OAuth(server)

google = oauth.register(
    name='google',
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    api_base_url='https://www.googleapis.com/oauth2/v3/',
    client_kwargs={'scope': 'openid profile email'}
)
        
# Flask routes for OAuth
@server.route('/signingoogle')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@server.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    resp.raise_for_status()
    user_info = resp.json()
    session['email'] = user_info
    return redirect('/')

@callback(
    Output('avatar_indicator', 'children'),
    Input("url", "pathname"),
)
def update_user_initials(url):
    user =''
    image=''
    size=0
    if  url =='/logout':
        user = ""
        size=0
    elif 'email' in session:
        acount = session['email']
        user = f"{acount.get('given_name', '')[:1]}{acount.get('family_name', '')[:1]}"
        image = acount.get('picture', '')
        size=8
    status = dmc.Indicator(
            dmc.Avatar(
                style = {"cursor": "pointer" },
                size="md",
                radius="xl",
                src=image,
            ),
            offset=3,
            position="middle-start",
            styles={
                "indicator": {"height": '20px', "padding": '2px', 'paddingInline':'0px'},
            },
            color='dark',
            size=size,
            label = user,
            withBorder=True,
            id = 'indicator'
        )
    return  status

if __name__ == "__main__":
    app.run(debug=True, port= 8050)