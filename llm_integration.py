"""
LLM integration for generating intelligent alerts and customer messages
"""
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import openai
from config import llm_config, eta_config

class LLMIntegration:
    """Handles LLM integration for generating intelligent delivery communications"""
    
    def __init__(self, config=None):
        self.config = config or llm_config
        
        # Initialize OpenAI client if API key is provided
        if self.config.OPENAI_API_KEY:
            openai.api_key = self.config.OPENAI_API_KEY
            self.llm_available = True
        else:
            self.llm_available = False
            print("Warning: OpenAI API key not found. Using mock responses.")
    
    def _call_llm(self, prompt: str, max_tokens: int = None) -> str:
        """Make a call to the LLM API"""
        
        if not self.llm_available:
            return self._generate_mock_response(prompt)
        
        try:
            import os
            from openai import OpenAI
            
            # Set the API key in environment if not already set
            if not os.getenv('OPENAI_API_KEY'):
                os.environ['OPENAI_API_KEY'] = self.config.OPENAI_API_KEY
            
            client = OpenAI()  # Will automatically use OPENAI_API_KEY from environment
            
            response = client.chat.completions.create(
                model=self.config.MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for delivery logistics."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens or self.config.MAX_TOKENS,
                temperature=self.config.TEMPERATURE
            )
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"LLM API error: {e}")
            return self._generate_mock_response(prompt)
    
    def _generate_mock_response(self, prompt: str) -> str:
        """Generate mock responses when LLM is not available"""
        
        if "routing supervisor" in prompt.lower():
            return json.dumps({
                "summary": "3 drivers with 24 total stops, 2 delays detected",
                "delays": [
                    {"stop_id": "driver_001_stop_003", "delay_minutes": 18.5},
                    {"stop_id": "driver_002_stop_005", "delay_minutes": 22.3}
                ],
                "recommendations": [
                    "Contact customers for delayed stops to manage expectations",
                    "Consider rerouting driver_002 to optimize remaining deliveries"
                ],
                "risk_level": "MEDIUM"
            })
        
        elif "dispatcher alert" in prompt.lower():
            return """DELIVERY ALERT - 2 stops delayed beyond threshold
            
Driver 001: Stop 3 delayed by 18.5 minutes
Driver 002: Stop 5 delayed by 22.3 minutes

RECOMMENDED ACTIONS:
1. Contact affected customers immediately to provide updated ETAs
2. Review driver 002's route for optimization opportunities

Current traffic conditions appear normal. Delays likely due to extended service times."""
        
        elif "customer message" in prompt.lower():
            return """Hi! We wanted to update you on your delivery status. 

Due to higher than expected delivery volume today, your package will arrive approximately 20 minutes later than originally scheduled. Your new estimated delivery window is 3:30-4:00 PM.

We sincerely apologize for any inconvenience and appreciate your patience. Your driver is making good progress and will be with you soon!"""
        
        else:
            return "Mock LLM response generated due to API unavailability."
    
    def generate_routing_supervisor_report(self, eta_df: pd.DataFrame, alerts_df: pd.DataFrame) -> Dict:
        """Generate routing supervisor JSON report"""
        
        # Prepare ETA data summary for the prompt
        eta_summary = {
            'total_drivers': eta_df['driver_id'].nunique(),
            'total_stops': len(eta_df),
            'delayed_stops': len(alerts_df),
            'average_delay': round(eta_df['delay_minutes'].mean(), 2),
            'max_delay': round(eta_df['delay_minutes'].max(), 2) if len(eta_df) > 0 else 0
        }
        
        # Format delayed stops for the prompt
        delayed_stops_info = []
        if len(alerts_df) > 0:
            for _, row in alerts_df.head(5).iterrows():  # Top 5 delays
                delayed_stops_info.append({
                    'stop_id': row['stop_id'],
                    'driver_id': row['driver_id'],
                    'delay_minutes': row['delay_minutes'],
                    'customer': row['customer_name']
                })
        
        prompt = self.config.ROUTING_SUPERVISOR_PROMPT.format(
            eta_data=json.dumps(eta_summary, indent=2),
            delay_threshold=eta_config.DELAY_THRESHOLD
        )
        
        response = self._call_llm(prompt)
        
        try:
            # Try to parse as JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback to structured response
            return {
                "summary": f"{eta_summary['total_drivers']} drivers with {eta_summary['total_stops']} stops, {eta_summary['delayed_stops']} delays",
                "delays": delayed_stops_info,
                "recommendations": ["Review delayed stops", "Contact affected customers"],
                "risk_level": "MEDIUM" if eta_summary['delayed_stops'] > 0 else "LOW",
                "raw_response": response
            }
    
    def generate_dispatcher_alert(self, alerts_df: pd.DataFrame) -> str:
        """Generate dispatcher alert message"""
        
        if len(alerts_df) == 0:
            return "No delivery delays detected. All stops are on schedule."
        
        # Format delayed stops for the prompt
        delayed_stops_text = []
        for _, row in alerts_df.head(5).iterrows():
            delayed_stops_text.append(
                f"Driver {row['driver_id']}: Stop {row['sequence']} ({row['customer_name']}) "
                f"delayed by {row['delay_minutes']:.1f} minutes"
            )
        
        prompt = self.config.DISPATCHER_ALERT_PROMPT.format(
            delayed_stops="\n".join(delayed_stops_text)
        )
        
        return self._call_llm(prompt, max_tokens=200)
    
    def generate_customer_message(self, stop_info: Dict) -> str:
        """Generate customer-friendly delay message"""
        
        prompt = self.config.CUSTOMER_MESSAGE_PROMPT.format(
            customer_name=stop_info.get('customer_name', 'Valued Customer'),
            original_eta=stop_info.get('planned_eta', 'N/A'),
            new_eta=stop_info.get('calculated_eta', 'N/A'),
            delay_minutes=stop_info.get('delay_minutes', 0)
        )
        
        return self._call_llm(prompt, max_tokens=150)
    
    def generate_all_communications(self, eta_df: pd.DataFrame, alerts_df: pd.DataFrame) -> Dict:
        """Generate all LLM communications for the delivery status"""
        
        communications = {
            'timestamp': datetime.now().isoformat(),
            'routing_supervisor_report': self.generate_routing_supervisor_report(eta_df, alerts_df),
            'dispatcher_alert': self.generate_dispatcher_alert(alerts_df),
            'customer_messages': []
        }
        
        # Generate customer messages for delayed stops
        if len(alerts_df) > 0:
            for _, row in alerts_df.iterrows():
                customer_msg = self.generate_customer_message(row.to_dict())
                communications['customer_messages'].append({
                    'stop_id': row['stop_id'],
                    'customer_name': row['customer_name'],
                    'delay_minutes': row['delay_minutes'],
                    'message': customer_msg
                })
        
        return communications
    
    def export_communications(self, communications: Dict, output_dir: str = "output") -> str:
        """Export LLM communications to JSON file"""
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"llm_communications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(communications, f, indent=2, default=str)
        
        return filepath

if __name__ == "__main__":
    # Test LLM integration with sample data
    from data_simulator import DeliveryDataSimulator
    from eta_engine import ETAEngine
    
    print("Testing LLM Integration...")
    
    # Generate test data
    simulator = DeliveryDataSimulator()
    stops_df, positions_df = simulator.generate_simulation_data()
    
    # Calculate ETAs
    engine = ETAEngine()
    eta_df = engine.calculate_all_etas(positions_df, stops_df)
    alerts_df = engine.generate_alerts(eta_df)
    
    # Generate LLM communications
    llm = LLMIntegration()
    communications = llm.generate_all_communications(eta_df, alerts_df)
    
    # Export communications
    comm_file = llm.export_communications(communications)
    
    print(f"\nLLM Integration Test Results:")
    print(f"- Communications generated for {len(eta_df)} stops")
    print(f"- Delayed stops: {len(alerts_df)}")
    print(f"- Customer messages: {len(communications['customer_messages'])}")
    print(f"- Communications file: {comm_file}")