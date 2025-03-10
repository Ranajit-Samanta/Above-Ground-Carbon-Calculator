import streamlit as st
import math
import os
import pandas as pd
import smtplib
from email.mime.text import MIMEText
import uuid
import base64
st.set_page_config(layout="wide")

# Apply Background Color
st.markdown(
    """
    <style>
    .stApp {
        background-color: lightgreen;
        background-image: linear-gradient(90deg,rgb(0, 223, 152),
rgb(148, 148, 148));
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state variables if not set
if "name" not in st.session_state:
    st.session_state.name = None
if "N" not in st.session_state:
    st.session_state.N = None
if "D" not in st.session_state:
    st.session_state.D = None
if "H" not in st.session_state:
    st.session_state.H = None  
if "A" not in st.session_state:
    st.session_state.A = None
if "two_pi_r" not in st.session_state:
    st.session_state.two_pi_r = None
if "two_pi_R" not in st.session_state:
    st.session_state.two_pi_R = None
if "r" not in st.session_state:
    st.session_state.r = None  
if "R" not in st.session_state:
    st.session_state.R = None
if "stem_biomass_per_tree" not in st.session_state:
    st.session_state.stem_biomass_per_tree = None   
if "stem_biomass" not in st.session_state:
    st.session_state.stem_biomass = None
if "branch_biomass_per_tree" not in st.session_state:
    st.session_state.branch_biomass_per_tree = None
if "branch_biomass" not in st.session_state:
    st.session_state.branch_biomass = None
if "leaf_biomass_per_tree" not in st.session_state:
    st.session_state.leaf_biomass_per_tree = None
if "leaf_biomass" not in st.session_state:
    st.session_state.leaf_biomass = None
if "above_ground_biomass" not in st.session_state:
    st.session_state.above_ground_biomass = None
if "above_ground_biomass_tonnes_per_hectare" not in st.session_state:
    st.session_state.above_ground_biomass_tonnes_per_hectare = None
if "stem_results" not in st.session_state:
    st.session_state.stem_results = {}  
if "branch_results" not in st.session_state:
    st.session_state.branch_results = {}  
if "leaf_results" not in st.session_state:
    st.session_state.leaf_results = {}
if "above_ground_biomass_results" not in st.session_state:
    st.session_state.above_ground_biomass_results = {}
if "carbon_results" not in st.session_state:
    st.session_state.carbon_results = {}
if "total_stem_carbon" not in st.session_state:
    st.session_state.total_stem_carbon = None
if "total_branch_carbon" not in st.session_state:
    st.session_state.total_branch_carbon = None
if "total_leaf_carbon" not in st.session_state:
    st.session_state.total_leaf_carbon = None
if "total_carbon" not in st.session_state:
    st.session_state.total_carbon = None
if "total_carbon_tonnes_per_hectare" not in st.session_state:
    st.session_state.total_carbon_tonnes_per_hectare = None 
if "co2_results" not in st.session_state:
    st.session_state.co2_results = {}



# Define calculations
def calculate_r_R(two_pi_r, two_pi_R):
    r = two_pi_r / (2 * math.pi)
    R = two_pi_R / (2 * math.pi)
    return r, R

def calculate_from_factor(r, R):
    return (r * r) / (R * R)

def calculate_stem_biomass_per_tree(r, H, D, from_factor):
    return math.pi * r * r * H * D * from_factor

def calculate_stem_biomass_tree(N, stem_biomass_per_tree):
    return N * stem_biomass_per_tree

def calculate_branch_biomass_per_tree(A, B):
    return A * B

def calculate_total_branch_biomass(n, branch_biomass_per_tree):
    return n * branch_biomass_per_tree

def calculate_total_leaf_biomass_per_tree(A, c, d):
    return A * c * d  # Fixed variable reference

def calculate_total_leaf_biomass(N, leaf_biomass_per_tree):
    return N * leaf_biomass_per_tree  # Used correct variable

def calculate_above_ground_biomass(stem_biomass,branch_biomass,leaf_biomass):
    return (stem_biomass+branch_biomass+leaf_biomass)

def calculate_above_ground_biomass_tonnes_per_hectare(total_biomass):
    return (total_biomass/10)

def calculate_stem_carbon(E,stem_biomass):
    return ((E/100)*stem_biomass)

def calculate_branch_carbon(G,branch_biomass):
    return ((G/100)*branch_biomass)

def calculate_leaf_carbon(H,leaf_biomass):
    return ((H/100)*leaf_biomass)

def calculate_total_carbon(total_stem_carbon,total_branch_carbon,total_leaf_carbon):
    return total_stem_carbon+total_branch_carbon+total_leaf_carbon
def calculate_total_carbon_tonnes_per_hectare(total_carbon):
    return (total_carbon/10)
def calculate_co2_equivalent(total_carbon_tonnes_per_hectare):
    return 3.67*total_carbon_tonnes_per_hectare

#========= user session id========#

def get_user_session_id():
    """Ensure the session ID persists across interactions."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())  # Create a new session ID for the user
    return st.session_state.session_id

#====== saving this values in excel ======#

def save_to_excel():
    # Define file path
    user_ip = get_user_session_id()
    excel_file = f"carbon_calculator_results_{user_ip}.xlsx"

    # Ensure all necessary calculations have been performed
    if None in [st.session_state.get("stem_biomass"), st.session_state.get("branch_biomass"), st.session_state.get("leaf_biomass")]:
        st.error("Please perform all calculations before saving to Excel.")
        return

    # Retrieve values from session state
    data = {
        "Name": [st.session_state.get("name", "N/A")],
        "No of trees per 100 m²": [st.session_state.get("N", "N/A")],
        "Wood Density (in kg/m³)": [st.session_state.get("D", "N/A")],
        "Height (in m)": [st.session_state.get("H", "N/A")],
        "Circumference at breast height (in m)": [st.session_state.get("two_pi_r", "N/A")],
        "Circumference at base (in m)": [st.session_state.get("two_pi_R", "N/A")],
        "r (Breast Height Radius) (in m)": [st.session_state.get("r", "N/A")],
        "R (Base Radius) (in m)": [st.session_state.get("R", "N/A")],
        "Stem Biomass Per Tree (kg)": [st.session_state.get("stem_biomass_per_tree", "N/A")],
        "Total Stem Biomass (kg)": [st.session_state.get("stem_biomass", "N/A")],
        "Branch Biomass Per Tree (kg)": [st.session_state.get("branch_biomass_per_tree", "N/A")],
        "Total Branch Biomass (kg)": [st.session_state.get("branch_biomass", "N/A")],
        "Leaf Biomass Per Tree (kg)": [st.session_state.get("leaf_biomass_per_tree", "N/A")],
        "Total Leaf Biomass (kg)": [st.session_state.get("leaf_biomass", "N/A")],
        "Above Ground Biomass (kg/100 m²)": [st.session_state.get("above_ground_biomass","N/A")],
        "AGB (t/ha)": [st.session_state.get("above_ground_biomass_tonnes_per_hectare","N/A")],
        "Total Stem Carbon (kg)": [st.session_state.get("total_stem_carbon","N/A")],
        "Total Branch Carbon (kg)": [st.session_state.get("total_branch_carbon","N/A")],
        "Total Leaf Carbon (kg)": [st.session_state.get("total_leaf_carbon","N/A")],
        "Above Ground Carbon (kg/100 m²)": [st.session_state.get("total_carbon", "N/A")],
        "AGC (t/ha)": [st.session_state.get("total_carbon_tonnes_per_hectare", "N/A")],
        "CO2 Equivalent (t/ha)": [st.session_state.get("co2_results", {}).get("CO2-Equivalent", "N/A")]
    }

    # Convert to DataFrame
    new_data = pd.DataFrame(data)

    # Check if the file exists
    if os.path.exists(excel_file):
        # Load existing data
        existing_data = pd.read_excel(excel_file, engine="openpyxl")
        # Append new data
        updated_data = pd.concat([existing_data, new_data], ignore_index=True)
    else:
        # If file doesn't exist, create a new one
        updated_data = new_data

    # Save data to Excel
    updated_data.to_excel(excel_file, index=False, engine="openpyxl")

    st.success(f"Session data saved to {excel_file} successfully!")

def display():
    user_ip=get_user_session_id()
    excel_file=f"carbon_calculator_results_{user_ip}.xlsx"
    #   Display existing data
    if os.path.exists(excel_file):
        st.subheader("Stored Data:")
        df = pd.read_excel(excel_file, engine="openpyxl")
        st.dataframe(df)
    
def delete_item_from_excel(delete_name):
    user_ip=get_user_session_id()
    excel_file=f"carbon_calculator_results_{user_ip}.xlsx"
    
    if os.path.exists(excel_file):
        # Read the existing Excel file into a DataFrame
        data = pd.read_excel(excel_file, engine="openpyxl")

        # Check if the name exists in the data and delete that row
        data = data[data["Name"] != delete_name]

        # Save the updated DataFrame back to Excel
        data.to_excel(excel_file, index=False, engine="openpyxl")

        st.success(f"Item with name '{delete_name}' has been deleted from the Excel file!")
    else:
        st.error("The Excel file does not exist.")

# Layout

# st.write("<h1 style='color:white; text-align:center; padding: 20px; background-color: black; font-family: Times New Roman, Times, serif; font-style: italic;'>🌳Unlocking the Tree Carbon Locker🌍</h1>", unsafe_allow_html=True)
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

image_base64 = get_base64_image("WhatsApp Image 2025-02-21 at 7.30.13 PM.png")

st.write(f"""
    <div class="unlocking_div" style='color: white; text-align:center; padding: 10px; background-color: #353839; 
    font-family: Times New Roman, Times, serif; font-style: italic; display: flex; 
    align-items: center; justify-content: center; gap: 18px;'>
        <img src="data:image/png;base64,{image_base64}" alt="Logo" 
        style="width:100px; height:auto;border-radius:50px">
        <h1 style='margin: 0; font-size: 42px;color: white;'>Unlocking the Tree Carbon Locker</h1>
    </div>
""", unsafe_allow_html=True)




col1, col2 = st.columns([2, 1])

# ======= STEM BIOMASS CALCULATOR =======
with col1:
    st.write("<h1 style='color: purple;'>STEM BIOMASS CALCULATOR</h1>", unsafe_allow_html=True)

    name = st.text_input("Name of the Species")
    N = st.number_input("No. of trees/100 m²", min_value=1, value=st.session_state.N if st.session_state.N is not None else 1, key="num_trees_stem")
    D = st.number_input("Wood Density (in kg/m³)",value=None)
    H = st.number_input("Height (in m)", min_value=0.0, value=None,format="%.5f")
    two_pi_r = st.number_input("Circumference at breast height (in m)", min_value=0.0, step=0.1,value=None,format="%.5f")
    two_pi_R = st.number_input("Circumference at base (in m)", min_value=0.0, step=0.1,value=None,format="%.5f")

    if st.button("Calculate Stem Biomass"):
        try:

            r, R = calculate_r_R(two_pi_r, two_pi_R)
            from_factor = calculate_from_factor(r, R)
            stem_biomass_per_tree = calculate_stem_biomass_per_tree(r, H, D, from_factor)
            total_stem_biomass = calculate_stem_biomass_tree(N, stem_biomass_per_tree)

            # Store results in session state
            st.session_state.name=name
            st.session_state.N = N
            st.session_state.D = D
            st.session_state.H=H
            st.session_state.two_pi_r=two_pi_r
            st.session_state.two_pi_R=two_pi_R
            st.session_state.r = r
            st.session_state.R=R
            st.session_state.stem_biomass_per_tree= stem_biomass_per_tree
            st.session_state.stem_biomass = total_stem_biomass
            st.session_state.stem_results = {
            "From Factor": from_factor,
            "Stem Biomass per Tree": f"{stem_biomass_per_tree} kg",
            "Total Stem Biomass": f"{total_stem_biomass} kg"
            }
        except:
            st.warning("Please enter proper values!!!")

    # Display Stem Biomass Results
    if st.session_state.stem_results:
        st.subheader("Calculated Stem Biomass:")
        for key, value in st.session_state.stem_results.items():
            st.write(f"{key}: {value}")

    #if st.session_state.stem_results:
        


with col2:
    st.write("<h1 style='color: purple;'>Field Activities</h1>", unsafe_allow_html=True)
    st.write("<h3 style='color: black;'>Stem Biomass</h3>", unsafe_allow_html=True)
    st.write(
        "<h6 style='color: dark green;'>For a tree of 5-10 years, stem biomass constitutes 50-70% of the total tree biomass."
        " However, this value is a function of species, age, and environmental conditions. Stem accumulates considerable amount of carbon.</h6>",
        unsafe_allow_html=True,
    )
    st.image("WhatsApp Image 2025-01-31 at 11.29.44 PM.jpeg")


# ======= BRANCH BIOMASS CALCULATOR =======
col1, col2 = st.columns([2, 1])
with col1:
    st.write("<h1 style='color: purple;'>BRANCH BIOMASS CALCULATOR</h1>", unsafe_allow_html=True)

    n = st.number_input("No. of trees/100 m²", min_value=1, value=st.session_state.N if st.session_state.N is not None else 1, key="num_trees_branch")
    A = st.number_input("No. of Branch per tree", min_value=1)
    B = st.number_input("Dry weight of one Branch (in kg)", min_value=0.0, step=0.00001, format="%.5f",value=None)

    if st.button("Calculate Branch Biomass"):
        try:
            branch_biomass_per_tree = calculate_branch_biomass_per_tree(A, B)
            total_branch_biomass = calculate_total_branch_biomass(n, branch_biomass_per_tree)

            # Store results in session state
            st.session_state.A = A
            st.session_state.branch_biomass_per_tree= branch_biomass_per_tree 
            st.session_state.branch_biomass= total_branch_biomass  
            st.session_state.branch_results = {
            "Branch Biomass per Tree": f"{branch_biomass_per_tree} kg",
            "Total Branch Biomass": f"{total_branch_biomass} kg"
            }
        except:
            st.warning("Please enter proper values!!!")
    # Display Branch Biomass Results
    if st.session_state.branch_results:
        st.subheader("Calculated Branch Biomass:")
        for key, value in st.session_state.branch_results.items():
            st.write(f"{key}: {value}")

with col2:
    st.write("<h3 style='color: black;'>Branch Biomass</h3>", unsafe_allow_html=True)
    st.write(
        "<h6 style='color: dark green;'>Branch biomass of trees plays a crucial role in carbon sequestration by storing atmospheric carbon in its woody structure. As trees grow, they absorb carbon dioxide through photosynthesis and allocate a significant portion of it to branches, which serve as long-term carbon reservoirs.</h6>",
        unsafe_allow_html=True,
    )
    st.image("WhatsApp Image 2025-02-19 at 11.54.29 PM.jpeg",width=270)

# ======= LEAF BIOMASS CALCULATOR =======
col1, col2 = st.columns([2, 1])
with col1:
    st.write("<h1 style='color: purple;'>LEAF BIOMASS CALCULATOR</h1>", unsafe_allow_html=True)

    N2 = st.number_input("No. of trees/100 m²", min_value=1, value=st.session_state.N if st.session_state.N is not None else 1, key="num_trees_leaf")
    A2 = st.number_input("No. of Branch per tree", min_value=1, value=st.session_state.A if st.session_state.A else 1,key="num_branch_leaf")
    C = st.number_input("No. of Leaves per Branch", min_value=0.0, step=0.1, format="%.5f", value=None)
    D = st.number_input("Dry weight of one leaf (in kg)", min_value=0.0, step=0.00001, format="%.5f", value=None)

    if st.button("Calculate Leaf Biomass"):
        try:
            leaf_biomass_per_tree = calculate_total_leaf_biomass_per_tree(A2, C, D)
            total_leaf_biomass = calculate_total_leaf_biomass(N2, leaf_biomass_per_tree)

            # Store results in session state
            st.session_state.leaf_biomass_per_tree= leaf_biomass_per_tree
            st.session_state.leaf_biomass= total_leaf_biomass
            st.session_state.leaf_results = {
                "Leaf Biomass per tree": f"{leaf_biomass_per_tree} kg",
                "Total Leaf Biomass": f"{total_leaf_biomass} kg"
            }
        except:
            st.warning("Please enter proper values!!!")
    # Display Leaf Biomass Results
    if st.session_state.leaf_results:
        st.subheader("Calculated Leaf Biomass:")
        for key, value in st.session_state.leaf_results.items():
            st.write(f"{key}: {value}")

with col2:
    st.write("<h3 style='color: black;'>Leaf Biomass</h3>", unsafe_allow_html=True)
    st.write(
        "<h6 style='color: dark green;'>Leaf biomass of trees plays a vital role in carbon sequestration by capturing atmospheric carbon dioxide through photosynthesis. Although leaves have a shorter lifespan than woody biomass, they contribute to the carbon cycle by storing carbon temporarily and enriching the soil with organic matter upon decomposition.</h6>",
        unsafe_allow_html=True,
    )
    st.image("WhatsApp Image 2025-02-01 at 7.29.43 PM.jpeg",width=250)



# ======= Total Biomass =======
if st.button("Calculate Above Ground Biomass:"):
    try:
        stem_biomass=st.session_state.stem_biomass
        branch_biomass=st.session_state.branch_biomass
        leaf_biomass=st.session_state.leaf_biomass
        total_biomass = calculate_above_ground_biomass(stem_biomass,branch_biomass,leaf_biomass)
        total_biomass_tones_per_hector =calculate_above_ground_biomass_tonnes_per_hectare(total_biomass)

        # Store results in session state
        st.session_state.above_ground_biomass=total_biomass
        st.session_state.above_ground_biomass_tonnes_per_hectare=total_biomass_tones_per_hector
        st.session_state.above_ground_biomass_results = {
            "Above Ground Biomass": f"{total_biomass} kg/100 m²",
            "Above Ground Biomass.": f"{total_biomass_tones_per_hector} t/ha"
         }
    except:
            st.write("Please perform all calculation!!!")
if st.session_state.above_ground_biomass_results:
    st.subheader("Calculated Above Ground Biomass:")
    for key, value in st.session_state.above_ground_biomass_results.items():
        st.write(f"{key}: {value}")



# ======= carbon calculator =======

col3,col4=st.columns([2,1])
with col3:
    st.write("<h1 style='color: purple;'>ABOVE GROUND CARBON CALCULATOR</h1>", unsafe_allow_html=True)
    
    E = st.number_input("%C of Stem", min_value=0.0, step=0.00001, format="%.5f", value=None)
    G = st.number_input("%C of Branch", min_value=0.0, step=0.00001, format="%.5f", value=None)
    H = st.number_input("%C of Leaf", min_value=0.0, step=0.00001, format="%.5f", value=None)
    
    if st.button("Calculate Carbon"):
        try:
            stem_biomass=st.session_state.stem_biomass
            branch_biomass=st.session_state.branch_biomass
            leaf_biomass=st.session_state.leaf_biomass    
            total_stem_carbon=calculate_stem_carbon(E,stem_biomass)
            total_branch_carbon=calculate_branch_carbon(G,branch_biomass)
            total_leaf_carbon=calculate_leaf_carbon(H,leaf_biomass)
            total_carbon=calculate_total_carbon(total_stem_carbon,total_branch_carbon,total_leaf_carbon)
            total_carbon_tonnes_per_hectare=calculate_total_carbon_tonnes_per_hectare(total_carbon)

            st.session_state.total_stem_carbon=total_stem_carbon
            st.session_state.total_branch_carbon=total_branch_carbon
            st.session_state.total_leaf_carbon=total_leaf_carbon
            st.session_state.total_carbon=total_carbon
            st.session_state.total_carbon_tonnes_per_hectare=total_carbon_tonnes_per_hectare
            st.session_state.carbon_results = {
                "Above Ground Carbon": f"{total_carbon} kg/100 m²",
                "Above Ground Carbon.": f"{total_carbon_tonnes_per_hectare} t/ha"
            }
        except:
            st.warning("Please perfrom all the calculation!!!")
    if st.session_state.carbon_results:
        for key, value in st.session_state.carbon_results.items():
            st.write(f"{key}: {value}")

    if st.button("Calculate CO2-Equivalent"):
        try:
            total_carbon_tonnes_per_hectare=st.session_state.total_carbon_tonnes_per_hectare
            co2_equivalent=calculate_co2_equivalent(total_carbon_tonnes_per_hectare)
            
            st.session_state.co2_results = {
        
                "CO2-Equivalent": co2_equivalent

            }
        except:
            st.warning("Please perfrom all the calculations!!!")
    if st.session_state.co2_results:
        st.subheader("Calculated CO2-Equivalent:")
        for key, value in st.session_state.co2_results.items():
            st.write(f"{key}: {value} t/ha")

with col4:
    
    st.write("<h3 style='color: black;'>Above Ground Carbon</h3>", unsafe_allow_html=True)
    st.write(
        "<h6 style='color: dark green;'>Above-ground carbon in trees refers to the carbon stored in stems, branches, leaves, and other aerial biomass, playing a vital role in carbon sequestration. Through photosynthesis, trees absorb atmospheric carbon dioxide and lock it in their biomass, reducing greenhouse gas concentrations and mitigating climate change. This stored carbon remains in the ecosystem until the tree decomposes or is burned, releasing it back into the atmosphere.</h6>",
        unsafe_allow_html=True,
    )
    st.image("WhatsApp Image 2025-02-01 at 7.48.03 PM.jpeg",width=250)

if st.button("Save Results to Excel"):
    save_to_excel()
    display()
    st.warning("Please download your Excel file before refresh the page!!!")

# Example usage: Delete a row with a specific name
delete_name = st.text_input("Enter the Name to delete:")
if st.button("Delete Item"):
    delete_item_from_excel(delete_name)


#====== end note1 ========#

col1,col2=st.columns([2,1])
with col1:
    st.write(
        "<h2 style='color: purple;'>Plant Communities as Natural Carbon Sinks: A Cost-Effective Nature-Based Solution</h2>",
        unsafe_allow_html=True,
    )
    st.write(
        "<h5 style='color: brown;'>Dr. Abhijit Mitra believes that there are vital ecosystem services of plant communities in the context of climate change, as they regulate atmospheric CO₂ levels, enhance soil carbon storage, and stabilize ecosystems. Their role in carbon sequestration, biodiversity conservation, and climate resilience makes them essential for mitigating global warming impacts.</h5>",
        unsafe_allow_html=True,
    )
    st.write(
        "<h5 style='color: blue;'>1.	Mitigates Climate Change – Plant communities absorb atmospheric CO₂ through photosynthesis, reducing greenhouse gas concentrations and mitigating global warming.</h5>",
        unsafe_allow_html=True,
    )
    st.write(
        "<h5 style='color: brown;'>2.	Enhances Soil Carbon Storage – Root systems and leaf litter contribute to soil organic carbon (SOC), improving soil fertility and carbon retention.</h5>",
        unsafe_allow_html=True,
    )
    st.write(
        "<h5 style='color: green;'>3.	Promotes Biodiversity – Carbon-sequestering ecosystems like forests, wetlands, and grasslands provide habitats for diverse flora and fauna, supporting ecological balance.</h5>",
        unsafe_allow_html=True,
    )
    st.write(
        "<h5 style='color: purple;'>4.	Supports Blue Carbon Ecosystems – Coastal plant communities, such as mangroves, seagrasses, and salt marshes, play a crucial role in storing carbon in sediments for centuries.</h5>",
        unsafe_allow_html=True,
    )
    st.write(
        "<h5 style='color: brown;'>5.	Reduces Ocean Acidification – By lowering atmospheric CO₂ levels, plant-based sequestration indirectly mitigates ocean acidification, benefiting marine life.</h5>",
        unsafe_allow_html=True,
    )

with col2:
    st.write("<h2 style='color: black;'>Be a part of our team</h2>", unsafe_allow_html=True)
    st.video("SEA LEVEL RISE - A MAJOR THREAT IN THE PRESENT ERA BY DR. ABHIJIT MITRA.mp4")


#===== end note 2 =========#
col1,col2=st.columns([2,1])
with col1:
    st.write(
        "<h2 style='color: purple;'>End Note</h2>",
        unsafe_allow_html=True,
    )
    st.write(
        "<h5 style='color: blue;'>There are three types of people in life:</h5>",
        unsafe_allow_html=True,
    )
    st.write(
        "<h5 style='color: blue;'>Leaf People – They enter our lives for a short time, focus on their own growth (career), and eventually drift away; they are not dependable.</h5>",
        unsafe_allow_html=True,
    )
    st.write(
        "<h5 style='color: blue;'>Branch People – Strong and sturdy at first, but they break when faced with adversity; they are only partially reliable.</h5>",
        unsafe_allow_html=True,
    )
    st.write(
        "<h5 style='color: blue;'>Root People – The true pillars of support who stay by your side, providing strength and nourishment from the environment; they are highly dependable.</h5>",
        unsafe_allow_html=True,
    )
    st.write(
        '<h5 style="color: green;">"Be the Root People—stand firm, support others, and become a source of strength for all who rely on you."</h5>',
        unsafe_allow_html=True,
    )

with col2:
   st.write("<h3 style='color: black;'>Rooted Reflections: The Human-Tree Connection</h3>", unsafe_allow_html=True)
   st.image("WhatsApp Image 2025-02-21 at 7.36.31 PM.jpeg",width=250) 




#========== email configuration=========#



col1,col2=st.columns([2,1])

with col1:

# # Email Configuration

# Load email credentials from Streamlit Secrets
    EMAIL_ADDRESS = st.secrets["email"]["EMAIL_ADDRESS"]
    EMAIL_PASSWORD = st.secrets["email"]["EMAIL_PASSWORD"]

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    def send_email(name, user_email, message):
        subject = f"New Contact Form Submission from {name}"
        body = f"Name: {name}\nEmail: {user_email}\n\nMessage:\n{message}"

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS  # Use your email as sender
        msg["To"] = EMAIL_ADDRESS  # Send to yourself

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()  # Secure the connection
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())
            server.quit()
            return "✅ Your message has been sent successfully!"
        except Exception as e:
            return f"❌ Error: {str(e)}"

# Streamlit UI
    st.title("📩 Contact Us")

    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    message = st.text_area("Your Message")

    if st.button("Send Email"):
        if name and email and message:
            response = send_email(name, email, message)
            st.success(response)
        else:
            st.error("⚠️ Please fill in all fields.")




with col2:
    st.title("Knowledge Hunter")
    st.image("WhatsApp Image 2025-02-05 at 12.09.09 AM.jpeg",width=250)
    st.write("<h3 style='color: purple;'>Dr. Abhijit Mitra</h3>", unsafe_allow_html=True)
    st.write("Email: abhijitresearchmitra@gmail.com")
    st.write('<h5 style="color: purple;">"Dive deep into the sea of knowledge to get pearl of peace."</h5>', unsafe_allow_html=True)



st.markdown(
    """
    <style>
        .footer {
            
            bottom: 0;
            width: 100%;
            text-align: center;
            font-size: 14px;
            color: gray;
            padding: 10px;
            background-color: #f8f9fa;
        }
    </style>
    <div class="footer">
        © 2025 Carbon Calculator. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)






