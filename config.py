"""
Configuration settings for Smart Delivery ETA Checker
"""
import os
from dataclasses import dataclass
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class ETAConfig:
    """Configuration parameters for ETA calculations"""
    
    # Driver-specific average speeds (km/h)
    DRIVER_SPEEDS: Dict[str, float] = None
    
    # Stop service time in minutes
    STOP_SERVICE_TIME: float = 5.0
    
    # Traffic multiplier range (min, max)
    TRAFFIC_MULTIPLIER_RANGE: tuple = (0.8, 1.5)
    
    # Delay threshold in minutes for alerts
    DELAY_THRESHOLD: float = 15.0
    
    # Simulation parameters
    GPS_UPDATE_INTERVAL: int = 30  # seconds
    SIMULATION_DURATION: int = 3600  # seconds (1 hour)
    
    def __post_init__(self):
        if self.DRIVER_SPEEDS is None:
            self.DRIVER_SPEEDS = {
                "driver_001": 45.0,  # km/h
                "driver_002": 40.0,  # km/h  
                "driver_003": 50.0,  # km/h
            }

@dataclass
class LLMConfig:
    """Configuration for LLM integration"""
    
    # OpenAI API settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MODEL: str = "gpt-3.5-turbo"
    MAX_TOKENS: int = 500
    TEMPERATURE: float = 0.3
    
    # Prompt templates
    ROUTING_SUPERVISOR_PROMPT: str = """
    You are a routing supervisor AI. Analyze the following delivery ETA data and provide a JSON response with delay flags and operational insights.
    
    ETA Data: {eta_data}
    
    Respond with JSON containing:
    - summary: Brief overview of delivery status
    - delays: List of stops with delays > {delay_threshold} minutes
    - recommendations: Top 2 operational actions
    - risk_level: LOW/MEDIUM/HIGH based on delay severity
    """
    
    DISPATCHER_ALERT_PROMPT: str = """
    You are a delivery dispatcher assistant. Create a concise alert message for the following delayed deliveries.
    
    Delayed Stops: {delayed_stops}
    
    Provide:
    1. Brief summary of the situation
    2. Top 2 recommended actions
    3. Keep it under 150 words, professional tone
    """
    
    CUSTOMER_MESSAGE_PROMPT: str = """
    Create a polite, concise customer message about a delivery delay.
    
    Customer: {customer_name}
    Original ETA: {original_eta}
    New ETA: {new_eta}
    Delay: {delay_minutes} minutes
    
    Requirements:
    - Apologetic but professional tone
    - Under 100 words
    - Include updated time window
    - No technical jargon
    """

# Global configuration instances
eta_config = ETAConfig()
llm_config = LLMConfig()