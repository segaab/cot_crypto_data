import streamlit as st
from streamlit_shadcn_ui import card, tabs, switch, metric_card, alert_dialog, input
from dotenv import load_dotenv
import os
from pathlib import Path
import json
import pandas as pd
import time
import altair as alt

# Get the absolute path to the root directory
ROOT_DIR = Path(__file__).parent.absolute()

# Load environment variables from the root .env file
load_dotenv(ROOT_DIR / '.env')

# Load mock data
def load_mock_data():
    data_path = ROOT_DIR / 'data' / 'mock_algo_upload.json'
    with open(data_path, 'r') as f:
        return json.load(f)

# Configure page settings first
st.set_page_config(
    page_title="COT Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply clean monochromatic theme
st.markdown("""
<style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Base theme */
    :root {
        --background: 0 0% 0%;
        --foreground: 0 0% 98%;
        --card: 0 0% 3%;
        --muted: 0 0% 7%;
        --border: 0 0% 14.9%;
    }

    /* Clean background */
    .stApp {
        background-color: hsl(var(--background));
        color: hsl(var(--foreground));
    }
    
    /* Remove default container styling */
    .element-container {
        background: transparent !important;
    }
    
    /* Clean metric cards */
    [data-testid="stMetricValue"] {
        color: hsl(var(--foreground));
        background: transparent !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: hsl(var(--muted-foreground));
    }
    
    /* Remove multiple borders */
    [data-testid="stVerticalBlock"] > div {
        background-color: transparent !important;
        border: none !important;
        padding: 0.5rem !important;
    }
    
    /* Clean selectbox */
    .stSelectbox > div > div {
        background-color: hsl(var(--card));
        border: 1px solid hsl(var(--border));
    }
    
    /* Clean table */
    .dataframe {
        background: hsl(var(--card));
        border: none !important;
    }
    
    /* Clean chart */
    .stChart > div > div > div {
        background-color: transparent !important;
    }
    
    /* Remove markdown container styling */
    .stMarkdown {
        background: transparent !important;
    }
    
    .element-container div {
        background: transparent !important;
    }
    
    /* Clean tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: hsl(var(--card));
        border: none;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: hsl(var(--muted));
    }
    
    /* Remove any remaining container borders */
    div[data-testid*="stVerticalBlock"] div[data-testid*="stVerticalBlock"] {
        border: none !important;
        background: transparent !important;
    }
    
    /* Remove space above title */
    .stApp > header {
        display: none;
    }
    
    .main-title {
        margin-top: -4rem;  /* Negative margin to remove space */
        padding-bottom: 1rem;
    }
    
    /* Custom toggle container */
    .toggle-container {
        background-color: #000000;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    
    /* Larger toggle and label */
    .toggle-container label {
        font-size: 1.2rem !important;
        color: #FFFFFF !important;
    }
    
    /* Make toggle bigger */
    [data-testid="stSwitch"] {
        transform: scale(1.2);
        margin: 0.5rem 0;
    }
    
    /* Active Trader card styling */
    [data-testid="stVerticalBlock"] > div:has([data-testid="metric-container"]) {
        background-color: #000000 !important;
        border: none !important;
        padding: 1rem !important;
    }
    
    /* Metric text colors */
    [data-testid="metric-container"] {
        color: #FFFFFF !important;
    }
    
    [data-testid="metric-container"] label {
        color: #FFFFFF !important;
    }
    
    /* Style for the inner selector */
    div[data-testid="stSelectbox"] {
        margin-bottom: 1rem;
    }
    
    .footer {
        position: relative;
        padding: 2rem 0;
        margin-top: 2rem;
        background: #1e1e1e;
        text-align: center;
    }
    
    .coffee-message {
        color: white;
        font-size: 1.2em;
        margin: 1em 0;
    }
    
    .kofi-button {
        display: inline-block;
        padding: 10px 20px;
        background-color: #000000;
        color: white;
        text-decoration: none;
        border-radius: 4px;
        border: 1px solid #333;
        transition: all 0.3s ease;
    }
    
    .kofi-button:hover {
        background-color: #333;
    }
    
    .coffee-container {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1.5rem;
        padding: 2rem;
    }
    
    /* Style for close button */
    [data-testid="stButton"] button {
        background: transparent;
        color: #FFFFFF;
        border: none;
        font-size: 1.2em;
        cursor: pointer;
        padding: 0.5em;
        transition: all 0.3s ease;
    }
    
    [data-testid="stButton"] button:hover {
        color: #ff4b4b;
        transform: scale(1.1);
    }
    
    /* Professional Header Styles */
    h1 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Slogan Style */
    .slogan {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 400;
        opacity: 0.8;
    }
    
    /* Support Button Container */
    .support-buttons {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .support-buttons:hover {
        background: rgba(255, 255, 255, 0.05);
    }
    
    /* Separator Style */
    hr {
        opacity: 0.1;
    }
</style>
""", unsafe_allow_html=True)

def format_positions_data(market_data):
    """Format market data for display in table"""
    latest = market_data['latest_report']
    
    return {
        'Commercial': {
            'Long': int(latest['comm_positions_long_all']),
            'Short': int(latest['comm_positions_short_all']),
            'Net': int(latest['comm_positions_long_all']) - int(latest['comm_positions_short_all'])
        },
        'Non-Commercial': {
            'Long': int(latest['noncomm_positions_long_all']),
            'Short': int(latest['noncomm_positions_short_all']),
            'Net': int(latest['noncomm_positions_long_all']) - int(latest['noncomm_positions_short_all'])
        },
        'Retail': {
            'Long': int(latest['nonrept_positions_long_all']),
            'Short': int(latest['nonrept_positions_short_all']),
            'Net': int(latest['nonrept_positions_long_all']) - int(latest['nonrept_positions_short_all'])
        }
    }

def prepare_chart_data(positions, normalize=False):
    """Prepare data for Vega-Lite chart"""
    data = []
    for trader_type in positions:
        data.append({
            'Trader': trader_type,
            'Position': 'Long',
            'Value': float(positions[trader_type]['Long'])
        })
        data.append({
            'Trader': trader_type,
            'Position': 'Short',
            'Value': float(positions[trader_type]['Short'])
        })
    
    return pd.DataFrame(data)

def calculate_key_metrics(market_data):
    """Calculate key metrics from market data"""
    latest = market_data['latest_report']
    
    # Calculate net positions for each trader type
    net_positions = {
        'Commercial': float(latest['comm_positions_long_all']) - float(latest['comm_positions_short_all']),
        'Non-Commercial': float(latest['noncomm_positions_long_all']) - float(latest['noncomm_positions_short_all']),
        'Retail': float(latest['nonrept_positions_long_all']) - float(latest['nonrept_positions_short_all'])
    }
    
    # Find dominant trader (trader with largest absolute net position)
    dominant_trader = max(net_positions.items(), key=lambda x: abs(x[1]))
    
    # Format net position with + sign for positive values
    net_position = dominant_trader[1]
    formatted_net = f"+{net_position:,.2f}" if net_position > 0 else f"{net_position:,.2f}"
    
    return {
        'dominant_trader': f"{dominant_trader[0]} ({formatted_net})"
    }

def main():
    # Create centered layout directly
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        # Header Section with Logo and Branding
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='color: white; font-size: 2.5em; margin-bottom: 0.5rem;'>CoT Analytics</h1>
            <p style='color: #666; font-size: 1.2em; margin-bottom: 2rem;'>Professional-Grade Market Positioning Analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add separator
        st.markdown("<hr style='margin: 2rem 0; border: none; border-top: 1px solid #333;'>", unsafe_allow_html=True)
        
        # Existing data loading code and main functionality
        try:
            data = load_mock_data()
            if not isinstance(data, list):
                st.error("Invalid data format. Expected a list of market data.")
                return
                
            # Extract display names for market selection
            market_options = [m.get('display_name') for m in data if isinstance(m, dict) and 'display_name' in m]
            if not market_options:
                st.error("No valid market options found in data.")
                return
                
            # Main market selector
            selected_market = st.selectbox(
                "Select Market",
                options=market_options,
                key="selected_market"
            )
            
            # Remove scroll behavior tracking since we don't have navigation
            if 'prev_market' not in st.session_state:
                st.session_state.prev_market = selected_market
            
            # Get selected market data and calculate metrics
            selected_market_data = next(
                (m for m in data if m['display_name'] == selected_market),
                data[0]
            )
            positions = format_positions_data(selected_market_data)
            metrics = calculate_key_metrics(selected_market_data)
            
            # Main metric with Humble View toggle
            col1, col2 = st.columns([6, 1])
            with col1:
                metric_card(
                    title="Active Trader",
                    content=metrics['dominant_trader'],
                    description=""
                )
            with col2:
                absolute_view = switch(
                    label="Humble View",
                    default_checked=False,
                    key="view_mode_toggle"
                )
                
                # Add scroll behavior for toggle
                if 'prev_view_state' not in st.session_state:
                    st.session_state.prev_view_state = absolute_view
                elif st.session_state.prev_view_state != absolute_view:
                    st.markdown(
                        """
                        <script>
                            setTimeout(() => {
                                const element = document.getElementById('market');
                                if (element) {
                                    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                                }
                            }, 100);
                        </script>
                        """,
                        unsafe_allow_html=True
                    )
                    st.session_state.prev_view_state = absolute_view
            
            # Table below Active Trader
            df = pd.DataFrame(positions).transpose()
            
            # Normalize the data if not in absolute view
            if not absolute_view:
                for col in ['Long', 'Short', 'Net']:
                    total = df[col].abs().sum()
                    df[col] = df[col] / total * 100
            
            # Format the display
            st.dataframe(
                df.style.format(
                    {
                        'Long': '{:.1f}%' if not absolute_view else '{:,.0f}',
                        'Short': '{:.1f}%' if not absolute_view else '{:,.0f}',
                        'Net': '{:.1f}%' if not absolute_view else '{:,.0f}'
                    }
                ).background_gradient(
                    subset=['Net'], 
                    cmap='gist_yarg',  # 'gist_yarg' is 'gray' reversed
                    vmin=df['Net'].min(),
                    vmax=df['Net'].max()
                ),
                use_container_width=True
            )
            
            # Chart configuration and display
            chart_data = prepare_chart_data(positions)
            colors = ['#FFFFFF', '#666666']
            
            # Create the base chart specification
            base = {
                "mark": "bar",
                "encoding": {
                    "x": {
                        "field": "Trader",
                        "type": "nominal",
                        "title": None,
                        "axis": {
                            "labelColor": "#FFFFFF",
                            "titleColor": "#FFFFFF",
                            "domainColor": "#333333",
                            "tickColor": "#333333"
                        }
                    },
                    "color": {
                        "field": "Position",
                        "type": "nominal",
                        "scale": {"range": colors},
                        "legend": {
                            "orient": "top",
                            "title": None,
                            "labelColor": "#FFFFFF"
                        },
                        "sort": ["Long", "Short"]  # Changed order to make Long appear at bottom
                    },
                    "order": {"field": "Position", "sort": "ascending"},  # Changed to ascending
                    "tooltip": [
                        {"field": "Trader", "type": "nominal", "title": "Trader Type"},
                        {"field": "Position", "type": "nominal"},
                        {"field": "Value", "type": "quantitative", 
                         "format": ".0f" if absolute_view else ".1%"}
                    ]
                },
                "config": {
                    "view": {"stroke": "transparent"},
                    "axis": {
                        "grid": "true",
                        "gridColor": "#333333",
                        "gridOpacity": 0.3
                    },
                    "background": "transparent"
                }
            }
            
            if not absolute_view:  # Normalized view
                base["encoding"]["y"] = {
                    "field": "Value",
                    "type": "quantitative",
                    "stack": "normalize",
                    "axis": {
                        "format": ".0%",
                        "title": "Percentage",
                        "labelColor": "#FFFFFF",
                        "titleColor": "#FFFFFF"
                    },
                    "scale": {"domain": [0, 1]}
                }
            else:  # Absolute view
                base["encoding"]["y"] = {
                    "field": "Value",
                    "type": "quantitative",
                    "title": "Contracts",
                    "axis": {
                        "grid": "true",
                        "gridColor": "#333333",
                        "labelColor": "#FFFFFF",
                        "titleColor": "#FFFFFF"
                    }
                }
            
            # Create and configure the chart
            chart = st.vega_lite_chart(
                chart_data,
                base,
                theme=None,
                use_container_width=True
            )
            
            # Update caption styling
            st.markdown(
                f"<div style='color: #FFFFFF; font-size: 0.8em; text-align: center;'>"
                f"{'Absolute view (contracts)' if absolute_view else 'Normalized view (0-100%)'}"
                "</div>",
                unsafe_allow_html=True
            )
            
            # Bottom section with feature requests and support
            st.markdown("<hr style='margin: 2rem 0; border: none; border-top: 1px solid #333;'>", unsafe_allow_html=True)
            
            # Promise text instead of Feature Requests header
            st.markdown("""
            <div style='text-align: center; margin-bottom: 1.5rem;'>
                <p style='color: #4CAF50; font-size: 1.2em;'>I will build and deploy your ideas in 2 days.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Input fields
            col1, col2 = st.columns(2)
            with col1:
                feature_request = st.text_input("Suggest a Feature", key="feature_request")
            with col2:
                contact_email = st.text_input("Your Email (optional)", key="contact_email")
            
            # Support section at the bottom
            st.markdown(
                """
                <div style='display: flex; flex-direction: column; align-items: center; gap: 1rem; margin: 2rem 0;'>
                    <a href='https://ko-fi.com/X7X47Q0EG' target='_blank'>
                        <img height='36' style='border:0px;height:36px;' 
                        src='https://storage.ko-fi.com/cdn/kofi2.png?v=3' 
                        border='0' alt='Buy Me a Coffee at ko-fi.com' />
                    </a>
                    <p style='color: #666; font-size: 0.9em; text-align: center; margin-top: 0.5rem;'>
                        All contributions go directly to my public projects.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        except Exception as e:
            st.error(f"Error loading data: {e}")
            return
    
    # Force initial scroll to market section
    if 'initial_load' not in st.session_state:
        st.session_state.initial_load = True
        st.markdown(
            """
            <script>
                window.location.hash = '#market';
            </script>
            """,
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main() 