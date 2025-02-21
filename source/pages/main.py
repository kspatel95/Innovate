import dash
from dash import Dash, Input, Output, State, callback, _dash_renderer, html, dcc, dash_table, MATCH, ALL, no_update, ctx
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import pandas as pd
from collections import OrderedDict
from dash_iconify import DashIconify
from datetime import datetime
import pytz
import timezonefinder
import orjson
from openai import OpenAI
import logging
import os
import flask
_dash_renderer._set_react_version("18.2.0")
from pages import pri
from pages import account_cred
import secrets_mgr


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ask_chatGPT(prompt):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # Requires funding the account: https://platform.openai.com/settings/organization/billing/overview
    try:
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt}",
                }
            ],
            model="gpt-4o-mini",
        )
        logger.info(completion.choices[0].message)
        return completion.choices[0].message
    except:
        return "Could not complete request"

block_style = {"background": "black", "padding": "10px", "borderRadius": "20px", "height": "content", "width": "content", "minHeight": "300px", "minWidth": "300px", "border": "1px solid rgba(0, 0, 0, 0.1)"}
transparent_banner_style = {"background": "rgba(255, 255, 255, 0.1)", "backdropFilter": "blur(10px)", "WebkitBackdropFilter": "blur(10px)", "height": "50px", "borderRadius": "24px", "border": "1px solid rgba(255, 255, 255, 0.1)", "marginRight": "5px"}
light_transparent_banner_style = {"background": "rgba(0, 0, 0, 0.1)", "backdropFilter": "blur(10px)", "WebkitBackdropFilter": "blur(10px)", "height": "50px", "borderRadius": "24px", "border": "1px solid rgba(0, 0, 0, 0.1)", "marginRight": "5px"}
transparent_block_style = {"background": "rgba(255, 255, 255, 0.1)", "backdropFilter": "blur(10px)", "WebkitBackdropFilter": "blur(10px)", "height": "content", "width": "content", "padding": "20px", "borderRadius": "20px", "border": "1px solid rgba(255, 255, 255, 0.1)"}
transparent_sub_block_style = {"background": "rgba(255, 255, 255, 0.1)", "height": "content", "width": "content", "padding": "20px", "borderRadius": "20px", "border": "1px solid rgba(255, 255, 255, 0.1)"}
transparent_menu_style = {"background": "rgba(255, 255, 255, 0.1)", "backdropFilter": "blur(10px)", "WebkitBackdropFilter": "blur(10px)", "height": "content", "width": "content", "padding": "0px", "borderRadius": "20px", "border": "1px solid rgba(255, 255, 255, 0.1)"}

# Theme Toggle
theme_toggle = dmc.ActionIcon(
    children=[
        dmc.Paper(DashIconify(icon="radix-icons:sun", width=20), bg="transparent", radius=20, darkHidden=True),
        dmc.Paper(DashIconify(icon="radix-icons:moon", width=20), bg="transparent", radius=20, lightHidden=True),
    ],
    variant="transparent",
    color="yellow",
    id="color_scheme_toggle",
    size="lg",
    ms="auto",
    n_clicks=0,
)

# Account
user = html.A(
        dmc.Tooltip(
            children=dmc.Avatar(src="assets/avatar.png", radius=20, style={"border": "0.5px solid rgba(255,255,255,0.2)"}),
            label="Krishan Patel",
            position="bottom",
        ),
    href="https://www.linkedin.com/in/kspatel95/",
    target="_blank",
)

