import streamlit as st
import pandas as pd
import json
import os
from agent.generator import DataGenerator
from agent.ranker import ProbabilityEngine

# Page Config - Set theme
st.set_page_config(
    page_title="LeadLattice Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Black & Blue" Theme
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        color: #ec4899; /* Medium Pink */
    }
    
    /* Dataframe */
    .stDataFrame {
        border: 1px solid #333;
    }
    
    /* Buttons */
    div.stButton > button {
        background-color: #db2777; /* Deep Pink */
        color: white;
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #be185d;
        color: white;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 1px solid #333;
    }
    
    /* Links */
    a {
        color: #ffffff !important; /* White */
        text-decoration: underline;
    }
    a:hover {
        color: #e4e4e7 !important; /* Zinc-200 */
        text-decoration: underline;
    }
    </style>
""", unsafe_allow_html=True)

def load_data():
    # Load logic - Try to load from json, else generate
    json_path = "dashboard/public/leads_data.json"
    
    data = []
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            data = json.load(f)
    else:
        # Fallback to generating live if file missing
        gen = DataGenerator()
        leads = gen.generate_sample_leads(100)
        ranker = ProbabilityEngine()
        ranked = ranker.rank_leads(leads)
        data = [l.model_dump() for l in ranked]

    if not data:
        return pd.DataFrame()

    # Flatten logic
    flat_data = []
    for item in data:
        # Ensure company is a dict (it should be)
        if 'company' in item and isinstance(item['company'], dict):
            comp = item.pop('company')
            item.update({f"company_{k}": v for k, v in comp.items()})
        
        flat_data.append(item)
            
    df = pd.DataFrame(flat_data)
    
    # Ensure critical columns exist (migration safety)
    if 'email' not in df.columns:
        df['email'] = 'Unavailable'
    if 'location_person' not in df.columns:
        df['location_person'] = 'Unknown'
        
    return df

st.title("🧬 LeadLattice")
st.caption("AI-Powered Lead Identification & Ranking System")

# Sidebar
with st.sidebar:
    st.header("Filters")
    min_score = st.slider("Min Probability Score", 0, 100, 50)
    
    st.markdown("---")
    st.info("**System Status**\n\n🟢 Agent: Active\n\n🟢 Model: v1.0.2")

# Main Data
df = load_data()

# Process Data for Display
if not df.empty:
    # Filter
    filtered_df = df[df['score'] >= min_score].copy()
    
    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Leads", len(filtered_df))
    c2.metric("Avg Probability", f"{filtered_df['score'].mean():.1f}%")
    high_intent = len(filtered_df[filtered_df['rank_tier'] == 'Highest'])
    c3.metric("High Intent Leads", high_intent)
    
    st.markdown("### Prioritized Leads")
    
    # Formatting for display
    display_cols = [
        'score', 'rank_tier', 'name', 'title', 'company_name', 
        'location_person', 'email', 'linkedin_url'
    ]
    
    # Renaming for cleaner table
    display_df = filtered_df.rename(columns={
        'company_name': 'Company',
        'score': 'Prob %',
        'rank_tier': 'Rank',
        'name': 'Name',
        'title': 'Title',
        'location_person': 'Location',
        'email': 'Email',
        'linkedin_url': 'LinkedIn'
    })
    
    # Make LinkedIn clickable (trickier in st.dataframe, easier in st.data_editor with column config)
    st.data_editor(
        display_df[['Prob %', 'Rank', 'Name', 'Title', 'Company', 'Location', 'Email', 'LinkedIn']],
        column_config={
            "Prob %": st.column_config.ProgressColumn(
                "Probability",
                help="AI Confidence Score",
                format="%d%%",
                min_value=0,
                max_value=100,
            ),
            "LinkedIn": st.column_config.LinkColumn("Profile")
        },
        hide_index=True,
        use_container_width=True,
        height=600
    )
    
    # Download
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download All Leads (CSV)",
        data=csv,
        file_name='lead_lattice_export.csv',
        mime='text/csv',
    )
    
else:
    st.warning("No data found. Please run the generation script.")

