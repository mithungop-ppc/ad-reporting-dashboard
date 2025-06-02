import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="AdMetrics Pro",
    page_icon="📊",
    layout="wide"
)

# Professional CSS styling
st.markdown("""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Global styling */
* {
    font-family: 'Inter', sans-serif;
}

.main {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    padding: 2rem 1rem;
}

/* Header styling */
.main-header {
    text-align: center;
    margin-bottom: 3rem;
}

.main-title {
    color: #1e293b;
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    letter-spacing: -0.025em;
}

.main-subtitle {
    color: #64748b;
    font-size: 1.25rem;
    font-weight: 400;
    margin-bottom: 2rem;
}

/* Custom button styling */
.stButton > button {
    background: linear-gradient(135deg, #ff6952 0%, #e55a47 100%);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0.4rem 0.8rem;
    font-weight: 500;
    font-size: 0.8rem;
    transition: all 0.2s ease;
    box-shadow: 0 1px 3px rgba(255, 105, 82, 0.2);
    width: auto;
    min-width: 80px;
    height: 32px;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #e55a47 0%, #d14a37 100%);
    transform: translateY(-1px);
    box-shadow: 0 2px 6px rgba(255, 105, 82, 0.3);
}

.stButton > button:active {
    transform: translateY(0);
}

/* Small button variant */
.small-btn > button {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    min-width: 60px;
    height: 28px;
}

/* Secondary button styling */
.secondary-btn > button {
    background: white;
    color: #64748b;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    font-weight: 500;
    transition: all 0.2s ease;
}

.secondary-btn > button:hover {
    border-color: #ff6952;
    color: #ff6952;
    background: #fef2f2;
}

/* Metric cards */
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid #f1f5f9;
    margin: 1rem 0;
    transition: all 0.2s ease;
}

.metric-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
}

/* Platform selector styling */
.stSelectbox > div > div > div {
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-weight: 500;
}

/* Table styling */
.dataframe {
    border: none;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* API Configuration Panel */
.api-config {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    border: 1px solid #f1f5f9;
    margin: 1rem 0;
}

.api-status-connected {
    background: #dcfce7;
    color: #166534;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-weight: 500;
    font-size: 0.875rem;
    display: inline-block;
    margin: 0.5rem 0;
}

.api-status-disconnected {
    background: #fef2f2;
    color: #dc2626;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-weight: 500;
    font-size: 0.875rem;
    display: inline-block;
    margin: 0.5rem 0;
}

/* Input styling */
.stTextInput > div > div > input {
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    padding: 0.75rem;
    font-weight: 500;
    transition: all 0.2s ease;
}

.stTextInput > div > div > input:focus {
    border-color: #ff6952;
    box-shadow: 0 0 0 3px rgba(255, 105, 82, 0.1);
}

/* Text area styling */
.stTextArea > div > div > textarea {
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    padding: 0.75rem;
    font-weight: 400;
    line-height: 1.5;
    transition: all 0.2s ease;
}

.stTextArea > div > div > textarea:focus {
    border-color: #ff6952;
    box-shadow: 0 0 0 3px rgba(255, 105, 82, 0.1);
}

/* Success/Error messages */
.stSuccess {
    background: #dcfce7;
    border: 1px solid #bbf7d0;
    border-radius: 8px;
    color: #166534;
}

.stError {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    color: #dc2626;
}

.stInfo {
    background: #dbeafe;
    border: 1px solid #bfdbfe;
    border-radius: 8px;
    color: #1d4ed8;
}

/* Section headers */
.section-header {
    color: #1e293b;
    font-size: 1.5rem;
    font-weight: 600;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #f1f5f9;
}

/* Divider styling */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_platform' not in st.session_state:
    st.session_state.selected_platform = 'Facebook'
if 'facebook_connected' not in st.session_state:
    st.session_state.facebook_connected = False
if 'facebook_token' not in st.session_state:
    st.session_state.facebook_token = ''
if 'facebook_account_id' not in st.session_state:
    st.session_state.facebook_account_id = ''
if 'date_ranges' not in st.session_state:
    # Initialize with default date ranges (last 4 weeks)
    today = datetime.now()
    st.session_state.date_ranges = {}
    for i in range(4):
        week_end = today - timedelta(days=7*i)
        week_start = week_end - timedelta(days=6)
        st.session_state.date_ranges[f'Week {4-i}'] = {
            'start': week_start.date(),
            'end': week_end.date()
        }

# Facebook API Integration
class FacebookAPI:
    def __init__(self, access_token, account_id):
        self.access_token = access_token
        self.account_id = account_id
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def test_connection(self):
        """Test Facebook API connection"""
        try:
            url = f"{self.base_url}/me"
            params = {
                'access_token': self.access_token,
                'fields': 'name'
            }
            response = requests.get(url, params=params)
            return response.status_code == 200
        except:
            return False
    
    def get_insights(self, start_date, end_date):
        """Fetch Facebook Ads insights"""
        fields = [
            'spend', 'impressions', 'clicks', 'cpm', 'cpc', 'ctr',
            'actions', 'action_values'
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
            return self.process_facebook_data(data.get('data', []))
        except Exception as e:
            st.error(f"Facebook API Error: {str(e)}")
            return self.get_empty_metrics()
    
    def process_facebook_data(self, raw_data):
        """Process Facebook API response"""
        metrics = self.get_empty_metrics()
        
        for day_data in raw_data:
            metrics['spend'] += float(day_data.get('spend', 0))
            metrics['impressions'] += int(day_data.get('impressions', 0))
            metrics['clicks'] += int(day_data.get('clicks', 0))
            
            # Process conversion actions
            actions = day_data.get('actions', [])
            for action in actions:
                action_type = action.get('action_type')
                value = int(action.get('value', 0))
                
                if action_type == 'purchase':
                    metrics['conversions'] += value
        
        return metrics
    
    def get_empty_metrics(self):
        """Return empty metrics structure"""
        return {
            'spend': 0,
            'impressions': 0,
            'clicks': 0,
            'conversions': 0
        }

# Sample data fallback
def get_sample_data():
    return {
        'Facebook': {
            'Week 1': {'spend': 5000, 'clicks': 2500, 'impressions': 250000, 'conversions': 125},
            'Week 2': {'spend': 6000, 'clicks': 3000, 'impressions': 300000, 'conversions': 150},
            'Week 3': {'spend': 5500, 'clicks': 2800, 'impressions': 280000, 'conversions': 140},
            'Week 4': {'spend': 6500, 'clicks': 3200, 'impressions': 320000, 'conversions': 160},
        },
        'Google Ads': {
            'Week 1': {'spend': 8000, 'clicks': 4000, 'impressions': 400000, 'conversions': 200},
            'Week 2': {'spend': 7500, 'clicks': 3800, 'impressions': 380000, 'conversions': 190},
            'Week 3': {'spend': 8200, 'clicks': 4100, 'impressions': 410000, 'conversions': 205},
            'Week 4': {'spend': 8800, 'clicks': 4400, 'impressions': 440000, 'conversions': 220},
        },
        'LinkedIn': {
            'Week 1': {'spend': 2000, 'clicks': 800, 'impressions': 80000, 'conversions': 40},
            'Week 2': {'spend': 2200, 'clicks': 880, 'impressions': 88000, 'conversions': 44},
            'Week 3': {'spend': 2100, 'clicks': 840, 'impressions': 84000, 'conversions': 42},
            'Week 4': {'spend': 2300, 'clicks': 920, 'impressions': 92000, 'conversions': 46},
        }
    }

def get_facebook_data():
    """Get Facebook data from API or sample with custom date ranges"""
    if st.session_state.facebook_connected and st.session_state.facebook_token and st.session_state.facebook_account_id:
        try:
            fb_api = FacebookAPI(st.session_state.facebook_token, st.session_state.facebook_account_id)
            
            # Get data for each week using custom date ranges
            facebook_data = {}
            
            for week, date_range in st.session_state.date_ranges.items():
                week_data = fb_api.get_insights(
                    date_range['start'].strftime('%Y-%m-%d'),
                    date_range['end'].strftime('%Y-%m-%d')
                )
                facebook_data[week] = week_data
            
            return facebook_data
        except Exception as e:
            st.error(f"Failed to fetch Facebook data: {str(e)}")
            return get_sample_data()['Facebook']
    else:
        return get_sample_data()['Facebook']

def calculate_metrics(week_data):
    """Calculate derived metrics"""
    spend = week_data['spend']
    clicks = week_data['clicks']
    impressions = week_data['impressions']
    conversions = week_data['conversions']
    
    ctr = (clicks / impressions * 100) if impressions > 0 else 0
    cpc = (spend / clicks) if clicks > 0 else 0
    conversion_rate = (conversions / clicks * 100) if clicks > 0 else 0
    cost_per_conversion = (spend / conversions) if conversions > 0 else 0
    
    return {
        'spend': spend,
        'clicks': clicks,
        'impressions': impressions,
        'conversions': conversions,
        'ctr': ctr,
        'cpc': cpc,
        'conversion_rate': conversion_rate,
        'cost_per_conversion': cost_per_conversion
    }

def create_metrics_table(platform_data):
    """Create metrics table with custom date ranges in headers"""
    metrics_list = [
        {'name': 'Spend', 'key': 'spend', 'format': 'currency'},
        {'name': 'Impressions', 'key': 'impressions', 'format': 'number'},
        {'name': 'Clicks', 'key': 'clicks', 'format': 'number'},
        {'name': 'Conversions', 'key': 'conversions', 'format': 'number'},
        {'name': 'CTR (%)', 'key': 'ctr', 'format': 'percentage'},
        {'name': 'CPC', 'key': 'cpc', 'format': 'currency'},
        {'name': 'Conversion Rate (%)', 'key': 'conversion_rate', 'format': 'percentage'},
        {'name': 'Cost per Conversion', 'key': 'cost_per_conversion', 'format': 'currency'},
    ]
    
    table_data = []
    for metric in metrics_list:
        row = {'Metric': metric['name']}
        for week in ['Week 1', 'Week 2', 'Week 3', 'Week 4']:
            week_metrics = calculate_metrics(platform_data[week])
            value = week_metrics[metric['key']]
            
            # Create column header with date range
            date_range = st.session_state.date_ranges[week]
            column_header = f"{week}\n({date_range['start'].strftime('%m/%d')} - {date_range['end'].strftime('%m/%d')})"
            
            if metric['format'] == 'currency':
                row[column_header] = f"${value:,.2f}"
            elif metric['format'] == 'percentage':
                row[column_header] = f"{value:.2f}%"
            elif metric['format'] == 'number':
                row[column_header] = f"{int(value):,}"
            else:
                row[column_header] = f"{value:.2f}"
        table_data.append(row)
    
    return pd.DataFrame(table_data)

# Main app
def main():
    # Header
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">AdMetrics Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">Professional advertising performance dashboard</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Facebook API Configuration
    with st.expander("Facebook API Configuration", expanded=not st.session_state.facebook_connected):
        st.markdown('<div class="api-config">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            facebook_token = st.text_input(
                "Facebook Access Token",
                value=st.session_state.facebook_token,
                type="password",
                help="Get from Facebook Graph API Explorer"
            )
            
        with col2:
            facebook_account_id = st.text_input(
                "Facebook Account ID",
                value=st.session_state.facebook_account_id,
                help="Your ad account ID (numbers only)"
            )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("Test Connection"):
                if facebook_token and facebook_account_id:
                    fb_api = FacebookAPI(facebook_token, facebook_account_id)
                    if fb_api.test_connection():
                        st.session_state.facebook_connected = True
                        st.session_state.facebook_token = facebook_token
                        st.session_state.facebook_account_id = facebook_account_id
                        st.success("Facebook API connected successfully!")
                    else:
                        st.error("Failed to connect to Facebook API")
                else:
                    st.error("Please enter both token and account ID")
        
        with col2:
            if st.button("Disconnect"):
                st.session_state.facebook_connected = False
                st.session_state.facebook_token = ''
                st.session_state.facebook_account_id = ''
                st.success("Disconnected from Facebook API")
        
        with col3:
            if st.session_state.facebook_connected:
                st.markdown('<div class="api-status-connected">Connected to Facebook API</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="api-status-disconnected">Not connected to Facebook API</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Date Range Configuration
    with st.expander("Configure Date Ranges for Each Column", expanded=False):
        st.markdown("**Customize the date range for each week column:**")
        
        cols = st.columns(4)
        for i, (week, date_range) in enumerate(st.session_state.date_ranges.items()):
            with cols[i]:
                st.markdown(f"**{week}**")
                
                new_start = st.date_input(
                    "Start",
                    value=date_range['start'],
                    key=f"start_{week}",
                    label_visibility="collapsed"
                )
                
                new_end = st.date_input(
                    "End", 
                    value=date_range['end'],
                    key=f"end_{week}",
                    label_visibility="collapsed"
                )
                
                if st.button("Update", key=f"update_{week}", help=f"Update {week} date range"):
                    st.session_state.date_ranges[week] = {
                        'start': new_start,
                        'end': new_end
                    }
                    st.success(f"{week} updated!")
                    st.rerun()
                
                st.caption(f"{date_range['start'].strftime('%m/%d')} - {date_range['end'].strftime('%m/%d')}")
    
    # Platform and controls
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        platforms = ['Facebook', 'Google Ads', 'LinkedIn']
        selected_platform = st.selectbox("Select Platform", platforms)
        st.session_state.selected_platform = selected_platform
    
    with col2:
        st.markdown('<div class="small-btn">', unsafe_allow_html=True)
        if st.button("Refresh"):
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="small-btn">', unsafe_allow_html=True)
        if st.button("Export"):
            st.success("Export ready!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="small-btn">', unsafe_allow_html=True)
        if st.button("Report"):
            st.success("Report generated!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Get data based on platform and connection status
    if selected_platform == 'Facebook':
        platform_data = get_facebook_data()
        data_source = "Facebook API" if st.session_state.facebook_connected else "Sample Data"
    else:
        all_data = get_sample_data()
        platform_data = all_data[selected_platform]
        data_source = "Sample Data"
    
    # Current week metrics for KPIs
    current_week = calculate_metrics(platform_data['Week 4'])
    previous_week = calculate_metrics(platform_data['Week 3'])
    
    # KPI Cards
    st.markdown(f'<h2 class="section-header">{selected_platform} - Current Week Performance</h2>', unsafe_allow_html=True)
    
    if data_source == "Facebook API":
        st.success("Showing live Facebook data")
    else:
        st.info(f"Showing {data_source.lower()} - Connect Facebook API for live data")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        spend_change = ((current_week['spend'] - previous_week['spend']) / previous_week['spend']) * 100
        st.metric(
            "Total Spend",
            f"${current_week['spend']:,.0f}",
            f"{spend_change:+.1f}%"
        )
    
    with col2:
        clicks_change = ((current_week['clicks'] - previous_week['clicks']) / previous_week['clicks']) * 100
        st.metric(
            "Total Clicks",
            f"{current_week['clicks']:,}",
            f"{clicks_change:+.1f}%"
        )
    
    with col3:
        ctr_change = current_week['ctr'] - previous_week['ctr']
        st.metric(
            "CTR",
            f"{current_week['ctr']:.2f}%",
            f"{ctr_change:+.2f}%"
        )
    
    with col4:
        conv_change = ((current_week['conversions'] - previous_week['conversions']) / previous_week['conversions']) * 100
        st.metric(
            "Conversions",
            f"{current_week['conversions']:,}",
            f"{conv_change:+.1f}%"
        )
    
    st.markdown("---")
    
    # Two column layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Main data table
        st.markdown('<h2 class="section-header">Performance Metrics</h2>', unsafe_allow_html=True)
        
        # Create and display table
        metrics_df = create_metrics_table(platform_data)
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
        
        st.markdown("**Data Source:** " + data_source)
    
    with col2:
        # Summary section
        st.markdown('<h3 class="section-header">Performance Summary</h3>', unsafe_allow_html=True)
        
        summary_text = st.text_area(
            "Insights & Analysis",
            f"{selected_platform} campaigns showing strong performance. CTR improved week-over-week. Consider increasing budget for top performers.",
            height=120,
            key="summary"
        )
        
        st.markdown('<h3 class="section-header">Action Items</h3>', unsafe_allow_html=True)
        
        actions = st.text_area(
            "Next Steps",
            "• Increase budget by 20%\n• Test new ad creatives\n• Optimize targeting\n• Review top campaigns",
            height=120,
            key="actions"
        )
        
        st.markdown('<h3 class="section-header">Quick Actions</h3>', unsafe_allow_html=True)
        
        st.markdown('<div class="small-btn">', unsafe_allow_html=True)
        if st.button("Sync Data", key="sync"):
            if selected_platform == 'Facebook' and st.session_state.facebook_connected:
                st.success("Facebook data synced!")
            else:
                st.success("Data sync completed!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="small-btn">', unsafe_allow_html=True)
        if st.button("Email Report", key="email"):
            st.success("Report emailed!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="small-btn">', unsafe_allow_html=True)
        if st.button("Auto-Sync", key="schedule"):
            st.success("Auto-sync enabled!")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
