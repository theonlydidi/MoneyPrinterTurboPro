import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

def render_dashboard():
    st.header("📊 Advanced Dashboard")
    st.markdown("Real-time analytics and performance metrics for MoneyPrinterTurboPro")
    
    # Create tabs for different dashboard views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🎬 Video Analytics", "🤖 AI Performance", "⚡ System Status"])
    
    with tab1:
        render_overview_tab()
    
    with tab2:
        render_video_analytics_tab()
    
    with tab3:
        render_ai_performance_tab()
    
    with tab4:
        render_system_status_tab()

def render_overview_tab():
    st.subheader("📈 Performance Overview")
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🎬 Total Videos Generated",
            value="1,247",
            delta="+23 this week",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="⏱️ Avg. Generation Time",
            value="3.2 min",
            delta="-0.8 min",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="💰 Total Cost",
            value="$312.45",
            delta="+$12.30",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="⭐ User Satisfaction",
            value="4.8/5.0",
            delta="+0.2",
            delta_color="normal"
        )
    
    # Charts Row
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 Video Generation Trends")
        
        # Generate sample data for the last 30 days
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        video_counts = np.random.poisson(15, len(dates))  # Average 15 videos per day
        cost_data = video_counts * np.random.uniform(0.2, 0.4)  # $0.20-$0.40 per video
        
        # Create trend chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=video_counts,
            mode='lines+markers',
            name='Videos Generated',
            line=dict(color='#667eea', width=3),
            marker=dict(size=6)
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=cost_data,
            mode='lines+markers',
            name='Daily Cost ($)',
            yaxis='y2',
            line=dict(color='#ff6b6b', width=3),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title="Daily Video Generation & Cost Trends",
            xaxis_title="Date",
            yaxis_title="Videos Generated",
            yaxis2=dict(title="Daily Cost ($)", overlaying="y", side="right"),
            hovermode='x unified',
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Quick Actions")
        
        if st.button("🚀 Generate New Video", type="primary", use_container_width=True):
            st.success("Redirecting to video generator...")
        
        if st.button("📊 View Analytics", use_container_width=True):
            st.info("Opening detailed analytics...")
        
        if st.button("⚙️ Settings", use_container_width=True):
            st.info("Opening settings...")
        
        st.markdown("---")
        
        st.markdown("### 📈 This Week's Stats")
        weekly_stats = {
            "Videos": "156",
            "Success Rate": "98.7%",
            "Avg. Quality": "4.9/5.0",
            "Cost Efficiency": "+12%"
        }
        
        for key, value in weekly_stats.items():
            st.metric(key, value)

