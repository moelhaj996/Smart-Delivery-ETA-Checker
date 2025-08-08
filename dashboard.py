"""
Professional Dashboard for Smart Delivery ETA Checker
Real-time visualization of delivery status, delays, and AI communications
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import glob
from pathlib import Path

# Import our modules
from data_simulator import DeliveryDataSimulator
from eta_engine import ETAEngine
from llm_integration import LLMIntegration

app = FastAPI(title="Smart Delivery ETA Dashboard", version="1.0.0")

# Setup templates and static files
templates = Jinja2Templates(directory="templates")

class DashboardData:
    """Class to manage dashboard data and analytics"""
    
    def __init__(self):
        self.output_dir = "output"
        
    def get_latest_files(self) -> Dict[str, str]:
        """Get the most recent output files"""
        files = {
            'eta_results': None,
            'delivery_alerts': None,
            'llm_communications': None,
            'eta_summary': None
        }
        
        for file_type in files.keys():
            pattern = os.path.join(self.output_dir, f"{file_type}_*.csv" if 'csv' in file_type else f"{file_type}_*.json")
            matching_files = glob.glob(pattern)
            if matching_files:
                files[file_type] = max(matching_files, key=os.path.getctime)
        
        return files
    
    def load_dashboard_data(self) -> Dict[str, Any]:
        """Load and process all dashboard data"""
        files = self.get_latest_files()
        
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {},
            'drivers': [],
            'delays': [],
            'communications': {},
            'metrics': {}
        }
        
        try:
            # Load ETA results
            if files['eta_results']:
                eta_df = pd.read_csv(files['eta_results'])
                dashboard_data['summary'] = self._generate_summary(eta_df)
                dashboard_data['drivers'] = self._process_driver_data(eta_df)
                dashboard_data['metrics'] = self._calculate_metrics(eta_df)
            
            # Load delivery alerts
            if files['delivery_alerts']:
                alerts_df = pd.read_csv(files['delivery_alerts'])
                dashboard_data['delays'] = self._process_delays(alerts_df)
            
            # Load LLM communications
            if files['llm_communications']:
                with open(files['llm_communications'], 'r') as f:
                    dashboard_data['communications'] = json.load(f)
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
            dashboard_data['error'] = str(e)
        
        return dashboard_data
    
    def _generate_summary(self, eta_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics"""
        return {
            'total_drivers': eta_df['driver_id'].nunique(),
            'total_stops': len(eta_df),
            'delayed_stops': len(eta_df[eta_df['is_delayed'] == True]),
            'on_time_rate': round((len(eta_df[eta_df['is_delayed'] == False]) / len(eta_df)) * 100, 1),
            'avg_delay': round(eta_df['delay_minutes'].mean(), 1),
            'max_delay': round(eta_df['delay_minutes'].max(), 1),
            'total_distance': round(eta_df['distance_km'].sum(), 1),
            'avg_speed': round(eta_df['avg_speed_kmh'].mean(), 1)
        }
    
    def _process_driver_data(self, eta_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Process driver-specific data"""
        drivers = []
        
        for driver_id in eta_df['driver_id'].unique():
            driver_data = eta_df[eta_df['driver_id'] == driver_id]
            
            drivers.append({
                'driver_id': driver_id,
                'total_stops': len(driver_data),
                'delayed_stops': len(driver_data[driver_data['is_delayed'] == True]),
                'on_time_stops': len(driver_data[driver_data['is_delayed'] == False]),
                'avg_delay': round(driver_data['delay_minutes'].mean(), 1),
                'total_distance': round(driver_data['distance_km'].sum(), 1),
                'avg_speed': round(driver_data['avg_speed_kmh'].mean(), 1),
                'status': 'delayed' if len(driver_data[driver_data['is_delayed'] == True]) > 0 else 'on_time'
            })
        
        return drivers
    
    def _process_delays(self, alerts_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Process delay information"""
        delays = []
        
        for _, row in alerts_df.iterrows():
            delays.append({
                'stop_id': row['stop_id'],
                'driver_id': row['driver_id'],
                'customer_name': row['customer_name'],
                'delay_minutes': round(row['delay_minutes'], 1),
                'severity': row['alert_severity'],
                'planned_eta': row['planned_eta'],
                'calculated_eta': row['calculated_eta']
            })
        
        return delays
    
    def _calculate_metrics(self, eta_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate performance metrics"""
        return {
            'efficiency_score': round(100 - (eta_df['delay_minutes'].mean() * 2), 1),
            'customer_satisfaction': round(85 + (eta_df[eta_df['is_delayed'] == False].shape[0] / eta_df.shape[0] * 15), 1),
            'route_optimization': round(eta_df['avg_speed_kmh'].mean() / 50 * 100, 1),
            'traffic_impact': round(eta_df['traffic_multiplier'].mean(), 2)
        }

# Initialize dashboard data manager
dashboard_data = DashboardData()

@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/dashboard-data")
async def get_dashboard_data():
    """API endpoint to get dashboard data"""
    return JSONResponse(dashboard_data.load_dashboard_data())

@app.get("/api/run-simulation")
async def run_simulation():
    """API endpoint to run a new simulation"""
    try:
        # Generate new simulation data
        simulator = DeliveryDataSimulator()
        stops_df, positions_df = simulator.generate_simulation_data()
        
        # Calculate ETAs
        engine = ETAEngine()
        eta_df = engine.calculate_all_etas(positions_df, stops_df)
        alerts_df = engine.generate_alerts(eta_df)
        
        # Generate LLM communications
        llm = LLMIntegration()
        communications = llm.generate_all_communications(eta_df, alerts_df)
        
        # Export results
        export_files = engine.export_results(eta_df, alerts_df)
        comm_file = llm.export_communications(communications)
        
        return JSONResponse({
            "status": "success",
            "message": "New simulation completed",
            "files": {
                "eta_results": export_files['eta_file'],
                "alerts": export_files['alerts_file'],
                "communications": comm_file
            }
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@app.get("/api/driver/{driver_id}")
async def get_driver_details(driver_id: str):
    """Get detailed information for a specific driver"""
    files = dashboard_data.get_latest_files()
    
    if not files['eta_results']:
        return JSONResponse({"error": "No data available"}, status_code=404)
    
    eta_df = pd.read_csv(files['eta_results'])
    driver_data = eta_df[eta_df['driver_id'] == driver_id]
    
    if driver_data.empty:
        return JSONResponse({"error": "Driver not found"}, status_code=404)
    
    stops = []
    for _, row in driver_data.iterrows():
        stops.append({
            'stop_id': row['stop_id'],
            'sequence': row['sequence'],
            'customer_name': row['customer_name'],
            'distance_km': round(row['distance_km'], 2),
            'travel_time_min': round(row['travel_time_min'], 1),
            'planned_eta': row['planned_eta'],
            'calculated_eta': row['calculated_eta'],
            'delay_minutes': round(row['delay_minutes'], 1),
            'is_delayed': row['is_delayed'],
            'traffic_multiplier': round(row['traffic_multiplier'], 2)
        })
    
    return JSONResponse({
        'driver_id': driver_id,
        'stops': stops,
        'summary': {
            'total_stops': len(stops),
            'delayed_stops': len([s for s in stops if s['is_delayed']]),
            'total_distance': round(driver_data['distance_km'].sum(), 1),
            'avg_delay': round(driver_data['delay_minutes'].mean(), 1)
        }
    })

if __name__ == "__main__":
    import uvicorn
    
    # Create templates directory if it doesn't exist
    os.makedirs("templates", exist_ok=True)
    
    print("🚀 Starting Smart Delivery ETA Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8000")
    print("🔄 API endpoints:")
    print("   • GET /api/dashboard-data - Get current dashboard data")
    print("   • GET /api/run-simulation - Run new simulation")
    print("   • GET /api/driver/{driver_id} - Get driver details")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)