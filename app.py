import streamlit as st
import pandas as pd
import plotly.express as px
from order_prediction_sql import get_db_connection, load_data, generate_prediction_for_record
import os
from dotenv import load_dotenv
import pyodbc
import xmltodict
import re
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("OrderPredictionApp")

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="AI Data Review",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    /* Modern, minimal UI styling */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global styles */
html, body, [class*="st-"] {
    font-family: 'Inter', sans-serif;
    color: #DCDCDC;
}

.stApp {
    background-color: white;
}

/* Main container */
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
    max-width: 100%;
}

/* Headers */
h1, h2, h3, h4, h5, h6 {
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 0.5rem;
}

h1 {
    font-size: 2rem;
    margin-bottom: 1.5rem;
}

h2 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
}

h3 {
    font-size: 1.2rem;
    margin-bottom: 0.75rem;
}

/* Sidebar styles */
section[data-testid="stSidebar"] {
    background-color: #f8fafc;
}

/* Search input styling */
.stTextInput>div>div>input {
    border-radius: 4px;
    border: 1px solid #e2e8f0;
    padding: 0.5rem 1rem;
    font-size: 1rem;
    background-color: white !important;
    color: #333 !important;
}

/* Search container */
.search-container {
    max-width: 300px;
    margin: 1rem 0 1.5rem auto;
}

/* Table styling */
.table-container {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 1.5rem;
}

