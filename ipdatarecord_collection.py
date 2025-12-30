import requests
import urllib3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
urllib3.disable_warnings()

# Configuration
OUTPUT_DIR = '~/raemis_reports'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_data():
    """Fetch data from API"""
    response = requests.get(
        'https://172.31.86.4/api/ip_data_record',
        auth=('raemis', 'password'),
        verify=False,
        timeout=30
    )
    response.raise_for_status()
    return response.json()

def save_csv(data, timestamp):
    """Save raw data as CSV"""
    df = pd.DataFrame(data)
    filename = f'{OUTPUT_DIR}/data_{timestamp}.csv'
    df.to_csv(filename, index=False)
    print(f"CSV saved: {filename}")
    return df

def save_charts(df, plot_title, file_title, timestamp):
    """Save specific charts"""
    plt.figure(figsize=(10, 6))
    plt.plot(df['hour'], df['mean'])
    plt.xlabel('Start Time')
    plt.ylabel('Transmitted and Recieved Megabytes')
    plt.title(f'Average Usage by Hour of {plot_title}')
    plt.xticks(range(0, 24), [f'{h:02d}:00' for h in range(24)], rotation=45, ha='right')
    plt.grid(False)
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/tx_rx_cumulative_avg_{file_title}_{timestamp}.png', dpi=300)
    plt.close()
    
    plt.figure(figsize=(10, 6))
    plt.bar(df['hour'], df['sum'])
    plt.xlabel('Start Time')
    plt.ylabel('Transmitted and Recieved Megabytes')
    plt.title(f'Sum of Usage by Hour of {plot_title}')
    plt.xticks(range(0, 24), [f'{h:02d}:00' for h in range(24)], rotation=45, ha='right')
    plt.grid(False)
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/tx_rx_cumulative_sum_{file_title}_{timestamp}.png', dpi=300)
    plt.close()

def generate_charts(df, timestamp):
    """Generate visualizations"""

    # Separate school year and summer break and weekdays from weekends
    df_school_year = df.loc[((df['start_time'] >= '2024-9-03') & (df['start_time'] < '2025-6-18'))
                     | (df['start_time'] >= '2025-9-03')]
    df_summer_break = df.loc[(df['start_time'] < '2024-9-03') |
                 ((df['start_time'] >= '2025-6-18')
                 & (df['start_time'] < '2025-9-03'))]
    
    df_school_weekdays = df_school_year.loc[df_school_year['start_time'].dt.dayofweek < 5]
    df_school_weekdays['hour'] = df_school_weekdays['start_time'].dt.hour
    school_weekday_hourly = df_school_weekdays.groupby('hour')['tx_and_rx_mb'].agg(['mean', 'sum', 'count', 'std'])
    school_weekday_hourly = school_weekday_hourly.reset_index()
    save_charts(school_weekday_hourly, "School Weekday", "school_weekday", timestamp)
    
    df_school_weekends = df_school_year.loc[df_school_year['start_time'].dt.dayofweek >= 5]
    df_school_weekends['hour'] = df_school_weekends['start_time'].dt.hour
    school_weekends_hourly = df_school_weekends.groupby('hour')['tx_and_rx_mb'].agg(['mean', 'sum', 'count', 'std'])
    school_weekends_hourly = school_weekends_hourly.reset_index()
    save_charts(school_weekends_hourly, "School Weekend", "school_weekend", timestamp)

    df_summer_weekdays = df_summer_break.loc[df_summer_break['start_time'].dt.dayofweek < 5]
    df_summer_weekdays['hour'] = df_summer_weekdays['start_time'].dt.hour
    summer_weekday_hourly = df_summer_weekdays.groupby('hour')['tx_and_rx_mb'].agg(['mean', 'sum', 'count', 'std'])
    summer_weekday_hourly = summer_weekday_hourly.reset_index()
    save_charts(summer_weekday_hourly, "Summer Weekday", "summer_weekday", timestamp)

    df_summer_weekends = df_summer_break.loc[df_summer_break['start_time'].dt.dayofweek >= 5]
    df_summer_weekends['hour'] = df_summer_weekends['start_time'].dt.hour
    summer_weekends_hourly = df_summer_weekends.groupby('hour')['tx_and_rx_mb'].agg(['mean', 'sum', 'count', 'std'])
    summer_weekends_hourly = summer_weekends_hourly.reset_index()
    save_charts(summer_weekends_hourly, "Summer Weekend", "summer_weekend", timestamp)

    # Extract last month's summary
    today = datetime.now()
    first_day_current_month = today.replace(day=1)
    first_day_last_month = (first_day_current_month - pd.Timedelta(days=1)).replace(day=1)
    df = df.loc[(df['start_time'] >= first_day_last_month.strftime('%Y-%m-%d'))
                & (df['start_time'] < first_day_current_month.strftime('%Y-%m-%d'))]
    
    plt.figure(figsize=(10, 6))
    plt.scatter(df['start_time'], df['tx_and_rx_mb'], alpha=0.5, s=6)
    plt.xlabel('Start Time')
    plt.ylabel('Transmitted and Recieved Megabytes')
    plt.title(f'Monthly Summary: {timestamp}')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/tx_rx_summary_{timestamp}.png', dpi=300)
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.scatter(df['start_time'], df['tx_mb'], alpha=0.5, s=6)
    plt.xlabel('Start Time')
    plt.ylabel('Transmitted Megabytes')
    plt.title(f'Monthly Summary: {timestamp}')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/tx_summary_{timestamp}.png', dpi=300)
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.scatter(df['start_time'], df['rx_mb'], alpha=0.5, s=6)
    plt.xlabel('Start Time')
    plt.ylabel('Recieved Megabytes')
    plt.title(f'Monthly Summary: {timestamp}')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/rx_summary_{timestamp}.png', dpi=300)
    plt.close()
    
    print("Charts generated")

def main():
    """Main execution"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    try:
        print(f"Fetching data at {timestamp}...")
        data = fetch_data()
        
        # Save CSV
        df = save_csv(data, timestamp)
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['tx_and_rx_mb'] = (df['tx_total_packets'] + df['rx_total_packets']) * 1500/1000000
        df['tx_mb'] = df['tx_total_packets'] * 1500/1000000
        df['rx_mb'] = df['rx_total_packets'] * 1500/1000000        
        
        # Generate charts
        generate_charts(df, timestamp)
        
        print("Report generation complete")
        
    except Exception as e:
        print(f"Error: {e}")
        # Optional: Send error notification

if __name__ == '__main__':
    main()