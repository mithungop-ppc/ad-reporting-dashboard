import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests
import json

# Page config with Salesforce-inspired styling
st.set_page_config(
    page_title="Ad Reporting Dashboard",
    page_icon="⚡",
    layout="wide"
)

# Salesforce-inspired CSS
st.markdown("""
<style>
    /* Import Salesforce Sans font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background-color: #f3f2f2;
    }
    
    /* Main container */
    .main-container {
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        margin: 1rem 0;
        padding: 1.5rem;
    }
    
    /* Header styling */
    .sf-header {
        background: linear-gradient(135deg, #1589ee 0%, #0176d3 100%);
        color: white;
        padding: 2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 8px rgba(21, 137, 238, 0.2);
    }
    
    .sf-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.025em;
    }
    
    .sf-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 400;
    }
    
    /* Card styling */
    .sf-card {
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    
    .sf-card-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e5e5e5;
    }
    
    .sf-card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #181818;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Button styling */
    .sf-button {
        background: #0176d3;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .sf-button:hover {
        background: #014486;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(1, 118, 211, 0.3);
    }
    
    .sf-button-secondary {
        background: white;
        color: #0176d3;
        border: 1px solid #0176d3;
    }
    
    .sf-button-secondary:hover {
        background: #f3f3f3;
        transform: translateY(-1px);
    }
    
    .sf-button-destructive {
        background: #ea001e;
        color: white;
    }
    
    .sf-button-destructive:hover {
        background: #ba0517;
    }
    
    .sf-button-success {
        background: #2e844a;
        color: white;
    }
    
    .sf-button-success:hover {
        background: #1e6b42;
    }
    
    /* Table styling */
    .sf-table {
        width: 100%;
        border-collapse: collapse;
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        margin: 1rem 0;
    }
    
    .sf-table th {
        background: #f8f9fa;
        color: #181818;
        font-weight: 600;
        padding: 1rem;
        text-align: left;
        border-bottom: 2px solid #e5e5e5;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    .sf-table td {
        padding: 1rem;
        border-bottom: 1px solid #f0f0f0;
        font-size: 0.875rem;
        color: #181818;
    }
    
    .sf-table tr:hover {
        background-color: #f8f9ff;
    }
    
    .sf-table-metric {
        font-weight: 600;
        background: #f8f9fa !important;
        color: #181818;
    }
    
    .sf-table-calculated {
        background: #e8f4fd !important;
        color: #0176d3;
        font-style: italic;
    }
    
    .sf-table-api {
        background: #e8f7ea !important;
        position: relative;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
        border-right: 1px solid #e5e5e5;
    }
    
    /* Metrics cards */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        transition: all 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #0176d3;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #706e6b;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    
    /* Status indicators */
    .status-api {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        background: #e8f7ea;
        color: #2e844a;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .status-manual {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        background: #fef7e8;
        color: #b8860b;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .status-calculated {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        background: #e8f4fd;
        color: #0176d3;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    /* Platform tabs */
    .platform-tabs {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 2rem;
        border-bottom: 2px solid #e5e5e5;
        padding-bottom: 0;
    }
    
    .platform-tab {
        padding: 1rem 1.5rem;
        background: transparent;
        border: none;
        border-bottom: 3px solid transparent;
        cursor: pointer;
        font-weight: 500;
        color: #706e6b;
        transition: all 0.2s;
    }
    
    .platform-tab.active {
        color: #0176d3;
        border-bottom-color: #0176d3;
        background: #f8f9ff;
    }
    
    .platform-tab:hover {
        color: #0176d3;
        background: #f8f9ff;
    }
    
    /* Date picker styling */
    .date-picker-container {
        background: #f8f9fa;
        border: 1px solid #e5e5e5;
        border-radius: 6px;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
    
    .date-range-label {
        font-size: 0.75rem;
        color: #706e6b;
        font-weight: 500;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    /* Legend */
    .legend {
        display: flex;
        gap: 1.5rem;
        margin: 1rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 6px;
        font-size: 0.875rem;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Success/Error messages */
    .success-message {
        background: #e8f7ea;
        color: #2e844a;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #2e844a;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #fef2f2;
        color: #ea001e;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #ea001e;
        margin: 1rem 0;
    }
    
    .warning-message {
        background: #fef7e8;
        color: #b8860b;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #b8860b;
        margin: 1rem 0;
    }
    
    /* Hide Streamlit default styling */
    .stTextInput > label {
        font-weight: 500;
        color: #181818;
    }
    
    .stSelectbox > label {
        font-weight: 500;
        color: #181818;
    }
    
    .stTextArea > label {
        font-weight: 500;
        color: #181818;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .sf-header h1 {
            font-size: 2rem;
        }
        
        .metrics-grid {
            grid-template-columns: 1fr;
        }
        
        .platform-tabs {
            flex-wrap: wrap;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'tables' not in st.session_state:
    st.session_state.tables = {}
if 'active_table' not in st.session_state:
    st.session_state.active_table = 'facebook'
if 'facebook_credentials' not in st.session_state:
    st.session_state.facebook_credentials = {'token': '', 'account_id': ''}

# Default metrics with calculation formulas
DEFAULT_METRICS = {
    # Raw metrics (from APIs or manual input)
    'spend': {'name': 'Spend', 'type': 'raw', 'format': 'currency'},
    'impressions': {'name': 'Impressions', 'type': 'raw', 'format': 'number'},
    'clicks': {'name': 'Clicks', 'type': 'raw', 'format': 'number'},
    'add_to_cart': {'name': 'Add to Cart', 'type': 'raw', 'format': 'number'},
    'checkout': {'name': 'Checkout', 'type': 'raw', 'format': 'number'},
    'purchase': {'name': 'Purchases', 'type': 'raw', 'format': 'number'},
    'purchase_revenue': {'name': 'Purchase Revenue', 'type': 'raw', 'format': 'currency'},
    
    # Calculated metrics
    'ctr': {'name': 'CTR', 'type': 'calculated', 'format': 'percentage'},
    'cpm': {'name': 'CPM', 'type': 'calculated', 'format': 'currency'},
    'cpc': {'name': 'CPC', 'type': 'calculated', 'format': 'currency'},
    'atc_rate': {'name': 'Add to Cart Rate', 'type': 'calculated', 'format': 'percentage'},
    'checkout_rate': {'name': 'Checkout Rate', 'type': 'calculated', 'format': 'percentage'},
    'purchase_rate': {'name': 'Purchase Rate', 'type': 'calculated', 'format': 'percentage'},
    'click_to_purchase': {'name': 'Click to Purchase Rate', 'type': 'calculated', 'format': 'percentage'},
    'roas': {'name': 'ROAS', 'type': 'calculated', 'format': 'ratio'},
    'cost_per_purchase': {'name': 'Cost per Purchase', 'type': 'calculated', 'format': 'currency'}
}

def format_value(value, format_type):
    """Format value based on type"""
    if value is None or pd.isna(value):
        return 'N/A'
    
    try:
        value = float(value)
        if format_type == 'currency':
            return f"${value:,.2f}"
        elif format_type == 'percentage':
            return f"{value:.2f}%"
        elif format_type == 'ratio':
            return f"{value:.2f}x"
        elif format_type == 'number':
            return f"{int(value):,}"
        else:
            return str(value)
    except:
        return 'N/A'

def calculate_metric(metric_key, raw_data):
    """Calculate metric based on raw data"""
    try:
        spend = float(raw_data.get('spend', 0))
        impressions = float(raw_data.get('impressions', 0))
        clicks = float(raw_data.get('clicks', 0))
        add_to_cart = float(raw_data.get('add_to_cart', 0))
        checkout = float(raw_data.get('checkout', 0))
        purchase = float(raw_data.get('purchase', 0))
        purchase_revenue = float(raw_data.get('purchase_revenue', 0))
        
        if metric_key == 'ctr':
            return (clicks / impressions * 100) if impressions > 0 else 0
        elif metric_key == 'cpm':
            return (spend / impressions * 1000) if impressions > 0 else 0
        elif metric_key == 'cpc':
            return (spend / clicks) if clicks > 0 else 0
        elif metric_key == 'atc_rate':
            return (add_to_cart / clicks * 100) if clicks > 0 else 0
        elif metric_key == 'checkout_rate':
            return (checkout / add_to_cart * 100) if add_to_cart > 0 else 0
        elif metric_key == 'purchase_rate':
            return (purchase / checkout * 100) if checkout > 0 else 0
        elif metric_key == 'click_to_purchase':
            return (purchase / clicks * 100) if clicks > 0 else 0
        elif metric_key == 'roas':
            return (purchase_revenue / spend) if spend > 0 else 0
        elif metric_key == 'cost_per_purchase':
            return (spend / purchase) if purchase > 0 else 0
        else:
            return float(raw_data.get(metric_key, 0))
    except:
        return 0

class FacebookAPI:
    def __init__(self, access_token, account_id):
        self.access_token = access_token
        self.account_id = account_id
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def get_insights(self, start_date, end_date):
        """Fetch Facebook Ads insights for specific date range"""
        
        # Define the fields we want
        fields = [
            'spend',
            'impressions', 
            'clicks',
            'cpm',
            'cpc', 
            'ctr',
            'actions',
            'action_values'
        ]
        
        params = {
            'access_token': self.access_token,
            'fields': ','.join(fields),
            'time_range': json.dumps({
                'since': start_date,
                'until': end_date
            }),
            'level': 'account',
            'time_increment': 1
        }
        
        url = f"{self.base_url}/act_{self.account_id}/insights"
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                return self.process_facebook_data(data['data'])
            else:
                return self.get_empty_metrics()
                
        except requests.exceptions.RequestException as e:
            st.error(f"Facebook API Error: {str(e)}")
            return self.get_empty_metrics()
        except Exception as e:
            st.error(f"Error processing Facebook data: {str(e)}")
            return self.get_empty_metrics()
    
    def process_facebook_data(self, raw_data):
        """Process Facebook API response into standardized format"""
        metrics = self.get_empty_metrics()
        
        # Aggregate data across all days in the period
        for day_data in raw_data:
            metrics['spend'] += float(day_data.get('spend', 0))
            metrics['impressions'] += int(day_data.get('impressions', 0))
            metrics['clicks'] += int(day_data.get('clicks', 0))
            
            # Process conversion actions
            actions = day_data.get('actions', [])
            action_values = day_data.get('action_values', [])
            
            for action in actions:
                action_type = action.get('action_type')
                value = int(action.get('value', 0))
                
                if action_type == 'add_to_cart':
                    metrics['add_to_cart'] += value
                elif action_type == 'initiate_checkout':
                    metrics['checkout'] += value
                elif action_type in ['purchase', 'complete_registration']:
                    metrics['purchase'] += value
            
            # Process revenue values
            for action_value in action_values:
                action_type = action_value.get('action_type')
                value = float(action_value.get('value', 0))
                
                if action_type in ['purchase', 'complete_registration']:
                    metrics['purchase_revenue'] += value
        
        return metrics
    
    def get_empty_metrics(self):
        """Return empty metrics structure"""
        return {
            'spend': 0,
            'impressions': 0,
            'clicks': 0,
            'add_to_cart': 0,
            'checkout': 0,
            'purchase': 0,
            'purchase_revenue': 0
        }

def fetch_facebook_data(start_date, end_date):
    """Fetch data from Facebook API"""
    creds = st.session_state.facebook_credentials
    
    if not creds['token'] or not creds['account_id']:
        return None
    
    try:
        fb_api = FacebookAPI(creds['token'], creds['account_id'])
        return fb_api.get_insights(start_date, end_date)
    except Exception as e:
        st.error(f"Error fetching Facebook data: {str(e)}")
        return None

def create_initial_table(platform):
    """Create initial table structure"""
    today = datetime.now()
    weeks = []
    
    # Generate last 4 weeks
    for i in range(3, -1, -1):
        week_end = today - timedelta(days=i*7)
        week_start = week_end - timedelta(days=6)
        
        weeks.append({
            'name': f'Week {4-i}',
            'start_date': week_start.strftime('%Y-%m-%d'),
            'end_date': week_end.strftime('%Y-%m-%d'),
            'display_name': f"{week_start.strftime('%m/%d')} - {week_end.strftime('%m/%d')}"
        })
    
    # Initialize data structure
    data = {}
    data_source = {}  # Track whether data came from API or manual input
    
    for metric_key in DEFAULT_METRICS.keys():
        data[metric_key] = {}
        data_source[metric_key] = {}
        for week in weeks:
            data[metric_key][week['name']] = 0.0
            data_source[metric_key][week['name']] = 'manual'  # default to manual
    
    return {
        'platform': platform,
        'columns': weeks,
        'metrics': DEFAULT_METRICS.copy(),
        'data': data,
        'data_source': data_source,
        'summary': f"{platform} performance summary will appear here. This section can be customized with insights, recommendations, and key takeaways."
    }

def initialize_tables():
    """Initialize all platform tables"""
    if not st.session_state.tables:
        platforms = ['Facebook', 'Google', 'LinkedIn', 'TikTok', 'Microsoft', 'Summary']
        st.session_state.tables = {
            platform.lower(): create_initial_table(platform)
            for platform in platforms
        }

def update_facebook_data_from_api():
    """Update Facebook table with API data"""
    if st.session_state.active_table != 'facebook':
        return
    
    facebook_table = st.session_state.tables['facebook']
    
    for column in facebook_table['columns']:
        with st.spinner(f"Fetching Facebook data for {column['display_name']}..."):
            api_data = fetch_facebook_data(column['start_date'], column['end_date'])
            
            if api_data:
                # Update raw metrics with API data
                raw_metrics = ['spend', 'impressions', 'clicks', 'add_to_cart', 'checkout', 'purchase', 'purchase_revenue']
                
                for metric in raw_metrics:
                    if metric in api_data:
                        facebook_table['data'][metric][column['name']] = api_data[metric]
                        facebook_table['data_source'][metric][column['name']] = 'api'
                
                st.success(f"✅ Updated {column['name']} with Facebook API data")
            else:
                st.warning(f"⚠️ Could not fetch data for {column['name']}")

def main():
    # Initialize tables
    initialize_tables()
    
    # Initialize section visibility state
    if 'section_visibility' not in st.session_state:
        st.session_state.section_visibility = {
            'summary': True,
            'controls': True,
            'date_config': True,
            'data_table': True,
            'edit_metrics': True,
            'quick_stats': True,
            'instructions': False
        }

    # Header with Salesforce styling
    st.markdown("""
    <div class="sf-header">
        <h1>Ad Reporting Dashboard</h1>
        <p>Generate comprehensive week-over-week performance reports with automated Facebook data and customizable metrics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for Facebook API Configuration
    with st.sidebar:
        st.markdown("""
        <div class="sf-card">
            <div class="sf-card-header">
                <h3 class="sf-card-title">Facebook API Configuration</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fb_token = st.text_input(
            "Facebook Access Token:",
            value=st.session_state.facebook_credentials['token'],
            type="password",
            help="Get from Facebook Graph API Explorer"
        )
        
        fb_account_id = st.text_input(
            "Facebook Account ID:",
            value=st.session_state.facebook_credentials['account_id'],
            help="Your ad account ID (numbers only, no 'act_' prefix)"
        )
        
        # Update credentials
        st.session_state.facebook_credentials['token'] = fb_token
        st.session_state.facebook_credentials['account_id'] = fb_account_id
        
        # Test connection
        if st.button("Test Facebook Connection", help="Verify your API credentials"):
            if fb_token and fb_account_id:
                test_data = fetch_facebook_data("2024-01-01", "2024-01-01")
                if test_data is not None:
                    st.markdown('<div class="success-message">Facebook API connected successfully!</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="error-message">Facebook API connection failed</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="warning-message">Please enter both token and account ID</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Facebook Auto-Pull
        if st.session_state.active_table == 'facebook':
            st.markdown("### Auto-Pull Facebook Data")
            if st.button("Fetch All Facebook Data", type="primary", help="Pull data for all date ranges"):
                if fb_token and fb_account_id:
                    update_facebook_data_from_api()
                else:
                    st.markdown('<div class="error-message">Please configure Facebook credentials first</div>', unsafe_allow_html=True)
    
    # Platform selection with tabs
    platforms = list(st.session_state.tables.keys())
    platform_display_names = [st.session_state.tables[p]['platform'] for p in platforms]
    
    # Create platform tabs
    tab_cols = st.columns(len(platforms))
    for i, (platform_key, display_name) in enumerate(zip(platforms, platform_display_names)):
        with tab_cols[i]:
            if st.button(
                display_name,
                key=f"tab_{platform_key}",
                help=f"Switch to {display_name} reporting",
                use_container_width=True
            ):
                st.session_state.active_table = platform_key
                st.rerun()
    
    # Highlight active tab
    if st.session_state.active_table in platforms:
        active_idx = platforms.index(st.session_state.active_table)
        st.markdown(f"""
        <style>
        div[data-testid="column"]:nth-child({active_idx + 1}) button {{
            background-color: #0176d3 !important;
            color: white !important;
            border-color: #0176d3 !important;
        }}
        </style>
        """, unsafe_allow_html=True)
    
    current_table = st.session_state.tables[st.session_state.active_table]
    
    # Summary section with toggle
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown(f"### {current_table['platform']} Summary")
    with col2:
        if st.button("Show/Hide" if st.session_state.section_visibility['summary'] else "Show/Hide", 
                    key="toggle_summary"):
            st.session_state.section_visibility['summary'] = not st.session_state.section_visibility['summary']
    
    if st.session_state.section_visibility['summary']:
        st.markdown(f"""
        <div class="sf-card">
            <div class="sf-card-header">
                <h3 class="sf-card-title">{current_table['platform']} Summary</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        summary_text = st.text_area(
            "Platform Summary:",
            value=current_table['summary'],
            height=100,
            key=f"summary_{st.session_state.active_table}",
            label_visibility="collapsed"
        )
        current_table['summary'] = summary_text
    
    # Controls section with toggle
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown("### Table Controls")
    with col2:
        if st.button("Show/Hide" if st.session_state.section_visibility['controls'] else "Show/Hide", 
                    key="toggle_controls"):
            st.session_state.section_visibility['controls'] = not st.session_state.section_visibility['controls']
    
    if st.session_state.section_visibility['controls']:
        st.markdown("""
        <div class="sf-card">
            <div class="sf-card-header">
                <h3 class="sf-card-title">Table Controls</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            add_metric = st.button("Add Custom Metric", help="Create a new metric for tracking")
        
        with col2:
            add_column = st.button("Add Custom Column", help="Add a new time period column")
        
        with col3:
            if st.button("Reset Table", help="Reset table to default state"):
                st.session_state.tables[st.session_state.active_table] = create_initial_table(
                    current_table['platform']
                )
                st.rerun()
        
        with col4:
            # Export functionality
            export_data = []
            for metric_key, metric in current_table['metrics'].items():
                row = {'Metric': metric['name']}
                for column in current_table['columns']:
                    if metric['type'] == 'calculated':
                        raw_data = {k: current_table['data'][k][column['name']] 
                                  for k in current_table['data'].keys()}
                        value = calculate_metric(metric_key, raw_data)
                    else:
                        value = current_table['data'][metric_key][column['name']]
                    
                    # Add data source indicator
                    source = current_table.get('data_source', {}).get(metric_key, {}).get(column['name'], 'manual')
                    source_indicator = " (API)" if source == 'api' else ""
                    
                    row[f"{column['name']} ({column['display_name']})"] = format_value(value, metric['format']) + source_indicator
                export_data.append(row)
            
            df_export = pd.DataFrame(export_data)
            csv = df_export.to_csv(index=False)
            
            st.download_button(
                label="Export CSV",
                data=csv,
                file_name=f"{st.session_state.active_table}_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                help="Download current table data as CSV"
            )
    
    # Add metric functionality
    if 'add_metric' in locals() and add_metric:
        st.markdown("""
        <div class="sf-card">
            <div class="sf-card-header">
                <h3 class="sf-card-title">Add Custom Metric</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("add_metric_form", clear_on_submit=True):
            new_metric_name = st.text_input("Metric Name:", placeholder="e.g., Video Views")
            metric_format = st.selectbox("Format:", ['number', 'currency', 'percentage', 'ratio'])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Add Metric", type="primary"):
                    if new_metric_name:
                        metric_key = new_metric_name.lower().replace(' ', '_').replace('-', '_')
                        current_table['metrics'][metric_key] = {
                            'name': new_metric_name,
                            'type': 'raw',
                            'format': metric_format
                        }
                        current_table['data'][metric_key] = {
                            col['name']: 0.0 for col in current_table['columns']
                        }
                        current_table['data_source'][metric_key] = {
                            col['name']: 'manual' for col in current_table['columns']
                        }
                        st.success(f"Added metric: {new_metric_name}")
                        st.rerun()
            with col2:
                if st.form_submit_button("Cancel"):
                    st.rerun()
    
    # Add column functionality
    if 'add_column' in locals() and add_column:
        st.markdown("""
        <div class="sf-card">
            <div class="sf-card-header">
                <h3 class="sf-card-title">Add Custom Column</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("add_column_form", clear_on_submit=True):
            new_column_name = st.text_input("Column Name:", placeholder="e.g., Week 5")
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date:", value=datetime.now().date())
            with col2:
                end_date = st.date_input("End Date:", value=datetime.now().date())
            
            button_col1, button_col2 = st.columns(2)
            with button_col1:
                if st.form_submit_button("Add Column", type="primary"):
                    if new_column_name:
                        new_column = {
                            'name': new_column_name,
                            'start_date': start_date.strftime('%Y-%m-%d'),
                            'end_date': end_date.strftime('%Y-%m-%d'),
                            'display_name': f"{start_date.strftime('%m/%d')} - {end_date.strftime('%m/%d')}"
                        }
                        current_table['columns'].append(new_column)
                        
                        # Add data for new column
                        for metric_key in current_table['data']:
                            current_table['data'][metric_key][new_column_name] = 0.0
                            current_table['data_source'][metric_key][new_column_name] = 'manual'
                        
                        st.success(f"Added column: {new_column_name}")
                        st.rerun()
            with button_col2:
                if st.form_submit_button("Cancel"):
                    st.rerun()
    
    # Date range configuration section with toggle
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown("### Date Range Configuration")
    with col2:
        if st.button("Show/Hide" if st.session_state.section_visibility['date_config'] else "Show/Hide", 
                    key="toggle_date_config"):
            st.session_state.section_visibility['date_config'] = not st.session_state.section_visibility['date_config']
    
    if st.session_state.section_visibility['date_config']:
        date_cols = st.columns(len(current_table['columns']))
        
        for i, column in enumerate(current_table['columns']):
            with date_cols[i]:
                st.markdown(f"""
                <div class="date-picker-container">
                    <div class="date-range-label">{column['name']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Parse current dates
                current_start = datetime.strptime(column['start_date'], '%Y-%m-%d').date()
                current_end = datetime.strptime(column['end_date'], '%Y-%m-%d').date()
                
                # Date inputs
                new_start = st.date_input(
                    f"Start",
                    value=current_start,
                    key=f"start_{column['name']}_{st.session_state.active_table}",
                    label_visibility="collapsed"
                )
                
                new_end = st.date_input(
                    f"End",
                    value=current_end,
                    key=f"end_{column['name']}_{st.session_state.active_table}",
                    label_visibility="collapsed"
                )
                
                # Update dates if changed
                if new_start != current_start or new_end != current_end:
                    current_table['columns'][i]['start_date'] = new_start.strftime('%Y-%m-%d')
                    current_table['columns'][i]['end_date'] = new_end.strftime('%Y-%m-%d')
                    current_table['columns'][i]['display_name'] = f"{new_start.strftime('%m/%d')} - {new_end.strftime('%m/%d')}"
    
    # Data table section with toggle
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown("### Performance Data Table")
    with col2:
        if st.button("Show/Hide" if st.session_state.section_visibility['data_table'] else "Show/Hide", 
                    key="toggle_data_table"):
            st.session_state.section_visibility['data_table'] = not st.session_state.section_visibility['data_table']
    
    if st.session_state.section_visibility['data_table']:
        # Create the main data table
        table_html = "<table class='sf-table'>"
        
        # Header row
        table_html += "<tr>"
        table_html += "<th style='text-align: left; min-width: 200px;'>Metric</th>"
        
        for column in current_table['columns']:
            table_html += f"<th style='text-align: center; min-width: 150px;'>"
            table_html += f"<strong>{column['name']}</strong><br>"
            table_html += f"<small style='color: #706e6b; font-weight: normal;'>{column['display_name']}</small></th>"
        
        table_html += "</tr>"
        
        # Data rows
        for metric_key, metric in current_table['metrics'].items():
            if metric['type'] == 'calculated':
                row_class = "sf-table-calculated"
                metric_icon = " (Calc)"
            else:
                row_class = ""
                metric_icon = ""
            
            table_html += f"<tr class='{row_class}'>"
            table_html += f"<td class='sf-table-metric'>{metric['name']}{metric_icon}</td>"
            
            for column in current_table['columns']:
                if metric['type'] == 'calculated':
                    raw_data = {k: current_table['data'][k][column['name']] for k in current_table['data'].keys()}
                    value = calculate_metric(metric_key, raw_data)
                    formatted_value = format_value(value, metric['format'])
                    table_html += f"<td style='text-align: center;'>"
                    table_html += f"<span class='status-calculated'>CALC {formatted_value}</span></td>"
                else:
                    value = current_table['data'][metric_key][column['name']]
                    formatted_value = format_value(value, metric['format'])
                    
                    # Add data source indicator
                    source = current_table.get('data_source', {}).get(metric_key, {}).get(column['name'], 'manual')
                    
                    if source == 'api':
                        cell_class = "sf-table-api"
                        status_html = f"<span class='status-api'>API {formatted_value}</span>"
                    else:
                        cell_class = ""
                        status_html = f"<span class='status-manual'>MANUAL {formatted_value}</span>"
                    
                    table_html += f"<td class='{cell_class}' style='text-align: center;'>{status_html}</td>"
            
            table_html += "</tr>"
        
        table_html += "</table>"
        
        # Legend
        st.markdown("""
        <div class="legend">
            <div class="legend-item">
                <span class="status-calculated">CALC Auto-calculated</span>
            </div>
            <div class="legend-item">
                <span class="status-api">API From Facebook API</span>
            </div>
            <div class="legend-item">
                <span class="status-manual">MANUAL Manual input</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display the HTML table
        st.markdown(table_html, unsafe_allow_html=True)
        else:
                value = current_table['data'][metric_key][column['name']]
                formatted_value = format_value(value, metric['format'])
                
                # Add data source indicator
                source = current_table.get('data_source', {}).get(metric_key, {}).get(column['name'], 'manual')
                
                if source == 'api':
                    cell_class = "sf-table-api"
                    status_html = f"<span class='status-api'>🤖 {formatted_value}</span>"
                else:
                    cell_class = ""
                    status_html = f"<span class='status-manual'>✋ {formatted_value}</span>"
                
                table_html += f"<td class='{cell_class}' style='text-align: center;'>{status_html}</td>"
        
        table_html += "</tr>"
    
    table_html += "</table>"
    
    # Legend
    st.markdown("""
    <div class="legend">
        <div class="legend-item">
            <span class="status-calculated">🧮 Auto-calculated</span>
        </div>
        <div class="legend-item">
            <span class="status-api">🤖 From Facebook API</span>
        </div>
        <div class="legend-item">
            <span class="status-manual">✋ Manual input</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display the HTML table
    st.markdown(table_html, unsafe_allow_html=True)
    
    # Editable inputs section with toggle
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown("### Edit Raw Metrics")
    with col2:
        if st.button("Show/Hide" if st.session_state.section_visibility['edit_metrics'] else "Show/Hide", 
                    key="toggle_edit_metrics"):
            st.session_state.section_visibility['edit_metrics'] = not st.session_state.section_visibility['edit_metrics']
    
    if st.session_state.section_visibility['edit_metrics']:
        st.markdown("""
        <div class="sf-card">
            <div class="sf-card-header">
                <h3 class="sf-card-title">Edit Raw Metrics</h3>
            </div>
            <p><em>Only raw metrics can be edited. Calculated metrics update automatically. API data can be overridden.</em></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create input fields for raw metrics only
        raw_metrics = {k: v for k, v in current_table['metrics'].items() if v['type'] == 'raw'}
        
        if raw_metrics:
            # Column headers for inputs
            input_cols = st.columns(len(current_table['columns']))
            for i, column in enumerate(current_table['columns']):
                input_cols[i].markdown(f"**{column['name']}**")
                input_cols[i].caption(column['display_name'])
            
            # Input fields for each raw metric
            for metric_key, metric in raw_metrics.items():
                st.markdown(f"### {metric['name']}")
                input_cols = st.columns(len(current_table['columns']))
                
                for i, column in enumerate(current_table['columns']):
                    current_value = current_table['data'][metric_key][column['name']]
                    source = current_table.get('data_source', {}).get(metric_key, {}).get(column['name'], 'manual')
                    
                    # Show different styling for API vs manual data
                    help_text = "API data (you can override)" if source == 'api' else "Manual input"
                    
                    new_value = input_cols[i].number_input(
                        f"{metric['name']} - {column['name']}",
                        value=float(current_value),
                        step=0.01,
                        key=f"input_{metric_key}_{column['name']}_{st.session_state.active_table}",
                        label_visibility="collapsed",
                        help=help_text
                    )
                    
                    # Update data and mark as manual if changed
                    if new_value != current_value:
                        current_table['data'][metric_key][column['name']] = new_value
                        current_table['data_source'][metric_key][column['name']] = 'manual'
    
    # Quick stats section with toggle
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown("### Quick Stats (Current Week)")
    with col2:
        if st.button("Show/Hide" if st.session_state.section_visibility['quick_stats'] else "Show/Hide", 
                    key="toggle_quick_stats"):
            st.session_state.section_visibility['quick_stats'] = not st.session_state.section_visibility['quick_stats']
    
    if st.session_state.section_visibility['quick_stats']:
        st.markdown("""
        <div class="sf-card">
            <div class="sf-card-header">
                <h3 class="sf-card-title">Quick Stats (Current Week)</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if current_table['columns']:
            current_week = current_table['columns'][-1]['name']  # Most recent week
            week_data = {k: current_table['data'][k][current_week] for k in current_table['data'].keys()}
            
            # Create metrics cards
            st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                spend = week_data.get('spend', 0)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{format_value(spend, 'currency')}</div>
                    <div class="metric-label">Total Spend</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                clicks = week_data.get('clicks', 0)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{format_value(clicks, 'number')}</div>
                    <div class="metric-label">Total Clicks</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                ctr = calculate_metric('ctr', week_data)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{format_value(ctr, 'percentage')}</div>
                    <div class="metric-label">CTR</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                roas = calculate_metric('roas', week_data)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{format_value(roas, 'ratio')}</div>
                    <div class="metric-label">ROAS</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Instructions section with toggle
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown("### How to Use Facebook Integration")
    with col2:
        if st.button("Show/Hide" if st.session_state.section_visibility['instructions'] else "Show/Hide", 
                    key="toggle_instructions"):
            st.session_state.section_visibility['instructions'] = not st.session_state.section_visibility['instructions']
    
    if st.session_state.section_visibility['instructions']:
        st.markdown("""
        <div class="sf-card">
            <div class="sf-card-header">
                <h3 class="sf-card-title">How to Use Facebook Integration</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        ### Facebook API Setup:
        1. **Get Access Token**: Go to Facebook Graph API Explorer and generate an access token with ads_read permissions
        2. **Find Account ID**: Your ad account ID (numbers only, no 'act_' prefix)
        3. **Enter Credentials**: Add both in the sidebar configuration panel
        4. **Test Connection**: Click "Test Facebook Connection" to verify setup
        5. **Pull Data**: Click "Fetch All Facebook Data" to pull data for all time periods
        
        ### Date Range Management:
        - **Flexible Dates**: Use the date pickers above each column to set custom date ranges
        - **Real-time Updates**: Date changes automatically update the display names
        - **API Compatibility**: Facebook API will pull data for the exact date ranges you specify
        
        ### Data Sources:
        - **API Data**: Automatically pulled from Facebook (green background)
        - **Manual Data**: Entered by you (white background)
        - **Calculated**: Auto-calculated from raw data (blue background)
        
        ### Editing Data:
        - **Override API Data**: You can always edit API data in the input fields below
        - **Manual Override**: Once edited, API data becomes manual data
        - **Auto-calculations**: Calculated metrics update instantly when raw data changes
        
        ### Facebook Metrics Available:
        - **Always Available**: Spend, Impressions, Clicks
        - **Conversion Tracking**: Add to Cart, Checkout, Purchases, Purchase Revenue (requires proper Facebook pixel setup)
        - **Calculated Metrics**: CTR, CPM, CPC, conversion rates, ROAS automatically calculated
        
        ### Export & Reporting:
        - **CSV Export**: Download complete reports with data source indicators
        - **Summary Notes**: Add platform-specific insights and recommendations
        - **Multi-Platform**: Switch between different ad platforms using the tabs
        
        ### Next Steps:
        - **Expand Platforms**: Add Google, LinkedIn, TikTok data manually or via future API integrations
        - **Custom Metrics**: Create platform-specific metrics as needed
        - **Time Periods**: Add custom date ranges beyond the default weekly structure
        """)

if __name__ == "__main__":
    main()
