import dash
from dash import html
import dash_mantine_components as dmc 
from flask import session
from dash_iconify import DashIconify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

loginButtonStyle =   {
    "padding": "5px 20px" ,
    "border": "none",
    "borderRadius": "20px",
    "color": "white",
    "fontSize":"16px",
    "width":"100%"
    
  }

loginWithGoogleStyle =   {
    "textDecoration": "none",
    "borderRadius": "50px",
  }

def login_layout():
    return dmc.Center(
    dmc.Paper(
        shadow='sm',
        p = "30px",
        radius="lg",
        mt = 140,
        children = [
            html.Form(
                style = {"width":'300px'},
                method='POST',
                children = [
                    dmc.Text("Sign in ",  size='xl', fw=700),
                    dmc.Text("Please log in to continue", c='gray', size='xs', mb = 10),
                    html.A(
                        href='/signingoogle', 
                        style = loginWithGoogleStyle,
                        children = [
                            dmc.Button(
                                "Google",
                                variant="outline",
                                fullWidth=True,
                                radius='xl',
                                leftSection=DashIconify(icon="flat-color-icons:google"),
                            ),
                        ]
                    )
                ]
            )
        ]
    )
)

def layout(request="signingoogle"):
    if request in ["login", "signingoogle"]:
        return login_layout()
    else:
        return login_layout()

dash.register_page(
    __name__,
    path="/signingoogle",
    layout=layout(),
    title='Account',
    name='Account',
    image="assets/favicon.ico",
)
