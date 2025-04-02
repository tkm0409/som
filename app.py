import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from order_prediction_sql import get_db_connection, load_data, prepare_prompt, get_prediction, update_database
import os
from dotenv import load_dotenv
import pyodbc
from datetime import datetime

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Order Prediction System",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        margin-top: 10px;
    }
    .main {
        padding: 2rem;
    }
    .server-status {
        padding: 5px 10px;
        border-radius: 4px;
        margin: 2px 0;
        font-size: 0.9em;
    }
    .server-status.online {
        background-color: #c2f5c2;
        color: #1a571a;
    }
    .server-status.offline {
        background-color: #ffc2c2;
        color: #5c1a1a;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def discover_servers():
    """Discover SQL Servers on the network"""
    try:
        # Get the primary server from environment variable
        primary_server = os.getenv('SQL_SERVER')
        servers = [primary_server] if primary_server else []
        
        # Try to discover other servers using SQL Browser service
        try:
            # Connect to the primary server to get linked servers
            conn = pyodbc.connect(f"DRIVER={{SQL Server}};SERVER={primary_server};Trusted_Connection=yes;")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    server_id,
                    name,
                    data_source
                FROM 
                    sys.servers 
                WHERE 
                    is_linked = 1
                    AND is_data_access_enabled = 1
            """)
            linked_servers = [row.data_source for row in cursor.fetchall()]
            servers.extend(linked_servers)
            
            # Remove duplicates while preserving order
            servers = list(dict.fromkeys(servers))
            
        except Exception as e:
            st.warning(f"Could not discover linked servers: {str(e)}")
        
        return servers
    except Exception as e:
        st.error(f"Error discovering servers: {str(e)}")
        return []

def test_server_connection(server):
    """Test connection to a server"""
    try:
        conn_str = f"DRIVER={{SQL Server}};SERVER={server};Trusted_Connection=yes;"
        conn = pyodbc.connect(conn_str, timeout=3)  # 3 second timeout
        conn.close()
        return True
    except:
        return False

def get_server_status(server):
    """Get server status with HTML formatting"""
    is_online = test_server_connection(server)
    status_class = "online" if is_online else "offline"
    status_text = "Online" if is_online else "Offline"
    return f'<div class="server-status {status_class}">{status_text}</div>'

def get_databases(server):
    """Get list of databases for the selected server"""
    try:
        # Create a connection string for the specific server
        conn_str = f"DRIVER={{SQL Server}};SERVER={server};UID={os.getenv('SQL_USERNAME')};PWD={os.getenv('SQL_PASSWORD')}"
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
        st.error(f"Error fetching databases from {server}: {str(e)}")
        return []

def get_tables(server, database):
    """Get list of tables for the selected database"""
    try:
        # Create a connection string for the specific server and database
        conn_str = f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={os.getenv('SQL_USERNAME')};PWD={os.getenv('SQL_PASSWORD')}"
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Get user tables with additional information
        cursor.execute("""
            SELECT 
                t.TABLE_SCHEMA + '.' + t.TABLE_NAME as full_name,
                (
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = t.TABLE_SCHEMA 
                    AND TABLE_NAME = t.TABLE_NAME
                ) as column_count,
                ISNULL(
                    (
                        SELECT SUM(p.rows) 
                        FROM sys.partitions p 
                        JOIN sys.tables tab ON p.object_id = tab.object_id
                        WHERE tab.name = t.TABLE_NAME
                    ), 0
                ) as row_count
            FROM 
                INFORMATION_SCHEMA.TABLES t
            WHERE 
                t.TABLE_TYPE = 'BASE TABLE'
            ORDER BY 
                t.TABLE_SCHEMA, t.TABLE_NAME
        """)
        
        # Format the results
        tables = []
        for row in cursor.fetchall():
            tables.append(f"{row.full_name} ({row.column_count} columns, {row.row_count:,} rows)")
        
        conn.close()
        return tables
    except Exception as e:
        st.error(f"Error fetching tables from {server}.{database}: {str(e)}")
        return []

def main():
    st.title("📊 Order Prediction System")
    st.markdown("---")

    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Server selection with status
        st.subheader("1. Select Server")
        servers = discover_servers()
        
        if not servers:
            st.error("No SQL Servers found. Please check your configuration.")
            return
            
        # Show servers with their status
        server_options = []
        for server in servers:
            status_html = get_server_status(server)
            st.markdown(f"**{server}** {status_html}", unsafe_allow_html=True)
            if test_server_connection(server):
                server_options.append(server)
        
        selected_server = st.selectbox(
            "Available Servers",
            options=server_options,
            help="Select a SQL Server to connect to"
        )
        
        # Database selection
        st.subheader("2. Select Database")
        if selected_server:
            databases = get_databases(selected_server)
            if databases:
                selected_database = st.selectbox(
                    "Available Databases",
                    options=databases,
                    help="Select a database to analyze"
                )
                
                # Table selection
                if selected_database:
                    st.subheader("3. Select Table")
                    tables = get_tables(selected_server, selected_database)
                    if tables:
                        selected_table = st.selectbox(
                            "Available Tables",
                            options=tables,
                            help="Select a table to analyze"
                        )
                        
                        # Extract the actual table name from the formatted string
                        if selected_table:
                            actual_table = selected_table.split(" (")[0]
                            
                            # Generate predictions button
                            if st.button("Generate Predictions", type="primary"):
                                try:
                                    with st.spinner("Generating predictions..."):
                                        # Load data
                                        df = load_data()
                                        if df is not None:
                                            # Get prediction
                                            prompt = prepare_prompt(df)
                                            prediction = get_prediction(prompt)
                                            
                                            # Update database
                                            if update_database(prediction):
                                                st.success("Predictions generated and database updated successfully!")
                                            else:
                                                st.warning("Predictions generated but failed to update database.")
                                        else:
                                            st.error("Failed to load data from the database.")
                                except Exception as e:
                                    st.error(f"Error generating predictions: {str(e)}")
                    else:
                        st.warning("No tables found in the selected database.")
            else:
                st.warning("No databases found on the selected server.")
        
        # Refresh button
        if st.button("🔄 Refresh Server List"):
            st.cache_data.clear()
            st.experimental_rerun()

    # Main content area
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Trend Analysis")
        if os.path.exists("trend_analysis.png"):
            st.image("trend_analysis.png", use_column_width=True)
        else:
            st.info("Generate predictions to view trend analysis")

    with col2:
        st.header("Latest Predictions")
        latest_result_file = max(
            [f for f in os.listdir() if f.startswith("prediction_results_")],
            key=os.path.getctime,
            default=None
        )
        if latest_result_file:
            with open(latest_result_file, "r") as f:
                st.text(f.read())
        else:
            st.info("Generate predictions to view results")

    # Download section
    st.markdown("---")
    st.header("Download Results")
    col3, col4 = st.columns(2)
    
    with col3:
        if os.path.exists("trend_analysis.png"):
            with open("trend_analysis.png", "rb") as f:
                st.download_button(
                    "Download Trend Analysis",
                    f,
                    file_name="trend_analysis.png",
                    mime="image/png"
                )
    
    with col4:
        if latest_result_file:
            with open(latest_result_file, "rb") as f:
                st.download_button(
                    "Download Predictions",
                    f,
                    file_name=latest_result_file,
                    mime="text/plain"
                )

if __name__ == "__main__":
    main() 