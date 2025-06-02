import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests
import json

# Page config
st.set_page_config(
    page_title="Ultimate Ad Reporting Dashboard",
    page_icon="🚀",
    layout="wide"
)

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
    
    # Header
    st.title("🚀 Ultimate Ad Reporting Dashboard")
    st.markdown("Generate week-over-week performance reports with automated Facebook data and customizable metrics")
    st.markdown("---")
    
    # Facebook API Configuration
    with st.sidebar:
        st.header("🔧 Facebook API Configuration")
        
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
        if st.button("🧪 Test Facebook Connection"):
            if fb_token and fb_account_id:
                test_data = fetch_facebook_data("2024-01-01", "2024-01-01")
                if test_data is not None:
                    st.success("✅ Facebook API connected successfully!")
                else:
                    st.error("❌ Facebook API connection failed")
            else:
                st.warning("⚠️ Please enter both token and account ID")
        
        st.markdown("---")
        
        # Facebook Auto-Pull
        if st.session_state.active_table == 'facebook':
            st.subheader("📡 Auto-Pull Facebook Data")
            if st.button("🔄 Fetch All Facebook Data", type="primary"):
                if fb_token and fb_account_id:
                    update_facebook_data_from_api()
                else:
                    st.error("❌ Please configure Facebook credentials first")
    
    # Platform selection
    platforms = list(st.session_state.tables.keys())
    platform_display_names = [st.session_state.tables[p]['platform'] for p in platforms]
    
    # Platform selector
    col1, col2 = st.columns([2, 4])
    with col1:
        selected_idx = st.selectbox(
            "Select Platform:",
            range(len(platforms)),
            format_func=lambda x: platform_display_names[x],
            index=platforms.index(st.session_state.active_table) if st.session_state.active_table in platforms else 0
        )
        st.session_state.active_table = platforms[selected_idx]
    
    current_table = st.session_state.tables[st.session_state.active_table]
    
    # Summary section
    st.subheader(f"📝 {current_table['platform']} Summary")
    summary_text = st.text_area(
        "Platform Summary:",
        value=current_table['summary'],
        height=100,
        key=f"summary_{st.session_state.active_table}"
    )
    current_table['summary'] = summary_text
    
    st.markdown("---")
    
    # Controls in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        add_metric = st.button("➕ Add Custom Metric")
    
    with col2:
        add_column = st.button("📅 Add Custom Column")
    
    with col3:
        if st.button("🔄 Reset Table"):
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
                source_indicator = " 🤖" if source == 'api' else ""
                
                row[f"{column['name']} ({column['display_name']})"] = format_value(value, metric['format']) + source_indicator
            export_data.append(row)
        
        df_export = pd.DataFrame(export_data)
        csv = df_export.to_csv(index=False)
        
        st.download_button(
            label="💾 Export CSV",
            data=csv,
            file_name=f"{st.session_state.active_table}_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    # Add metric functionality
    if add_metric:
        with st.form("add_metric_form", clear_on_submit=True):
            st.subheader("Add Custom Metric")
            new_metric_name = st.text_input("Metric Name:")
            metric_format = st.selectbox("Format:", ['number', 'currency', 'percentage', 'ratio'])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Add Metric"):
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
    
    # Add column functionality
    if add_column:
        with st.form("add_column_form", clear_on_submit=True):
            st.subheader("Add Custom Column")
            new_column_name = st.text_input("Column Name:")
            start_date = st.date_input("Start Date:", value=datetime.now().date())
            end_date = st.date_input("End Date:", value=datetime.now().date())
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Add Column"):
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
    
    st.markdown("---")
    
    # Data table
    st.subheader("📊 Performance Data Table")
    
    # Create a properly aligned table using HTML
    table_html = "<table style='width: 100%; border-collapse: collapse; margin: 20px 0;'>"
    
    # Header row
    table_html += "<tr style='background-color: #f0f2f6; border-bottom: 2px solid #ddd;'>"
    table_html += "<th style='text-align: left; padding: 12px; font-weight: bold; border-right: 1px solid #ddd;'>Metric</th>"
    
    for column in current_table['columns']:
        table_html += f"<th style='text-align: center; padding: 12px; font-weight: bold; border-right: 1px solid #ddd;'>"
        table_html += f"{column['name']}<br><small style='color: #666; font-weight: normal;'>({column['display_name']})</small></th>"
    
    table_html += "</tr>"
    
    # Data rows
    for metric_key, metric in current_table['metrics'].items():
        bg_color = "#f8f9ff" if metric['type'] == 'calculated' else "#ffffff"
        metric_icon = " 🧮" if metric['type'] == 'calculated' else ""
        
        table_html += f"<tr style='background-color: {bg_color}; border-bottom: 1px solid #eee;'>"
        table_html += f"<td style='text-align: left; padding: 12px; font-weight: 500; border-right: 1px solid #ddd; background-color: #f8f9fa;'>{metric['name']}{metric_icon}</td>"
        
        for column in current_table['columns']:
            if metric['type'] == 'calculated':
                raw_data = {k: current_table['data'][k][column['name']] for k in current_table['data'].keys()}
                value = calculate_metric(metric_key, raw_data)
                formatted_value = format_value(value, metric['format'])
                table_html += f"<td style='text-align: center; padding: 12px; border-right: 1px solid #ddd; font-style: italic; color: #2563eb;'>{formatted_value}</td>"
            else:
                value = current_table['data'][metric_key][column['name']]
                formatted_value = format_value(value, metric['format'])
                
                # Add API indicator
                source = current_table.get('data_source', {}).get(metric_key, {}).get(column['name'], 'manual')
                api_indicator = " 🤖" if source == 'api' else ""
                cell_bg = "#e8f5e8" if source == 'api' else "#ffffff"
                
                table_html += f"<td style='text-align: center; padding: 12px; border-right: 1px solid #ddd; background-color: {cell_bg};'>{formatted_value}{api_indicator}</td>"
        
        table_html += "</tr>"
    
    table_html += "</table>"
    
    # Legend
    st.markdown("""
    **Legend:** 🧮 = Auto-calculated | 🤖 = From Facebook API | 🟢 = API data | No icon = Manual input
    """)
    
    # Display the HTML table
    st.markdown(table_html, unsafe_allow_html=True)
    
    # Editable inputs section
    st.subheader("✏️ Edit Raw Metrics")
    st.markdown("*Only raw metrics can be edited. Calculated metrics (🧮) update automatically. API data (🤖) can be overridden.*")
    
    # Create input fields for raw metrics only
    raw_metrics = {k: v for k, v in current_table['metrics'].items() if v['type'] == 'raw'}
    
    if raw_metrics:
        cols = st.columns(len(current_table['columns']))
        
        # Column headers
        for i, column in enumerate(current_table['columns']):
            cols[i].markdown(f"**{column['name']}**")
            cols[i].caption(column['display_name'])
        
        # Input fields for each raw metric
        for metric_key, metric in raw_metrics.items():
            st.markdown(f"**{metric['name']}**")
            cols = st.columns(len(current_table['columns']))
            
            for i, column in enumerate(current_table['columns']):
                current_value = current_table['data'][metric_key][column['name']]
                source = current_table.get('data_source', {}).get(metric_key, {}).get(column['name'], 'manual')
                
                # Show different styling for API vs manual data
                help_text = "🤖 API data (you can override)" if source == 'api' else "Manual input"
                
                new_value = cols[i].number_input(
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
    
    # Quick stats
    st.markdown("---")
    st.subheader("📈 Quick Stats (Current Week)")
    
    if current_table['columns']:
        current_week = current_table['columns'][-1]['name']  # Most recent week
        week_data = {k: current_table['data'][k][current_week] for k in current_table['data'].keys()}
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            spend = week_data.get('spend', 0)
            st.metric("Total Spend", format_value(spend, 'currency'))
        
        with col2:
            clicks = week_data.get('clicks', 0)
            st.metric("Total Clicks", format_value(clicks, 'number'))
        
        with col3:
            ctr = calculate_metric('ctr', week_data)
            st.metric("CTR", format_value(ctr, 'percentage'))
        
        with col4:
            roas = calculate_metric('roas', week_data)
            st.metric("ROAS", format_value(roas, 'ratio'))
    
    # Instructions
    st.markdown("---")
    st.subheader("📋 How to Use Facebook Integration")
    with st.expander("Click to see instructions"):
        st.markdown("""
        **Facebook API Setup:**
        1. Enter your Facebook Access Token and Account ID in the sidebar
        2. Click "Test Facebook Connection" to verify it works
        3. Click "Fetch All Facebook Data" to pull data for all weeks
        
        **Data Sources:**
        - 🤖 **API Data**: Automatically pulled from Facebook (shown with green background)
        - **Manual Data**: Entered by you (white background)
        - 🧮 **Calculated**: Auto-calculated from raw data (blue background)
        
        **Editing:**
        - You can always override API data by editing the input fields below
        - Once you edit API data, it becomes manual data
        - Calculated metrics update automatically when raw data changes
        
        **Facebook Metrics Pulled:**
        - Spend, Impressions, Clicks (always available)
        - Add to Cart, Checkout, Purchases, Purchase Revenue (if configured in Facebook)
        
        **Next Steps:**
        - Use this for Facebook reporting while setting up other platform APIs
        - All your customization features still work (add metrics, columns, export, etc.)
        """)

if __name__ == "__main__":
    main()
