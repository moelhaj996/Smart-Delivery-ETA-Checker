"""
Core ETA calculation engine for Smart Delivery ETA Checker
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from geopy.distance import geodesic
import random
import json

from config import eta_config

class ETAEngine:
    """Core engine for calculating delivery ETAs"""
    
    def __init__(self, config=None):
        self.config = config or eta_config
        
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula via geopy"""
        point1 = (lat1, lon1)
        point2 = (lat2, lon2)
        return geodesic(point1, point2).kilometers
    
    def calculate_travel_time(self, distance_km: float, avg_speed_kmh: float, 
                            traffic_multiplier: float = 1.0) -> float:
        """Calculate travel time in minutes"""
        if avg_speed_kmh <= 0:
            return 0
        
        # Time in hours, then convert to minutes
        time_hours = (distance_km / avg_speed_kmh) * traffic_multiplier
        return time_hours * 60
    
    def generate_traffic_multiplier(self) -> float:
        """Generate random traffic multiplier within configured range"""
        min_mult, max_mult = self.config.TRAFFIC_MULTIPLIER_RANGE
        return random.uniform(min_mult, max_mult)
    
    def calculate_eta_for_driver(self, driver_position: Dict, stops: List[Dict]) -> List[Dict]:
        """Calculate ETAs for all remaining stops for a driver"""
        
        driver_id = driver_position['driver_id']
        current_lat = driver_position['latitude']
        current_lon = driver_position['longitude']
        current_time = datetime.fromisoformat(driver_position['timestamp'].replace('Z', '+00:00'))
        
        # Get driver's average speed
        avg_speed = self.config.DRIVER_SPEEDS.get(driver_id, 45.0)
        
        # Filter stops for this driver and sort by sequence
        driver_stops = [s for s in stops if s['driver_id'] == driver_id]
        driver_stops.sort(key=lambda x: x['sequence'])
        
        eta_results = []
        cumulative_time = current_time
        current_position = (current_lat, current_lon)
        
        for stop in driver_stops:
            stop_position = (stop['latitude'], stop['longitude'])
            
            # Calculate distance to this stop
            distance_km = self.calculate_distance(
                current_position[0], current_position[1],
                stop_position[0], stop_position[1]
            )
            
            # Generate traffic multiplier for this segment
            traffic_multiplier = self.generate_traffic_multiplier()
            
            # Calculate travel time
            travel_time_min = self.calculate_travel_time(
                distance_km, avg_speed, traffic_multiplier
            )
            
            # Add travel time to get arrival time
            arrival_time = cumulative_time + timedelta(minutes=travel_time_min)
            
            # Calculate delay compared to planned ETA
            planned_eta = datetime.fromisoformat(stop['planned_eta'].replace('Z', '+00:00'))
            delay_minutes = (arrival_time - planned_eta).total_seconds() / 60
            
            # Create ETA result
            eta_result = {
                'driver_id': driver_id,
                'stop_id': stop['stop_id'],
                'sequence': stop['sequence'],
                'customer_name': stop['customer_name'],
                'distance_km': round(distance_km, 2),
                'travel_time_min': round(travel_time_min, 1),
                'service_time_min': self.config.STOP_SERVICE_TIME,
                'planned_eta': stop['planned_eta'],
                'calculated_eta': arrival_time.isoformat(),
                'delay_minutes': round(delay_minutes, 1),
                'avg_speed_kmh': avg_speed,
                'traffic_multiplier': round(traffic_multiplier, 2),
                'is_delayed': delay_minutes > self.config.DELAY_THRESHOLD,
                'latitude': stop['latitude'],
                'longitude': stop['longitude']
            }
            
            eta_results.append(eta_result)
            
            # Update position and time for next iteration
            current_position = stop_position
            cumulative_time = arrival_time + timedelta(minutes=self.config.STOP_SERVICE_TIME)
        
        return eta_results
    
    def calculate_all_etas(self, positions_df: pd.DataFrame, stops_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate ETAs for all drivers"""
        
        all_eta_results = []
        
        # Convert DataFrames to lists of dictionaries for easier processing
        positions = positions_df.to_dict('records')
        stops = stops_df.to_dict('records')
        
        for position in positions:
            driver_etas = self.calculate_eta_for_driver(position, stops)
            all_eta_results.extend(driver_etas)
        
        return pd.DataFrame(all_eta_results)
    
    def generate_alerts(self, eta_df: pd.DataFrame) -> pd.DataFrame:
        """Generate alerts for delayed deliveries"""
        
        delayed_stops = eta_df[eta_df['is_delayed'] == True].copy()
        
        if len(delayed_stops) == 0:
            return pd.DataFrame()
        
        # Add alert metadata
        delayed_stops['alert_timestamp'] = datetime.now().isoformat()
        delayed_stops['alert_severity'] = delayed_stops['delay_minutes'].apply(
            lambda x: 'HIGH' if x > 30 else 'MEDIUM' if x > 20 else 'LOW'
        )
        
        # Sort by delay severity
        delayed_stops = delayed_stops.sort_values('delay_minutes', ascending=False)
        
        return delayed_stops
    
    def export_results(self, eta_df: pd.DataFrame, alerts_df: pd.DataFrame, 
                      output_dir: str = "output") -> Dict[str, str]:
        """Export results to CSV files"""
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Export ETA results
        eta_file = os.path.join(output_dir, f"eta_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        eta_df.to_csv(eta_file, index=False)
        
        # Export alerts
        alerts_file = os.path.join(output_dir, f"delivery_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        if len(alerts_df) > 0:
            alerts_df.to_csv(alerts_file, index=False)
        else:
            # Create empty alerts file with headers
            pd.DataFrame(columns=eta_df.columns).to_csv(alerts_file, index=False)
        
        # Export summary JSON
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_stops': len(eta_df),
            'delayed_stops': len(alerts_df),
            'drivers_processed': eta_df['driver_id'].nunique(),
            'average_delay': round(eta_df['delay_minutes'].mean(), 2),
            'max_delay': round(eta_df['delay_minutes'].max(), 2) if len(eta_df) > 0 else 0
        }
        
        summary_file = os.path.join(output_dir, f"eta_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return {
            'eta_file': eta_file,
            'alerts_file': alerts_file,
            'summary_file': summary_file
        }

if __name__ == "__main__":
    # Test the ETA engine with sample data
    from data_simulator import DeliveryDataSimulator
    
    print("Testing ETA Engine...")
    
    # Generate test data
    simulator = DeliveryDataSimulator()
    stops_df, positions_df = simulator.generate_simulation_data()
    
    # Calculate ETAs
    engine = ETAEngine()
    eta_df = engine.calculate_all_etas(positions_df, stops_df)
    alerts_df = engine.generate_alerts(eta_df)
    
    # Export results
    files = engine.export_results(eta_df, alerts_df)
    
    print(f"\nETA Engine Test Results:")
    print(f"- Total stops processed: {len(eta_df)}")
    print(f"- Delayed stops: {len(alerts_df)}")
    print(f"- Files generated: {list(files.values())}")