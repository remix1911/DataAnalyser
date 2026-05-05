
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, Optional

class Visualizer:
    @staticmethod
    def recommend_chart(df: pd.DataFrame, x_col: str = None, y_col: str = None) -> str:
        if x_col is None or y_col is None:
            return 'bar'
        
        x_type = df[x_col].dtype
        y_type = df[y_col].dtype if y_col else None
        
        if x_type in [np.int64, np.float64]:
            if y_type in [np.int64, np.float64]:
                return 'scatter'
            return 'histogram'
        else:
            if y_type in [np.int64, np.float64]:
                return 'bar'
            return 'pie'

    @staticmethod
    def plot_line(df: pd.DataFrame, x_col: str, y_col: str, title: str = '') -> go.Figure:
        fig = px.line(df, x=x_col, y=y_col, title=title)
        return fig

    @staticmethod
    def plot_bar(df: pd.DataFrame, x_col: str, y_col: str, title: str = '') -> go.Figure:
        fig = px.bar(df, x=x_col, y=y_col, title=title)
        return fig

    @staticmethod
    def plot_pie(df: pd.DataFrame, values_col: str, names_col: str, title: str = '') -> go.Figure:
        fig = px.pie(df, values=values_col, names=names_col, title=title)
        return fig

    @staticmethod
    def plot_scatter(df: pd.DataFrame, x_col: str, y_col: str, title: str = '', color_col: str = None) -> go.Figure:
        if color_col:
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=title)
        else:
            fig = px.scatter(df, x=x_col, y=y_col, title=title)
        return fig

    @staticmethod
    def plot_heatmap(df: pd.DataFrame, title: str = '') -> go.Figure:
        corr = df.corr()
        fig = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale='Viridis'
        ))
        fig.update_layout(title=title)
        return fig

    @staticmethod
    def plot_histogram(df: pd.DataFrame, x_col: str, title: str = '') -> go.Figure:
        fig = px.histogram(df, x=x_col, title=title)
        return fig

    @staticmethod
    def plot_boxplot(df: pd.DataFrame, x_col: str, y_col: str, title: str = '') -> go.Figure:
        fig = px.box(df, x=x_col, y=y_col, title=title)
        return fig

    @staticmethod
    def plot_dashboard(df: pd.DataFrame) -> go.Figure:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return go.Figure()
        
        fig = make_subplots(rows=2, cols=2, subplot_titles=['数据分布', '相关性热力图'])
        
        first_col = numeric_cols[0]
        fig.add_trace(go.Histogram(x=df[first_col], name=first_col), row=1, col=1)
        
        if len(numeric_cols) >= 2:
            fig.add_trace(go.Scatter(x=df[numeric_cols[0]], y=df[numeric_cols[1]], 
                                   mode='markers', name=f'{numeric_cols[0]} vs {numeric_cols[1]}'), 
                         row=1, col=2)
        
        corr = df[numeric_cols].corr()
        fig.add_trace(go.Heatmap(z=corr.values, x=corr.columns, y=corr.columns), row=2, col=1)
        
        fig.update_layout(height=600, width=800, title_text="数据仪表盘")
        return fig

    @staticmethod
    def plot_trend(df: pd.DataFrame, date_col: str, value_col: str, title: str = '') -> go.Figure:
        fig = px.line(df, x=date_col, y=value_col, title=title)
        if 'rolling_mean' in df.columns:
            fig.add_trace(go.Scatter(x=df[date_col], y=df['rolling_mean'], 
                                   mode='lines', name='7日移动平均', line=dict(color='red', dash='dash')))
        return fig

    @staticmethod
    def plot_clusters(df: pd.DataFrame, x_col: str, y_col: str, cluster_col: str = 'cluster', title: str = '') -> go.Figure:
        fig = px.scatter(df, x=x_col, y=y_col, color=cluster_col, title=title)
        return fig

    @staticmethod
    def generate_plot(df: pd.DataFrame, chart_type: str, **kwargs) -> go.Figure:
        title = kwargs.get('title', '')
        
        if chart_type == 'line':
            return Visualizer.plot_line(df, kwargs['x'], kwargs['y'], title)
        elif chart_type == 'bar':
            return Visualizer.plot_bar(df, kwargs['x'], kwargs['y'], title)
        elif chart_type == 'pie':
            return Visualizer.plot_pie(df, kwargs['values'], kwargs['names'], title)
        elif chart_type == 'scatter':
            return Visualizer.plot_scatter(df, kwargs['x'], kwargs['y'], title, kwargs.get('color'))
        elif chart_type == 'heatmap':
            return Visualizer.plot_heatmap(df, title)
        elif chart_type == 'histogram':
            return Visualizer.plot_histogram(df, kwargs['x'], title)
        elif chart_type == 'boxplot':
            return Visualizer.plot_boxplot(df, kwargs['x'], kwargs['y'], title)
        elif chart_type == 'dashboard':
            return Visualizer.plot_dashboard(df)
        elif chart_type == 'trend':
            return Visualizer.plot_trend(df, kwargs['x'], kwargs['y'], title)
        elif chart_type == 'cluster':
            return Visualizer.plot_clusters(df, kwargs['x'], kwargs['y'], kwargs.get('cluster', 'cluster'), title)
        
        return go.Figure()
