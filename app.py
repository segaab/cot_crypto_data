import streamlit as st
from streamlit_shadcn_ui import card, tabs, switch, metric_card, alert_dialog, input
from dotenv import load_dotenv
import os
from pathlib import Path
import json
import pandas as pd
import time
import altair as alt
import pathlib

# Setup static file serving
STATIC_DIR = pathlib.Path(__file__).parent / "static"
if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True)

# Copy fonts to static directory if they don't exist
FONTS_DIR = STATIC_DIR / "fonts"
if not FONTS_DIR.exists():
    FONTS_DIR.mkdir(parents=True)
    # Copy font files from source to static/fonts directory
    import shutil
    source_fonts = pathlib.Path(__file__).parent / "fonts"
    for font_file in source_fonts.glob("*.ttf"):
        shutil.copy2(font_file, FONTS_DIR / font_file.name)

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
    /* Base theme and other styles... */
    
    /* Responsive Typography */
    :root {
        --font-size-base: 16px;
        --font-size-scale: 1.2;
        --spacing-unit: 1rem;
    }
    
    /* Update font references to use the configured CustomFont */
    body, input, button, select, textarea {
        font-family: CustomFont, -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Rest of your existing styles... */
    
    /* Ko-fi Widget Styling */
    #kofi-widget-container,
    #kofi-widget-container-sidebar {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 1rem 0;
    }
    
    /* Ko-fi Button Styling */
    .kofi-button {
        background-color: #000000 !important;
        border: 1px solid #333 !important;
        color: #FFFFFF !important;
        padding: 8px 16px !important;
        border-radius: 4px !important;
        transition: all 0.3s ease !important;
    }
    
    .kofi-button:hover {
        background-color: #333333 !important;
        transform: translateY(-2px) !important;
    }
    
    /* Bottom Section Styling */
    .contact-form input,
    .contact-form textarea {
        background-color: #1a1a1a;
        color: white;
        border: 1px solid #333;
        padding: 0.8rem;
        border-radius: 4px;
        font-size: var(--font-size-base);
        width: 100%;
        box-sizing: border-box;
        margin-bottom: 1rem;
    }
    
    .contact-form input:focus,
    .contact-form textarea:focus {
        border-color: #666;
        outline: none;
    }
    
    /* Separator Styling */
    hr {
        margin: 4rem 0;
        border: none;
        border-top: 1px solid #333;
        opacity: 0.5;
    }
    
    /* Bottom Container Spacing */
    .container-sm {
        padding: 2rem 1rem;
    }
    
    @media screen and (max-width: 640px) {
        .container-sm {
            padding: 1rem;
        }
    }
    
    /* Updated Input Styling */
    .input-group {
        margin-bottom: 1.5rem;
        width: 100%;
    }
    
    .input-group input {
        transition: all 0.3s ease;
    }
    
    .input-group input:focus {
        border-color: #666 !important;
        outline: none;
        box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1);
    }
    
    .input-group input::placeholder {
        color: #666;
        opacity: 1;
    }
    
    /* Remove old contact form styles */
    .contact-form {
        width: 100%;
        max-width: 400px;
        margin: 0 auto;
        padding: 0 1rem;
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
        <div id='cot-analytics' class='responsive-padding container-md' style='text-align: center; margin: 0 auto;'>
            <h1 class='text-h1' style='color: white;'>CoT Analytics</h1>
            <p class='text-body' style='color: #666;'>Find Your Edge With Institutional & Commercial Data</p>
        </div>
        """, unsafe_allow_html=True)
        
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
                    cmap='gist_yarg',
                    vmin=df['Net'].min(),
                    vmax=df['Net'].max()
                ),
                use_container_width=True
            )
            
            # Prepare and create chart
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
                        "sort": ["Long", "Short"]
                    },
                    "order": {"field": "Position", "sort": "ascending"},
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
            
            if not absolute_view:
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
            else:
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
            
            # Create chart
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
            
            # Add separator before support section
            st.markdown("<hr style='margin: 4rem 0; border: none; border-top: 1px solid #333;'>", unsafe_allow_html=True)
            
            # Support section at the bottom
            st.markdown(
                """
                <div class='container-sm responsive-padding' style='margin: 0 auto; text-align: center;'>
                    <h2 class='text-h2' style='
                        font-family: CustomFont, sans-serif;
                        font-weight: 800;
                        color: white;
                        margin-bottom: 2rem;
                    '>
                        I'll build and ship your ideas<br>in 2 days
                    </h2>
                    <div style='display: flex; flex-direction: column; align-items: center; gap: var(--spacing-unit);'>
                        <!-- Ko-fi Widget -->
                        <script type='text/javascript' src='https://storage.ko-fi.com/cdn/widget/Widget_2.js'></script>
                        <script type='text/javascript'>
                            kofiwidget2.init('Support me on Ko-fi', '#ffffff', 'Q5Q818G1MT');
                            kofiwidget2.draw();
                        </script>
                        <div id="kofi-widget-container"></div>
                        <p class='text-small' style='
                            font-family: CustomFont, sans-serif;
                            font-weight: 300;
                            color: #666;
                            text-align: center;
                            margin-bottom: 2rem;
                        '>
                            All contributions go directly into our projects.
                        </p>
                        
                        <!-- New Input Fields -->
                        <div class='contact-form' style='width: 100%; max-width: 400px; margin: 0 auto;'>
                            <div class='input-group'>
                                <input type="email" 
                                       placeholder="Enter your email" 
                                       style='
                                           width: 100%;
                                           margin-bottom: 1rem;
                                           background: #1a1a1a;
                                           border: 1px solid #333;
                                           color: white;
                                           padding: 12px;
                                           border-radius: 4px;
                                           font-size: 14px;
                                       '
                                >
                            </div>
                            <div class='input-group'>
                                <input type="text" 
                                       placeholder="What would you like me to build?" 
                                       style='
                                           width: 100%;
                                           background: #1a1a1a;
                                           border: 1px solid #333;
                                           color: white;
                                           padding: 12px;
                                           border-radius: 4px;
                                           font-size: 14px;
                                       '
                                >
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return
    
    # Force initial scroll to cot-analytics section
    if 'initial_load' not in st.session_state:
        st.session_state.initial_load = True
        st.markdown(
            """
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    window.location.hash = 'cot-analytics';
                });
                
                // Fallback for Streamlit's dynamic loading
                setTimeout(function() {
                    window.location.hash = 'cot-analytics';
                }, 1000);
            </script>
            """,
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main() 