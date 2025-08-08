"""
Data simulator for generating GPS positions and delivery stops
"""
import random
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import numpy as np

class DeliveryDataSimulator:
    """Simulates GPS positions and delivery stops for testing"""
    
    def __init__(self):
        # Dubai coordinates as base (can be changed for other cities)
        self.city_center = (25.2048, 55.2708)
        self.city_radius = 0.1  # degrees (~11km)
        
    def generate_stops(self, driver_id: str, num_stops: int = 8) -> List[Dict]:
        """Generate ordered delivery stops for a driver"""
        stops = []
        
        # Start from a depot location
        depot_lat = self.city_center[0] + random.uniform(-0.02, 0.02)
        depot_lon = self.city_center[1] + random.uniform(-0.02, 0.02)
        
        for i in range(num_stops):
            # Generate stops in a roughly logical delivery route
            angle = (i / num_stops) * 2 * np.pi + random.uniform(-0.5, 0.5)
            distance = random.uniform(0.01, self.city_radius)
            
            lat = self.city_center[0] + distance * np.cos(angle)
            lon = self.city_center[1] + distance * np.sin(angle)
            
            # Generate planned delivery time (every 30 minutes starting from now)
            planned_time = datetime.now() + timedelta(minutes=30 * (i + 1))
            
            stop = {
                'stop_id': f"{driver_id}_stop_{i+1:03d}",
                'driver_id': driver_id,
                'sequence': i + 1,
                'latitude': round(lat, 6),
                'longitude': round(lon, 6),
                'customer_name': f"Customer_{i+1:03d}",
                'address': f"Building {i+1}, Street {random.randint(1, 50)}, Dubai",
                'planned_eta': planned_time.isoformat(),
                'status': 'pending'
            }
            stops.append(stop)
            
        return stops
    
    def generate_driver_position(self, driver_id: str, stops: List[Dict], 
                                current_stop_index: int = 0) -> Dict:
        """Generate current GPS position for a driver"""
        
        if current_stop_index == 0:
            # Driver is starting from depot or first stop area
            base_lat = stops[0]['latitude'] + random.uniform(-0.001, 0.001)
            base_lon = stops[0]['longitude'] + random.uniform(-0.001, 0.001)
        elif current_stop_index < len(stops):
            # Driver is between stops - interpolate position
            prev_stop = stops[current_stop_index - 1]
            next_stop = stops[current_stop_index]
            
            # Random position between previous and next stop
            progress = random.uniform(0.1, 0.9)
            base_lat = prev_stop['latitude'] + progress * (next_stop['latitude'] - prev_stop['latitude'])
            base_lon = prev_stop['longitude'] + progress * (next_stop['longitude'] - prev_stop['longitude'])
        else:
            # Driver completed all stops
            last_stop = stops[-1]
            base_lat = last_stop['latitude']
            base_lon = last_stop['longitude']
        
        return {
            'driver_id': driver_id,
            'timestamp': datetime.now().isoformat(),
            'latitude': round(base_lat, 6),
            'longitude': round(base_lon, 6),
            'speed': random.uniform(20, 60),  # km/h
            'heading': random.uniform(0, 360),  # degrees
            'accuracy': random.uniform(3, 10)  # meters
        }
    
    def generate_simulation_data(self, num_drivers: int = 3) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Generate complete simulation dataset"""
        
        all_stops = []
        all_positions = []
        
        driver_ids = [f"driver_{i+1:03d}" for i in range(num_drivers)]
        
        for driver_id in driver_ids:
            # Generate stops for this driver
            stops = self.generate_stops(driver_id, num_stops=random.randint(6, 10))
            all_stops.extend(stops)
            
            # Generate current position
            current_stop = random.randint(0, len(stops) - 1)
            position = self.generate_driver_position(driver_id, stops, current_stop)
            all_positions.append(position)
        
        stops_df = pd.DataFrame(all_stops)
        positions_df = pd.DataFrame(all_positions)
        
        return stops_df, positions_df
    
    def save_simulation_data(self, output_dir: str = "data"):
        """Generate and save simulation data to CSV files"""
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        stops_df, positions_df = self.generate_simulation_data()
        
        stops_file = os.path.join(output_dir, "delivery_stops.csv")
        positions_file = os.path.join(output_dir, "driver_positions.csv")
        
        stops_df.to_csv(stops_file, index=False)
        positions_df.to_csv(positions_file, index=False)
        
        print(f"Generated simulation data:")
        print(f"- Stops: {stops_file} ({len(stops_df)} records)")
        print(f"- Positions: {positions_file} ({len(positions_df)} records)")
        
        return stops_file, positions_file

if __name__ == "__main__":
    simulator = DeliveryDataSimulator()
    simulator.save_simulation_data()