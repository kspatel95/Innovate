import dash
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
from dash import Dash, Input, Output, State, callback, _dash_renderer, html, dcc, MATCH, ALL, no_update, ctx
_dash_renderer._set_react_version("18.2.0")
import logging
from dash.exceptions import PreventUpdate
import os
import orjson

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

prescription_medications = {
    "Antibiotics": {
        "Generic": ["Amoxicillin", "Ciprofloxacin", "Doxycycline", "Azithromycin", "Clindamycin"],
        "Brand": ["Augmentin", "Cipro", "Vibramycin", "Zithromax", "Cleocin"]
    },
    "Antivirals": {
        "Generic": ["Acyclovir", "Oseltamivir", "Valacyclovir", "Tenofovir", "Sofosbuvir"],
        "Brand": ["Zovirax", "Tamiflu", "Valtrex", "Viread", "Sovaldi"]
    },
    "Pain Management": {
        "Opioids": {
            "Generic": ["Oxycodone", "Hydrocodone", "Morphine", "Fentanyl", "Tramadol"],
            "Brand": ["OxyContin", "Vicodin", "MS Contin", "Duragesic", "Ultram"]
        },
        "NSAIDs & Others": {
            "Generic": ["Celecoxib", "Naproxen", "Diclofenac"],
            "Brand": ["Celebrex", "Aleve (OTC but higher doses Rx)", "Voltaren"]
        }
    },
    "Cardiovascular Medications": {
        "Antihypertensives": {
            "Generic": ["Lisinopril", "Amlodipine", "Metoprolol", "Losartan", "Hydrochlorothiazide"],
            "Brand": ["Prinivil", "Norvasc", "Lopressor", "Cozaar", "Microzide"]
        },
        "Anticoagulants": {
            "Generic": ["Warfarin", "Rivaroxaban", "Apixaban", "Dabigatran"],
            "Brand": ["Coumadin", "Xarelto", "Eliquis", "Pradaxa"]
        }
    },
    "Diabetes Medications": {
        "Oral": {
            "Generic": ["Metformin", "Sitagliptin", "Empagliflozin", "Glyburide"],
            "Brand": ["Glucophage", "Januvia", "Jardiance", "Diabeta"]
        },
        "Injectable": {
            "Generic": ["Insulin glargine", "Insulin aspart", "Liraglutide"],
            "Brand": ["Lantus", "Novolog", "Victoza"]
        }
    },
    "Mental Health Medications": {
        "Antidepressants": {
            "Generic": ["Fluoxetine", "Sertraline", "Escitalopram", "Bupropion"],
            "Brand": ["Prozac", "Zoloft", "Lexapro", "Wellbutrin"]
        },
        "Antipsychotics": {
            "Generic": ["Risperidone", "Olanzapine", "Quetiapine"],
            "Brand": ["Risperdal", "Zyprexa", "Seroquel"]
        },
        "Anxiolytics": {
            "Generic": ["Alprazolam", "Diazepam", "Clonazepam"],
            "Brand": ["Xanax", "Valium", "Klonopin"]
        }
    },
    "Neurological Medications": {
        "Anti-Seizure": {
            "Generic": ["Levetiracetam", "Gabapentin", "Topiramate"],
            "Brand": ["Keppra", "Neurontin", "Topamax"]
        },
        "Migraine Treatment": {
            "Generic": ["Sumatriptan", "Rizatriptan"],
            "Brand": ["Imitrex", "Maxalt"]
        }
    },
    "Hormonal Medications": {
        "Thyroid": {
            "Generic": ["Levothyroxine"],
            "Brand": ["Synthroid"]
        },
        "Hormonal Therapy": {
            "Generic": ["Estradiol", "Progesterone", "Testosterone"],
            "Brand": ["Estrace", "Prometrium", "AndroGel"]
        }
    },
    "Gastrointestinal Medications": {
        "Acid Reducers": {
            "Generic": ["Omeprazole", "Pantoprazole", "Ranitidine (discontinued)"],
            "Brand": ["Prilosec", "Protonix", "Zantac"]
        },
        "IBD/IBS Treatments": {
            "Generic": ["Mesalamine", "Loperamide"],
            "Brand": ["Asacol", "Imodium"]
        }
    },
    "Respiratory Medications": {
        "Asthma & COPD": {
            "Generic": ["Albuterol", "Budesonide", "Fluticasone/Salmeterol"],
            "Brand": ["ProAir", "Pulmicort", "Advair"]
        },
        "Allergy Treatments": {
            "Generic": ["Montelukast"],
            "Brand": ["Singulair"]
        }
    },
    "Oncology Medications": {
        "Chemotherapy": {
            "Generic": ["Methotrexate", "Paclitaxel", "Imatinib"],
            "Brand": ["Trexall", "Taxol", "Gleevec"]
        },
        "Targeted Therapy": {
            "Generic": ["Trastuzumab", "Pembrolizumab"],
            "Brand": ["Herceptin", "Keytruda"]
        }
    },
    "Autoimmune & Immunosuppressants": {
        "Generic": ["Methotrexate", "Hydroxychloroquine", "Adalimumab"],
        "Brand": ["Trexall", "Plaquenil", "Humira"]
    },
    "Ophthalmic Medications": {
        "Glaucoma Treatments": {
            "Generic": ["Latanoprost", "Timolol"],
            "Brand": ["Xalatan", "Timoptic"]
        }
    }
}

