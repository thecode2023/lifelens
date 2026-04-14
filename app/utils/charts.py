"""Chart and map utilities for LifeLens."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# LifeLens color palette
COLORS = {
    'bg': '#0a0f1a',
    'card': '#111827',
    'card_border': 'rgba(255,255,255,0.06)',
    'text': '#e5e7eb',
    'muted': '#6b7280',
    'accent': '#3b82f6',
    'accent_light': '#60a5fa',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'critical': '#dc2626',
    'cyan': '#06b6d4',
    'purple': '#8b5cf6',
}

TIER_COLORS = {
    'High': '#10b981',
    'Good': '#3b82f6',
    'Moderate': '#f59e0b',
    'Low': '#f97316',
    'Critical': '#ef4444',
}

EQUITY_COLORSCALE = [
    [0.0, '#dc2626'],
    [0.15, '#ef4444'],
    [0.3, '#f97316'],
    [0.45, '#f59e0b'],
    [0.6, '#3b82f6'],
    [0.75, '#2563eb'],
    [0.9, '#10b981'],
    [1.0, '#059669'],
]


def dark_layout(fig, title=None, height=None):
    """Apply dark theme to any plotly figure."""
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='"Inter", "SF Pro Display", system-ui, sans-serif', color=COLORS['text'], size=12),
        title=dict(
            text=title if title else '',
            font=dict(size=16, color=COLORS['text']),
            x=0.01, xanchor='left',
        ),
        height=height,
        margin=dict(l=40, r=40, t=60 if title else 20, b=40),
        hoverlabel=dict(
            bgcolor='#1f2937',
            bordercolor='rgba(255,255,255,0.1)',
            font=dict(size=12, color=COLORS['text']),
        ),
    )
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.04)', zeroline=False)
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.04)', zeroline=False)
    return fig


def choropleth_map(df, value_col='health_equity_index', title=None):
    """Create US county choropleth map."""
    fig = go.Figure(go.Choropleth(
        geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
        locations=df['county_fips'],
        z=df[value_col],
        colorscale=EQUITY_COLORSCALE,
        zmin=0, zmax=100,
        marker_line_width=0.2,
        marker_line_color='rgba(255,255,255,0.05)',
        colorbar=dict(
            title=dict(text='Score', font=dict(size=11, color=COLORS['muted'])),
            tickfont=dict(size=10, color=COLORS['muted']),
            thickness=12,
            len=0.5,
            bgcolor='rgba(0,0,0,0)',
            outlinewidth=0,
        ),
        hovertemplate=(
            '<b>%{customdata[0]}, %{customdata[1]}</b><br>'
            'Score: %{z:.1f}/100<br>'
            'Pop: %{customdata[2]:,.0f}'
            '<extra></extra>'
        ),
        customdata=df[['county_name', 'state_abbr', 'population']].values,
    ))

    fig.update_geos(
        scope='usa',
        bgcolor='rgba(0,0,0,0)',
        lakecolor='rgba(0,0,0,0)',
        landcolor='#151b2d',
        showlakes=False,
        showframe=False,
    )

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='"Inter", system-ui, sans-serif', color=COLORS['text']),
        height=520,
        margin=dict(l=0, r=0, t=10, b=0),
        geo=dict(projection_type='albers usa'),
    )
    return fig


def gauge_chart(value, title, max_val=100):
    """Create a gauge chart for index scores."""
    if value <= 25:
        bar_color = COLORS['critical']
    elif value <= 40:
        bar_color = COLORS['danger']
    elif value <= 60:
        bar_color = COLORS['warning']
    elif value <= 75:
        bar_color = COLORS['accent']
    else:
        bar_color = COLORS['success']

    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=value,
        number=dict(font=dict(size=32, color=COLORS['text']), suffix='', valueformat='.1f'),
        gauge=dict(
            axis=dict(
                range=[0, max_val],
                tickwidth=1,
                tickcolor='rgba(255,255,255,0.1)',
                dtick=25,
                tickfont=dict(size=9, color=COLORS['muted']),
            ),
            bar=dict(color=bar_color, thickness=0.75),
            bgcolor='rgba(255,255,255,0.03)',
            borderwidth=0,
            steps=[
                dict(range=[0, 25], color='rgba(220,38,38,0.08)'),
                dict(range=[25, 40], color='rgba(249,115,22,0.08)'),
                dict(range=[40, 60], color='rgba(245,158,11,0.08)'),
                dict(range=[60, 75], color='rgba(59,130,246,0.08)'),
                dict(range=[75, 100], color='rgba(16,185,129,0.08)'),
            ],
        ),
    ))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='"Inter", system-ui, sans-serif', color=COLORS['text']),
        height=200,
        margin=dict(l=20, r=20, t=30, b=0),
        annotations=[dict(
            text=title,
            x=0.5, y=-0.05,
            xref='paper', yref='paper',
            showarrow=False,
            font=dict(size=12, color=COLORS['muted']),
        )],
    )
    return fig


def bar_comparison(labels, values, national_values=None, title=None):
    """Horizontal bar chart comparing county to national average."""
    fig = go.Figure()

    if national_values is not None:
        fig.add_trace(go.Bar(
            y=labels, x=national_values, orientation='h',
            name='National Avg',
            marker_color='rgba(107,114,128,0.3)',
            marker_line_width=0,
        ))

    fig.add_trace(go.Bar(
        y=labels, x=values, orientation='h',
        name='County',
        marker_color=COLORS['accent'],
        marker_line_width=0,
    ))

    dark_layout(fig, title=title, height=max(280, len(labels) * 38 + 80))
    fig.update_layout(
        barmode='overlay',
        legend=dict(
            orientation='h', y=1.08, x=0.5, xanchor='center',
            bgcolor='rgba(0,0,0,0)',
            font=dict(size=11),
        ),
        yaxis=dict(tickfont=dict(size=11)),
    )
    return fig


def scatter_correlation(df, x_col, y_col, x_label, y_label, title=None):
    """Scatter plot with numpy trendline and R² value. No statsmodels needed."""
    clean = df[[x_col, y_col, 'county_name', 'state_abbr', 'population']].dropna()

    if len(clean) < 3:
        fig = go.Figure()
        dark_layout(fig, title='Not enough data', height=400)
        return fig

    corr = clean[x_col].corr(clean[y_col])
    r_squared = corr ** 2

    # Numpy trendline
    coeffs = np.polyfit(clean[x_col], clean[y_col], 1)
    x_range = np.linspace(clean[x_col].min(), clean[x_col].max(), 100)
    y_trend = np.polyval(coeffs, x_range)

    pop_normalized = clean['population'] / clean['population'].max() * 20 + 4

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=clean[x_col], y=clean[y_col],
        mode='markers',
        marker=dict(
            size=pop_normalized,
            color=clean['population'],
            colorscale='blues',
            showscale=False,
            opacity=0.7,
            line=dict(width=0.5, color='rgba(255,255,255,0.15)'),
        ),
        text=clean['county_name'] + ', ' + clean['state_abbr'],
        hovertemplate='<b>%{text}</b><br>' + x_label + ': %{x:,.1f}<br>' + y_label + ': %{y:.1f}<extra></extra>',
        name='Counties',
    ))

    fig.add_trace(go.Scatter(
        x=x_range, y=y_trend,
        mode='lines',
        line=dict(color=COLORS['accent_light'], width=2, dash='dash'),
        name=f'Trend (R² = {r_squared:.3f})',
        hoverinfo='skip',
    ))

    plot_title = title or f'{y_label} vs {x_label}'
    plot_title += f'   ·   R² = {r_squared:.3f}'

    dark_layout(fig, title=plot_title, height=460)
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
        showlegend=True,
        legend=dict(
            orientation='h', y=-0.15, x=0.5, xanchor='center',
            bgcolor='rgba(0,0,0,0)', font=dict(size=10),
        ),
    )
    return fig