def render_video_analytics_tab():
    st.subheader("🎬 Video Generation Analytics")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        time_range = st.selectbox(
            "⏰ Time Range",
            ["Last 7 days", "Last 30 days", "Last 90 days", "Last year", "All time"],
            index=1
        )
    
    with col2:
        video_quality = st.selectbox(
            "🎨 Quality Filter",
            ["All Qualities", "HD (720p)", "Full HD (1080p)", "2K (1440p)", "4K"],
            index=0
        )
    
    with col3:
        video_style = st.selectbox(
            "🎭 Style Filter",
            ["All Styles", "Professional", "Casual", "Educational", "Entertainment"],
            index=0
        )
    
    # Analytics Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Video Quality Distribution")
        
        # Sample quality data
        quality_data = {
            "720p": 15,
            "1080p": 45,
            "1440p": 25,
            "4K": 15
        }
        
        fig = px.pie(
            values=list(quality_data.values()),
            names=list(quality_data.keys()),
            title="Video Quality Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎭 Video Style Popularity")
        
        # Sample style data
        style_data = {
            "Professional": 35,
            "Educational": 28,
            "Entertainment": 22,
            "Casual": 15
        }
        
        fig = px.bar(
            x=list(style_data.keys()),
            y=list(style_data.values()),
            title="Video Style Popularity",
            color=list(style_data.values()),
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed Analytics Table
    st.markdown("### 📋 Recent Video Generation Details")
    
    # Sample video data
    video_data = {
        "Video ID": ["VID_001", "VID_002", "VID_003", "VID_004", "VID_005"],
        "Topic": ["Coffee Making Guide", "Productivity Tips", "Cooking Basics", "Tech Review", "Travel Guide"],
        "Duration": ["2:15", "3:42", "1:58", "4:12", "2:35"],
        "Quality": ["1080p", "4K", "720p", "1080p", "1440p"],
        "Style": ["Educational", "Professional", "Casual", "Professional", "Entertainment"],
        "Cost": ["$0.35", "$0.48", "$0.28", "$0.42", "$0.38"],
        "Status": ["✅ Complete", "✅ Complete", "✅ Complete", "✅ Complete", "✅ Complete"]
    }
    
    df = pd.DataFrame(video_data)
    st.dataframe(df, use_container_width=True)
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📥 Export as CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name=f"video_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 Export as CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=f"video_analytics_{datetime.now().strftime('%Y%m%d_%H%m%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            st.download_button(
                label="📊 Export as Excel",
                data=df.to_excel(index=False, engine='openpyxl').encode('utf-8'),
                file_name=f"video_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

def render_ai_performance_tab():
    st.subheader("🤖 AI Model Performance Analytics")
    
    # AI Model Performance Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🧠 Script Generation",
            value="99.2%",
            delta="+0.8%",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="🗣️ Voice Synthesis",
            value="98.7%",
            delta="+1.2%",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            label="🎵 Music Generation",
            value="96.5%",
            delta="+2.1%",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="🎨 Effects Processing",
            value="97.8%",
            delta="+1.5%",
            delta_color="normal"
        )
    
    # AI Model Comparison
    st.markdown("### 🏆 AI Model Performance Comparison")
    
    # Sample model performance data
    models_data = {
        "Model": ["GPT-4", "Claude", "Gemini", "Qwen", "Moonshot"],
        "Script Quality": [9.8, 9.6, 9.4, 9.2, 9.0],
        "Processing Speed": [8.5, 9.2, 8.8, 9.5, 8.0],
        "Cost Efficiency": [7.5, 8.8, 9.0, 8.5, 9.2],
        "Overall Score": [8.6, 9.2, 9.1, 9.1, 8.7]
    }
    
    df = pd.DataFrame(models_data)
    
    # Create radar chart
    fig = go.Figure()
    
    for _, row in df.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[row['Script Quality'], row['Processing Speed'], row['Cost Efficiency']],
            theta=['Script Quality', 'Processing Speed', 'Cost Efficiency'],
            fill='toself',
            name=row['Model']
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=True,
        title="AI Model Performance Comparison",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Model Usage Statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Model Usage Statistics")
        
        usage_data = {
            "Model": ["GPT-4", "Claude", "Gemini", "Qwen", "Moonshot"],
            "Usage Count": [456, 234, 189, 156, 98],
            "Success Rate": ["99.1%", "98.7%", "97.8%", "96.9%", "95.2%"],
            "Avg. Response Time": ["2.3s", "1.8s", "2.1s", "1.9s", "2.5s"]
        }
        
        usage_df = pd.DataFrame(usage_data)
        st.dataframe(usage_df, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Performance Insights")
        
        insights = [
            "🎯 **GPT-4** leads in script quality and reliability",
            "⚡ **Claude** excels in processing speed",
            "💰 **Gemini** offers best cost efficiency",
            "🔄 **Qwen** provides consistent performance",
            "🚀 **Moonshot** shows promising potential"
        ]
        
        for insight in insights:
            st.markdown(insight)

def render_system_status_tab():
    st.subheader("⚡ System Health & Performance")
    
    # System Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🖥️ CPU Usage",
            value="23%",
            delta="-5%",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            label="💾 Memory Usage",
            value="67%",
            delta="+3%",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            label="💿 Disk Usage",
            value="45%",
            delta="+2%",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="🌐 Network",
            value="12%",
            delta="-8%",
            delta_color="inverse"
        )
    
    # Real-time System Monitoring
    st.markdown("### 📊 Real-time System Monitoring")
    
    # Simulate real-time data
    time_points = pd.date_range(start=datetime.now() - timedelta(hours=6), end=datetime.now(), freq='5min')
    cpu_usage = np.random.normal(25, 8, len(time_points))
    memory_usage = np.random.normal(65, 5, len(time_points))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=time_points,
        y=cpu_usage,
        mode='lines',
        name='CPU Usage (%)',
        line=dict(color='#ff6b6b', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=time_points,
        y=memory_usage,
        mode='lines',
        name='Memory Usage (%)',
        line=dict(color='#4ecdc4', width=2)
    ))
    
    fig.update_layout(
        title="System Resource Usage (Last 6 Hours)",
        xaxis_title="Time",
        yaxis_title="Usage (%)",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Service Status
    st.markdown("### 🔧 Service Status")
    
    services = {
        "Service": ["Video Generator", "AI Service", "Voice Service", "Music Service", "Storage Service", "Database"],
        "Status": ["🟢 Online", "🟢 Online", "🟢 Online", "🟡 Warning", "🟢 Online", "🟢 Online"],
        "Response Time": ["45ms", "120ms", "89ms", "450ms", "23ms", "67ms"],
        "Uptime": ["99.98%", "99.95%", "99.97%", "99.89%", "99.99%", "99.96%"]
    }
    
    services_df = pd.DataFrame(services)
    st.dataframe(services_df, use_container_width=True)
    
    # System Alerts
    st.markdown("### 🚨 System Alerts")
    
    if st.button("🔄 Refresh Status", use_container_width=True):
        st.success("System status refreshed!")
    
    # Sample alerts
    alerts = [
        "⚠️ Music service response time increased (450ms)",
        "ℹ️ Database connection pool at 85% capacity",
        "✅ All critical services operational"
    ]
    
    for alert in alerts:
        if "⚠️" in alert:
            st.warning(alert)
        elif "ℹ️" in alert:
            st.info(alert)
        else:
            st.success(alert)

# Main function
if __name__ == "__main__":
    render_dashboard()
