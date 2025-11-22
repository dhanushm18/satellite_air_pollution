"""
AI Agents for Agentic Air Quality Monitor
4 specialized agents working together autonomously
"""
from crewai import Agent, Task, Crew, Process
from .tools import satellite_search_tool, analysis_tool, notification_tool, report_generator_tool
import os

# Define Agents
class SatelliteAgents:
    def scout_agent(self):
        return Agent(
            role='Satellite Data Scout',
            goal='Find and download the latest satellite imagery for target cities',
            backstory='You are an expert in remote sensing and satellite data acquisition. Your job is to scour the archives (Earth Engine) to find the best, cloud-free images for analysis.',
            tools=[satellite_search_tool],
            verbose=True,
            allow_delegation=False
        )

    def analyst_agent(self):
        return Agent(
            role='Air Quality Analyst',
            goal='Analyze satellite data to determine air quality levels and identify pollution hotspots',
            backstory='You are a seasoned environmental scientist. You take raw satellite data and turn it into actionable insights about air quality.',
            tools=[analysis_tool],
            verbose=True,
            allow_delegation=False
        )

    def reporter_agent(self):
        return Agent(
            role='Environmental Reporter',
            goal='Create comprehensive reports based on analysis findings',
            backstory='You are a science communicator who can translate complex data into clear, easy-to-understand reports for the general public and policy makers.',
            tools=[report_generator_tool],
            verbose=True,
            allow_delegation=False
        )
    
    def alert_agent(self):
        return Agent(
            role='Alert Manager',
            goal='Send timely notifications about air quality conditions to stakeholders',
            backstory='You are responsible for keeping people informed about air quality. You send alerts via Pushover when pollution levels are concerning.',
            tools=[notification_tool],
            verbose=True,
            allow_delegation=False
        )

# Define Tasks
class SatelliteTasks:
    def search_task(self, agent, city, start_date, end_date):
        return Task(
            description=f'Search for and download Sentinel-5P NO2 data for {city} between {start_date} and {end_date}. Ensure the data is downloaded successfully.',
            agent=agent,
            expected_output='A confirmation message with the path to the downloaded GeoTIFF file.'
        )

    def analysis_task(self, agent, context):
        return Task(
            description='Analyze the downloaded satellite data. Calculate average and peak NO2 levels, and categorize the air quality. Use the file path provided by the previous task.',
            agent=agent,
            context=context,
            expected_output='A detailed analysis of the air quality, including specific numbers and a category (e.g., Good, Moderate, Severe).'
        )

    def report_task(self, agent, context, city, start_date, end_date):
        return Task(
            description=f'''Generate comprehensive regulatory reports for {city} covering {start_date} to {end_date}.
            
IMPORTANT: Extract the numeric NO2 values from the analysis results:
- Find the "Average NO2" value (in µg/m³) and use it as avg_no2
- Find the "Peak NO2" value (in µg/m³) and use it as max_no2
- Find the category (Good/Moderate/Poor/Very Poor/Severe)

Then call the report generator tool with these extracted values.
Example: If analysis shows "Average NO2: 45.23 µg/m³", use avg_no2=45.23

Generate both the regulatory compliance report and prevention guide.''',
            agent=agent,
            context=context,
            expected_output='Paths to generated PDF reports (regulatory report and prevention guide).'
        )
    
    def alert_task(self, agent, context, city):
        return Task(
            description=f'''Send notifications about air quality in {city}.
            
IMPORTANT: Extract these values from the analysis results:
- Find the "Average NO2" value (in µg/m³) and use it as no2_level
- Find the category (Good/Moderate/Poor/Very Poor/Severe)

Then call the notification tool with: city="{city}", no2_level=<extracted_value>, category="<extracted_category>"
Example: If analysis shows "Average NO2: 45.23 µg/m³ (Moderate)", use no2_level=45.23, category="Moderate"

Send both Pushover and Email notifications.''',
            agent=agent,
            context=context,
            expected_output='Confirmation that the notification was sent successfully.'
        )

# Crew Manager
def run_satellite_crew(city, start_date, end_date, send_alerts=True, generate_reports=True):
    """
    Run the complete satellite monitoring crew
    
    Args:
        city: City name
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        send_alerts: Whether to send Pushover notifications
        generate_reports: Whether to generate PDF reports
    """
    agents = SatelliteAgents()
    tasks = SatelliteTasks()

    # Instantiate Agents
    scout = agents.scout_agent()
    analyst = agents.analyst_agent()
    reporter = agents.reporter_agent()
    alert_manager = agents.alert_agent()

    # Instantiate Tasks
    task1 = tasks.search_task(scout, city, start_date, end_date)
    task2 = tasks.analysis_task(analyst, context=[task1])
    
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

    result = crew.kickoff()
    return result
