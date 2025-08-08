# Smart Delivery ETA Checker

A comprehensive delivery tracking and ETA prediction system with AI-powered communications and real-time monitoring dashboard.

## System Architecture

```mermaid
graph TB
    A[Data Input] --> B[ETA Engine]
    A --> C[Data Simulator]
    B --> D[Delay Detection]
    C --> B
    D --> E[LLM Integration]
    E --> F[AI Communications]
    F --> G[Dashboard]
    D --> H[Alert System]
    H --> G
    B --> I[Data Export]
    I --> J[CSV/JSON Files]
    
    subgraph "Input Data"
        A1[Delivery Stops]
        A2[Driver Positions]
        A3[Traffic Conditions]
    end
    
    subgraph "AI Features"
        E1[Customer Messages]
        E2[Dispatcher Alerts]
        E3[Supervisor Reports]
    end
    
    subgraph "Output"
        G1[Web Dashboard]
        G2[Real-time Charts]
        G3[Performance Metrics]
    end
    
    A --> A1
    A --> A2
    A --> A3
    
    F --> E1
    F --> E2
    F --> E3
    
    G --> G1
    G --> G2
    G --> G3
```

## Data Flow Process

```mermaid
flowchart LR
    Start([Start Simulation]) --> Load[Load Data]
    Load --> Process[Process ETAs]
    Process --> Check{Delays Detected?}
    Check -->|Yes| AI[Generate AI Messages]
    Check -->|No| Export[Export Results]
    AI --> Alert[Send Alerts]
    Alert --> Export
    Export --> Dashboard[Update Dashboard]
    Dashboard --> End([End])
    
    style Start fill:#e1f5fe
    style AI fill:#fff3e0
    style Alert fill:#ffebee
    style Dashboard fill:#e8f5e8
    style End fill:#f3e5f5
```

## Component Relationships

```mermaid
classDiagram
    class ETAEngine {
        +calculate_eta()
        +detect_delays()
        +generate_alerts()
    }
    
    class DataSimulator {
        +generate_delivery_stops()
        +simulate_driver_positions()
        +create_traffic_conditions()
    }
    
    class LLMIntegration {
        +generate_customer_message()
        +create_dispatcher_alert()
        +routing_supervisor_report()
    }
    
    class Dashboard {
        +load_data()
        +render_charts()
        +display_metrics()
    }
    
    ETAEngine --> DataSimulator
    ETAEngine --> LLMIntegration
    LLMIntegration --> Dashboard
    ETAEngine --> Dashboard
```

## File Structure

```mermaid
graph TD
    Root[Smart-Delivery-ETA-Checker/] --> Config[config.py]
    Root --> Main[main.py]
    Root --> ETA[eta_engine.py]
    Root --> LLM[llm_integration.py]
    Root --> Sim[data_simulator.py]
    Root --> Dash[dashboard.py]
    
    Root --> Data[data/]
    Data --> Stops[delivery_stops.csv]
    Data --> Drivers[driver_positions.csv]
    
    Root --> Output[output/]
    Output --> Results[eta_results_*.csv]
    Output --> Alerts[delivery_alerts_*.csv]
    Output --> Summary[eta_summary_*.json]
    Output --> Comms[llm_communications_*.json]
    
    Root --> Templates[templates/]
    Templates --> HTML[dashboard.html]
    
    style Root fill:#e3f2fd
    style Data fill:#fff3e0
    style Output fill:#e8f5e8
    style Templates fill:#fce4ec
```

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment**
   ```bash
   cp .env.example .env
   # Add your OpenAI API key to .env
   ```

3. **Run Simulation**
   ```bash
   python demo_realistic_delays.py
   ```

4. **Start Dashboard**
   ```bash
   python dashboard.py
   ```

5. **View Results**
   - Dashboard: http://localhost:8000
   - Output files in `/output` directory

## Features

- 🚚 **Real-time ETA Calculation**
- 🚨 **Intelligent Delay Detection**
- 🤖 **AI-Powered Communications**
- 📊 **Professional Dashboard**
- 📈 **Performance Analytics**
- 📱 **Responsive Design**

## API Endpoints

- `GET /` - Dashboard interface
- `GET /api/dashboard-data` - Current data
- `GET /api/run-simulation` - Trigger simulation
- `GET /api/driver/{driver_id}` - Driver details

## Technology Stack

- **Backend**: Python, FastAPI
- **AI**: OpenAI GPT
- **Frontend**: HTML5, Tailwind CSS, Chart.js
- **Data**: Pandas, NumPy
- **Visualization**: Mermaid, Chart.js