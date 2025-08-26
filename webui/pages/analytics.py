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
        yaxis=dict(title="Success Rate (%)", side="left"),
        yaxis2=dict(title="Processing Time (min)", side="right", overlaying="y"),
        yaxis3=dict(title="Quality Score", side="right", overlaying="y", position=0.95),
        hovermode='x unified',
        showlegend=True,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance Insights
    st.markdown("### 💡 Performance Insights")
    
    insights = [
        "📈 **Success Rate**: Consistently above 98% with steady improvement",
        "⚡ **Processing Time**: Reduced by 20% over the last month",
        "🎯 **Quality Score**: Maintained high quality with slight improvements",
        "🔄 **Uptime**: Excellent reliability with 99.9% availability"
    ]
    
    for insight in insights:
        st.markdown(insight)

def render_video_insights():
    st.subheader("🎬 Video Generation Insights")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        time_range = st.selectbox(
            "⏰ Time Range",
            ["Last 7 days", "Last 30 days", "Last 90 days", "Last year", "All time"],
            index=1
        )
    
    with col2:
        video_type = st.selectbox(
            "🎬 Video Type",
            ["All Types", "Business", "Educational", "Entertainment", "Marketing", "Social Media"],
            index=0
        )
    
    with col3:
        quality_filter = st.selectbox(
            "🎨 Quality Filter",
            ["All Qualities", "HD (720p)", "Full HD (1080p)", "2K (1440p)", "4K"],
            index=0
        )
    
    # Video Generation Statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Video Generation by Category")
        
        # Sample category data
        category_data = {
            "Business": 35,
            "Educational": 28,
            "Entertainment": 22,
            "Marketing": 10,
            "Social Media": 5
        }
        
        fig = px.pie(
            values=list(category_data.values()),
            names=list(category_data.keys()),
            title="Video Distribution by Category",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Video Generation Trends")
        
        # Generate sample trend data
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        video_counts = np.random.poisson(15, len(dates))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=video_counts,
            mode='lines+markers',
            name='Videos Generated',
            line=dict(color='#667eea', width=3),
            fill='tonexty'
        ))
        
        fig.update_layout(
            title="Daily Video Generation",
            xaxis_title="Date",
            yaxis_title="Number of Videos",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Video Quality Analysis
    st.markdown("### 🎨 Video Quality Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📺 Quality Distribution")
        
        quality_data = {
            "720p": 15,
            "1080p": 45,
            "1440p": 25,
            "4K": 15
        }
        
        fig = px.bar(
            x=list(quality_data.keys()),
            y=list(quality_data.values()),
            title="Video Quality Distribution",
            color=list(quality_data.values()),
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### ⏱️ Duration Analysis")
        
        duration_data = {
            "15-30s": 20,
            "30-60s": 35,
            "1-2min": 25,
            "2-5min": 15,
            "5+ min": 5
        }
        
        fig = px.pie(
            values=list(duration_data.values()),
            names=list(duration_data.keys()),
            title="Video Duration Distribution",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

def render_ai_analytics():
    st.subheader("🤖 AI Model Performance Analytics")
    
    # AI Model Performance Overview
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

def render_cost_analysis():
    st.subheader("💰 Cost Analysis & Optimization")
    
    # Cost Overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Cost",
            value="$312.45",
            delta="+$12.30",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="📊 Avg. Cost per Video",
            value="$0.25",
            delta="-$0.05",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="🎯 Cost Efficiency",
            value="+15%",
            delta="+3%",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="💡 Savings",
            value="$45.20",
            delta="+$8.50",
            delta_color="normal"
        )
    
    # Cost Trends Chart
    st.markdown("### 📈 Cost Trends Over Time")
    
    # Generate sample cost data
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    daily_costs = np.random.poisson(8, len(dates)) * 0.25  # Average $2 per day
    cumulative_costs = np.cumsum(daily_costs)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=daily_costs,
        mode='lines+markers',
        name='Daily Cost ($)',
        line=dict(color='#ff6b6b', width=3),
        yaxis='y'
    ))
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=cumulative_costs,
        mode='lines+markers',
        name='Cumulative Cost ($)',
        line=dict(color='#667eea', width=3),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title="Cost Analysis Over Time",
        xaxis_title="Date",
        yaxis=dict(title="Daily Cost ($)", side="left"),
        yaxis2=dict(title="Cumulative Cost ($)", side="right", overlaying="y"),
        hovermode='x unified',
        showlegend=True,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Cost Breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💸 Cost Breakdown by Service")
        
        cost_breakdown = {
            "AI Script Generation": 45,
            "Voice Synthesis": 25,
            "Music Generation": 15,
            "Video Processing": 10,
            "Storage & Delivery": 5
        }
        
        fig = px.pie(
            values=list(cost_breakdown.values()),
            names=list(cost_breakdown.keys()),
            title="Cost Distribution by Service",
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Cost Optimization Insights")
        
        insights = [
            "💰 **AI Script Generation** is the highest cost driver (45%)",
            "🗣️ **Voice Synthesis** costs can be optimized with bulk processing",
            "🎵 **Music Generation** shows good cost efficiency",
            "🎬 **Video Processing** costs are well-controlled",
            "💾 **Storage costs** are minimal and optimized"
        ]
        
        for insight in insights:
            st.markdown(insight)
    
    # Cost Optimization Recommendations
    st.markdown("### 💡 Cost Optimization Recommendations")
    
    recommendations = [
        "🚀 **Batch Processing**: Process multiple videos together to reduce per-video costs",
        "🤖 **Model Selection**: Use cost-efficient AI models for non-critical content",
        "🗣️ **Voice Optimization**: Choose standard voice options for cost-sensitive projects",
        "🎵 **Music Selection**: Use stock music for predictable costs",
        "📱 **Quality Settings**: Adjust resolution based on platform requirements"
    ]
    
    for recommendation in recommendations:
        st.markdown(recommendation)

# Main function
if __name__ == "__main__":
    render_analytics()
