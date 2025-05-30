import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

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
    for metric_key in DEFAULT_METRICS.keys():
        data[metric_key] = {}
        for week in weeks:
            data[metric_key][week['name']] = 0.0
    
    return {
        'platform': platform,
        'columns': weeks,
        'metrics': DEFAULT_METRICS.copy(),
        'data': data,
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

def main():
    # Initialize tables
    initialize_tables()
    
    # Header
    st.title("🚀 Ultimate Ad Reporting Dashboard")
    st.markdown("Generate week-over-week performance reports with customizable metrics and date ranges")
    st.markdown("---")
    
    # Platform selection tabs
    platforms = list(st.session_state.tables.keys())
    platform_names = [st.session_state.tables[p]['platform'] for p in platforms]
    
    selected_idx = st.tabs(platform_names)
    
    # Use radio buttons for platform selection
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        selected_platform = st.selectbox(
            "Select Platform:",
            platforms,
            format_func=lambda x: st.session_state.tables[x]['platform'],
            index=platforms.index(st.session_state.active_table)
        )
        st.session_state.active_table = selected_platform
    
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
    
    # Controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Add Custom Metric"):
            st.session_state.show_add_metric = True
    
    with col2:
        if st.button("📅 Add Custom Column"):
            st.session_state.show_add_column = True
    
    with col3:
        if st.button("💾 Export CSV"):
            # Create CSV export
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
                    
                    row[f"{column['name']} ({column['display_name']})"] = format_value(value, metric['format'])
                export_data.append(row)
            
            df_export = pd.DataFrame(export_data)
            csv = df_export.to_csv(index=False)
            
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"{st.session_state.active_table}_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col4:
        if st.button("🔄 Reset Table"):
            st.session_state.tables[st.session_state.active_table] = create_initial_table(
                current_table['platform']
            )
            st.rerun()
    
    # Add metric modal
    if getattr(st.session_state, 'show_add_metric', False):
        with st.form("add_metric_form"):
            st.subheader("Add Custom Metric")
            new_metric_name = st.text_input("Metric Name:")
            metric_format = st.selectbox("Format:", ['number', 'currency', 'percentage', 'ratio'])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Add Metric"):
                    if new_metric_name:
                        metric_key = new_metric_name.lower().replace(' ', '_')
                        current_table['metrics'][metric_key] = {
                            'name': new_metric_name,
                            'type': 'raw',
                            'format': metric_format
                        }
                        current_table['data'][metric_key] = {
                            col['name']: 0.0 for col in current_table['columns']
                        }
                        st.session_state.show_add_metric = False
                        st.rerun()
            
            with col2:
                if st.form_submit_button("Cancel"):
                    st.session_state.show_add_metric = False
                    st.rerun()
    
    # Add column modal
    if getattr(st.session_state, 'show_add_column', False):
        with st.form("add_column_form"):
            st.subheader("Add Custom Column")
            new_column_name = st.text_input("Column Name:")
            start_date = st.date_input("Start Date:")
            end_date = st.date_input("End Date:")
            
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
                        
                        st.session_state.show_add_column = False
                        st.rerun()
            
            with col2:
                if st.form_submit_button("Cancel"):
                    st.session_state.show_add_column = False
                    st.rerun()
    
    st.markdown("---")
    
    # Data table
    st.subheader("📊 Performance Data")
    
    # Create editable data table
    metrics_list = list(current_table['metrics'].items())
    
    # Create columns for the table
    cols = st.columns([2] + [1] * len(current_table['columns']))
    
    # Header row
    cols[0].markdown("**Metric**")
    for i, column in enumerate(current_table['columns']):
        cols[i+1].markdown(f"**{column['name']}**")
        cols[i+1].caption(column['display_name'])
    
    # Data rows
    for metric_key, metric in metrics_list:
        cols[0].markdown(f"{metric['name']}" + (" 🧮" if metric['type'] == 'calculated' else ""))
        
        for i, column in enumerate(current_table['columns']):
            if metric['type'] == 'calculated':
                # Calculate value
                raw_data = {k: current_table['data'][k][column['name']] for k in current_table['data'].keys()}
                value = calculate_metric(metric_key, raw_data)
                cols[i+1].markdown(f"*{format_value(value, metric['format'])}*")
            else:
                # Editable raw value
                current_value = current_table['data'][metric_key][column['name']]
                new_value = cols[i+1].number_input(
                    f"{metric_key}_{column['name']}",
                    value=float(current_value),
                    step=0.01,
                    key=f"input_{metric_key}_{column['name']}_{st.session_state.active_table}",
                    label_visibility="collapsed"
                )
                current_table['data'][metric_key][column['name']] = new_value
    
    # Quick stats
    st.markdown("---")
    st.subheader("📈 Quick Stats")
    
    # Calculate totals for Week 1
    if current_table['columns']:
        week1_data = {k: current_table['data'][k][current_table['columns'][0]['name']] 
                     for k in current_table['data'].keys()}
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            spend = week1_data.get('spend', 0)
            st.metric("Total Spend", format_value(spend, 'currency'))
        
        with col2:
            clicks = week1_data.get('clicks', 0)
            st.metric("Total Clicks", format_value(clicks, 'number'))
        
        with col3:
            ctr = calculate_metric('ctr', week1_data)
            st.metric("CTR", format_value(ctr, 'percentage'))
        
        with col4:
            roas = calculate_metric('roas', week1_data)
            st.metric("ROAS", format_value(roas, 'ratio'))

if __name__ == "__main__":
    main()
