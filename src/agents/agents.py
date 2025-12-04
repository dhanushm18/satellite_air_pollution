"""
AI Agents for Agentic Air Quality Monitor
4 specialized agents working together autonomously
"""
from crewai import Agent, Task, Crew, Process
from .tools import satellite_search_tool, analysis_tool, notification_tool, report_generator_tool
import os

# Define Agents
class SatelliteAgents:
    def scout_agent(self, callback=None):
        return Agent(
            role='Satellite Data Scout',
            goal='Retrieve the latest satellite NO2 pollution data for target cities',
            backstory='You are an expert in remote sensing and atmospheric data. Your job is to fetch accurate NO2 pollution levels from Sentinel-5P satellites. You prioritize getting the actual data values over raw imagery.',
            tools=[satellite_search_tool],
            verbose=True,
            allow_delegation=False,
            step_callback=callback
        )

    def analyst_agent(self, callback=None): 
        return Agent(
            role='Air Quality Analyst',
            goal='Analyze pollution data to determine air quality levels and health risks and perdict the current data',
            backstory='You are a seasoned environmental scientist. You interpret NO2 levelss air quality severity and potential health impacts.',
            tools=[analysis_tool],
            verbose=True,
            allow_delegation=False,
            step_callback=callback
        )

    def reporter_agent(self, callback=None):
        return Agent(
            role='Environmental Reporter',
            goal='Create comprehensive reports based on pollution data',
            backstory='You are a science communicator who can translate complex pollution data into clear, easy-to-understand reports for the general public and policy makers.',
            tools=[report_generator_tool],
            verbose=True,
            allow_delegation=False,
            step_callback=callback
        )
    
    def alert_agent(self, callback=None):
        return Agent(
            role='Alert Manager',
            goal='Send timely notifications about air quality conditions to stakeholders',
            backstory='You are responsible for keeping people informed about air quality. You send alerts via Pushover when pollution levels are concerning.',
            tools=[notification_tool],
            verbose=True,
            allow_delegation=False,
            step_callback=callback
        )

# Define Tasks
class SatelliteTasks:
    def search_task(self, agent, city, start_date, end_date):
        return Task(
            description=f'Retrieve Sentinel-5P NO2 pollution data for {city} between {start_date} and {end_date}. Focus on obtaining the NO2 column number density values.',
            agent=agent,
            expected_output='The absolute path to the saved JSON data file.'
        )

    def analysis_task(self, agent, context, city):
        return Task(
            description=f'''Analyze the retrieved NO2 data for {city}. 
            The output of the previous task IS the absolute file path to the JSON data. 
            You MUST use that EXACT path string as the "file_path" argument for the "Analyze Air Quality" tool. 
            Do not modify the path or use a placeholder.

            After getting the analysis results, compare the values with the following expected ranges for today:
            - Delhi: 40 – 130 µg/m³
            - Mumbai: 30 – 50 µg/m³
            - Bengaluru: below ~ 40 µg/m³

            Explicitly state if the current values for {city} are within, above, or below these expected ranges.
            ''',
            agent=agent,
            context=context,
            expected_output='Analysis results text containing "Average NO2", "Peak NO2", category, and range comparison.'
        )

    def report_task(self, agent, context, city, start_date, end_date):
        return Task(
            description=f'''Generate comprehensive regulatory reports for {city}.
            
1. Read the analysis results from the previous task.
2. Extract the "Average NO2" value (number only).
3. Extract the "Peak NO2" value (number only).
4. Extract the category (e.g., Good, Moderate).
5. Call the "Generate Regulatory Reports" tool with these values.
''',
            agent=agent,
            context=context,
            expected_output='Paths to the generated PDF reports.'
        )
    
    def alert_task(self, agent, context, city):
        return Task(
            description=f'''Send notifications about air quality in {city}.
            
1. Read the analysis results.
2. Extract the "Average NO2" value and category.
3. Call the "Send Pushover Notification" tool. Do NOT provide a "date" argument; let the tool use the default.
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
        send_alerts: Whether to send Pushover notifications
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
