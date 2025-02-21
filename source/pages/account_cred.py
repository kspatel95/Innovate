import dash
from dash import html
import dash_mantine_components as dmc 
from flask import session
import json
from dash_iconify import DashIconify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# dash.register_page(__name__)
loginButtonStyle =   {
    # "background": "#E418C2ff",
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
    # "textDecorationColor": "white"
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
                    # dmc.TextInput(
                    #     label="Email",
                    #     name='email',
                    #     placeholder="Enter your Email",
                    #     required = True,

                    #     # leftSection=iconify(icon="ic:round-alternate-email", width=20),
                    # ),
                    # dmc.PasswordInput(
                    #     mb=20,
                    #     label="Password",
                    #     placeholder="Enter your password",
                    #     # leftSection=iconify(icon="bi:shield-lock", width=20),
                    #     name='password',
                    #     required = True
                    # ),
                    # html.Button(
                    #     children="Sign in", 
                    #     n_clicks=0, 
                    #     type="submit", 
                    #     id="login-button", 
                    #     style =loginButtonStyle
                    # ),
                    # dmc.Divider(label="Or continue with", mb = 10, mt = 10),
                    html.A(
                        href='/signingoogle', 
                        style = loginWithGoogleStyle,
                        children = [
                            dmc.Button(
                                "Google",
                                variant="outline",
                                # color = "#E418C2ff",
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

def logout_layout(**kwargs):
    session.pop('email', None)
    return html.Div(
        [
            html.Div(html.H2("You have been logged out")),
            
        ]
    )

def register_layout():
    return dmc.Center(
    dmc.Paper(
        shadow='sm',
        p = "30px",
        mt = 60,
        children = [
            html.Form(
                style = {"width":'300px'},
                method='POST',
                children = [
                    dmc.Text("Sign up",  size='xl', fw=700),
                    dmc.Text("Please up in to continue", c='gray', size='xs', mb = 10),
                    dmc.TextInput(
                        label="First Name",
                        name='given_name',
                        placeholder="Enter your first name",
                        required = True,
                    ),
                    dmc.TextInput(
                        label="Last Name",
                        name='family_name',
                        placeholder="Enter your last name",
                        required = True,
                    ),
                    dmc.TextInput(
                        label="Email",
                        name='email',
                        placeholder="Enter your Email",
                        required = True,
                        # leftSection=iconify(icon="ic:round-alternate-email", width=20),
                    ),
                    dmc.PasswordInput(
                        mb=20,
                        label="Password",
                        placeholder="Enter your password",
                        # leftSection=iconify(icon="bi:shield-lock", width=20),
                        name='password',
                        required = True
                    ),
                    html.Button(
                        children="Sign up", 
                        n_clicks=0, 
                        type="submit", 
                        id="register-button", 
                        style =loginButtonStyle
                    ),
                    dmc.Flex(
                         mt = 10,
                        align = 'center',
                        children = [
                            dmc.Text(f"Already have an Account?", c='gray', size = 'xs'),
                            html.A('Sign in', href='/login', style = {'fontSize':'12px'})
                        ]
                    )  
                ]
            )
        ]
    )
)

def secret_layout(**kwargs):
    if 'email' in session:
        acount = session['email']
        acount = json.dumps(acount, indent=4)
        return dmc.Center(
                    mt= 50, pt=50,
                    children = [   
                        dmc.Paper(
                        pt=20,
                        shadow='sm',
                        children=[
                            dmc.Text("Here are your account details"),
                            dmc.CodeHighlight(
                                language="json",
                                code=str(acount),
                            )
                        ]
                    )
                ]
            )

    else:   
        return dmc.Center(
            m = 30,
            children =[
                dmc.Flex(
                    align="center",
                    children=[
                        dmc.Text("This page requires login. Please", p =5),
                        html.A('login', href='/login'),
                        dmc.Text("to continue", p = 5),
                    ]
                )
            ]
        )

def layout(request="signingoogle"):
    if request in ["login", "signingoogle"]:
        return login_layout()
    elif request == "register":
        return register_layout()
    elif request == "logout":
        return logout_layout()
    elif request == "secret":
        return secret_layout()
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