medication_usage = {
    "Amoxicillin": "Take 500mg every 8 hours or 875mg every 12 hours for bacterial infections. Complete the full course.",
    "Ciprofloxacin": "Take 500-750mg every 12 hours for bacterial infections. Avoid dairy and antacids.",
    "Azithromycin": "Take 500mg on day 1, followed by 250mg daily for 4 days for bacterial infections.",
    "Metformin": "Start with 500mg once or twice daily with food, then increase as needed for diabetes control.",
    "Lisinopril": "Take 10-40mg once daily for hypertension. Monitor blood pressure and kidney function.",
    "Atorvastatin": "Take 10-80mg once daily for cholesterol management. Best taken in the evening.",
    "Levothyroxine": "Take 25-200mcg once daily in the morning on an empty stomach, 30 minutes before eating.",
    "Albuterol": "Inhale 2 puffs every 4-6 hours as needed for asthma or bronchospasm.",
    "Prednisone": "Dosage varies; commonly 5-60mg daily for inflammation. Taper gradually to avoid withdrawal.",
    "Insulin glargine": "Inject subcutaneously once daily at the same time each day for blood sugar control.",
    "Fluoxetine": "Start with 10-20mg daily for depression or anxiety, may increase based on response.",
    "Hydrocodone": "Take 5-10mg every 4-6 hours as needed for pain. Use with caution due to addiction risk.",
    "Warfarin": "Dose varies (2-10mg daily) based on INR levels for blood thinning. Regular monitoring required.",
    "Omeprazole": "Take 20-40mg once daily before meals for acid reflux or ulcers.",
    "Sumatriptan": "Take 25-100mg at migraine onset; may repeat after 2 hours if needed (max 200mg/day)."
}

def get_medication_usage(med_name):
    """
    Returns the recommended clinical usage for a given medication name.
    
    Parameters:
    med_name (str): The name of the medication (generic or brand).
    
    Returns:
    str: Recommended usage instructions based on clinical guidelines.
    """
    med_name = med_name.strip().capitalize()  # Normalize input capitalization
    return medication_usage.get(med_name, "No clinical usage found. Consult a healthcare provider.")

# Main Layout
pri_layout = dmc.MantineProvider(
    id="mantine_provider",
    forceColorScheme="dark",
    children=[
        dmc.Group(
            justify="center",
            grow=True,
            children=[
                dmc.Text("Hey Priyanka!", size="lg"),
                dmc.Text("Let's start coding practice", size="sm"),
                html.A("Guides", href="https://www.dash-mantine-components.com/components/button"),
                dmc.Button(
                    "Bump Pri to 5 Stars 🌟",
                    id="button",
                    variant="gradient",
                    radius=20,
                    gradient={"from": "grape", "to": "pink", "deg": 35},
                    n_clicks=0,
                ),
                dmc.Stack(
                    [
                        dmc.Group([dmc.Text("Priyanka"), dmc.Rating(id="rating", fractions=2, value=4)]),
                        dmc.Group([dmc.Text("Krishan"), dmc.Rating(fractions=3, value=3.5)]),
                        dmc.Group([dmc.Text("Both"), dmc.Rating(fractions=4, value=5)]),
                    ]
                ),
            ],
        ),
        dmc.Divider(size="lg"),
        dmc.Space(h="lg"),
        dmc.Group(
            justify="center",
            children=[
                dmc.Stack(
                    w=500,
                    children=[
                        dmc.Text("Drug Lookup"),
                        dmc.SegmentedControl(id="generic_or_brand", data=["Generic","Brand"], value="Generic", radius=20),
                        dmc.Select(id="med_category", placeholder="Drug Category", data=list(prescription_medications.keys()), value=None, radius=20),
                        dmc.Select(id="med_sub_category", placeholder="Drug Sub Category", radius=20, display="none"),
                        dmc.Select(id="med_name", placeholder="Drug Name", radius=20, display="none"),
                        dmc.Text(id="recommended_instructions", display="none"),
                    ],
                ),
            ],
        ),
    ],
)

@callback(
    Output("rating", "value"),
    Input("button", "n_clicks"),
)
def pri_is_the_best(clicks):
    if clicks > 0:
        return 5
    else:
        return 1
    
@callback(
    Output("med_sub_category", "display"),
    Output("med_sub_category", "data"),
    Output("med_name", "display"),
    Output("med_name", "data"),
    Output("recommended_instructions", "display"),
    Output("recommended_instructions", "children"),
    Input("generic_or_brand", "value"),
    Input("med_category", "value"),
    Input("med_sub_category", "value"),
    Input("med_name", "value"),
)
def drug_lookup(generic_or_brand_val, category_val, sub_category_val, med_name_val):
    hide = "none"
    show = ""
    sub_categories = []
    med_names = []
    instructions = ""

    if category_val:
        sub_categories = list(prescription_medications[category_val])
        if sub_categories == ["Generic", "Brand"]:
            med_names = prescription_medications[category_val][generic_or_brand_val]
            if med_name_val:
                instructions = get_medication_usage(med_name_val)
                return hide, sub_categories, show, med_names, show, instructions
            return hide, sub_categories, show, med_names, hide, instructions
        elif sub_category_val:
            med_names = prescription_medications[category_val][sub_category_val][generic_or_brand_val]
            if med_name_val:
                instructions = get_medication_usage(med_name_val)
                return show, sub_categories, show, med_names, show, instructions
            return show, sub_categories, show, med_names, hide, instructions
        else:
            return show, sub_categories, hide, med_names, hide, instructions
    else:
        return hide, sub_categories, hide, med_names, hide, instructions
    

dash.register_page(
    __name__,
    path="/priyanka",
    redirect_from=['/pri'],
    layout=pri_layout,
    title='Priyanka',
    name='Priyanka',
    image="assets/favicon.ico",
)
