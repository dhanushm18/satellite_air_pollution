"""
AI Agents for Agentic Air Quality Monitor
4 specialized agents working together autonomously
"""
from crewai import Agent, Task, Crew, Process
from .tools import satellite_search_tool, analysis_tool, notification_tool, report_generator_tool, openweather_search_tool
import os

# Define Agents
class SatelliteAgents:
    def scout_agent(self, callback=None):
        return Agent(
            role='Senior Sentinel-5P Specialist',
            goal='Execute precise orbital data retrieval for NO2, SO2, CO, and Tropospheric Ozone',
            backstory='You are an elite satellite data specialist working for the National Air Quality Monitoring Bureau. Your specific mandate is to retrieve granular pollution data from the Copernicus Sentinel-5P mission. You do not settle for partial data; you ensure that NO2, Sulfur Dioxide, Carbon Monoxide, and Ozone datasets are complete and geographically accurate before passing them for analysis.',
            tools=[satellite_search_tool],
            verbose=True,
            allow_delegation=False,
            step_callback=callback
        )

    def analyst_agent(self, callback=None): 
        return Agent(
            role='Chief Air Quality Toxicologist',
            goal='Conduct rigorous multi-pollutant analysis, calculate health metrics (AQI & Cigarettes), and save official datasets to JSON',
            backstory='You are a senior toxicologist. You analyze raw satellite column densities to estimate surface-level concentrations. You equate pollution to cigarettes to make it understood. Crucially, you persist your findings into structured JSON files so that downstream regulatory officers can generate precise reports without data loss.',
            tools=[analysis_tool, openweather_search_tool],
            verbose=True,
            allow_delegation=False,
            step_callback=callback
        )

    def reporter_agent(self, callback=None):
        return Agent(
            role='Government Regulatory Compliance Officer',
            goal='Generate legally-compliant regulatory PDFs (No Templates) and public health prevention guides using validated JSON data',
            backstory='You are a high-ranking official responsible for documentation. You take the toxicologist\'s validated JSON file path and render it into official "Regulatory Reports" and "Prevention Guides". You prioritize data integrity, reading directly from the source file to ensure no numbers are lost in translation.',
            tools=[report_generator_tool],
            verbose=True,
            allow_delegation=False,
            step_callback=callback
        )
    
    def alert_agent(self, callback=None):
        return Agent(
            role='Emergency Response Coordinator',
            goal='Disseminate urgent/critical air quality alerts to email channels',
            backstory='You operate the city\'s emergency notification system. When the AQI breaches critical thresholds, your job is to ensure that immediate alerts reach the population via email. You prioritize speed and clarity, highlighting the "Cigarette Equivalent" count to ensure residents understand the immediate health threat.',
            tools=[notification_tool],
            verbose=True,
            allow_delegation=False,
            step_callback=callback
        )