.table-header {
    background-color: #f8fafc;
    padding: 0.75rem 1rem;
    font-weight: 600;
    border-bottom: 1px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.table-row {
    padding: 0.75rem 0;
    border-bottom: 1px solid #f1f5f9;
    transition: background-color 0.2s ease;
}

.table-row:hover {
    background-color: #f8fafc;
}

.table-row:last-child {
    border-bottom: none;
}

/* Table cell styling for better display */
.table-row p {
    padding: 0.75rem 1rem;
    margin: 0;
    border-right: 1px solid #e2e8f0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Column sizing and layout */
.st-ci {
    overflow: hidden;
    border-right: 1px solid #e2e8f0;
}

/* Dataframe styling for proper data display */
.stDataFrame {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* Prediction section */
.prediction-card {
    background-color: #fff;
    border-radius: 8px;
    margin-top: 1rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.prediction-header {
    font-size: 1.2rem;
    font-weight: 600;
    color: #1a1a1a;
    padding: 0.75rem 1.25rem;
    background-color: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
}

.prediction-content {
    padding: 1.25rem;
    background-color: #fff;
}

.prediction-content p {
    margin-bottom: 0.75rem;
    color: #1a1a1a;
    font-size: 1rem;
    line-height: 1.5;
}

.prediction-content p:last-child {
    margin-bottom: 0;
}

/* Status indicator */
.status {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.85rem;
    display: inline-block;
    font-weight: 500;
    background-color: #e6f7ed;
    color: #0a7b3e;
}

/* Transitions and animations */
.stButton>button, .stTextInput>div>div>input, .stSelectbox>div>div {
    transition: all 0.2s ease;
}

.stButton>button:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Dropdown styling */
.stSelectbox>div>div {
    border-radius: 4px;
    border: 1px solid #e2e8f0;
    background-color: white !important;
}

.stSelectbox select {
    background-color: white !important;
}

/* Fix for dropdown background */
div[data-baseweb="select"] {
    background-color: white !important;
}

div[data-baseweb="select"] * {
    background-color: white !important;
}

/* Update select box text color to ensure visibility */
div[data-baseweb="select"] span {
    color: #333 !important;
}

/* Fix for dropdown menu items */
div[data-baseweb="popover"] * {
    background-color: white !important;
    color: #333 !important;
}

/* Fix for dropdown list items */
div[data-baseweb="menu"] {
    background-color: white !important;
}

div[data-baseweb="menu"] div[role="option"] {
    background-color: white !important;
    color: #333 !important;
}

/* Fix hover state on dropdown options */
div[data-baseweb="menu"] div[role="option"]:hover {
    background-color: #f1f5f9 !important;
}

/* Ensure dropdown selected value is visible */
div[data-testid="stSelectbox"] div[data-baseweb="select"] div {
    color: #333 !important;
}

/* Card styling */
.card {
    background-color: white;
    border-radius: 8px;
    padding: 1.25rem;
    border: 1px solid #e2e8f0;
    margin-bottom: 1rem;
    transition: box-shadow 0.2s ease;
}

.card:hover {
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

/* Fixed button styling */
.stButton > button {
    background-color: #4263eb !important;
    color: white !important;
}

/* Select button styling */
.table-row .stButton > button, td .stButton > button {
    background-color: #f8fafc !important;
    color: #1a1a1a !important;
    border: 1px solid #e2e8f0 !important;
}

.table-row .stButton > button:hover, td .stButton > button:hover {
    background-color: #f1f5f9 !important;
}

.stSelectbox p, .stSelectbox > div > div > div {
    color: #333 !important;
}

/* Primary buttons styling */
button[kind="primary"] {
    background-color: #4263eb !important;
    color: white !important;
}

/* Secondary buttons styling */
.stButton > button[kind="secondary"], .stButton > button[data-testid="baseButton-secondary"] {
    background-color: #f8fafc !important;
    color: #1a1a1a !important;
    border: 1px solid #e2e8f0 !important;
}

/* Ensure all text elements have proper contrast */
p, h1, h2, h3, h4, h5, h6, span, div.row-widget.stButton, label {
    color: #333 !important;
}

/* Table cell content color */
.table-row p {
    color: #333 !important;
    margin: 0;
}

/* Input placeholder color */
.stTextInput > div > div > input::placeholder {
    color: #a0aec0 !important;
}

/* Additional table scrolling behavior */
.st-cy {
    overflow-x: auto !important; 
}

/* Button override to fix streamlit default styling */
div.stButton button {
    background-color: #f8fafc !important;
    color: #1a1a1a !important;
    border: 1px solid #e2e8f0 !important;
}

/* Primary buttons only */
div.stButton button[kind="primary"] {
    background-color: #4263eb !important;
    color: white !important;
}
    </style>
""", unsafe_allow_html=True)

def parse_connection_string(conn_str):
    """Parse SQL Server connection string into components"""
    try:
        # Extract server and database using regex
        server_match = re.search(r'data source=([^;]+)', conn_str, re.IGNORECASE)
        database_match = re.search(r'initial catalog=([^;]+)', conn_str, re.IGNORECASE)
        user_match = re.search(r'User ID=([^;]+)', conn_str, re.IGNORECASE)
        password_match = re.search(r'Password=([^;]+)', conn_str, re.IGNORECASE)
        
        return {
            'server': server_match.group(1) if server_match else None,
            'database': database_match.group(1) if database_match else None,
            'username': user_match.group(1) if user_match else None,
            'password': password_match.group(1) if password_match else None
        }
    except Exception as e:
        st.error(f"Error parsing connection string: {str(e)}")
        return None

def load_company_config():
    """Load and parse the company configuration XML file"""
    try:
        with open('dataaccessconfig.xml', 'r') as file:
            config = xmltodict.parse(file.read())
            companies = []
            
            for company in config['Config']['Company']:
                conn_str = company.get('ConnectionString', '')
                conn_data = parse_connection_string(conn_str)
                
                if conn_data:
                    companies.append({
                        'name': company['Name'],
                        'server': conn_data['server'],
                        'database': conn_data['database'],
                        'username': conn_data['username'],
                        'password': conn_data['password']
                    })
            
            return companies
    except Exception as e:
        st.error(f"Error loading company configuration: {str(e)}")
        return []

def test_connection(server, database, username, password):
    """Test connection to a SQL Server"""
    try:
        conn_str = f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
        conn = pyodbc.connect(conn_str, timeout=3)  # 3 second timeout
        conn.close()
        return True
    except Exception as e:
        return False

def get_server_status(company):
    """Get server status with HTML formatting"""
    is_online = test_connection(
        company['server'],
        company['database'],
        company['username'],
        company['password']
    )
    status_class = "online" if is_online else "offline"
    status_text = "Online" if is_online else "Offline"
    return f'<div class="server-status {status_class}">{status_text}</div>'

def get_databases(company):
    """Get list of databases for the selected company"""
    try:
        conn_str = f"DRIVER={{SQL Server}};SERVER={company['server']};UID={company['username']};PWD={company['password']}"
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Get user databases (exclude system databases)
        cursor.execute("""
            SELECT name 
            FROM sys.databases 
            WHERE database_id > 4 
                AND state = 0  -- Online databases only
                AND is_read_only = 0  -- Exclude read-only databases
            ORDER BY name
        """)
        
        databases = [row[0] for row in cursor.fetchall()]
        conn.close()
        return databases
    except Exception as e:
        st.error(f"Error fetching databases from {company['server']}: {str(e)}")
        return []

def main():
    # Header
    st.markdown("<h1>AI Data Review</h1>", unsafe_allow_html=True)
    
    # Debug mode toggle
    debug_mode = st.sidebar.checkbox("Debug Mode", value=False)
    if debug_mode:
        st.sidebar.info("Debug mode is enabled. Check the logs for detailed information.")
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    
    # Sidebar for configuration
    with st.sidebar:
        st.markdown("<h1>AI Data Review</h1>", unsafe_allow_html=True)
        
        # Server selection
        st.markdown("<h3>Server</h3>", unsafe_allow_html=True)
        
        # Load company configuration
        companies = load_company_config()
        
        if not companies:
            st.error("No server configurations found. Please check the dataaccessconfig.xml file.")
            st.info("You can create a dataaccessconfig.xml file based on the dataaccessconfig.xml.example template.")
            return
        
        # Server selection dropdown
        company_names = [company['name'] for company in companies]
        company_names.sort()  # Sort company names alphabetically
        selected_company_name = st.selectbox(
            "",
            options=company_names,
            help="Select a server to connect to"
        )
        
        # Get selected company details
        selected_company = next((c for c in companies if c['name'] == selected_company_name), None)
        
        if selected_company:
            # Database selection
            st.markdown("<h3>Database</h3>", unsafe_allow_html=True)
            databases = get_databases(selected_company)
            
            if databases:
                selected_database = st.selectbox(
                    "",
                    options=databases,
                    help="Select a database to analyze"
                )
                
                # Load data button
                if selected_database:
                    if st.button("Load Data", type="primary"):
                        try:
                            with st.spinner("Loading data..."):
                                # Set environment variables for the selected company
                                os.environ['SQL_SERVER'] = selected_company['server']
                                os.environ['SQL_DATABASE'] = selected_database
                                os.environ['SQL_USERNAME'] = selected_company['username']
                                os.environ['SQL_PASSWORD'] = selected_company['password']
                                
                                # Load data
                                df = load_data(
                                    selected_company['server'],
                                    selected_database,
                                    selected_company['username'],
                                    selected_company['password']
                                )
                                
                                if df is not None and not df.empty:
                                    # Store the dataframe in session state
                                    st.session_state['data'] = df
                                    st.success(f"Successfully loaded {len(df)} records!")
                                else:
                                    st.error("No data available. Check the logs for details.")
                        except Exception as e:
                            logger.error(f"Error loading data: {e}")
                            st.error(f"Error loading data: {str(e)}")
            else:
                st.warning("No databases found on the selected server.")

    # Main content area - search box
    st.markdown("<div class='search-container'>", unsafe_allow_html=True)
    search_term = st.text_input("", placeholder="Search orders", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Main content area - record selection and prediction
    if 'data' in st.session_state:
        df = st.session_state['data']
        
        # Initialize selected_record if not already in session state
        if 'selected_record' not in st.session_state:
            st.session_state['selected_record'] = None
        
        # Filter data based on search term
        if search_term:
            # Search across all string columns
            mask = pd.Series(False, index=df.index)
            searchable_columns = df.columns  # Search across all columns
            for col in searchable_columns:
                if col in df.columns:
                    mask = mask | df[col].astype(str).str.contains(search_term, case=False, na=False)
            filtered_df = df[mask]
        else:
            filtered_df = df
        
        # Wrap main table in an expander, hidden by default
        with st.expander("View All Order Data", expanded=False):
            # Table header setup with scrollability
            st.markdown("<div class='table-container' style='overflow-x: auto; max-height: 500px;'>", unsafe_allow_html=True)
            
            # Get all columns from data for display
            display_columns = df.columns.tolist()
            
            # Reintroduce pagination
            page_size = 10
            total_pages = len(filtered_df) // page_size + (1 if len(filtered_df) % page_size > 0 else 0)
            
            if 'current_page' not in st.session_state:
                st.session_state['current_page'] = 0
                
            # Calculate start and end indices
            start_idx = st.session_state['current_page'] * page_size
            end_idx = min(start_idx + page_size, len(filtered_df))
            
            # Get the current page of data
            page_df = filtered_df.iloc[start_idx:end_idx].copy()
            
            # Add a "Select" column to indicate clickable row
            page_df = page_df.reset_index(drop=True)
            
            # Create a clean table for display
            st.markdown("<h3>Order Data</h3>", unsafe_allow_html=True)
            
            # Display the table using Streamlit's native dataframe display
            st.dataframe(page_df, use_container_width=True, hide_index=True)
            
            # Pagination controls below the table
            if total_pages > 1:
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    if st.session_state['current_page'] > 0:
                        if st.button("← Previous"):
                            st.session_state['current_page'] -= 1
                            st.experimental_rerun()
                with col3:
                    if st.session_state['current_page'] < total_pages - 1:
                        if st.button("Next →"):
                            st.session_state['current_page'] += 1
                            st.experimental_rerun()
                with col2:
                    st.write(f"Page {st.session_state['current_page'] + 1} of {total_pages}")
            
            # End table container
            st.markdown("</div>", unsafe_allow_html=True)

        # Create Actions section below expander
        st.markdown("<h4>Recent Orders for Action</h4>", unsafe_allow_html=True)
        
        # Get the 10 most recent records from the full dataset
        recent_records = df.tail(10).copy() if not df.empty else pd.DataFrame()
        
        # Prepare a simplified view for the action table
        if not recent_records.empty:
            # Identify trend columns dynamically
            trend_columns = [col for col in df.columns if 'TREND' in col]
            
            # Select columns to display in the dataframe
            display_cols = ['ORDERNUMBER', 'INGRD_GRP_NM', 'ORDERSTRENGTH', 'CUMULSTRENGTH'] + trend_columns
            action_df = recent_records[display_cols].copy()
            
            # Rename columns for better display if needed (optional)
            action_df.columns = ['Order #', 'Ingredient Group', 'Order Str', 'Cumul. Str'] + trend_columns

            # Display the recent records using st.dataframe for a clean look
            st.dataframe(
                action_df,
                use_container_width=True,
                hide_index=True,
                # Optional: configure column widths/types if needed
                # column_config={ ... }
            )

            # --- Selection Dropdown Below Dataframe --- 
            st.markdown("**Select an Order to Predict:** <small>_(Tip: Copy Order # from table above)_</small>", unsafe_allow_html=True)
            
            # Get order numbers from the recent records for the dropdown
            order_numbers = recent_records['ORDERNUMBER'].tolist()
            # Add a placeholder option
            options = ["Select..."] + order_numbers 
            
            # Create the selectbox
            selected_order_num = st.selectbox(
                "Select Order Number", 
                options=options,
                key="action_order_select",
                label_visibility="collapsed" # Hide label as we have markdown above
            )
            
            # If a valid order number is selected, find the record and update state
            if selected_order_num != "Select...":
                # Find the original index in the main df corresponding to the selected number
                # Note: Assumes ORDERNUMBER is unique within the recent_records
                selected_idx = recent_records[recent_records['ORDERNUMBER'] == selected_order_num].index[0]
                # Check if selection actually changed to avoid unnecessary reruns
                current_selection_idx = st.session_state.get('selected_record_idx', None)
                if selected_idx != current_selection_idx:
                    st.session_state['selected_record'] = df.loc[selected_idx] 
                    st.session_state['selected_record_idx'] = selected_idx # Store index too
                    st.experimental_rerun()
            # If 'Select...' is chosen and a record was previously selected, clear it (optional)
            elif st.session_state.get('selected_record') is not None:
                 if st.session_state.get('selected_record_idx') in recent_records.index:
                     # Only clear if the previously selected record was from this action list
                     # This prevents clearing if a selection was made elsewhere (e.g. via search)
                     pass # Decided not to auto-clear for now, user can trigger prediction explicitly

        # Generate prediction if a record is selected
        if st.session_state.get('selected_record') is not None:
            selected_record = st.session_state['selected_record']
            
            # Show selected record details
            st.markdown("<h3>Selected Record</h3>", unsafe_allow_html=True)
            st.write(f"Order Number: {selected_record['ORDERNUMBER']}")
            st.write(f"Comment: {selected_record['ORDER_JRNL_CMT_TXT']}")
            
            # Generate prediction button
            if st.button("Generate AI Comment Prediction", type="primary"):
                with st.spinner("Generating prediction..."):
                    # Generate prediction for the selected record
                    prediction = generate_prediction_for_record(selected_record, df)
                    st.session_state['prediction'] = prediction
                    st.experimental_rerun()
        
        # Add the prediction section if we have a prediction
        if 'prediction' in st.session_state:
            prediction = st.session_state['prediction']
            
            # Create a clean card layout using Streamlit's native components
            st.subheader("Predicted Comment")
            
            # Add the prediction in a styled text area
            st.info(prediction['predicted_comment'])
            
            # Add the reasoning in an expandable section
            with st.expander("View Reasoning", expanded=True):
                st.write(prediction['reason'])
    else:
        # Welcome message when no data has been loaded
        st.markdown("""
            <div class="card">
                <h3>Welcome to AI Data Review</h3>
                <p>Select a server and database from the sidebar, then click "Load Data" to get started.</p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 