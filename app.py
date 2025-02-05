import streamlit as st
import math
import os
import pandas as pd
import requests

st.set_page_config(layout="wide")

# Apply Background Color
st.markdown(
    """
    <style>
    .stApp {
        background-color: lightgreen;
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
if "total_carbon" not in st.session_state:
    st.session_state.total_carbon = None
if "total_carbon_tones_per_hector" not in st.session_state:
    st.session_state.total_carbon_tones_per_hector = None 
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

def calculate_above_ground_biomass_tones_per_hector(total_biomass):
    return (total_biomass/10)

def calculate_stem_carbon(E,stem_biomass):
    return ((E/100)*stem_biomass)

def calculate_branch_carbon(G,branch_biomass):
    return ((G/100)*branch_biomass)

def calculate_leaf_carbon(H,leaf_biomass):
    return ((H/100)*leaf_biomass)

def calculate_total_carbon(total_stem_carbon,total_branch_carbon,total_leaf_carbon):
    return total_stem_carbon+total_branch_carbon+total_leaf_carbon
def calculate_total_carbon_tones_per_hector(total_carbon):
    return (total_carbon/10)
def calculate_co2_equivalent(total_carbon_tones_per_hector):
    return 3.67*total_carbon_tones_per_hector


def get_user_ip():
    """Get the user's IP address using an external API."""
    try:
        response = requests.get('https://api.ipify.org?format=json')
        user_ip = response.json().get('ip')
        return user_ip
    except requests.exceptions.RequestException:
        return "unknown_ip"


def save_to_excel():
    # Define file path
    user_ip = get_user_ip()
    excel_file = f"{user_ip}_carbon_calculator_results.xlsx"

    # Ensure all necessary calculations have been performed
    if None in [st.session_state.get("stem_biomass"), st.session_state.get("branch_biomass"), st.session_state.get("leaf_biomass")]:
        st.error("Please perform all calculations before saving to Excel.")
        return

    # Retrieve values from session state
    data = {
        "Name": [st.session_state.get("name", "N/A")],
        "No_of_trees_per_100m": [st.session_state.get("N", "N/A")],
        "Population_Density": [st.session_state.get("A", "N/A")],
        "Height": [st.session_state.get("H", "N/A")],
        "Circumference_at_breast_height": [st.session_state.get("two_pi_r", "N/A")],
        "Circumference_at_base": [st.session_state.get("two_pi_R", "N/A")],
        "r (Breast Height Radius)": [st.session_state.get("r", "N/A")],
        "R (Base Radius)": [st.session_state.get("R", "N/A")],
        "Stem Biomass Per Tree": [st.session_state.get("stem_biomass_per_tree", "N/A")],
        "Total Stem Biomass": [st.session_state.get("stem_biomass", "N/A")],
        "Branch Biomass Per Tree": [st.session_state.get("branch_biomass_per_tree", "N/A")],
        "Total Branch Biomass": [st.session_state.get("branch_biomass", "N/A")],
        "Leaf Biomass Per Tree": [st.session_state.get("leaf_biomass_per_tree", "N/A")],
        "Total Leaf Biomass": [st.session_state.get("leaf_biomass", "N/A")],
        "Total Biomass": [st.session_state.get("above_ground_biomass_results", {}).get("Total Biomass ", "N/A")],
        "Total Biomass tones per hectare": [st.session_state.get("above_ground_biomass_results", {}).get("Total Biomass tones per hector", "N/A")],
        "Carbon of Stem": [st.session_state.get("carbon_results", {}).get("Total Above ground Carbon", "N/A")],
        "Total Carbon": [st.session_state.get("total_carbon", "N/A")],
        "Total Carbon tones per hectare": [st.session_state.get("carbon_results", {}).get("Total Above ground Carbon tones per hector", "N/A")],
        "CO2 Equivalent": [st.session_state.get("co2_results", {}).get("CO2 Equivalent", "N/A")]
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

    


# Layout

st.write("<h1 style='color: white; text-align:center; padding: 20px; background-color: black; font-family: Arial, sans-serif; font-style: italic;'>CARBON CALCULATOR</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

# ======= STEM BIOMASS CALCULATOR =======
with col1:
    st.write("<h1 style='color: purple;'>STEM BIOMASS CALCULATOR</h1>", unsafe_allow_html=True)

    name = st.text_input("Name of the Species")
    N = st.number_input("No. of trees per 100 Sq. m", min_value=1, value=st.session_state.N if st.session_state.N is not None else 1, key="num_trees_stem")
    D = st.number_input("Wood Density (in kg/Cu. m)",value=None)
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
    st.write("<h1 style='color: purple;'>Field Acitivities</h3>", unsafe_allow_html=True)
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

    n = st.number_input("No. of trees", min_value=1, value=st.session_state.N if st.session_state.N is not None else 1, key="num_trees_branch")
    A = st.number_input("No. of Branch per tree", min_value=1)
    B = st.number_input("Dry weight of one Branch", min_value=0.0, step=0.00001, format="%.5f",value=None)

    if st.button("Calculate Branch Biomass"):
        try:
            branch_biomass_per_tree = calculate_branch_biomass_per_tree(A, B)
            total_branch_biomass = calculate_total_branch_biomass(n, branch_biomass_per_tree)

            # Store results in session state
            st.session_state.A = A
            st.session_state.branch_biomass_per_tree= branch_biomass_per_tree 
            st.session_state.branch_biomass= total_branch_biomass  
            st.session_state.branch_results = {
            "Branch Biomass per Tree": branch_biomass_per_tree,
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
    st.image("WhatsApp Image 2025-02-01 at 7.28.33 PM.jpeg",width=250)

# ======= LEAF BIOMASS CALCULATOR =======
col1, col2 = st.columns([2, 1])
with col1:
    st.write("<h1 style='color: purple;'>LEAF BIOMASS CALCULATOR</h1>", unsafe_allow_html=True)

    N2 = st.number_input("No. of trees", min_value=1, value=st.session_state.N if st.session_state.N is not None else 1, key="num_trees_leaf")
    A2 = st.number_input("No. of Branch per tree", min_value=1, value=st.session_state.A if st.session_state.A else 1,key="num_branch_leaf")
    C = st.number_input("No. of Leaves per Branch", min_value=0.0, step=0.1, format="%.5f", value=None)
    D = st.number_input("Dry weight of one leaf", min_value=0.0, step=0.00001, format="%.5f", value=None)

    if st.button("Calculate Leaf Biomass"):
        try:
            leaf_biomass_per_tree = calculate_total_leaf_biomass_per_tree(A2, C, D)
            total_leaf_biomass = calculate_total_leaf_biomass(N2, leaf_biomass_per_tree)

            # Store results in session state
            st.session_state.leaf_biomass_per_tree= leaf_biomass_per_tree
            st.session_state.leaf_biomass= total_leaf_biomass
            st.session_state.leaf_results = {
                "Leaf Biomass per Tree": leaf_biomass_per_tree,
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
        total_biomass_tones_per_hector =calculate_above_ground_biomass_tones_per_hector(total_biomass)

        # Store results in session state
        st.session_state.above_ground_biomass_results = {
            "Total Biomass ": total_biomass,
            "Total Biomass tones per hector": f"{total_biomass_tones_per_hector} kg"
         }
    except:
            st.write("Please perform all calculation!!!")
if st.session_state.above_ground_biomass_results:
    st.subheader("Calculated Total Biomass:")
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
            total_carbon_tones_per_hector=calculate_total_carbon_tones_per_hector(total_carbon)

        
            st.session_state.total_carbon=total_carbon
            st.session_state.total_carbon_tones_per_hector=total_carbon_tones_per_hector
            st.session_state.carbon_results = {
                "Total Above ground Carbon": total_carbon,
                "Total Above ground Carbon tones per hector": f"{total_carbon_tones_per_hector} kg"
            }
        except:
            st.warning("Please perfrom all the calculation!!!")
    if st.session_state.carbon_results:
        st.subheader("Calculated Above Ground Total Carbon:")
        for key, value in st.session_state.carbon_results.items():
            st.write(f"{key}: {value}")

    if st.button("Calculate CO2-Equivalent"):
        try:
            total_carbon_tones_per_hector=st.session_state.total_carbon_tones_per_hector
            co2_equivalent=calculate_co2_equivalent(total_carbon_tones_per_hector)

            st.session_state.co2_results = {
        
                "CO2 Equivalent": f"{co2_equivalent} kg"

            }
        except:
            st.warning("Please perfrom all the calculations!!!")
    if st.session_state.co2_results:
        st.subheader("Calculated CO2-equivalent CO2")
        for key, value in st.session_state.co2_results.items():
            st.write(f"{key}: {value}")

with col4:
    
    st.write("<h3 style='color: black;'>Above Ground Carbon</h3>", unsafe_allow_html=True)
    st.write(
        "<h6 style='color: dark green;'>Above-ground carbon in trees refers to the carbon stored in stems, branches, leaves, and other aerial biomass, playing a vital role in carbon sequestration. Through photosynthesis, trees absorb atmospheric carbon dioxide and lock it in their biomass, reducing greenhouse gas concentrations and mitigating climate change. This stored carbon remains in the ecosystem until the tree decomposes or is burned, releasing it back into the atmosphere.</h6>",
        unsafe_allow_html=True,
    )
    st.image("WhatsApp Image 2025-02-01 at 7.48.03 PM.jpeg",width=250)




if st.button("Save Results to Excel"):
    save_to_excel()
def display():
    user_ip=get_user_ip()
    excel_file=f"{user_ip}carbon_calculator_results.xlsx"
    #   Display existing data
    if os.path.exists(excel_file):
        st.subheader("Stored Data:")
        df = pd.read_excel(excel_file)
        st.dataframe(df)
def delete_item_from_excel(delete_name):
    user_ip=get_user_ip()
    excel_file=f"{user_ip}carbon_calculator_results.xlsx"
    
    if os.path.exists(excel_file):
        # Read the existing Excel file into a DataFrame
        data = pd.read_excel(excel_file)

        # Check if the name exists in the data and delete that row
        data = data[data["Name"] != delete_name]

        # Save the updated DataFrame back to Excel
        data.to_excel(excel_file, index=False)

        st.success(f"Item with name '{delete_name}' has been deleted from the Excel file!")
    else:
        st.error("The Excel file does not exist.")

# Example usage: Delete a row with a specific name
delete_name = st.text_input("Enter the Name to delete:")
if st.button("Delete Item"):
    delete_item_from_excel(delete_name)


col1,col2=st.columns([2,1])
with col1:
    FILE_NAME = "contact_messages.xlsx"

    # Function to save data to an Excel file
    def save_to_excel(name, email, message):
        new_data = pd.DataFrame({"Name": [name], "Email": [email], "Message": [message]})
    
        if os.path.exists(FILE_NAME):
            existing_data = pd.read_excel(FILE_NAME, engine="openpyxl")
            updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        else:
            updated_data = new_data

        updated_data.to_excel(FILE_NAME, index=False, engine="openpyxl")
    
    st.title("📩 Contact Us")

    # Contact Form Inputs
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    message = st.text_area("Your Message")

    # Submit Button
    if st.button("Submit res"):
        if name and email and message:
            save_to_excel(name, email, message)
            st.success("✅ Thank you! Your message has been saved.")
        else:
            st.warning("⚠️ Please fill in all fields before submitting.")

with col2:
    st.title("Knowledge Hunter")
    st.image("WhatsApp Image 2025-02-05 at 12.09.09 AM.jpeg",width=250)
    st.write("Email: abhijitresearchmitra@gmail.com")
    st.write("<h5 style='color: black;'>Dive deep into the sea of knowledge to get pearl of peace.</h5>", unsafe_allow_html=True)



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