# Login Menu
login = dmc.Flex(
            children = [
                dmc.Menu(
                    children = [
                        dmc.MenuTarget(
                            children=[
                                dmc.Box(id="avatar_indicator"),
                            ],
                        ),
                        dmc.MenuDropdown(
                            children=[
                                dmc.MenuItem(
                                    children=[
                                        dmc.NavLink(
                                            label="🔓 Login",
                                            href='/signingoogle',
                                        ),
                                    ],
                                ),
                                dmc.MenuItem(
                                    children=[
                                        dmc.NavLink(
                                            label="🔒 Logout",
                                            href='/logout',
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ) 

# Time
local_timezone = pytz.timezone('America/Los_Angeles')
local_now = dmc.Title(datetime.now(local_timezone).strftime("%I:%M %p %Z"), id="time_display", order=6)
time_module = dmc.Badge(dmc.Group(children=[local_now, login, dcc.Geolocation(id="geolocation", update_now=False, show_alert=True, maximum_age=3600000)], h="content"), size="lg", pr=0, h=40, color="rgba(255,255,255,0.1)")

# Backgrounds
background_dark = dmc.Affix(
    zIndex=0,
    position={"top": 20, "left": 130, "right": 130},
    lightHidden=True,
    children=[
        html.Div(
            style=transparent_banner_style,
        ),
    ],
)

background_light = dmc.Affix(
    zIndex=0,
    position={"top": 20, "left": 130, "right": 130},
    darkHidden=True,
    children=[
        html.Div(
            style=light_transparent_banner_style,
        ),
    ],
)

# Banner
def banner(page):
    if page:
        page = f"/{page}"
    else:
        page = "/home"
    return dmc.Affix(
            zIndex=1,
            position={"top": 31, "left": 150, "right": 150},
            children=[
                dmc.Grid(
                    align="center",
                    children=[
                        dmc.Title("Innovate", order=1, style={"paddingLeft": "10px", "paddingRight": "10px"}),
                        dmc.SegmentedControl(
                            id="page_selector",
                            data=[
                                {"label": "Home", "value": "/home"},
                                {"label": "Cafe", "value": "/cafe"},
                                {"label": "Hospitality", "value": "/hospitality"},
                            ],
                            value=page,
                            withItemsBorders=False,
                            size="sm",
                            radius=20,
                            color="blue",
                            bg="rgba(255, 255, 255, 0.15)",
                        ),
                        theme_toggle,
                        time_module,
                    ],
                ),
                background_dark,
                background_light,
            ],
)

# Home Content
home_content = dmc.Center(
    dmc.Group(
        id="home_content",
        mt=100,
        align="center",
        children=[
            html.Div(
                style=transparent_block_style,
                children=[
                    dmc.Title("Welcome", order=3),
                    dmc.Divider(h="sm"),
                    dmc.Text("Welcome to Innovate!"),
                    dmc.Text("This is intended for visualizing some user experiences and showcasing my skills."),
                    dmc.Space(h="sm"),
                    dmc.Text("This is a work in progress and will be updated frequently."),
                    dmc.Text("Please check back often for new features and improvements."),
                    dmc.Space(h="sm"),
                    dmc.Text("Thank you for visiting!"),
                    dmc.Space(h="sm"),
                    dmc.Divider(h="sm"),
                    dmc.Text("Feel free to reach out to me at: kspatel95@gmail.com"),
                ],
            ),
        ],
    ),
)

# Cafe Content
def cafe_content(menu):
    if menu in ["☕️ Drinks", "🥪 Food", "🧢 Other", "🛒 Order"]:
        menu = menu
    elif menu in ["drinks", "food", "other", "order"]:
        menu = menu.capitalize()
        if menu == "Drinks":
            menu = "☕️ Drinks"
        elif menu == "Food":
            menu = "🥪 Food"
        elif menu == "Other":
            menu = "🧢 Other"
        elif menu == "Order":
            menu = "🛒 Order"
    else:
        menu = "☕️ Drinks"

    drinks_list = ["Cappuccino", "Americano", "Cortado", "Latte", "Shakkerato", "Drip Coffee", "Chai", "Matcha", "Tea", "Hot Chocolate", "Milk"]
    food_list = ["Croissant", "Breakfast Sandwich", "Breakfast Burrito", "Bagel", "Avocado Toast", "Granola & Yogurt", "Fruit Cup"]
    other_list = ["Hat", "T Shirt", "Sweatshirt", "Mug", "Coffee Beans", "Tea Leaves", "Matcha Powder"]
    drinks_menu = [dmc.List(children=[dmc.ListItem(dmc.Button(drink, id={"type": "cafe_menu_drinks_item", "index": drink.lower().replace(" ","_")}, variant="subtle", radius=20, color="primary")) for drink in drinks_list if drinks_list.index(drink) <= len(drinks_list) // 2]), dmc.List(children=[dmc.ListItem(dmc.Button(drink, id={"type": "cafe_menu_drinks_item", "index": drink.lower().replace(" ","_")}, variant="subtle", radius=20, color="primary")) for drink in drinks_list if drinks_list.index(drink) > len(drinks_list) // 2])]
    food_menu = [dmc.List(children=[dmc.ListItem(dmc.Button(food, id={"type": "cafe_menu_food_item", "index": food.lower().replace(" ","_")}, variant="subtle", radius=20, color="primary")) for food in food_list if food_list.index(food) <= len(food_list) // 2]), dmc.List(children=[dmc.ListItem(dmc.Button(food, id={"type": "cafe_menu_food_item", "index": food.lower().replace(" ","_")}, variant="subtle", radius=20, color="primary")) for food in food_list if food_list.index(food) > len(food_list) // 2])]
    other_menu = [dmc.List(children=[dmc.ListItem(dmc.Button(other, id={"type": "cafe_menu_other_item", "index": other.lower().replace(" ","_")}, variant="subtle", radius=20, color="primary")) for other in other_list if other_list.index(other) <= len(other_list) // 2]), dmc.List(children=[dmc.ListItem(dmc.Button(other, id={"type": "cafe_menu_other_item", "index": other.lower().replace(" ","_")}, variant="subtle", radius=20, color="primary")) for other in other_list if other_list.index(other) > len(other_list) // 2])]
    menu_layout = [dmc.Title("Menu", id="cafe_menu_title", order=3),dmc.Divider(h="sm")]
    menu_options = ["drinks", "food", "other"]
    for option in menu_options:
        menu_layout.append(dmc.Group(id=f"cafe_menu_{option}", justify="center", grow=True, pb=20, miw=800, children=eval(f"{option}_menu"), style=transparent_sub_block_style))
    
    return dmc.Center(
    dmc.Group(
        id="cafe_content",
        mt=100,
        align="center",
        children=[
            html.Div(
                style=transparent_menu_style,
                children=[
                    dbc.Popover(
                        "",
                        id="cafe_menu_hover",
                        target="cafe_menu_selector",
                        body=True,
                        trigger="hover",
                        delay={"show": 500, "hide": 500},
                    ),
                    dmc.SegmentedControl(
                        id="cafe_menu_selector",
                        data=
                        [
                            {"label": "☕️", "value": "☕️ Drinks"},
                            {"label": "🥪", "value": "🥪 Food"},
                            {"label": "🧢", "value": "🧢 Other"},
                            {"label": "🛒", "value": "🛒 Order"},
                        ],
                        value=menu,
                        orientation="vertical",
                        size="md",
                        radius=20,
                        withItemsBorders=False,
                        bg="transparent",
                    ),
                ],
            ),
            dmc.Stack(
                maw=1350,
                children=[
                    html.Div(
                        id="cafe_menu_layout",
                        style=transparent_block_style,
                        children=menu_layout,
                    ),
                    html.Div(
                        id="cafe_order_layout",
                        style=transparent_block_style,
                        children=[
                            html.Div(
                                style=transparent_sub_block_style,
                                children=[
                                    dmc.Group(
                                        miw=700,
                                        h=40,
                                        mt=-10,
                                        mb=0,
                                        justify="space-around",
                                        grow=True,
                                        children=[
                                            dmc.Popover(
                                                id="cafe_add_items",
                                                children=[
                                                    dmc.PopoverTarget(dmc.Button("+", color="green", radius=20)),
                                                    dmc.PopoverDropdown(
                                                        style={"borderRadius": "20px"},
                                                        bg="rgba(0,0,0,0.2)",
                                                        children=[
                                                            dmc.MultiSelect(
                                                                id="cafe_cart_items",
                                                                data=[
                                                                    {"group": "Drinks", "items": drinks_list},
                                                                    {"group": "Food", "items": food_list},
                                                                    {"group": "Other", "items": other_list},
                                                                ],
                                                                bg="transparent",
                                                                radius=20,
                                                                size="xs",
                                                                w=500,
                                                                clearable=True,
                                                                hidePickedOptions=True,
                                                                maxValues=8,
                                                                comboboxProps={"withinPortal": False},
                                                                leftSection=DashIconify(icon="bi-plus"),
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                            dmc.Text("🛒 Your cart is empty", id="cafe_cart_notification", ta="center"),
                                            dmc.Button("Place Order", id="cafe_place_order_button", color="blue", radius=20, disabled=True),
                                        ],
                                    ),
                                    dmc.Space(h="sm"),
                                    dmc.Group(
                                        id="cafe_order_items_customization",
                                        justify="center",
                                        align="start",
                                        grow=True,
                                    ),
                                    dmc.Group(
                                        id="cafe_order_summary",
                                        justify="start",
                                        align="start",
                                        # grow=True,
                                        display="none",
                                        children=[
                                            dmc.JsonInput(
                                                id="cafe_order_summary_json",
                                                autoComplete=True,
                                                validationError="Invalid JSON",
                                                formatOnBlur=True,
                                                autosize=True,
                                                minRows=4,
                                                radius=20,
                                                display="none",
                                            ),
                                            dmc.List(
                                                id="cafe_order_summary_list",
                                                icon=dmc.ThemeIcon(
                                                    DashIconify(icon="radix-icons:check-circled", width=16),
                                                    radius="xl",
                                                    color="teal",
                                                    size=24,
                                                ),
                                                size="md",
                                                w="content",
                                                spacing="sm",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    ),
)

def cafe_mods(item):
    has_mods = False
    mods_dictionary = {}
    if item == "Cappuccino":
        has_mods = True
        mods_dictionary = {"Milk": ["*2%", "Whole", "Alt"]}
    elif item == "Americano":
        has_mods = True
        mods_dictionary = {"Milk": ["*2%", "Whole", "Alt"], "Temperature": ["*Hot", "Iced"]}
    elif item == "Cortado":
        has_mods = True
        mods_dictionary = {"Milk": ["*2%", "Whole", "Alt"], "Flavor": ["*Brown Sugar", "Vanilla", "Caramel"]}
    elif item == "Latte":
        has_mods = True
        mods_dictionary = {"Milk": ["*2%", "Whole", "Alt"], "Flavor": ["Brown Sugar", "*Vanilla", "Caramel"], "Temperature": ["Hot", "*Iced"]}
    elif item == "Shakkerato":
        has_mods = True
        mods_dictionary = {"Milk": ["*2%", "Whole", "Alt"], "Flavor": ["Brown Sugar", "Vanilla", "*Caramel"]}
    elif item == "Drip Coffee":
        has_mods = True
        mods_dictionary = {"Milk": ["*2%", "Whole", "Alt"], "Flavor": ["Brown Sugar", "Creamer", "*Half & Half"], "Temperature": ["Hot", "*Iced"]}
    elif item == "Chai":
        has_mods = True
        mods_dictionary = {"Milk": ["*2%", "Whole", "Alt"], "Flavor": ["Brown Sugar", "*Vanilla", "Caramel"], "Temperature": ["*Hot", "Iced"]}
    elif item == "Matcha":
        has_mods = True
        mods_dictionary = {"Flavor": ["Brown Sugar", "*Honey", "Maple Syrup"], "Temperature": ["*Hot", "Drinkable"]}
    elif item == "Tea":
        has_mods = True
        mods_dictionary = {"Flavor": ["Black Tea", "Earl Grey", "*Green Tea"], "Temperature": ["Hot", "*Iced"]}
    elif item == "Hot Chocolate":
        has_mods = True
        mods_dictionary = {"Flavor": ["*Marshmallow", "Chocolate", "Vanilla"], "Temperature": ["*Hot", "Drinkable"]}
    elif item == "Milk":
        has_mods = True
        mods_dictionary = {"Flavor": ["Plain", "Chocolate", "Banana", "*Turmeric"], "Temperature": ["Hot", "*Drinkable", "Cold"]}
    elif item == "Croissant":
        has_mods = True
        mods_dictionary = {"Flavor": ["Plain", "*Almond", "Chocolate"], "Temperature": ["*Toasted", "Normal"]}
    elif item == "Breakfast Sandwich":
        has_mods = True
        mods_dictionary = {"Flavor": ["*Egg & Cheese", "Veggie", "Sausage"], "Temperature": ["*Toasted", "Normal"]}
    elif item == "Breakfast Burrito":
        has_mods = True
        mods_dictionary = {"Flavor": ["Veggie", "Sausage", "*Spicy Chorizo"], "Sauce": ["Green Salsa", "Red Salsa", "*Hot Sauce"], "Temperature": ["*Toasted", "Normal"]}
    elif item == "Bagel":
        has_mods = True
        mods_dictionary = {"Flavor": ["Plain", "*Everything", "Jalapeno Asiago"], "Toppings": ["Cream Cheese", "*Lox", "Plain"], "Temperature": ["*Toasted", "Normal"]}
    elif item == "Avocado Toast":
        has_mods = True
        mods_dictionary = {"Flavor": ["*Sourdough", "Wheat", "Croissant"], "Toppings": ["Tomatoes", "Bacon", "*Plain"], "Temperature": ["Toasted", "*Normal"]}
    elif item in ["Hat", "T Shirt", "Sweatshirt"]:
        has_mods = True
        mods_dictionary = {"Size": ["XS", "S", "*M", "L", "XL"]}
    return item, has_mods, mods_dictionary, len(mods_dictionary.keys())

# Hospitality Content
def hospitality_content(menu):
    if menu in ["overview", "front_desk", "housekeeping", "maintenance", "performance"]:
        pass
    else:
        menu = "overview"

    def front_desk(details=False, name:str=None, category:str=None, datetime:datetime=None, loyalty:str=None, payment:str=None, self_checkin=None, guest_message=None, self_checkout=None):
        if not name or not datetime:
            return None
        first = name.split(" ")[0]
        time = datetime.time().strftime("%I:%M %p")
        date = datetime.date()
        if details == False:
            if category == "checkin":
                return dmc.ListItem(f"{first} - {time}")
            elif category == "inhouse":
                return dmc.ListItem(f"{first} - {date}")
            elif category == "checkout":
                return dmc.ListItem(f"{first} - {time}")
        membership_badge = dmc.Badge(f"{loyalty.title()} Member") if loyalty else dmc.Badge("None", color="gray")
        if payment in ["prepaid", "current"]:
            payment_color = "green"
        elif payment == "at_risk":
            payment_color = "red"
        else:
            if payment == "required":
                payment = "Payment Required"
            payment_color = "yellow"
        if category == "checkin":
            variable_message = dmc.Text(self_checkin) if self_checkin else dmc.Text("Arrives soon")
            quick_action_info = [
                                dmc.Text(name),
                                dmc.Badge(payment.title(), color=payment_color),
                                dmc.Text("2:00 PM"),
                                dmc.Button("Check In", radius=20, variant="subtle"),
                                ]
        elif category == "inhouse":
            variable_message = dmc.Text(guest_message) if guest_message else dmc.Text("Staying for X more days")
            quick_action_info = [
                                dmc.Text(name),
                                dmc.Badge(payment.title(), color=payment_color),
                                dmc.Text("Till 2/16"),
                                dmc.Button("In Room Dining", color="yellow", radius=20, variant="subtle"),
                                dmc.Button("Cleaning", color="teal", radius=20, variant="subtle"),
                                dmc.Button("Maintenance", color="red", radius=20, variant="subtle"),
                                ]
        elif category == "checkout":
            variable_message = dmc.Text(self_checkout) if self_checkout else dmc.Text("Ready for Checkout")
            quick_action_info = [
                                dmc.Text(name),
                                dmc.Badge(payment.title(), color=payment_color),
                                dmc.Text("11:00 AM"),
                                dmc.Button("Edit Folio", color="yellow", radius=20, variant="subtle"),
                                dmc.Button("Close Folio", color="teal", radius=20, variant="subtle"),
                                ]
        return dmc.ListItem(
            children=[
                dmc.HoverCard(
                    openDelay=1000,
                    radius=20,
                    children=[
                        dmc.HoverCardTarget(
                            children=[
                                dmc.Group(
                                    children=[
                                        dmc.Text(first),
                                        membership_badge,
                                        variable_message,
                                    ],
                                ),
                            ],
                        ),
                        dmc.HoverCardDropdown(
                            children=[
                                dmc.Group(
                                    children=quick_action_info,
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )
    
    housekeeping_df_room_status = pd.DataFrame(OrderedDict([
        ("Rooms", ["101", "102", "103", "104", "105", "106", "107", "108", "109"]),
        ("Status", ["Clean", "Dirty", "Light", "Occupied", "DND", "Down", "Clean", "Dirty", "Clean"]),
        ("Cleaning", ["Done", "Requested", "Try Again", "Try Again", "Skipped", "NA", "Done", "In Progress", "Done"]),
    ]))

    maintenance_df_room_status = pd.DataFrame(OrderedDict([
        ("Rooms", ["101", "102", "103", "104", "105", "106", "107", "108", "109"]),
        ("Status", ["Preventative", "Down", "Replacement", "Resolved", "Down", "Down", "Check", "Preventative", "Check"]),
        ("Maintenance", ["Requested", "In Progress", "Replaced", "Done", "Long Term", "Prioritized", "Checked", "Replaced", "Temporary Fix"]),
    ]))
    
    return dmc.Center(
    dmc.Group(
        id="hospitality_content",
        mt=100,
        align="center",
        children=[
            html.Div(
                style=transparent_menu_style,
                children=[
                    dbc.Popover(
                        "",
                        id="hospitality_menu_hover",
                        target="hospitality_menu_selector",
                        body=True,
                        trigger="hover",
                        delay={"show": 500, "hide": 500},
                    ),
                    dmc.SegmentedControl(
                        id="hospitality_menu_selector",
                        data=
                        [
                            {"label": "🏨 Overview", "value": "overview"},
                            {"label": "🖥️ Front Desk", "value": "front_desk"},
                            {"label": "🧼 Housekeeping", "value": "housekeeping"},
                            {"label": "🛠️ Maintenance", "value": "maintenance"},
                            {"label": "🚀 Performance", "value": "performance"},
                        ],
                        value=menu,
                        orientation="vertical",
                        size="md",
                        radius=20,
                        withItemsBorders=False,
                        bg="transparent",
                    ),
                ],
            ),
            html.Div(
                style=transparent_block_style,
                children=[
                    dmc.Title("Overview", id="hospitality_menu_title", order=3),
                    dmc.Space(h="sm"),
                    dmc.Group(
                        align="start",
                        pb=20,
                        grow=True,
                        children=[
                            dmc.ProgressRoot(
                                children=[
                                    dmc.ProgressSection(dmc.ProgressLabel("Occupied"), value=33, color="blue"),
                                    dmc.ProgressSection(dmc.ProgressLabel("Checking Out"), value=28, color="orange"),
                                    dmc.ProgressSection(dmc.ProgressLabel("Checking In"), value=15, color="teal"),
                                    dmc.ProgressSection(dmc.ProgressLabel("Down"), value=3, color="red"),
                                ],
                                size="xl",
                                radius=20,
                            ),
                        ],
                    ),
                    dmc.Group(
                        id="hospitality_menu_overview",
                        align="start",
                        children=[
                            dmc.Stack(
                                justify="center",
                                children=[
                                    dmc.Text("Overall Service Score"),
                                    dmc.Group(
                                        children=dmc.Rating(fractions=2, value=4.5, readOnly=True), justify="center"
                                    ),
                                    dmc.Text("Staff"),
                                    dmc.BarChart(
                                        h=500,
                                        w=300,
                                        dataKey="day",
                                        orientation="horizontal",
                                        maxBarWidth=40,
                                        withLegend=True,
                                        withTooltip=False,
                                        legendProps={"verticalAlign": "bottom"},
                                        data=[
                                            {"day": "Today", "Front Desk": 2, "Housekeeping": 5, "Maintenance": 1},
                                            {"day": "Tomorrow", "Front Desk": 3, "Housekeeping": 4, "Maintenance": 2},
                                            {"day": "Next Day", "Front Desk": 2, "Housekeeping": 3, "Maintenance": 1},
                                        ],
                                        series=[
                                            {"name": "Front Desk", "color": "violet.6"},
                                            {"name": "Housekeeping", "color": "teal.6"},
                                            {"name": "Maintenance", "color": "blue.6"},
                                        ],
                                    ),
                                ],
                            ),
                            dmc.Stack(
                                justify="center",
                                children=[
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("Check In", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.List(
                                                children=[
                                                    dmc.ListItem("Aaron - 2:00 PM"),
                                                    dmc.ListItem("Bobby - 2:30 PM"),
                                                    dmc.ListItem("Charlie - 3:00 PM"),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("In House Guests", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.List(
                                                children=[
                                                    dmc.ListItem("David"),
                                                    dmc.ListItem("Edgar"),
                                                    dmc.ListItem("Frank"),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("Check Out", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.List(
                                                children=[
                                                    dmc.ListItem("Greg"),
                                                    dmc.ListItem("Henry"),
                                                    dmc.ListItem("Ivan"),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            dmc.Stack(
                                justify="center",
                                children=[
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("Cleaning Queue", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.List(
                                                children=[
                                                    dmc.ListItem("101"),
                                                    dmc.ListItem("102"),
                                                    dmc.ListItem("103"),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("Stayover", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.List(
                                                children=[
                                                    dmc.ListItem("201"),
                                                    dmc.ListItem("202"),
                                                    dmc.ListItem("203"),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("Ready Rooms", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.List(
                                                children=[
                                                    dmc.ListItem("301"),
                                                    dmc.ListItem("302"),
                                                    dmc.ListItem("303"),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            dmc.Stack(
                                justify="center",
                                children=[
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("Maintenance Queue", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.List(
                                                children=[
                                                    dmc.ListItem("104"),
                                                    dmc.ListItem("105"),
                                                    dmc.ListItem("106"),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("Preventative Maintenance", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.List(
                                                children=[
                                                    dmc.ListItem("204"),
                                                    dmc.ListItem("205"),
                                                    dmc.ListItem("206"),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("Fixed Rooms", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.List(
                                                children=[
                                                    dmc.ListItem("304"),
                                                    dmc.ListItem("305"),
                                                    dmc.ListItem("306"),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    dmc.Group(
                        id="hospitality_menu_front_desk",
                        align="start",
                        children=[
                            dmc.Stack(
                                justify="center",
                                children=[
                                    dmc.Text("Customer Service Score"),
                                    dmc.Group(
                                        children=dmc.Rating(fractions=2, value=4.5, readOnly=True), justify="center"
                                    ),
                                    dmc.Text("Staff"),
                                    dmc.BarChart(
                                        h=500,
                                        w=300,
                                        dataKey="day",
                                        orientation="horizontal",
                                        maxBarWidth=40,
                                        withLegend=True,
                                        withTooltip=False,
                                        legendProps={"verticalAlign": "bottom"},
                                        data=[
                                            {"day": "Today", "Front Desk": 2},
                                            {"day": "Tomorrow", "Front Desk": 3},
                                            {"day": "Next Day", "Front Desk": 2},
                                        ],
                                        series=[
                                            {"name": "Front Desk", "color": "violet.6"},
                                        ],
                                    ),
                                ],
                            ),
                            dmc.Stack(
                                justify="center",
                                children=[
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("Check In", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.List(
                                                children=[
                                                    front_desk(details=True, name="Aaron Apple", category="checkin", datetime=datetime.now(), loyalty="Gold", payment="prepaid", self_checkin="Mobile Checkin", guest_message=None, self_checkout=None),
                                                    front_desk(details=True, name="Bobby Brown", category="checkin", datetime=datetime.now(), loyalty="Silver", payment="required", self_checkin="Verification Required", guest_message=None, self_checkout=None),
                                                    front_desk(details=True, name="Charlie Carpenter", category="checkin", datetime=datetime.now(), loyalty=None, payment="required", self_checkin="Verification Required", guest_message=None, self_checkout=None),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("In House Guests", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.List(
                                                children=[
                                                    front_desk(details=True, name="David Danvers", category="inhouse", datetime=datetime.now(), loyalty="Gold", payment="current", self_checkin=None, guest_message="Staying for 2 more days", self_checkout=None),
                                                    front_desk(details=True, name="Edgar Ernest", category="inhouse", datetime=datetime.now(), loyalty="Silver", payment="+$150", self_checkin=None, guest_message="DND, Staying for 3 more days", self_checkout=None),
                                                    front_desk(details=True, name="Frank Foster", category="inhouse", datetime=datetime.now(), loyalty=None, payment="+$50", self_checkin=None, guest_message="Staying for 1 more day", self_checkout=None),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("Check Out", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.List(
                                                children=[
                                                    front_desk(details=True, name="Greg Grey", category="checkout", datetime=datetime.now(), loyalty="Gold", payment="current", self_checkin=None, guest_message=None, self_checkout="Mobile Checkout"),
                                                    front_desk(details=True, name="Henry Hardy", category="checkout", datetime=datetime.now(), loyalty="Silver", payment="+$150", self_checkin=None, guest_message=None, self_checkout="Extended to 12pm, Card on file"),
                                                    front_desk(details=True, name="Ivan Iore", category="checkout", datetime=datetime.now(), loyalty=None, payment="+$50", self_checkin=None, guest_message=None, self_checkout="Cash Security Deposit on Hold"),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            dmc.List(
                                children=[
                                    dmc.ListItem("✅ Customer Service Score"),
                                    dmc.ListItem("Checkin Guests"),
                                    dmc.ListItem("✅    -   Checkin Time"),
                                    dmc.ListItem("✅    -   Prepaid vs Payment Needed"),
                                    dmc.ListItem("✅    -   Loyalty Member"),
                                    dmc.ListItem("   -   Source of Booking"),
                                    dmc.ListItem("   -   Room Assignment / Room Type"),
                                    dmc.ListItem("In House Guests"),
                                    dmc.ListItem("   -   Requests"),
                                    dmc.ListItem("   -   Food / Bev"),
                                    dmc.ListItem("   -   Folio"),
                                    dmc.ListItem("Checkout Guests"),
                                    dmc.ListItem("   -   Checkout Time"),
                                    dmc.ListItem("✅    -   Prepaid vs Payment Needed"),
                                    dmc.ListItem("Front Desk Inventory"),
                                ],
                            ),
                        ],
                    ),
                    dmc.Group(
                        id="hospitality_menu_housekeeping",
                        align="start",
                        children=[
                            dmc.Stack(
                                justify="center",
                                children=[
                                    dmc.Text("Housekeeping Service Score"),
                                    dmc.Group(
                                        children=dmc.Rating(fractions=2, value=4.5, readOnly=True), justify="center"
                                    ),
                                    dmc.Text("Staff"),
                                    dmc.BarChart(
                                        h=500,
                                        w=300,
                                        dataKey="day",
                                        orientation="horizontal",
                                        maxBarWidth=40,
                                        withLegend=True,
                                        withTooltip=False,
                                        legendProps={"verticalAlign": "bottom"},
                                        data=[
                                            {"day": "Today", "Housekeeping": 5},
                                            {"day": "Tomorrow", "Housekeeping": 4},
                                            {"day": "Next Day", "Housekeeping": 3},
                                        ],
                                        series=[
                                            {"name": "Housekeeping", "color": "teal.6"},
                                        ],
                                    ),
                                ],
                            ),
                            dmc.Stack(
                                justify="center",
                                children=[
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("Cleaning Queue", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.List(
                                                children=[
                                                    dmc.ListItem("101"),
                                                    dmc.ListItem("102"),
                                                    dmc.ListItem("103"),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("Stayover", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.List(
                                                children=[
                                                    dmc.ListItem("201"),
                                                    dmc.ListItem("202"),
                                                    dmc.ListItem("203"),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("Ready Rooms", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.List(
                                                children=[
                                                    dmc.ListItem("301"),
                                                    dmc.ListItem("302"),
                                                    dmc.ListItem("303"),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("Room Type Availability", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.List(
                                                children=[
                                                    dmc.ListItem("Suite - 2/5"),
                                                    dmc.ListItem("King - 20/30"),
                                                    dmc.ListItem("Double Queen - 35/40"),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            dmc.Stack(
                                justify="center",
                                children=[
                                    html.Div(
                                        children=[
                                            dash_table.DataTable(
                                                id="housekeeping_table",
                                                data=housekeeping_df_room_status.to_dict("records"),
                                                columns=[
                                                    {"id": "Rooms", "name": "Rooms"},
                                                    {"id": "Status", "name": "Status", "presentation": "dropdown"},
                                                    {"id": "Cleaning", "name": "Cleaning", "presentation": "dropdown"}
                                                ],
                                                editable=True,
                                                style_header={
                                                    'backgroundColor': 'rgba(30, 30, 30, 0.2)',
                                                    'color': 'rgb(255,255,255)'
                                                },
                                                style_data={
                                                    'backgroundColor': 'rgba(50, 50, 50, 0.2)',
                                                    'color': 'rgb(255,255,255)'
                                                },
                                                style_table=transparent_sub_block_style,
                                                style_cell=transparent_sub_block_style,
                                                style_data_conditional=[{
                                                    'if': {
                                                        'state': 'active'  # 'active' | 'selected'
                                                    },
                                                'backgroundColor': 'rgba(0, 116, 217, 0.2)',
                                                'border': '1px solid rgb(0, 116, 217)',
                                                'color': 'rgb(255,255,255)',
                                                }, {
                                                    'if': {
                                                        'column_id': ['Status', 'Cleaning']
                                                    },
                                                'backgroundColor': 'rgba(150, 150, 150, 0.4)',
                                                'color': 'rgb(255,255,255)',
                                                }
                                                ],
                                                dropdown_conditional=[{
                                                    "if": {
                                                        "column_id": "Status",
                                                    },
                                                    "options": [{"label": i, "value": i}
                                                                    for i in ["Clean", "Dirty", "Light", "Occupied", "DND", "Down"]]
                                                }, {
                                                    "if": {
                                                        "column_id": "Cleaning",
                                                        "filter_query": "{Status} eq 'Clean'"
                                                    },
                                                    "options": [{"label": i, "value": i}
                                                                    for i in [
                                                                        "Done",
                                                                        "Requested",
                                                                ]]
                                                }, {
                                                    "if": {
                                                        "column_id": "Cleaning",
                                                        "filter_query": "{Status} eq 'Dirty'"
                                                    },
                                                    "options": [{"label": i, "value": i}
                                                                    for i in [
                                                                        "Requested",
                                                                        "In Progress",
                                                                        "Skipped", 
                                                                        "Try Again", 
                                                                        "Done",
                                                                ]]
                                                }, {
                                                    "if": {
                                                        "column_id": "Cleaning",
                                                        "filter_query": "{Status} eq 'Light'"
                                                    },
                                                    "options": [{"label": i, "value": i}
                                                                    for i in [
                                                                        "Requested",
                                                                        "In Progress",
                                                                        "Skipped", 
                                                                        "Try Again", 
                                                                        "Done",
                                                                ]]
                                                }, {
                                                    "if": {
                                                        "column_id": "Cleaning",
                                                        "filter_query": "{Status} eq 'Occupied'"
                                                    },
                                                    "options": [{"label": i, "value": i}
                                                                    for i in [
                                                                        "Requested",
                                                                        "In Progress",
                                                                        "Skipped", 
                                                                        "Try Again", 
                                                                        "Done",
                                                                ]]
                                                }, {
                                                    "if": {
                                                        "column_id": "Cleaning",
                                                        "filter_query": "{Status} eq 'DND'"
                                                    },
                                                    "options": [{"label": i, "value": i}
                                                                    for i in [
                                                                        "Requested",
                                                                        "In Progress",
                                                                        "Skipped", 
                                                                        "Try Again", 
                                                                        "Done",
                                                                ]]
                                                }, {
                                                    "if": {
                                                        "column_id": "Cleaning",
                                                        "filter_query": "{Status} eq 'Down'"
                                                    },
                                                    "options": [{"label": i, "value": i}
                                                                    for i in [
                                                                        "NA",
                                                                        "Requested",
                                                                        "In Progress",
                                                                        "Done",
                                                                ]]
                                                }, {
                                                    "if": {
                                                        "column_id": "Status",
                                                        "filter_query": "{Cleaning} eq 'Done'"
                                                    },
                                                    "options": [{"label": "Clean", "value": "Clean"}]
                                                }
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            dmc.List(
                                children=[
                                    dmc.ListItem("✅ Housekeeping Service Score"),
                                    dmc.ListItem("Ready Room Supply"),
                                    dmc.ListItem("Checkout Rooms"),
                                    dmc.ListItem("   -   Ability to sort by room type"),
                                    dmc.ListItem("   -   Update when rooms are checked out"),
                                    dmc.ListItem("   -   Time till checkout"),
                                    dmc.ListItem("   -   Maintenance Requests"),
                                    dmc.ListItem("In House Guests"),
                                    dmc.ListItem("   -   Cleaning Requests"),
                                    dmc.ListItem("   -   Linen Requests"),
                                    dmc.ListItem("   -   Cleaning Preference / DND"),
                                    dmc.ListItem("Laundry"),
                                    dmc.ListItem("   -   Inventory"),
                                    dmc.ListItem("   -   Timers / Current Status"),
                                ],
                            ),
                        ],
                    ),
                    dmc.Group(
                        id="hospitality_menu_maintenance",
                        align="start",
                        children=[
                            dmc.Stack(
                                justify="center",
                                children=[
                                    dmc.Text("Maintenance Service Score"),
                                    dmc.Group(
                                        children=dmc.Rating(fractions=2, value=4.5, readOnly=True), justify="center"
                                    ),
                                    dmc.Text("Staff"),
                                    dmc.BarChart(
                                        h=500,
                                        w=300,
                                        dataKey="day",
                                        orientation="horizontal",
                                        maxBarWidth=40,
                                        withLegend=True,
                                        withTooltip=False,
                                        legendProps={"verticalAlign": "bottom"},
                                        data=[
                                            {"day": "Today", "Maintenance": 1},
                                            {"day": "Tomorrow", "Maintenance": 2},
                                            {"day": "Next Day", "Maintenance": 1},
                                        ],
                                        series=[
                                            {"name": "Maintenance", "color": "blue.6"},
                                        ],
                                    ),
                                ],
                            ),
                            dmc.Stack(
                                justify="center",
                                children=[
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("Maintenance Queue", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.List(
                                                children=[
                                                    dmc.ListItem("104"),
                                                    dmc.ListItem("105"),
                                                    dmc.ListItem("106"),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("Preventative Maintenance", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.List(
                                                children=[
                                                    dmc.ListItem("204"),
                                                    dmc.ListItem("205"),
                                                    dmc.ListItem("206"),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("Fixed Rooms", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.List(
                                                children=[
                                                    dmc.ListItem("304"),
                                                    dmc.ListItem("305"),
                                                    dmc.ListItem("306"),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("Room Type Availability", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.List(
                                                children=[
                                                    dmc.ListItem("Suite - 2/5"),
                                                    dmc.ListItem("King - 20/30"),
                                                    dmc.ListItem("Double Queen - 35/40"),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            dmc.Stack(
                                justify="center",
                                children=[
                                    html.Div(
                                        children=[
                                            dash_table.DataTable(
                                                id="maintenane_table",
                                                data=maintenance_df_room_status.to_dict("records"),
                                                columns=[
                                                    {"id": "Rooms", "name": "Rooms"},
                                                    {"id": "Status", "name": "Status", "presentation": "dropdown"},
                                                    {"id": "Maintenance", "name": "Maintenance", "presentation": "dropdown"}
                                                ],
                                                editable=True,
                                                style_header={
                                                    'backgroundColor': 'rgba(30, 30, 30, 0.2)',
                                                    'color': 'rgb(255,255,255)'
                                                },
                                                style_data={
                                                    'backgroundColor': 'rgba(50, 50, 50, 0.2)',
                                                    'color': 'rgb(255,255,255)'
                                                },
                                                style_table=transparent_sub_block_style,
                                                style_cell=transparent_sub_block_style,
                                                style_data_conditional=[{
                                                    'if': {
                                                        'state': 'active'  # 'active' | 'selected'
                                                    },
                                                'backgroundColor': 'rgba(0, 116, 217, 0.2)',
                                                'border': '1px solid rgb(0, 116, 217)',
                                                'color': 'rgb(255,255,255)',
                                                }, {
                                                    'if': {
                                                        'column_id': ['Status', 'Maintenance']
                                                    },
                                                'backgroundColor': 'rgba(150, 150, 150, 0.4)',
                                                'color': 'rgb(255,255,255)',
                                                }
                                                ],
                                                dropdown_conditional=[{
                                                    "if": {
                                                        "column_id": "Status",
                                                    },
                                                    "options": [{"label": i, "value": i}
                                                                    for i in [
                                                                        "Check",
                                                                        "Replacement",
                                                                        "Preventative",
                                                                        "Down",
                                                                        "Resolved"]]
                                                }, {
                                                    "if": {
                                                        "column_id": "Maintenance",
                                                        "filter_query": "{Status} eq 'Preventative'"
                                                    },
                                                    "options": [{"label": i, "value": i}
                                                                    for i in [
                                                                        "Requested",
                                                                        "Prioritized",
                                                                        "In Progress",
                                                                        "Checked",
                                                                        "Replaced",
                                                                        "No Longer Occurring",
                                                                        "Done",
                                                                ]]
                                                }, {
                                                    "if": {
                                                        "column_id": "Maintenance",
                                                        "filter_query": "{Status} eq 'Down'"
                                                    },
                                                    "options": [{"label": i, "value": i}
                                                                    for i in [
                                                                        "Requested",
                                                                        "Prioritized",
                                                                        "In Progress",
                                                                        "Checked",
                                                                        "Replaced",
                                                                        "No Longer Occurring",
                                                                        "Long Term",
                                                                        "Done",
                                                                ]]
                                                }, {
                                                    "if": {
                                                        "column_id": "Maintenance",
                                                        "filter_query": "{Status} eq 'Replacement'"
                                                    },
                                                    "options": [{"label": i, "value": i}
                                                                    for i in [
                                                                        "Requested",
                                                                        "Prioritized",
                                                                        "In Progress",
                                                                        "Checked",
                                                                        "Replaced",
                                                                        "Temporary Fix",
                                                                        "Done",
                                                                ]]
                                                }, {
                                                    "if": {
                                                        "column_id": "Maintenance",
                                                        "filter_query": "{Status} eq 'Check'"
                                                    },
                                                    "options": [{"label": i, "value": i}
                                                                    for i in [
                                                                        "Requested",
                                                                        "Prioritized",
                                                                        "In Progress",
                                                                        "Checked",
                                                                        "Replaced",
                                                                        "Temporary Fix",
                                                                        "NA",
                                                                        "Done",
                                                                ]]
                                                }, {
                                                    "if": {
                                                        "column_id": "Maintenance",
                                                        "filter_query": "{Status} eq 'Resolved'"
                                                    },
                                                    "options": [{"label": i, "value": i}
                                                                    for i in [
                                                                        "Done",
                                                                ]]
                                                }, {
                                                    "if": {
                                                        "column_id": "Status",
                                                        "filter_query": "{Maintenance} eq 'Done'"
                                                    },
                                                    "options": [{"label": "Resolved", "value": "Resolved"}]
                                                }
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            dmc.List(
                                children=[
                                    dmc.ListItem("✅ Maintenance Service Score"),
                                    dmc.ListItem("Down Room Maintenance"),
                                    dmc.ListItem("   -   Ability to sort by room type"),
                                    dmc.ListItem("   -   Update when rooms are resolved"),
                                    dmc.ListItem("   -   Reason"),
                                    dmc.ListItem("   -   Estimated time to complete"),
                                    dmc.ListItem("Preventative Room Maintenance"),
                                    dmc.ListItem("   -   Ability to sort by room type"),
                                    dmc.ListItem("   -   Update when rooms are available to check"),
                                    dmc.ListItem("   -   Date it will go down if not checked"),
                                    dmc.ListItem("   -   Estimated time to complete"),
                                    dmc.ListItem("In House Guests"),
                                    dmc.ListItem("   -   Maintenance Requests"),
                                    dmc.ListItem("Equipement"),
                                    dmc.ListItem("   -   Inventory"),
                                    dmc.ListItem("   -   Last Checked / Current Status"),
                                ],
                            ),
                        ],
                    ),
                    dmc.Group(
                        id="hospitality_menu_performance",
                        align="start",
                        children=[
                            dmc.Stack(
                                justify="center",
                                children=[
                                    dmc.Text("Overall Service Score"),
                                    dmc.Group(
                                        children=dmc.Rating(fractions=2, value=4.5, readOnly=True), justify="center"
                                    ),
                                    dmc.Text("Staff"),
                                    dmc.BarChart(
                                        h=500,
                                        w=300,
                                        dataKey="day",
                                        orientation="horizontal",
                                        maxBarWidth=40,
                                        withLegend=True,
                                        withTooltip=False,
                                        legendProps={"verticalAlign": "bottom"},
                                        data=[
                                            {"day": "Today", "Front Desk": 2, "Housekeeping": 5, "Maintenance": 1},
                                            {"day": "Tomorrow", "Front Desk": 3, "Housekeeping": 4, "Maintenance": 2},
                                            {"day": "Next Day", "Front Desk": 2, "Housekeeping": 3, "Maintenance": 1},
                                        ],
                                        series=[
                                            {"name": "Front Desk", "color": "violet.6"},
                                            {"name": "Housekeeping", "color": "teal.6"},
                                            {"name": "Maintenance", "color": "blue.6"},
                                        ],
                                    ),
                                ],
                            ),
                            dmc.Stack(
                                justify="center",
                                children=[
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("Occupancy Rate", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.Group(
                                                justify="space-between",
                                                children=[
                                                    dmc.List(
                                                        children=[
                                                            dmc.ListItem("Today: 80%"),
                                                            dmc.ListItem("This Week: 90%"),
                                                            dmc.ListItem("This Month: 88%"),
                                                        ],
                                                    ),
                                                    dmc.List(
                                                        children=[
                                                            dmc.ListItem("LY Today: 75%"),
                                                            dmc.ListItem("LY This Week: 87%"),
                                                            dmc.ListItem("LY This Month: 85%"),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("ADR (Average Daily Rate)", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.Group(
                                                justify="space-between",
                                                children=[
                                                    dmc.List(
                                                        children=[
                                                            dmc.ListItem("Today: $104.34"),
                                                            dmc.ListItem("This Week: $110.42"),
                                                            dmc.ListItem("This Month: $108.09"),
                                                        ],
                                                    ),
                                                    dmc.List(
                                                        children=[
                                                            dmc.ListItem("LY Today: $102.01"),
                                                            dmc.ListItem("LY This Week: $103.59"),
                                                            dmc.ListItem("LY This Month: $104.90"),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("RevPAR (Revenue Per Available Room)", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.Group(
                                                justify="space-between",
                                                children=[
                                                    dmc.List(
                                                        children=[
                                                            dmc.ListItem("Today: $83.47"),
                                                            dmc.ListItem("This Week: $99.38"),
                                                            dmc.ListItem("This Month: $95.12"),
                                                        ],
                                                    ),
                                                    dmc.List(
                                                        children=[
                                                            dmc.ListItem("LY Today: $76.51"),
                                                            dmc.ListItem("LY This Week: $90.12"),
                                                            dmc.ListItem("LY This Month: $89.17"),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style=transparent_sub_block_style,
                                        children=[
                                            dmc.Title("MPI (Market Penetration Index) ", order=3),
                                            dmc.Divider(h="sm"),
                                            dmc.Group(
                                                justify="space-between",
                                                children=[
                                                    dmc.List(
                                                        children=[
                                                            dmc.ListItem("Today: 20%"),
                                                            dmc.ListItem("This Week: 22%"),
                                                            dmc.ListItem("This Month: 21%"),
                                                        ],
                                                    ),
                                                    dmc.List(
                                                        children=[
                                                            dmc.ListItem("LY Today: 15%"),
                                                            dmc.ListItem("LY This Week: 18%"),
                                                            dmc.ListItem("LY This Month: 12%"),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            dmc.List(
                                children=[
                                    dmc.ListItem("Customer Service Score"),
                                    dmc.ListItem("Housekeeping Service Score"),
                                    dmc.ListItem("Maintenance Service Score"),
                                    dmc.ListItem("Metrics"),
                                    dmc.ListItem("   -   Occupany %"),
                                    dmc.ListItem("   -   ADR"),
                                    dmc.ListItem("   -   Cost / Available Room"),
                                    dmc.ListItem("   -   Room Uptime"),
                                    dmc.ListItem("   -   On Time Checkin / Rooms Available for Checkin time"),
                                    dmc.ListItem("   -   Trends over longer time frames"),
                                    dmc.ListItem("Overviews of all three teams metrics"),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    ),
)

# Main Layout
def layout(page="/", menu=None):
    if page in ["signingoogle", "login"]:
        user_content = account_cred.layout(page)
    else:
        user_content = None
    if page == "priyanka": # TODO: Learning playground, should not go on server
        return pri.pri_layout
    if page and "." in page:
        menu = page.split(".")[1]
        if "%20" in menu:
            menu.replace("%20", "_")
        page = page.split(".")[0]
    if page.lower() in ["/","/home","/cafe","/hospitality"]:
        if menu:
            current_page = dcc.Location(id="page_updater", pathname=f"/{page.lower()}.{menu.lower()}", refresh=False)
        current_page = dcc.Location(id="page_updater", pathname=f"/{page.lower()}", refresh=False)
    elif page.lower() in ["signingoogle", "login", "logout"]:
        current_page = dcc.Location(id="page_updater", pathname=f"/{page.lower()}", refresh=True)
    else:
        current_page = dcc.Location(id="page_updater", pathname="/", refresh=False)

    return dmc.MantineProvider(
    id="mantine_provider",
    forceColorScheme="dark",
    children=[
        current_page,
        dcc.Location(id="url"),
        dcc.Interval(id="interval_time", interval=6000),
        html.Div(
            children=[
                html.Img(
                    id="background_image",
                    src="assets/background.jpeg", 
                    style={
                        "position": "absolute", 
                        "width": "100%", 
                        "height": "100%", 
                        "objectFit": "cover",
                        "zIndex": -1,
                        "opacity": 0.5,
                    }
                ),
                banner(page),
                user_content,
                home_content,
                cafe_content(menu),
                hospitality_content(menu),
            ],
        ),
    ],
)

# Callbacks
@callback(
    Output("mantine_provider", "forceColorScheme"),
    Input("color_scheme_toggle", "n_clicks"),
    State("mantine_provider", "forceColorScheme"),
    prevent_initial_call=True,
)
def switch_theme(clicks, theme):
    return "dark" if theme == "light" else "light"

@callback(
    Output("page_updater", "pathname"),
    Output("page_updater", "refresh"),
    Input("page_selector", "value"),
    Input("cafe_menu_selector", "value"),
    Input("hospitality_menu_selector", "value"),
)
def update_page(page, cafe_menu, hospitality_menu):
    page = page.lower()
    cafe_menu = cafe_menu.lower().split(" ")[1] if cafe_menu else None
    hospitality_menu = hospitality_menu.lower() if hospitality_menu else None
    if page in ["/signingoogle"]:
        pathname = "/signingoogle"
    elif page in ["/cafe"] and cafe_menu:
        pathname = f"{page}.{cafe_menu}"
    elif page in ["/hospitality"] and hospitality_menu:
        pathname = f"{page}.{hospitality_menu}"
    else:
        pathname = f"{page}"
    if pathname in ["/", "/home"]:
        pathname = "/"
    refresh=False if page not in ["/signingoogle"] else True
    return pathname, refresh

@callback(
    Output("background_image", "src"),
    Output("home_content", "display"),
    Output("cafe_content", "display"),
    Output("hospitality_content", "display"),
    Input("page_selector", "value"),
)
def switch_page(page):
    stone = "assets/background.jpeg"
    wood = "assets/wood.jpeg"
    vivid_colors = "assets/vivid_colors.jpg"

    if page in ["/", "/home"]:
        return stone, "", "none", "none"
    elif page == "/cafe":
        return wood, "none", "", "none"
    elif page == "/hospitality":
        return vivid_colors, "none", "none", ""
    elif page in ["/signingoogle", "/login", "/register", "/logout"]:
        return stone, "none", "none", "none"
    else:
        return stone, "", "none", "none"
    
@callback(
    Output("time_display", "children", allow_duplicate=True),
    Input("interval_time", "n_intervals"),
    State("time_display", "children"),
    State("geolocation", "position"),
    prevent_initial_call=True,
)
def update_time(interval, time, pos):
    if pos:
        time_str = datetime.now(pytz.timezone(timezonefinder.TimezoneFinder().certain_timezone_at(lat=pos['lat'], lng=pos['lon']))).strftime("%I:%M %p %Z")
        if time is None:
            time = time_str
        if time == time_str:
            return no_update
        elif pos and time:
            return time_str
        elif pos:
            return time_str
    else:
        return datetime.now(local_timezone).strftime("%I:%M %p %Z")

@callback(
    Output("time_display", "children"),
    Input("geolocation", "position"),
)
def local_time(pos):
    if pos:
        time_str = datetime.now(pytz.timezone(timezonefinder.TimezoneFinder().certain_timezone_at(lat=pos['lat'], lng=pos['lon']))).strftime("%I:%M %p %Z")
        return time_str
    return datetime.now(local_timezone).strftime("%I:%M %p %Z")
    
@callback(
    Output("cafe_menu_selector", "data"),
    Input("cafe_menu_hover", "is_open"),
)
def cafe_menu_hover(opened):
    if opened:
        return [
            {"label": "☕️ Drinks", "value": "☕️ Drinks"},
            {"label": "🥪 Food", "value": "🥪 Food"},
            {"label": "🧢 Other", "value": "🧢 Other"},
            {"label": "🛒 Order", "value": "🛒 Order"},
        ]
    else: 
        return [
            {"label": "☕️", "value": "☕️ Drinks"},
            {"label": "🥪", "value": "🥪 Food"},
            {"label": "🧢", "value": "🧢 Other"},
            {"label": "🛒", "value": "🛒 Order"},
        ]

@callback(
    Output("cafe_menu_layout", "style"),
    Output("cafe_menu_title", "children"),
    Output("cafe_menu_drinks", "display"),
    Output("cafe_menu_food", "display"),
    Output("cafe_menu_other", "display"),
    Input("cafe_menu_selector", "value"),
)
def cafe_menu(menu):
    if menu == "☕️ Drinks":
        return transparent_block_style, "Menu", "", "none", "none"
    elif menu == "🥪 Food":
        return transparent_block_style, "Menu", "none", "", "none"
    elif menu == "🧢 Other":
        return transparent_block_style, "Shop", "none", "none", ""
    elif menu == "🛒 Order":
        return {"display": "none"}, "Here's your recent order!", "none", "none", "none"
    else:
        return no_update, "Menu", "", "none", "none"
    
@callback(
    Output("cafe_cart_notification", "children"),
    Output("cafe_cart_items", "value"),
    Input("cafe_place_order_button", "n_clicks"),
    Input({"type": "cafe_menu_drinks_item", "index": ALL}, "n_clicks"),
    Input({"type": "cafe_menu_food_item", "index": ALL}, "n_clicks"),
    Input({"type": "cafe_menu_other_item", "index": ALL}, "n_clicks"),
    Input("cafe_cart_items", "n_blur"),
    State("cafe_cart_notification", "children"),
    State("cafe_cart_items", "value"),
)
def update_cafe_cart(order_started, click_drinks, click_food, click_other, cart_update, cart_notification, cart_items:list):
    if order_started:
        cart = f"🛒 {len(cart_items)} items in your order"
        return cart, cart_items
    if cart_items and cart_notification in ["", "🛒 Your cart is empty"]:
        cart = f"🛒 {len(cart_items)} items in your cart"
        return cart, cart_items
    if click_drinks or click_food or click_other or cart_update:
        if "cafe_cart_items.n_blur" in ctx.triggered_prop_ids:
            return "Cart Updated", cart_items
        if ctx.triggered_id and ctx.triggered_id["index"]:
            item = str(ctx.triggered_id["index"])
            item = item.replace("_", " ")
            item = item.title()
            if cart_items:
                if len(cart_items) >= 8:
                    cart = "🛒 Your cart has reached the max"
                    return cart, cart_items
                elif item in cart_items:
                    cart = f"{item} already in your cart!"
                    return cart, cart_items
                else:
                    cart = f"{item} added to your cart!"
                    cart_items.append(item)
                    return cart, cart_items
            else:
                cart = f"{item} added to your cart!"
                cart_items = [item]
                return cart, cart_items

    if cart_notification in ["", "🛒 Your cart is empty"]:
        if cart_notification == "🛒 Your cart is empty":
            PreventUpdate
        return "🛒 Your cart is empty", []

@callback(
    Output("cafe_place_order_button", "disabled", allow_duplicate=True),
    Output("cafe_order_items_customization", "children"),
    Input("cafe_cart_items", "value"),
    prevent_initial_call=True
)
def customize_cafe_items(cart_items:list):
    item_display = []
    for item in cart_items:
        item = item.title()
        item = item.replace("_", " ")
        order_item, has_mods, mods_dictionary, mods_count = cafe_mods(item)
        order_display = [dmc.Group(justify="space-between", children=[dmc.Text(order_item, id={"type": "cafe_order_item_name", "index": order_item}), dmc.NumberInput(id={"type": "cafe_order_item_count", "index": order_item}, value=1, w=60, allowDecimal=False, allowNegative=False, variant="unstyled")])]
        if has_mods:
            order_display += [dmc.Divider(size="sm")]
            order_display += [dmc.Space(h="sm")]
            if mods_dictionary:
                for mod_item, options in mods_dictionary.items():
                    default = None
                    i = 0
                    for option in options:
                        if "*" in option:
                            default = option.replace("*", "")
                            options[i] = default
                        i += 1
                    order_display += [dmc.Text(mod_item, size="xs", id={"type": "cafe_order_item_mod_name", "index": order_item})]
                    order_display += [dmc.SegmentedControl(data=options, id={"type": "cafe_order_item_mod_selection", "index": order_item}, value=default, radius=20, bg="transparent", withItemsBorders=False, size="xs")]
        if item_display == [] or None:
            item_display = [dmc.Card(miw=300,children=order_display, style=transparent_sub_block_style)]
        else:
            item_display += [dmc.Card(miw=300,children=order_display, style=transparent_sub_block_style)]
    place_order_disabled=True
    if cart_items:
        place_order_disabled=False
    return place_order_disabled, item_display

@callback(
    Output("cafe_place_order_button", "display"),
    Output("cafe_add_items", "display"),
    Output("cafe_order_items_customization", "display"),
    Output("cafe_order_summary", "display"),
    Output("cafe_order_summary_json", "value"),
    Output("cafe_order_summary_list", "children"),
    Input("cafe_place_order_button", "n_clicks"),
    State({"type": "cafe_order_item_name", "index": ALL}, "children"),
    State({"type": "cafe_order_item_mod_name", "index": ALL}, "children"),
    State({"type": "cafe_order_item_mod_selection", "index": ALL}, "value"),
    State({"type": "cafe_order_item_count", "index": ALL}, "value"),
)
def cafe_order_summary(click, items:list, mods:list, mod_values:list, count:list):
    cafe_order_summary = {"order": {}}
    i=0        
    for item in items:
        quantity = count[i]
        i+=1
        if quantity != 0:
            order_item, has_mods, mods_dictionary, mods_count = cafe_mods(item)
            cafe_order_summary["order"][f"item{i}"] = {}
            cafe_order_summary["order"][f"item{i}"]["name"] = item.lower()
            cafe_order_summary["order"][f"item{i}"]["quantity"] = quantity
            cafe_order_summary["order"][f"item{i}"]["mod"] = {}
            j=0
            while j < mods_count:
                mod_name = mods[0].lower()
                mod_value = mod_values[0].lower()
                cafe_order_summary["order"][f"item{i}"]["mod"][f"{mod_name}"] = mod_value
                mods.pop(0)
                mod_values.pop(0)
                j+=1
    if click and "cafe_place_order_button.n_clicks" in ctx.triggered_prop_ids:
        json_value = orjson.dumps(cafe_order_summary).decode()
        list_value = orjson.loads(json_value).get("order")
        items_num = dict(list_value).keys()
        list_display = []
        if items_num:
            for item in items_num:
                if list_value.get(item).get("mod"):
                    modifications = dmc.Code(str(list_value.get(item).get("mod")).replace("{","").replace("}",""), fz=10)
                else:
                    modifications = None
                list_items = [dmc.ListItem(
                                children=[
                                    dmc.Group(
                                        children=[
                                            dmc.Code(list_value.get(item).get("quantity")),
                                            dmc.Text(list_value.get(item).get("name").title()),
                                            modifications
                                        ],
                                    ),
                                ],
                            )]
                if list_display == []:
                    list_display = list_items
                else:
                    list_display = list_display + list_items
        hide = "none"
        return hide, hide, "none", "", json_value, list_display
    else:
        show = ""
        return show, show, "", "none", None, None
    
@callback(
    Output("hospitality_menu_selector", "data"),
    Input("hospitality_menu_hover", "is_open"),
)
def cafe_menu_hover(opened):
    if opened:
        return [
            {"label": "🏨 Overview", "value": "overview"},
            {"label": "🖥️ Front Desk", "value": "front_desk"},
            {"label": "🧼 Housekeeping", "value": "housekeeping"},
            {"label": "🛠️ Maintenance", "value": "maintenance"},
            {"label": "🚀 Performance", "value": "performance"},
        ]
    else: 
        return [
            {"label": "🏨", "value": "overview"},
            {"label": "🖥️", "value": "front_desk"},
            {"label": "🧼", "value": "housekeeping"},
            {"label": "🛠️", "value": "maintenance"},
            {"label": "🚀", "value": "performance"},
        ]

@callback(
    Output("hospitality_menu_title", "children"),
    Output("hospitality_menu_overview", "display"),
    Output("hospitality_menu_front_desk", "display"),
    Output("hospitality_menu_housekeeping", "display"),
    Output("hospitality_menu_maintenance", "display"),
    Output("hospitality_menu_performance", "display"),
    Input("hospitality_menu_selector", "value"),
)
def hospitality_menu(menu):
    hide="none"
    show=""
    if menu == "overview":
        return "Overview",show,hide,hide,hide,hide
    elif menu == "front_desk":
        return "Front Desk",hide,show,hide,hide,hide
    elif menu == "housekeeping":
        return "Housekeeping",hide,hide,show,hide,hide
    elif menu == "maintenance":
        return "Maintenance",hide,hide,hide,show,hide
    elif menu == "performance":
        return "Performance",hide,hide,hide,hide,show
    else:
        return "Overview",show,hide,hide,hide,hide

dash.register_page(
    __name__,
    path="/" if __name__ in ["/", "/home", "/signingoogle", "/logout", "/cafe", "/hospitality", "/priyanka"] else "/", # Remove Priyanka if pushing to server
    path_template="/<page>",
    redirect_from=['/home', '/logout'],
    title='Innovate',
    name='Innovate',
    image="assets/favicon.ico",
)