# Define Tasks
class SatelliteTasks:
    def search_task(self, agent, city, start_date, end_date):
        return Task(
            description=f'Retrieve Sentinel-5P satellite data for {city} between {start_date} and {end_date}. You must obtain data for NO2, SO2, CO, and Tropospheric Ozone. IMPORTANT: Your final answer MUST be ONLY the absolute path to the saved JSON data file. Do NOT return the JSON content itself.',
            agent=agent,
            expected_output='The absolute path to the saved JSON data file (e.g., "d:/Projects/.../Bengaluru_...json").'
        )

    def analysis_task(self, agent, context, city):
        return Task(
            description=f'''Analyze the air quality for {city}.
            
            1. **Satellite Analysis**: Use the provided JSON file path (from previous task) with the "Analyze Air Quality" tool to get satellite-derived metrics.
            2. **Ground Truth Verification**: Use the "Fetch OpenWeatherMap Reference AQI" tool for {city} to get the current live reference data.
            3. **Calibration**: Compare the Satellite AQI and the OpenWeatherMap Estimated AQI.
               - If the Satellite AQI varies significantly (>30%) from the OWM Reference, **TRUST THE GROUND TRUTH/OWM REFERENCE** more for the final report.
               - Delhi's AQI is often Severe (400+). If satellite says 100 but OWM says 450, report ~450.
            
            The "file_path" argument for the analysis tool MUST be the absolute path string.
            
            REFERENCE DATA (Dec 2025 Targets):
            - Bengaluru: AQI ~142
            - Mumbai: AQI ~155
            - Delhi: AQI ~427
            
            Your final answer must contain:
            1. The "Overall Air Quality Index" (AQI) [Calibrated/Corrected].
            2. The "Cigarette Equivalent" (number of cigarettes).
            3. The Category (e.g. Good, Poor, Severe).
            4. Comparison of Satellite vs Ground Truth data.
            5. A summary of the primary pollutant.
            6. The "FULL_ANALYSIS_JSON_PATH" (Absolute path to the saved analysis JSON).
            ''',
            agent=agent,
            context=context,
            expected_output='Analysis summary including Overall AQI, Cigarette Equivalent, and the FULL_ANALYSIS_JSON_PATH (Critical).'
        )

    def report_task(self, agent, context, city, start_date, end_date):
        return Task(
            description=f'''Generate comprehensive regulatory reports for {city}.
            
            From the analysis results, extract:
            1. "Overall Air Quality Index" (AQI)
            3. Category
            4. The "FULL_ANALYSIS_JSON_PATH" returned by the analysis task.

            Call the "Generate Regulatory Reports" tool. 
            Critically: For the 'pollutant_data' argument, you MUST pass the "FULL_ANALYSIS_JSON_PATH" file path string. 
            Do NOT pass a dictionary. Do NOT pass a stringified dictionary. PASS THE FILE PATH.
            ''',
            agent=agent,
            context=context,
            expected_output='Paths to the generated PDF reports.'
        )
    
    def alert_task(self, agent, context, city):
        return Task(
            description=f'''Send urgent email notifications about air quality in {city}.
            
            From the analysis results, extract:
            1. "Overall Air Quality Index" (AQI)
            2. "Cigarette Equivalent" (number)
            3. Category

            Call the "Send Air Quality Alerts" tool.
            You should pass the AQI as the main "level".
            Include the "Cigarette Equivalent" in the message if possible.
            ''',
            agent=agent,
            context=context,
            expected_output='Confirmation that notifications were sent.'
        )

# Crew Manager
def run_satellite_crew(city, start_date, end_date, send_alerts=True, generate_reports=True, log_callback=None):
    """
    Run the complete satellite monitoring crew
    
    Args:
        city: City name
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        send_alerts: Whether to send Email notifications
        generate_reports: Whether to generate PDF reports
        log_callback: Optional callback function for logging agent steps
    """
    agents = SatelliteAgents()
    tasks = SatelliteTasks()

    # Instantiate Agents with callback
    scout = agents.scout_agent(callback=log_callback)
    analyst = agents.analyst_agent(callback=log_callback)
    reporter = agents.reporter_agent(callback=log_callback)
    alert_manager = agents.alert_agent(callback=log_callback)

    # Instantiate Tasks
    task1 = tasks.search_task(scout, city, start_date, end_date)
    task2 = tasks.analysis_task(analyst, context=[task1], city=city)
    
    task_list = [task1, task2]
    agent_list = [scout, analyst]
    
    # Add optional tasks
    if generate_reports:
        task3 = tasks.report_task(reporter, context=[task2], city=city, start_date=start_date, end_date=end_date)
        task_list.append(task3)
        agent_list.append(reporter)
    
    if send_alerts:
        task4 = tasks.alert_task(alert_manager, context=[task2], city=city)
        task_list.append(task4)
        agent_list.append(alert_manager)

    # Create Crew
    crew = Crew(
        agents=agent_list,
        tasks=task_list,
        process=Process.sequential,
        verbose=True
    )

    try:
        result = crew.kickoff()
        return result
    except Exception as e:
        print(f"Crew execution failed: {e}")
        raise e
