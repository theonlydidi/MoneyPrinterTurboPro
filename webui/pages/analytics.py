import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

def render_analytics():
    st.header("📊 Advanced Analytics")
    st.markdown("Comprehensive insights and performance metrics for your video generation platform")
    
    # Create tabs for different analytics views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Performance Metrics", "🎬 Video Insights", "🤖 AI Analytics", "💰 Cost Analysis"])
    
    with tab1:
        render_performance_metrics()
    
    with tab2:
        render_video_insights()
    
    with tab3:
        render_ai_analytics()
    
    with tab4:
        render_cost_analysis()

def render_performance_metrics():
    st.subheader("📈 Performance Metrics Overview")
    
    # Key Performance Indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🚀 Success Rate",
            value="98.7%",
            delta="+1.2%",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="⚡ Avg. Processing Time",
            value="3.2 min",
            delta="-0.8 min",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="🎯 Quality Score",
            value="4.8/5.0",
            delta="+0.2",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="🔄 Uptime",
            value="99.9%",
            delta="+0.1%",
            delta_color="normal"
        )
    
    # Performance Trends Chart
    st.markdown("### 📊 Performance Trends (Last 30 Days)")
    
    # Generate sample performance data
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    success_rates = np.random.normal(98.5, 1.0, len(dates))
    processing_times = np.random.normal(3.2, 0.5, len(dates))
    quality_scores = np.random.normal(4.8, 0.2, len(dates))
    
    # Create performance trends chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=success_rates,
        mode='lines+markers',
        name='Success Rate (%)',
        line=dict(color='#00ff88', width=3),
        yaxis='y'
    ))
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=processing_times,
        mode='lines+markers',
        name='Processing Time (min)',
        line=dict(color='#ff6b6b', width=3),
        yaxis='y2'
    ))
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=quality_scores,
        mode='lines+markers',
        name='Quality Score',
        line=dict(color='#667eea', width=3),
        yaxis='y3'
    ))
    
    fig.update_layout(
        title="Performance Metrics Over Time",
        xaxis_title="Date",
        yaxis_title="Success Rate (%)",
        yaxis2=dict(title="Processing Time (min)", overlaying="y", side="right"),
        yaxis3=dict(title="Quality Score", overlaying="y", side="right", position=0.95),
        hovermode='x unified',
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance Insights
    st.markdown("### 💡 Performance Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**🚀 Success Rate Trend**")
        st.markdown("• **Current**: 98.7%")
        st.markdown("• **Target**: 99.0%")
        st.markdown("• **Improvement**: +1.2% this month")
        
        st.info("**⚡ Processing Time**")
        st.markdown("• **Current**: 3.2 min")
        st.markdown("• **Target**: <3.0 min")
        st.markdown("• **Improvement**: -0.8 min this month")
    
    with col2:
        st.info("**🎯 Quality Score**")
        st.markdown("• **Current**: 4.8/5.0")
        st.markdown("• **Target**: 4.9/5.0")
        st.markdown("• **Improvement**: +0.2 this month")
        
        st.info("**🔄 System Uptime**")
        st.markdown("• **Current**: 99.9%")
        st.markdown("• **Target**: 99.95%")
        st.markdown("• **Improvement**: +0.1% this month")

def render_video_insights():
    st.subheader("🎬 Video Generation Insights")
    
    # Video Generation Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📹 Total Videos",
            value="1,247",
            delta="+23 this week"
        )
    
    with col2:
        st.metric(
            label="🎨 HD Quality",
            value="89%",
            delta="+5%"
        )
    
    with col3:
        st.metric(
            label="⏱️ Avg Duration",
            value="2.8 min",
            delta="-0.3 min"
        )
    
    with col4:
        st.metric(
            label="💰 Cost per Video",
            value="$0.32",
            delta="-$0.05"
        )
    
    # Video Quality Distribution
    st.markdown("### 📊 Video Quality Distribution")
    
    quality_data = {
        "Quality": ["720p", "1080p", "1440p", "4K"],
        "Count": [125, 456, 234, 432],
        "Percentage": [10, 37, 19, 34]
    }
    
    df = pd.DataFrame(quality_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            values=df['Count'],
            names=df['Quality'],
            title="Video Quality Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            x=df['Quality'],
            y=df['Count'],
            title="Video Quality Count",
            color=df['Count'],
            color_continuous_scale='viridis'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Video Style Analysis
    st.markdown("### 🎭 Video Style Analysis")
    
    style_data = {
        "Style": ["Educational", "Professional", "Entertainment", "Corporate", "Creative"],
        "Count": [456, 389, 234, 123, 45],
        "Avg. Duration": [3.2, 2.8, 2.1, 4.5, 1.8],
        "Success Rate": [99.1, 98.7, 97.8, 99.5, 96.2]
    }
    
    style_df = pd.DataFrame(style_data)
    st.dataframe(style_df, use_container_width=True)

def render_ai_analytics():
    st.subheader("🤖 AI Model Performance Analytics")
    
    # AI Model Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🧠 Script Generation",
            value="99.2%",
            delta="+0.8%"
        )
    
    with col2:
        st.metric(
            label="🗣️ Voice Synthesis",
            value="98.7%",
            delta="+1.2%"
        )
    
    with col3:
        st.metric(
            label="🎵 Music Generation",
            value="96.5%",
            delta="+2.1%"
        )
    
    with col4:
        st.metric(
            label="🎨 Effects Processing",
            value="97.8%",
            delta="+1.5%"
        )
    
    # AI Model Comparison
    st.markdown("### 🏆 AI Model Performance Comparison")
    
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

