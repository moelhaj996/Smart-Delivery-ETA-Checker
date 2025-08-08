"""
Comprehensive Mock Data Generator for Smart Delivery ETA Checker Dashboard
Creates realistic data to showcase all dashboard features
"""

import pandas as pd
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os

class MockDataGenerator:
    """Generate comprehensive mock data for dashboard demonstration"""
    
    def __init__(self):
        self.output_dir = "output"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Mock data configurations
        self.drivers = [
            {"id": "DRV001", "name": "Ahmed Hassan", "vehicle": "Toyota Hiace", "experience": "5 years"},
            {"id": "DRV002", "name": "Sarah Al-Mansouri", "vehicle": "Nissan NV200", "experience": "3 years"},
            {"id": "DRV003", "name": "Mohammed Al-Rashid", "vehicle": "Ford Transit", "experience": "7 years"},
            {"id": "DRV004", "name": "Fatima Al-Zahra", "vehicle": "Hyundai H1", "experience": "4 years"},
            {"id": "DRV005", "name": "Omar Al-Khouri", "vehicle": "Mercedes Sprinter", "experience": "6 years"}
        ]
        
        self.customers = [
            "Khalid Al-Mansoori", "Aisha Al-Qasimi", "Hassan Al-Maktoum", "Mariam Al-Nuaimi",
            "Abdullah Al-Rashid", "Noura Al-Shamsi", "Salem Al-Dhaheri", "Layla Al-Mazrouei",
            "Rashid Al-Falasi", "Hind Al-Suwaidi", "Majid Al-Ketbi", "Shamma Al-Hosani",
            "Saeed Al-Marri", "Moza Al-Thani", "Hamdan Al-Nahyan", "Reem Al-Maktoum"
        ]
        
        self.locations = [
            {"area": "Dubai Marina", "district": "Marina Walk", "traffic": "High"},
            {"area": "Downtown Dubai", "district": "Burj Khalifa", "traffic": "Very High"},
            {"area": "Jumeirah", "district": "Beach Road", "traffic": "Medium"},
            {"area": "Business Bay", "district": "Bay Square", "traffic": "High"},
            {"area": "DIFC", "district": "Gate Village", "traffic": "Medium"},
            {"area": "JLT", "district": "Cluster A", "traffic": "High"},
            {"area": "Al Barsha", "district": "Mall of Emirates", "traffic": "Very High"},
            {"area": "Deira", "district": "Gold Souk", "traffic": "High"},
            {"area": "Bur Dubai", "district": "Al Fahidi", "traffic": "Medium"},
            {"area": "Karama", "district": "Shopping Complex", "traffic": "Medium"}
        ]
        
    def generate_comprehensive_mock_data(self):
        """Generate all mock data files for dashboard"""
        print("🎯 Generating comprehensive mock data for dashboard...")
        
        # Generate ETA results
        eta_df = self._generate_eta_results()
        eta_file = os.path.join(self.output_dir, f"eta_results_{self.timestamp}.csv")
        eta_df.to_csv(eta_file, index=False)
        
        # Generate delivery alerts
        alerts_df = self._generate_delivery_alerts(eta_df)
        alerts_file = os.path.join(self.output_dir, f"delivery_alerts_{self.timestamp}.csv")
        alerts_df.to_csv(alerts_file, index=False)
        
        # Generate LLM communications
        communications = self._generate_llm_communications(eta_df, alerts_df)
        comm_file = os.path.join(self.output_dir, f"llm_communications_{self.timestamp}.json")
        with open(comm_file, 'w') as f:
            json.dump(communications, f, indent=2)
        
        # Generate summary data
        summary = self._generate_summary_data(eta_df, alerts_df)
        summary_file = os.path.join(self.output_dir, f"eta_summary_{self.timestamp}.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✅ Mock data generated successfully!")
        print(f"📁 Files created:")
        print(f"   • {eta_file}")
        print(f"   • {alerts_file}")
        print(f"   • {comm_file}")
        print(f"   • {summary_file}")
        
        return {
            'eta_file': eta_file,
            'alerts_file': alerts_file,
            'communications_file': comm_file,
            'summary_file': summary_file
        }
    
    def _generate_eta_results(self) -> pd.DataFrame:
        """Generate comprehensive ETA results data"""
        data = []
        stop_id = 1
        
        for driver in self.drivers:
            # Each driver has 4-8 stops
            num_stops = random.randint(4, 8)
            
            for i in range(num_stops):
                location = random.choice(self.locations)
                customer = random.choice(self.customers)
                
                # Base travel time
                base_time = random.randint(15, 45)
                
                # Traffic multiplier based on area
                traffic_multipliers = {"Low": 1.0, "Medium": 1.3, "High": 1.8, "Very High": 2.5}
                traffic_mult = traffic_multipliers[location["traffic"]]
                
                # Calculate times
                planned_time = datetime.now() + timedelta(minutes=base_time + (i * 20))
                # Introduce more realistic delays
                if random.random() < 0.4:  # 40% chance of delay
                    delay_factor = random.uniform(1.2, 2.0)
                    actual_time = planned_time + timedelta(minutes=base_time * delay_factor * (traffic_mult - 1) + random.randint(10, 30))
                else:
                    actual_time = planned_time + timedelta(minutes=base_time * (traffic_mult - 1))
                delay_minutes = (actual_time - planned_time).total_seconds() / 60
                
                # Distance and speed
                distance = random.uniform(2.5, 15.0)
                avg_speed = distance / (base_time / 60) if base_time > 0 else 30
                
                data.append({
                    'stop_id': f"STOP_{stop_id:03d}",
                    'driver_id': driver["id"],
                    'customer_name': customer,
                    'delivery_address': f"{location['district']}, {location['area']}",
                    'planned_eta': planned_time.strftime("%H:%M"),
                    'calculated_eta': actual_time.strftime("%H:%M"),
                    'delay_minutes': round(delay_minutes, 1),
                    'is_delayed': delay_minutes > 10,
                    'distance_km': round(distance, 2),
                    'avg_speed_kmh': round(avg_speed, 1),
                    'traffic_multiplier': traffic_mult,
                    'traffic_condition': location["traffic"],
                    'priority': random.choice(["Standard", "Express", "Premium"]),
                    'order_value': round(random.uniform(45, 250), 2),
                    'delivery_window': f"{planned_time.strftime('%H:%M')}-{(planned_time + timedelta(hours=1)).strftime('%H:%M')}"
                })
                stop_id += 1
        
        return pd.DataFrame(data)
    
    def _generate_delivery_alerts(self, eta_df: pd.DataFrame) -> pd.DataFrame:
        """Generate delivery alerts based on ETA data"""
        alerts = []
        
        # Filter delayed deliveries
        delayed_deliveries = eta_df[eta_df['is_delayed'] == True]
        
        for _, row in delayed_deliveries.iterrows():
            # Determine severity
            delay = row['delay_minutes']
            if delay > 45:
                severity = "HIGH"
                impact = "Critical delay affecting customer satisfaction"
            elif delay > 25:
                severity = "MEDIUM"
                impact = "Moderate delay requiring customer notification"
            else:
                severity = "LOW"
                impact = "Minor delay within acceptable range"
            
            alerts.append({
                'alert_id': f"ALT_{len(alerts)+1:03d}",
                'stop_id': row['stop_id'],
                'driver_id': row['driver_id'],
                'customer_name': row['customer_name'],
                'delivery_address': row['delivery_address'],
                'planned_eta': row['planned_eta'],
                'calculated_eta': row['calculated_eta'],
                'delay_minutes': row['delay_minutes'],
                'alert_severity': severity,
                'traffic_condition': row['traffic_condition'],
                'impact_description': impact,
                'recommended_action': self._get_recommended_action(severity, delay),
                'alert_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'priority_level': row['priority'],
                'order_value': row['order_value']
            })
        
        return pd.DataFrame(alerts)
    
    def _get_recommended_action(self, severity: str, delay: float) -> str:
        """Get recommended action based on severity"""
        if severity == "HIGH":
            return f"Immediate customer contact required. Consider route optimization or backup driver."
        elif severity == "MEDIUM":
            return f"Notify customer of delay. Monitor traffic conditions for route adjustment."
        else:
            return f"Continue monitoring. Delay within acceptable parameters."
    
    def _generate_llm_communications(self, eta_df: pd.DataFrame, alerts_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate AI-powered communications"""
        
        # Customer messages
        customer_messages = []
        for _, alert in alerts_df.iterrows():
            if alert['alert_severity'] in ['HIGH', 'MEDIUM']:
                message = {
                    "recipient": alert['customer_name'],
                    "type": "delay_notification",
                    "delay_minutes": alert['delay_minutes'],
                    "new_eta": alert['calculated_eta'],
                    "message": f"Dear {alert['customer_name']},\n\nWe sincerely apologize for the delay in your delivery. Due to unexpected traffic conditions in {alert['delivery_address'].split(',')[1].strip()}, your new estimated delivery time is {alert['calculated_eta']}.\n\nWe appreciate your patience and will ensure your order arrives as soon as possible. If you have any concerns, please don't hesitate to contact us.\n\nThank you for your understanding.\n\nBest regards,\nSmart Delivery Team",
                    "priority": alert['priority_level'],
                    "order_value": alert['order_value']
                }
                customer_messages.append(message)
        
        # Dispatcher alerts
        dispatcher_alerts = []
        for driver_id in eta_df['driver_id'].unique():
            driver_alerts = alerts_df[alerts_df['driver_id'] == driver_id]
            if len(driver_alerts) > 0:
                high_alerts = len(driver_alerts[driver_alerts['alert_severity'] == 'HIGH'])
                medium_alerts = len(driver_alerts[driver_alerts['alert_severity'] == 'MEDIUM'])
                
                alert_text = f"**DISPATCH ALERT: Driver {driver_id}**\n\n"
                alert_text += f"• {high_alerts} HIGH priority delays\n"
                alert_text += f"• {medium_alerts} MEDIUM priority delays\n\n"
                alert_text += "Recommended Actions:\n"
                alert_text += "1. Contact affected customers immediately\n"
                alert_text += "2. Review route optimization options\n"
                alert_text += "3. Consider backup driver assignment for critical orders\n"
                alert_text += "4. Monitor traffic conditions for remaining stops"
                
                dispatcher_alerts.append({
                    "driver_id": driver_id,
                    "alert_level": "HIGH" if high_alerts > 0 else "MEDIUM",
                    "affected_stops": len(driver_alerts),
                    "message": alert_text,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Supervisor report
        total_delays = len(alerts_df)
        high_priority = len(alerts_df[alerts_df['alert_severity'] == 'HIGH'])
        avg_delay = alerts_df['delay_minutes'].mean() if len(alerts_df) > 0 else 0
        
        supervisor_report = {
            "report_type": "operational_summary",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_active_drivers": len(eta_df['driver_id'].unique()),
                "total_deliveries": len(eta_df),
                "delayed_deliveries": total_delays,
                "high_priority_delays": high_priority,
                "average_delay_minutes": round(avg_delay, 1),
                "on_time_percentage": round(((len(eta_df) - total_delays) / len(eta_df)) * 100, 1)
            },
            "recommendations": [
                "Implement dynamic route optimization for high-traffic areas",
                "Increase buffer time for deliveries in Dubai Marina and Downtown",
                "Consider additional drivers during peak hours (5-7 PM)",
                "Enhance real-time traffic monitoring integration"
            ],
            "risk_assessment": "MEDIUM" if high_priority > 2 else "LOW"
        }
        
        return {
            "customer_messages": customer_messages,
            "dispatcher_alerts": dispatcher_alerts,
            "supervisor_report": supervisor_report,
            "generation_timestamp": datetime.now().isoformat(),
            "total_communications": len(customer_messages) + len(dispatcher_alerts) + 1
        }
    
    def _generate_summary_data(self, eta_df: pd.DataFrame, alerts_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive summary statistics"""
        return {
            "operational_metrics": {
                "total_drivers": len(eta_df['driver_id'].unique()),
                "total_stops": len(eta_df),
                "completed_deliveries": len(eta_df) - len(alerts_df),
                "delayed_deliveries": len(alerts_df),
                "on_time_rate": round(((len(eta_df) - len(alerts_df)) / len(eta_df)) * 100, 1),
                "average_delay": round(alerts_df['delay_minutes'].mean() if len(alerts_df) > 0 else 0, 1),
                "total_distance": round(eta_df['distance_km'].sum(), 1),
                "average_speed": round(eta_df['avg_speed_kmh'].mean(), 1)
            },
            "performance_indicators": {
                "efficiency_score": round(85 + random.uniform(-10, 10), 1),
                "customer_satisfaction": round(88 + random.uniform(-5, 7), 1),
                "route_optimization": round(78 + random.uniform(-8, 12), 1),
                "traffic_adaptation": round(82 + random.uniform(-6, 8), 1)
            },
            "alert_breakdown": {
                "high_priority": len(alerts_df[alerts_df['alert_severity'] == 'HIGH']),
                "medium_priority": len(alerts_df[alerts_df['alert_severity'] == 'MEDIUM']),
                "low_priority": len(alerts_df[alerts_df['alert_severity'] == 'LOW'])
            },
            "driver_performance": [
                {
                    "driver_id": driver_id,
                    "total_stops": len(eta_df[eta_df['driver_id'] == driver_id]),
                    "delayed_stops": len(alerts_df[alerts_df['driver_id'] == driver_id]),
                    "efficiency": round(random.uniform(75, 95), 1)
                }
                for driver_id in eta_df['driver_id'].unique()
            ],
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    generator = MockDataGenerator()
    generator.generate_comprehensive_mock_data()