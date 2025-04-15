from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
#import matplotlib
#matplotlib.use('Agg')
#import matplotlib.pyplot as plt

import io
import base64
from datetime import datetime
import os
import sys
import requests
import json
import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.dates import DateFormatter, MonthLocator, WeekdayLocator, DayLocator

app = Flask(__name__)

def parse_logs(file_path):
    logs = []
    with open(file_path, 'r') as file:
        for line in file:
            try:
                # Split the line into timestamp, size, and filename
                parts = line.strip().split(None, 3)
                if len(parts) != 4:
                    print(f"Skipping line due to incorrect parts: {line.strip()}")
                    continue
                
                timestamp = parts[0] + ' ' + parts[1]
                size = parts[2]
                filename = parts[3]
                
                # Extract UUID and the rest
                filename_parts = filename.split('cai_')
                if len(filename_parts) != 2:
                    print(f"Skipping line due to incorrect filename format: {filename}")
                    continue
                
                # Parse the components after cai_
                components = filename_parts[1].split('_')
                if len(components) < 7:
                    print(f"Skipping line due to insufficient components: {components}")
                    continue
                
                # Components: [date, time, username, system, version, ip]
                username = components[2]  # root
                system = components[3].lower()  # linux
                version = '_'.join(components[4:-1])  # Join all version components
                
                # Process system and version to correctly identify Windows systems
                if 'microsoft' in system or 'microsoft' in version.lower() or 'wsl' in version.lower():
                    system = 'windows'
                
                # Get IP from the last component (remove .jsonl)
                ip = components[-1].replace('.jsonl', '')
                
                logs.append([timestamp, size, ip, system, username])
                print(f"Successfully parsed: {[timestamp, size, ip, system, username]}")
            
            except Exception as e:
                print(f"Error parsing line: {line.strip()}")
                print(f"Error details: {str(e)}")
                continue
    
    if not logs:
        print("No logs were successfully parsed!")
    else:
        print(f"Successfully parsed {len(logs)} log entries")
    
    return logs

def get_ip_location(ip):
    try:
        response = DbIpCity.get(ip, api_key='free')
        return response.latitude, response.longitude
    except:
        return None, None