def render_cost_analysis():
    st.subheader("💰 Cost Analysis & Optimization")
    
    # Cost Overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Cost",
            value="$312.45",
            delta="+$12.30"
        )
    
    with col2:
        st.metric(
            label="📊 Avg. Cost/Video",
            value="$0.32",
            delta="-$0.05"
        )
    
    with col3:
        st.metric(
            label="🎯 Cost Efficiency",
            value="+15%",
            delta="+3%"
        )
    
    with col4:
        st.metric(
            label="💡 Savings",
            value="$45.20",
            delta="+$8.50"
        )
    
    # Cost Breakdown
    st.markdown("### 📊 Cost Breakdown by Service")
    
    cost_data = {
        "Service": ["AI Script Generation", "Voice Synthesis", "Music Generation", "Video Processing", "Storage"],
        "Cost": [156.23, 89.45, 34.67, 23.89, 8.21],
        "Percentage": [50.1, 28.7, 11.1, 7.7, 2.6]
    }
    
    cost_df = pd.DataFrame(cost_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            values=cost_df['Cost'],
            names=cost_df['Service'],
            title="Cost Distribution by Service",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            x=cost_df['Service'],
            y=cost_df['Cost'],
            title="Cost by Service ($)",
            color=cost_df['Cost'],
            color_continuous_scale='viridis'
        )
        fig.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Cost Trends
    st.markdown("### 📈 Cost Trends Over Time")
    
    # Generate sample cost data
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    daily_costs = np.random.normal(10.5, 2.5, len(dates))  # Average $10.50 per day
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=daily_costs,
        mode='lines+markers',
        name='Daily Cost ($)',
        line=dict(color='#ff6b6b', width=3),
        marker=dict(size=6)
    ))
    
    # Add trend line
    z = np.polyfit(range(len(dates)), daily_costs, 1)
    p = np.poly1d(z)
    fig.add_trace(go.Scatter(
        x=dates,
        y=p(range(len(dates))),
        mode='lines',
        name='Trend Line',
        line=dict(color='#667eea', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title="Daily Cost Trends (Last 30 Days)",
        xaxis_title="Date",
        yaxis_title="Daily Cost ($)",
        hovermode='x unified',
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Cost Optimization Recommendations
    st.markdown("### 💡 Cost Optimization Recommendations")
    
    recommendations = [
        "🎯 **Use Claude for faster processing** - Save 15% on processing time",
        "💰 **Batch video generation** - Reduce per-video costs by 20%",
        "🎵 **Use royalty-free music** - Save $0.05 per video",
        "🎨 **Optimize video quality** - Balance quality vs. cost",
        "🔄 **Implement caching** - Reduce redundant API calls"
    ]
    
    for rec in recommendations:
        st.info(rec)
    
    # Export Options
    st.markdown("### 📥 Export Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📊 Export as CSV",
            data=cost_df.to_csv(index=False).encode('utf-8'),
            file_name=f"cost_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        st.download_button(
            label="📈 Export as Excel",
            data=cost_df.to_excel(index=False, engine='openpyxl').encode('utf-8'),
            file_name=f"cost_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Main function for testing
if __name__ == "__main__":
    render_analytics()
