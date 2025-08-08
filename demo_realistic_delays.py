"""
Demo script that creates realistic delays by simulating traffic and operational issues
"""
import pandas as pd
from datetime import datetime, timedelta
import random

from data_simulator import DeliveryDataSimulator
from eta_engine import ETAEngine
from llm_integration import LLMIntegration
from config import eta_config

class DelayedETAEngine(ETAEngine):
    """Modified ETA engine that simulates realistic delays"""
    
    def generate_traffic_multiplier(self) -> float:
        """Generate traffic multiplier with higher chance of delays"""
        # Simulate rush hour traffic and incidents
        if random.random() < 0.3:  # 30% chance of heavy traffic
            return random.uniform(2.0, 3.5)  # Heavy delays
        elif random.random() < 0.5:  # 50% chance of moderate traffic
            return random.uniform(1.5, 2.0)  # Moderate delays
        else:
            return random.uniform(0.8, 1.2)  # Normal traffic
    
    def calculate_eta_for_driver(self, driver_position: dict, stops: list) -> list:
        """Calculate ETAs with realistic service time variations"""
        
        # Call parent method
        eta_results = super().calculate_eta_for_driver(driver_position, stops)
        
        # Add realistic service time variations
        for result in eta_results:
            # Simulate longer service times for some stops (delivery complications)
            if random.random() < 0.2:  # 20% chance of extended service
                extra_service_time = random.uniform(5, 15)  # 5-15 extra minutes
                result['service_time_min'] += extra_service_time
                
                # Recalculate ETA with extended service time
                original_eta = datetime.fromisoformat(result['calculated_eta'])
                new_eta = original_eta + timedelta(minutes=extra_service_time)
                result['calculated_eta'] = new_eta.isoformat()
                
                # Recalculate delay
                planned_eta = datetime.fromisoformat(result['planned_eta'])
                delay_minutes = (new_eta - planned_eta).total_seconds() / 60
                result['delay_minutes'] = round(delay_minutes, 1)
                result['is_delayed'] = delay_minutes > self.config.DELAY_THRESHOLD
        
        return eta_results

def create_realistic_delay_scenario():
    """Create a scenario with realistic operational delays"""
    
    print("🚚 Smart Delivery ETA Checker - REALISTIC DELAY SCENARIO")
    print("=" * 60)
    
    # Generate base simulation data
    simulator = DeliveryDataSimulator()
    stops_df, positions_df = simulator.generate_simulation_data(3)
    
    # Set more realistic planned ETAs (closer to current time)
    current_time = datetime.now()
    
    for idx, row in stops_df.iterrows():
        # Set planned ETAs to be more realistic but tight
        sequence = row['sequence']
        # Each stop planned 20 minutes apart starting in 10 minutes
        planned_time = current_time + timedelta(minutes=10 + (sequence * 20))
        stops_df.at[idx, 'planned_eta'] = planned_time.isoformat()
    
    print(f"📊 Generated realistic scenario:")
    print(f"   • {len(stops_df)} delivery stops")
    print(f"   • {len(positions_df)} driver positions")
    print(f"   • Tight delivery schedule")
    print(f"   • Simulated traffic conditions")
    
    # Use the delayed ETA engine
    engine = DelayedETAEngine()
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
        
        # Show severity breakdown
        severity_counts = alerts_df['alert_severity'].value_counts()
        for severity, count in severity_counts.items():
            print(f"      • {severity} severity: {count} stops")
    
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
    
    # Display detailed results
    if len(alerts_df) > 0:
        print(f"\n🚨 DETAILED DELAY ALERTS:")
        print("=" * 50)
        for idx, alert in alerts_df.head(5).iterrows():
            planned = datetime.fromisoformat(alert['planned_eta'])
            calculated = datetime.fromisoformat(alert['calculated_eta'])
            
            print(f"🚛 {alert['driver_id']} - Stop {alert['sequence']}")
            print(f"   Customer: {alert['customer_name']}")
            print(f"   Planned ETA: {planned.strftime('%H:%M')}")
            print(f"   Calculated ETA: {calculated.strftime('%H:%M')}")
            print(f"   Delay: {alert['delay_minutes']:.1f} minutes")
            print(f"   Severity: {alert['alert_severity']}")
            print(f"   Traffic Impact: {alert['traffic_multiplier']:.1f}x")
            print()
    
    if communications['customer_messages']:
        print(f"📱 SAMPLE CUSTOMER MESSAGES:")
        print("=" * 50)
        for i, msg in enumerate(communications['customer_messages'][:2]):
            print(f"Message {i+1}:")
            print(f"To: {msg['customer_name']}")
            print(f"Delay: {msg['delay_minutes']:.1f} minutes")
            print(f"Content: {msg['message']}")
            print("-" * 30)
    
    print(f"\n📋 DISPATCHER ALERT:")
    print("=" * 50)
    print(communications['dispatcher_alert'])
    
    print(f"\n🎯 ROUTING SUPERVISOR REPORT:")
    print("=" * 50)
    supervisor_report = communications['routing_supervisor_report']
    print(f"Summary: {supervisor_report['summary']}")
    print(f"Risk Level: {supervisor_report['risk_level']}")
    print("Recommendations:")
    for i, rec in enumerate(supervisor_report['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    return eta_df, alerts_df, communications

if __name__ == "__main__":
    create_realistic_delay_scenario()