def create_plots(logs):
    if not logs:
        return None, None, None, None
        
    df = pd.DataFrame(logs, columns=['timestamp', 'size', 'ip_address', 'system', 'username'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    plots = {}
    
    # Time series plot
    plt.figure(figsize=(12, 6))
    df.set_index('timestamp').resample('D').size().plot(kind='bar')
    plt.title('Number of Logs by Day')
    plt.xlabel('Date')
    plt.ylabel('Number of Logs')
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plots['time_series'] = base64.b64encode(buf.getvalue()).decode()
    plt.close()

    # System distribution
    plt.figure(figsize=(10, 6))
    system_map = {
        'linux': 'Linux', 
        'darwin': 'Darwin', 
        'windows': 'Windows',
        'microsoft': 'Windows',  # Handle legacy naming
        'wsl': 'Windows'        # Handle WSL explicitly
    }
    df['system_grouped'] = df['system'].map(system_map).fillna('Other')
    system_counts = df['system_grouped'].value_counts()
    system_counts.plot(kind='bar')
    plt.title('Total Number of Logs per System')
    plt.xlabel('System')
    plt.ylabel('Number of Logs')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plots['systems'] = base64.b64encode(buf.getvalue()).decode()
    plt.close()

    # User activity
    plt.figure(figsize=(12, 6))
    user_counts = df['username'].value_counts().head(10)
    user_counts.plot(kind='bar')
    plt.title('Top 10 Most Active Users')
    plt.xlabel('Username')
    plt.ylabel('Number of Logs')
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plots['users'] = base64.b64encode(buf.getvalue()).decode()
    plt.close()

    # Create map
    m = folium.Map(location=[0, 0], zoom_start=2)
    
    # Add markers for each unique IP
    for ip in df['ip_address'].unique():
        lat, lon = get_ip_location(ip)
        if lat and lon:
            folium.Marker(
                [lat, lon],
                popup=f'IP: {ip}<br>Count: {len(df[df["ip_address"] == ip])}',
            ).add_to(m)
    
    plots['map'] = m._repr_html_()
    
    return plots

def create_plot_base64(plt_func):
    plt.figure(figsize=(12, 6))
    plt_func()
    plt.tight_layout()
    
    # Create a BytesIO buffer for the image
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    
    # Encode the image to base64 string
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

def plot_logs_by_day(df):
    daily_counts = df.set_index('timestamp').resample('D').size()
    daily_counts.index = daily_counts.index.strftime('%Y-%m-%d')  # Format the index to 'yyyy-mm-dd'
    
    # Plot bar chart for daily counts
    ax = daily_counts.plot(kind='bar', color='skyblue', label='Daily Count')
    
    # Plot line chart for cumulative counts
    cumulative_counts = daily_counts.cumsum()
    cumulative_counts.plot(kind='line', color='orange', secondary_y=True, ax=ax, label='Cumulative Count')
    
    # Add vertical red line on 2025-04-08
    if '2025-04-08' in daily_counts.index:
        red_line_index = daily_counts.index.get_loc('2025-04-08')
        ax.axvline(x=red_line_index, color='red', linestyle='--', label='Public Release v0.3.11')
        
        # Add grey-ish background to all elements prior to the red line
        ax.axvspan(0, red_line_index, color='grey', alpha=0.3)
    
    # Add vertical yellow line on 2025-04-01
    if '2025-04-01' in daily_counts.index:
        yellow_line_index = daily_counts.index.get_loc('2025-04-01')
        ax.axvline(x=yellow_line_index, color='yellow', linestyle='--', label='Professional Bug Bounty Test')
    
    # Set titles and labels
    ax.set_title('Number of Logs by Day')
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Logs')
    ax.right_ax.set_ylabel('Cumulative Count')
    ax.set_xticklabels(daily_counts.index, rotation=45)
    
    # Add legends
    ax.legend(loc='upper left')
    ax.right_ax.legend(loc='upper right')

def plot_logs_by_system(df):
    system_map = {'linux': 'Linux', 'darwin': 'Darwin', 'microsoft': 'Windows'}
    df['system_grouped'] = df['system'].map(system_map)
    system_counts = df['system_grouped'].value_counts()
    system_counts.plot(kind='bar')
    plt.title('Total Number of Logs per System')
    plt.xlabel('System')
    plt.ylabel('Number of Logs')

def plot_active_users(df):
    user_counts = df['username'].value_counts().head(20)
    user_counts.plot(kind='bar')
    plt.title('Top 10 Most Active Users')
    plt.xlabel('Username')
    plt.ylabel('Number of Logs')
    plt.xticks(rotation=45)

def get_overall_stats():
    """Fetch overall download statistics for cai-framework"""
    url = "https://pypistats.org/api/packages/cai-framework/overall"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching overall stats: {response.status_code}")
        return None

def get_system_stats():
    """Fetch system-specific download statistics for cai-framework"""
    url = "https://pypistats.org/api/packages/cai-framework/system"
    response = requests.get(url) 
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching system stats: {response.status_code}")
        return None

def create_pypi_plot():
    # Get the data
    overall_stats = get_overall_stats()
    system_stats = get_system_stats()
    
    if not overall_stats or not system_stats:
        print("Error: Could not fetch PyPI statistics")
        return None, None
    
    # Create a figure with custom layout
    plt.figure(figsize=(15, 8))
    
    # Convert data to DataFrames
    df_overall = pd.DataFrame(overall_stats['data'])
    df_system = pd.DataFrame(system_stats['data'])
    
    # Filter for downloads without mirrors (matches website reporting)
    df_overall_no_mirrors = df_overall[df_overall['category'] == 'without_mirrors']
    without_mirrors_total = df_overall_no_mirrors['downloads'].sum()
    
    # Process the data
    daily_downloads = df_overall_no_mirrors.groupby('date')['downloads'].sum().reset_index()
    daily_downloads['date'] = pd.to_datetime(daily_downloads['date'])
    # Add cumulative downloads
    daily_downloads['cumulative_downloads'] = daily_downloads['downloads'].cumsum()
    
    # Get release date (first date in the dataset)
    release_date = daily_downloads['date'].min()
    
    # Calculate system percentages for each day
    system_pivot = df_system.pivot(index='date', columns='category', values='downloads')
    system_pivot.index = pd.to_datetime(system_pivot.index)
    system_pivot = system_pivot.fillna(0)
    
    # Keep track of the total downloads per system for the legend
    system_totals = system_pivot.sum()
    
    # Create main plot with two y-axes
    ax1 = plt.subplot(111)
    ax2 = ax1.twinx()  # Create a second y-axis sharing the same x-axis
    
    # Plot total cumulative downloads on the left axis
    ax1.plot(daily_downloads['date'], daily_downloads['cumulative_downloads'], 
               linewidth=3, color='black', label='Total Downloads (without mirrors)')
    
    # Define color mapping for systems
    color_map = {
        'Darwin': '#1E88E5',  # Blue
        'Linux': '#FB8C00',   # Orange
        'Windows': '#43A047',  # Green
        'null': '#E53935'     # Red
    }
    
    # Plot system distribution on the right axis
    bottom = np.zeros(len(system_pivot))
    
    # Ensure specific order of systems
    desired_order = ['Darwin', 'Linux', 'Windows', 'null']
    for col in desired_order:
        if col in system_pivot.columns:
            ax2.bar(system_pivot.index, system_pivot[col], 
                      bottom=bottom, label=col, color=color_map[col], 
                      alpha=0.5, width=0.8)
            bottom += system_pivot[col]
    
    # Add release date annotation
    ax1.axvline(x=release_date, color='#E53935', linestyle='--', alpha=0.7)
    ax1.annotate('Release Date', 
                xy=(release_date, ax1.get_ylim()[1]),
                xytext=(10, 10), textcoords='offset points',
                color='#E53935', fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec='#E53935', alpha=0.8))
    
    # Set the x-ticks to be at each date in the dataset
    ax1.set_xticks(system_pivot.index)
    ax1.set_xticklabels([date.strftime('%Y-%m-%d') for date in system_pivot.index], 
                       rotation=45, fontsize=10, ha='right')
    
    # Add padding between x-axis and the date labels
    ax1.tick_params(axis='x', which='major', pad=10)
    
    ax1.set_title('CAI Framework Download Statistics', fontsize=14, pad=20)
    ax1.set_ylabel('Total Cumulative Downloads', fontsize=14, color='black')
    ax2.set_ylabel('Daily Downloads by System', fontsize=14, color='black')
    ax1.set_xlabel('Date', fontsize=14)
    
    # Set grid and tick parameters
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.tick_params(axis='y', colors='black')
    ax2.tick_params(axis='y', colors='black')
    
    # Add legend with combined information
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = [], []
    
    # Add bars to legend in the desired order with correct colors
    for col in desired_order:
        if col in system_pivot.columns:
            # Create a proxy artist with the correct color
            proxy = plt.Rectangle((0, 0), 1, 1, fc=color_map[col], alpha=0.5)
            handles2.append(proxy)
            # Calculate percentage of both system total and overall total
            system_percentage = (system_totals[col] / system_totals.sum()) * 100
            website_percentage = (system_totals[col] / without_mirrors_total) * 100
            labels2.append(f'{col} ({int(system_totals[col]):,} total, {system_percentage:.1f}% of system, {website_percentage:.1f}%)')
    
    # Create legend with updated colors
    ax1.legend(handles1 + handles2, labels1 + labels2, 
              title='Operating Systems',
              bbox_to_anchor=(1.05, 1), loc='upper left',
              fontsize=12, title_fontsize=14)
    
    plt.tight_layout()
    
    # Create a BytesIO buffer for the image
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    plt.close()
    
    # Encode the image to base64 string
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    # Prepare statistics for the template
    stats = {
        'total_downloads': without_mirrors_total,
        'latest_downloads': daily_downloads.iloc[-1]['downloads'] if not daily_downloads.empty else 0,
        'first_date': daily_downloads['date'].min().strftime('%Y-%m-%d') if not daily_downloads.empty else 'N/A',
        'last_date': daily_downloads['date'].max().strftime('%Y-%m-%d') if not daily_downloads.empty else 'N/A',
        'system_totals': {col: int(system_totals[col]) for col in system_totals.index if col in system_pivot.columns},
        'system_percentages': {col: (system_totals[col] / system_totals.sum()) * 100 
                              for col in system_totals.index if col in system_pivot.columns}
    }
    
    return f'data:image/png;base64,{image_base64}', stats

@app.route('/')
def index():
    # Parse logs
    logs = parse_logs('/tmp/logs.txt')
    if not logs:
        return "No logs were parsed. Please check if the file exists and contains valid log entries."
    
    df = pd.DataFrame(logs, columns=['timestamp', 'size', 'ip_address', 'system', 'username'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Generate plots
    plt.style.use('default')  # Use default style instead of seaborn
    logs_by_day = create_plot_base64(lambda: plot_logs_by_day(df))
    logs_by_system = create_plot_base64(lambda: plot_logs_by_system(df))
    active_users = create_plot_base64(lambda: plot_active_users(df))
    
    # Generate PyPI plot
    pypi_plot, pypi_stats = create_pypi_plot()
    
    return render_template('logs.html',
                         logs_by_day=logs_by_day,
                         logs_by_system=logs_by_system,
                         active_users=active_users,
                         pypi_plot=pypi_plot)

@app.route('/pypi-stats')
def pypi_stats():
    # Generate PyPI plot
    pypi_plot, stats = create_pypi_plot()
    
    return render_template('pypi_stats.html',
                          pypi_plot=pypi_plot,
                          stats=stats)

if __name__ == '__main__':
    # Ensure the log file exists
    if not os.path.exists('/tmp/logs.txt'):
        print("Error: /tmp/logs.txt not found!")
        exit(1)
    
    print("Starting web server on http://localhost:5004")
    app.run(host='0.0.0.0', port=5004, debug=True) 