"""
Demo script that creates realistic delays to showcase the alert system
"""
import pandas as pd
from datetime import datetime, timedelta
import random

from data_simulator import DeliveryDataSimulator
from eta_engine import ETAEngine
from llm_integration import LLMIntegration
from config import eta_config

def create_delayed_scenario():
    """Create a scenario with realistic delays"""
    
    print("🚚 Smart Delivery ETA Checker - DELAY SCENARIO DEMO")
    print("=" * 60)
    
    # Generate base simulation data
    simulator = DeliveryDataSimulator()
    stops_df, positions_df = simulator.generate_simulation_data(3)
    
    # Modify some planned ETAs to be more aggressive (creating delays)
    current_time = datetime.now()
    
    for idx, row in stops_df.iterrows():
        # Make some planned ETAs more aggressive (earlier than realistic)
        if row['sequence'] > 3:  # Later stops more likely to be delayed
            # Move planned ETA earlier by 10-30 minutes to create delays
            original_eta = datetime.fromisoformat(row['planned_eta'])
            aggressive_eta = original_eta - timedelta(minutes=random.randint(10, 30))
            stops_df.at[idx, 'planned_eta'] = aggressive_eta.isoformat()
    
    # Modify driver positions to be further from their next stops
    for idx, row in positions_df.iterrows():
        driver_stops = stops_df[stops_df['driver_id'] == row['driver_id']]
        if len(driver_stops) > 0:
            # Position driver further from first stop to create travel delays
            first_stop = driver_stops.iloc[0]
            # Add some distance to create realistic delays
            positions_df.at[idx, 'latitude'] = first_stop['latitude'] + random.uniform(-0.02, 0.02)
            positions_df.at[idx, 'longitude'] = first_stop['longitude'] + random.uniform(-0.02, 0.02)
    
    print(f"📊 Modified simulation data to create realistic delays")
    print(f"   • {len(stops_df)} delivery stops")
    print(f"   • {len(positions_df)} driver positions")
    print(f"   • Aggressive planned ETAs for later stops")
    
    # Calculate ETAs with the modified data
    engine = ETAEngine()
    eta_df = engine.calculate_all_etas(positions_df, stops_df)
    alerts_df = engine.generate_alerts(eta_df)
    
    print(f"\n🧮 ETA Calculation Results:")
    print(f"   ✓ Calculated ETAs for {len(eta_df)} stops")
    print(f"   ✓ Detected {len(alerts_df)} delayed deliveries")
    
    if len(alerts_df) > 0:
        print(f"   📊 Delay Statistics:")
        print(f"      • Average delay: {alerts_df['delay_minutes'].mean():.1f} minutes")
        print(f"      • Maximum delay: {alerts_df['delay_minutes'].max():.1f} minutes")
        print(f"      • Affected drivers: {alerts_df['driver_id'].nunique()}")
    
    # Generate LLM communications
    llm = LLMIntegration()
    communications = llm.generate_all_communications(eta_df, alerts_df)
    
    print(f"\n🤖 AI Communications Generated:")
    print(f"   ✓ Routing supervisor report")
    print(f"   ✓ Dispatcher alerts")
    print(f"   ✓ {len(communications['customer_messages'])} customer messages")
    
    # Export results
    eta_files = engine.export_results(eta_df, alerts_df)
    comm_file = llm.export_communications(communications)
    
    print(f"\n💾 Results exported:")
    print(f"   • ETA results: {eta_files['eta_file']}")
    print(f"   • Alerts: {eta_files['alerts_file']}")
    print(f"   • Communications: {comm_file}")
    
    # Display sample alerts and messages
    if len(alerts_df) > 0:
        print(f"\n🚨 SAMPLE DELAY ALERTS:")
        print("=" * 40)
        for idx, alert in alerts_df.head(3).iterrows():
            print(f"• {alert['driver_id']} - Stop {alert['sequence']}")
            print(f"  Customer: {alert['customer_name']}")
            print(f"  Delay: {alert['delay_minutes']:.1f} minutes")
            print(f"  Severity: {alert['alert_severity']}")
            print()
    
    if communications['customer_messages']:
        print(f"📱 SAMPLE CUSTOMER MESSAGE:")
        print("=" * 40)
        sample_msg = communications['customer_messages'][0]
        print(f"To: {sample_msg['customer_name']}")
        print(f"Delay: {sample_msg['delay_minutes']:.1f} minutes")
        print(f"Message:")
        print(f"{sample_msg['message']}")
        print()
    
    print(f"📈 DISPATCHER ALERT:")
    print("=" * 40)
    print(communications['dispatcher_alert'])
    
    return eta_df, alerts_df, communications

if __name__ == "__main__":
    create_delayed_scenario()