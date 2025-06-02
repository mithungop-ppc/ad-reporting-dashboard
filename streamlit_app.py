import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page config
st.set_page_config(
    page_title="AdMetrics Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    /* Main background */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header styling */
    .title {
        color: #ff6952;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0;
    }
    
    .subtitle {
        color: #64748b;
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 4px solid #ff6952;
        margin: 1rem 0;
    }
    
    /* Platform tabs */
    .platform-tab {
        background: #ff6952;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 0.25rem;
        border: none;
        font-weight: 600;
    }
    
    /* Summary boxes */
    .summary-box {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-top: 4px solid #ff6952;
    }
    
    /* Data source indicators */
    .api-data { background: #ecfdf5; border-left: 3px solid #10b981; }
    .manual-data { background: #f8fafc; border-left: 3px solid #64748b; }
    .calculated-data { background: #ede9fe; border-left: 3px solid #8b5cf6; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_platform' not in st.session_state:
    st.session_state.selected_platform = 'Facebook'
if 'data_source' not in st.session_state:
    st.session_state.data_source = 'sample'  # 'sample', 'api', 'manual'

# Sample data for different platforms
@st.cache_data
def get_sample_data():
    """Generate sample data for all platforms"""
    platforms = {
        'Facebook': {
            'Week 1': {'spend': 5000, 'impressions': 250000, 'clicks': 2500, 'conversions': 125, 'revenue': 6250},
            'Week 2': {'spend': 6000, 'impressions': 300000, 'clicks': 3000, 'conversions': 150, 'revenue': 7500},
            'Week 3': {'spend': 5500, 'impressions': 280000, 'clicks': 2800, 'conversions': 140, 'revenue': 7000},
            'Week 4': {'spend': 6500, 'impressions': 320000, 'clicks': 3200, 'conversions': 160, 'revenue': 8000},
        },
        'Google Ads': {
            'Week 1': {'spend': 8000, 'impressions': 400000, 'clicks': 4000, 'conversions': 200, 'revenue': 10000},
            'Week 2': {'spend': 7500, 'impressions': 380000, 'clicks': 3800, 'conversions': 190, 'revenue': 9500},
            'Week 3': {'spend': 8200, 'impressions': 410000, 'clicks': 4100, 'conversions': 205, 'revenue': 10250},
            'Week 4': {'spend': 8800, 'impressions': 440000, 'clicks': 4400, 'conversions': 220, 'revenue': 11000},
        },
        'LinkedIn': {
            'Week 1': {'spend': 2000, 'impressions': 80000, 'clicks': 800, 'conversions': 40, 'revenue': 4000},
            'Week 2': {'spend': 2200, 'impressions': 88000, 'clicks': 880, 'conversions': 44, 'revenue': 4400},
            'Week 3': {'spend': 2100, 'impressions': 84000, 'clicks': 840, 'conversions': 42, 'revenue': 4200},
            'Week 4': {'spend': 2300, 'impressions': 92000, 'clicks': 920, 'conversions': 46, 'revenue': 4600},
        },
        'TikTok': {
            'Week 1': {'spend': 3000, 'impressions': 500000, 'clicks': 5000, 'conversions': 100, 'revenue': 5000},
            'Week 2': {'spend': 3500, 'impressions': 550000, 'clicks': 5500, 'conversions': 110, 'revenue': 5500},
            'Week 3': {'spend': 3200, 'impressions': 520000, 'clicks': 5200, 'conversions': 104, 'revenue': 5200},
            'Week 4': {'spend': 3800, 'impressions': 580000, 'clicks': 5800, 'conversions': 116, 'revenue': 5800},
        }
    }
    return platforms

def calculate_metrics(data):
    """Calculate derived metrics from raw data"""
    metrics = {}
    for week, week_data in data.items():
        spend = week_data['spend']
        impressions = week_data['impressions']
        clicks = week_data['clicks']
        conversions = week_data['conversions']
        revenue = week_data['revenue']
        
        metrics[week] = {
            'spend': spend,
            'impressions': impressions,
            'clicks': clicks,
            'conversions': conversions,
            'revenue': revenue,
            'ctr': (clicks / impressions * 100) if impressions > 0 else 0,
            'cpm': (spend / impressions * 1000) if impressions > 0 else 0,
            'cpc': (spend / clicks) if clicks > 0 else 0,
            'conversion_rate': (conversions / clicks * 100) if clicks > 0 else 0,
            'roas': (revenue / spend) if spend > 0 else 0,
            'cost_per_conversion': (spend / conversions) if conversions > 0 else 0,
        }
    return metrics

def create_metrics_table(data):
    """Create a beautiful metrics table"""
    metrics_data = calculate_metrics(data)
    
    # Define metrics with their properties
    metric_definitions = [
        {'name': 'Spend', 'key': 'spend', 'format': 'currency', 'type': 'raw'},
        {'name': 'Impressions', 'key': 'impressions', 'format': 'number', 'type': 'raw'},
        {'name': 'Clicks', 'key': 'clicks', 'format': 'number', 'type': 'raw'},
        {'name': 'Conversions', 'key': 'conversions', 'format': 'number', 'type': 'raw'},
        {'name': 'Revenue', 'key': 'revenue', 'format': 'currency', 'type': 'raw'},
        {'name': 'CTR (%)', 'key': 'ctr', 'format': 'percentage', 'type': 'calculated'},
        {'name': 'CPM', 'key': 'cpm', 'format': 'currency', 'type': 'calculated'},
        {'name': 'CPC', 'key': 'cpc', 'format': 'currency', 'type': 'calculated'},
        {'name': 'Conversion Rate (%)', 'key': 'conversion_rate', 'format': 'percentage', 'type': 'calculated'},
        {'name': 'ROAS', 'key': 'roas', 'format': 'ratio', 'type': 'calculated'},
        {'name': 'Cost per Conversion', 'key': 'cost_per_conversion', 'format': 'currency', 'type': 'calculated'},
    ]
    
    # Build DataFrame
    table_data = []
    for metric in metric_definitions:
        row = {'Metric': metric['name'], 'Type': metric['type']}
        for week in ['Week 1', 'Week 2', 'Week 3', 'Week 4']:
            value = metrics_data[week][metric['key']]
            if metric['format'] == 'currency':
                row[week] = f"${value:,.2f}"
            elif metric['format'] == 'percentage':
                row[week] = f"{value:.2f}%"
            elif metric['format'] == 'ratio':
                row[week] = f"{value:.2f}x"
            elif metric['format'] == 'number':
                row[week] = f"{int(value):,}"
            else:
                row[week] = f"{value:.2f}"
        table_data.append(row)
    
    return pd.DataFrame(table_data)

def create_performance_chart(data):
    """Create a performance trend chart"""
    metrics_data = calculate_metrics(data)
    
    weeks = list(metrics_data.keys())
    spend = [metrics_data[week]['spend'] for week in weeks]
    revenue = [metrics_data[week]['revenue'] for week in weeks]
    roas = [metrics_data[week]['roas'] for week in weeks]
    
    fig = go.Figure()
    
    # Add spend line
    fig.add_trace(go.Scatter(
        x=weeks, y=spend,
        mode='lines+markers',
        name='Spend',
        line=dict(color='#ff6952', width=3),
        marker=dict(size=8)
    ))
    
    # Add revenue line  
    fig.add_trace(go.Scatter(
        x=weeks, y=revenue,
        mode='lines+markers',
        name='Revenue',
        line=dict(color='#10b981', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title=f"{st.session_state.selected_platform} - Spend vs Revenue Trend",
        xaxis_title="Week",
        yaxis_title="Amount ($)",
        template="plotly_white",
        height=400,
        showlegend=True
    )
    
    return fig

# Main App
def main():
    # Header
    st.markdown('<h1 class="title">🚀 AdMetrics Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Track and optimize your advertising performance across all platforms</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Dashboard Controls")
        
        # Platform selector
        platforms = ['Facebook', 'Google Ads', 'LinkedIn', 'TikTok']
        selected_platform = st.selectbox(
            "📊 Select Platform:",
            platforms,
            index=platforms.index(st.session_state.selected_platform)
        )
        st.session_state.selected_platform = selected_platform
        
        st.divider()
        
        # Data source options
        st.subheader("📂 Data Source")
        data_source = st.radio(
            "Choose data source:",
            ['Sample Data', 'API Connection', 'Manual Input'],
            index=['Sample Data', 'API Connection', 'Manual Input'].index(
                'Sample Data' if st.session_state.data_source == 'sample' else
                'API Connection' if st.session_state.data_source == 'api' else 'Manual Input'
            )
        )
        
        if data_source == 'Sample Data':
            st.session_state.data_source = 'sample'
        elif data_source == 'API Connection':
            st.session_state.data_source = 'api'
            st.info("📡 API integration coming soon!")
        else:
            st.session_state.data_source = 'manual'
            st.info("✏️ Manual input mode enabled")
        
        st.divider()
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        if st.button("🔄 Refresh Data", type="primary"):
            st.cache_data.clear()
            st.rerun()
        
        if st.button("📥 Export CSV"):
            st.success("📄 Export functionality ready!")
        
        if st.button("📧 Schedule Report"):
            st.success("📬 Reporting scheduled!")
    
    # Main content
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Platform performance summary
        st.markdown(f"""
        <div class="summary-box">
            <h3>📈 {selected_platform} Performance Summary</h3>
            <p>Your {selected_platform} campaigns are showing strong performance this week. 
            Click on the metrics below to see detailed insights and recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Get data for selected platform
        sample_data = get_sample_data()
        platform_data = sample_data[selected_platform]
        
        # Performance chart
        st.subheader("📊 Performance Trends")
        chart = create_performance_chart(platform_data)
        st.plotly_chart(chart, use_container_width=True)
        
        # Metrics table
        st.subheader("📋 Detailed Metrics")
        
        # Data source indicator
        if st.session_state.data_source == 'sample':
            st.info("📊 Showing sample data. Connect your APIs for real-time data.")
        elif st.session_state.data_source == 'api':
            st.success("📡 Connected to live API data")
        else:
            st.warning("✏️ Manual input mode - edit values directly")
        
        # Create and display table
        metrics_df = create_metrics_table(platform_data)
        
        # Style the table based on data type
        def style_table(df):
            def highlight_rows(row):
                if row['Type'] == 'raw':
                    return ['background-color: #ecfdf5'] * len(row)
                elif row['Type'] == 'calculated':
                    return ['background-color: #ede9fe'] * len(row)
                else:
                    return [''] * len(row)
            
            return df.style.apply(highlight_rows, axis=1)
        
        styled_df = style_table(metrics_df)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Legend
        st.markdown("""
        **Legend:** 
        🟢 Raw Data (from APIs/input) | 🟣 Calculated Metrics (auto-computed) | 📊 = Sample Data
        """)
    
    with col2:
        # KPI Cards
        st.subheader("🎯 Key Metrics")
        
        # Calculate current week metrics
        current_week_data = calculate_metrics(platform_data)['Week 4']
        previous_week_data = calculate_metrics(platform_data)['Week 3']
        
        # Spend metric
        spend_change = ((current_week_data['spend'] - previous_week_data['spend']) / previous_week_data['spend']) * 100
        st.metric(
            "💰 Total Spend",
            f"${current_week_data['spend']:,.0f}",
            f"{spend_change:+.1f}% vs last week"
        )
        
        # ROAS metric
        roas_change = ((current_week_data['roas'] - previous_week_data['roas']) / previous_week_data['roas']) * 100
        st.metric(
            "📈 ROAS",
            f"{current_week_data['roas']:.2f}x",
            f"{roas_change:+.1f}% vs last week"
        )
        
        # CTR metric
        ctr_change = current_week_data['ctr'] - previous_week_data['ctr']
        st.metric(
            "🎯 CTR",
            f"{current_week_data['ctr']:.2f}%",
            f"{ctr_change:+.2f}% vs last week"
        )
        
        # Conversions metric
        conv_change = ((current_week_data['conversions'] - previous_week_data['conversions']) / previous_week_data['conversions']) * 100
        st.metric(
            "🏆 Conversions",
            f"{current_week_data['conversions']:,.0f}",
            f"{conv_change:+.1f}% vs last week"
        )
        
        st.divider()
        
        # Action items
        st.subheader("📝 Next Actions")
        st.markdown("""
        **Recommended Actions:**
        - ✅ Increase budget for top performers
        - 🎯 Optimize underperforming ads  
        - 📊 Test new creative variations
        - 🔍 Analyze audience segments
        - 📈 Scale successful campaigns
        """)
        
        # Quick insights
        st.subheader("💡 Quick Insights")
        if current_week_data['roas'] > 2.0:
            st.success("🎉 Excellent ROAS performance!")
        elif current_week_data['roas'] > 1.0:
            st.info("👍 Good ROAS, room for improvement")
        else:
            st.warning("⚠️ ROAS needs attention")
        
        if current_week_data['ctr'] > 2.0:
            st.success("🎯 Great click-through rate!")
        else:
            st.info("💡 Consider testing new ad creatives")

if __name__ == "__main__":
    main()
