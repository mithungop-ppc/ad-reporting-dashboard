import streamlit as st
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(
    page_title="AdMetrics Pro",
    page_icon="🚀",
    layout="wide"
)

# Simple CSS
st.markdown("""
<style>
.main {
    background-color: #f8fafc;
}
.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #ff6952;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_platform' not in st.session_state:
    st.session_state.selected_platform = 'Facebook'

# Sample data
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
    """Create metrics table"""
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
            
            if metric['format'] == 'currency':
                row[week] = f"${value:,.2f}"
            elif metric['format'] == 'percentage':
                row[week] = f"{value:.2f}%"
            elif metric['format'] == 'number':
                row[week] = f"{int(value):,}"
            else:
                row[week] = f"{value:.2f}"
        table_data.append(row)
    
    return pd.DataFrame(table_data)

# Main app
def main():
    # Header
    st.markdown("# 🚀 AdMetrics Pro")
    st.markdown("**Track and optimize your advertising performance across all platforms**")
    st.markdown("---")
    
    # Platform selector
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        platforms = ['Facebook', 'Google Ads', 'LinkedIn']
        selected_platform = st.selectbox("Select Platform:", platforms)
        st.session_state.selected_platform = selected_platform
    
    with col2:
        if st.button("🔄 Refresh Data", type="primary"):
            st.rerun()
    
    with col3:
        if st.button("📥 Export CSV"):
            st.success("Export ready!")
    
    st.markdown("---")
    
    # Get data
    all_data = get_sample_data()
    platform_data = all_data[selected_platform]
    
    # Current week metrics for KPIs
    current_week = calculate_metrics(platform_data['Week 4'])
    previous_week = calculate_metrics(platform_data['Week 3'])
    
    # KPI Cards
    st.subheader(f"📊 {selected_platform} - Current Week Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        spend_change = ((current_week['spend'] - previous_week['spend']) / previous_week['spend']) * 100
        st.metric(
            "💰 Spend",
            f"${current_week['spend']:,.0f}",
            f"{spend_change:+.1f}%"
        )
    
    with col2:
        clicks_change = ((current_week['clicks'] - previous_week['clicks']) / previous_week['clicks']) * 100
        st.metric(
            "👆 Clicks",
            f"{current_week['clicks']:,}",
            f"{clicks_change:+.1f}%"
        )
    
    with col3:
        ctr_change = current_week['ctr'] - previous_week['ctr']
        st.metric(
            "🎯 CTR",
            f"{current_week['ctr']:.2f}%",
            f"{ctr_change:+.2f}%"
        )
    
    with col4:
        conv_change = ((current_week['conversions'] - previous_week['conversions']) / previous_week['conversions']) * 100
        st.metric(
            "🏆 Conversions",
            f"{current_week['conversions']:,}",
            f"{conv_change:+.1f}%"
        )
    
    st.markdown("---")
    
    # Two column layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Main data table
        st.subheader("📋 Performance Metrics")
        st.info("📊 Showing sample data - connect APIs for real-time updates")
        
        # Create and display table
        metrics_df = create_metrics_table(platform_data)
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
        
        st.markdown("**Legend:** 💰 Raw Data | 📊 Calculated Metrics")
    
    with col2:
        # Summary section
        st.subheader("📝 Summary")
        
        summary_text = st.text_area(
            "Performance Insights:",
            f"{selected_platform} campaigns showing strong performance. CTR improved week-over-week. Consider increasing budget for top performers.",
            height=100
        )
        
        st.subheader("🎯 Next Actions")
        actions = st.text_area(
            "Action Items:",
            "• Increase budget by 20%\n• Test new ad creatives\n• Optimize targeting\n• Review top campaigns",
            height=100
        )
        
        st.subheader("⚡ Quick Actions")
        if st.button("🔄 Sync Data", key="sync"):
            st.success("Data synced!")
        
        if st.button("📊 Generate Report", key="report"):
            st.success("Report generated!")
        
        if st.button("📧 Email Summary", key="email"):
            st.success("Email sent!")

if __name__ == "__main__":
    main()
