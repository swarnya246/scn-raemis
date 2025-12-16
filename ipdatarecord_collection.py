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

def generate_charts(df, timestamp):
    """Generate visualizations"""
    plt.figure(figsize=(10, 6))
    plt.scatter(df_school_weekends['start_time'], df_school_weekends['tx_and_rx_mb'], alpha=0.5, s=6)
    plt.xlabel('Start Time')
    plt.ylabel('Transmitted and Recieved Megabytes')
    plt.title(f'Monthly Summary: {timestamp}')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/summary_{timestamp}.png', dpi=300)
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

        # Extract last month
        today = datetime.now()
        first_day_current_month = today.replace(day=1)
        first_day_last_month = (first_day_current_month - pd.Timedelta(days=1)).replace(day=1)
        df = df.loc[(df['start_time'] >= first_day_last_month.strftime('%Y-%m-%d'))
                    & (df['start_time'] < first_day_current_month.strftime('%Y-%m-%d'))]
        
        # Generate charts
        generate_charts(df, timestamp)
        
        print("Report generation complete")
        
    except Exception as e:
        print(f"Error: {e}")
        # Optional: Send error notification

if __name__ == '__main__':
    main()