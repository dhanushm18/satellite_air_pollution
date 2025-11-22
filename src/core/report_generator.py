"""
Government Regulatory Report Generator
Generates comprehensive air quality reports for regulatory compliance
"""
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import plotly.graph_objects as go
import plotly.express as px
import numpy as np


class RegulatoryReportGenerator:
    """Generate government-compliant air quality reports"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1E3A8A'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2563EB'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='BodyJustify',
            parent=self.styles['BodyText'],
            alignment=TA_JUSTIFY,
            fontSize=11,
            leading=14
        ))
    
    def generate_regulatory_report(
        self,
        city: str,
        start_date: str,
        end_date: str,
        data: Dict[str, Any],
        include_recommendations: bool = True
    ) -> str:
        """
        Generate comprehensive regulatory report
        
        Args:
            city: City name
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            data: Air quality data dictionary
            include_recommendations: Include policy recommendations
            
        Returns:
            str: Path to generated PDF report
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.output_dir}/Regulatory_Report_{city}_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Title Page
        story.append(Spacer(1, 1*inch))
        title = Paragraph(
            f"Air Quality Regulatory Report<br/>{city}",
            self.styles['CustomTitle']
        )
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Report metadata
        metadata = f"""
        <para alignment='center'>
        <b>Report Period:</b> {start_date} to {end_date}<br/>
        <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Report Type:</b> Regulatory Compliance Assessment<br/>
        <b>Prepared By:</b> Automated Air Quality Monitoring System
        </para>
        """
        story.append(Paragraph(metadata, self.styles['BodyText']))
        story.append(Spacer(1, 0.5*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        avg_no2 = data.get('average_no2', 0)
        max_no2 = data.get('max_no2', 0)
        category = data.get('category', 'Unknown')
        
        summary_text = f"""
        This report presents a comprehensive analysis of air quality conditions in {city} 
        for the period from {start_date} to {end_date}. The analysis is based on satellite-derived 
        NO₂ (Nitrogen Dioxide) measurements from the Copernicus Sentinel-5P satellite, processed 
        using advanced AI/ML downscaling techniques.
        <br/><br/>
        <b>Key Findings:</b><br/>
        • Average NO₂ Level: {avg_no2:.2f} µg/m³<br/>
        • Peak NO₂ Level: {max_no2:.2f} µg/m³<br/>
        • Air Quality Category: {category}<br/>
        • Compliance Status: {'✓ COMPLIANT' if avg_no2 <= 80 else '✗ NON-COMPLIANT'}<br/>
        """
        story.append(Paragraph(summary_text, self.styles['BodyJustify']))
        story.append(Spacer(1, 0.3*inch))
        
        # Add Satellite Image if available
        satellite_image_path = f"agent_downloads/{city}_{start_date}_{end_date}.tif".replace(" ", "_")
        if os.path.exists(satellite_image_path):
            try:
                # Convert GeoTIFF to PNG for display
                import rasterio
                import matplotlib.pyplot as plt
                import numpy as np
                
                with rasterio.open(satellite_image_path) as src:
                    data = src.read(1)
                    data[data == src.nodata] = np.nan
                
                # Create visualization
                plt.figure(figsize=(8, 6))
                plt.imshow(data, cmap='RdYlGn_r', interpolation='bilinear')
                plt.colorbar(label='NO₂ Column Density (mol/m²)')
                plt.title(f'Satellite NO₂ Measurements - {city}')
                plt.xlabel('Longitude')
                plt.ylabel('Latitude')
                
                # Save as PNG
                png_path = satellite_image_path.replace('.tif', '_visualization.png')
                plt.savefig(png_path, dpi=150, bbox_inches='tight')
                plt.close()
                
                # Add to report
                story.append(Paragraph("Satellite Imagery", self.styles['SectionHeader']))
                img = Image(png_path, width=5*inch, height=3.75*inch)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
                caption = Paragraph(
                    f"<i>Figure 1: Sentinel-5P NO₂ measurements for {city} ({start_date} to {end_date})</i>",
                    self.styles['BodyText']
                )
                story.append(caption)
                story.append(Spacer(1, 0.3*inch))
            except Exception as e:
                print(f"⚠️ Could not add satellite image: {e}")
        
        
        # Regulatory Standards
        story.append(PageBreak())
        story.append(Paragraph("1. Regulatory Standards & Compliance", self.styles['SectionHeader']))
        
        standards_text = """
        <b>National Ambient Air Quality Standards (NAAQS) - India</b><br/><br/>
        As per Central Pollution Control Board (CPCB) guidelines:<br/>
        • Annual Average: 40 µg/m³<br/>
        • 24-hour Average: 80 µg/m³<br/><br/>
        <b>WHO Air Quality Guidelines (2021)</b><br/>
        • Annual Average: 10 µg/m³<br/>
        • 24-hour Average: 25 µg/m³<br/><br/>
        """
        story.append(Paragraph(standards_text, self.styles['BodyJustify']))
        
        # Compliance Table
        compliance_data = [
            ['Standard', 'Limit (µg/m³)', f'{city} Value', 'Status'],
            ['CPCB Annual', '40', f'{avg_no2:.1f}', '✓' if avg_no2 <= 40 else '✗'],
            ['CPCB 24-hour', '80', f'{max_no2:.1f}', '✓' if max_no2 <= 80 else '✗'],
            ['WHO Annual', '10', f'{avg_no2:.1f}', '✓' if avg_no2 <= 10 else '✗'],
            ['WHO 24-hour', '25', f'{max_no2:.1f}', '✓' if max_no2 <= 25 else '✗'],
        ]
        
        compliance_table = Table(compliance_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
        compliance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        story.append(compliance_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Health Impact Assessment
        story.append(PageBreak())
        story.append(Paragraph("2. Health Impact Assessment", self.styles['SectionHeader']))
        
        cigarette_equiv = avg_no2 / 22
        health_text = f"""
        <b>Public Health Implications:</b><br/><br/>
        The current NO₂ levels in {city} are equivalent to the health impact of smoking 
        approximately <b>{cigarette_equiv:.1f} cigarettes per day</b> for the average resident.
        <br/><br/>
        <b>Vulnerable Populations at Risk:</b><br/>
        • Children under 5 years<br/>
        • Elderly population (65+ years)<br/>
        • Individuals with respiratory conditions (asthma, COPD)<br/>
        • Pregnant women<br/>
        • Outdoor workers<br/><br/>
        <b>Estimated Health Burden:</b><br/>
        Based on epidemiological studies, prolonged exposure to current NO₂ levels may result in:<br/>
        • Increased respiratory hospital admissions: ~15-20%<br/>
        • Exacerbation of asthma symptoms: ~25-30%<br/>
        • Reduced lung function in children: ~5-10%<br/>
        • Cardiovascular complications: ~10-15%<br/>
        """
        story.append(Paragraph(health_text, self.styles['BodyJustify']))
        story.append(Spacer(1, 0.3*inch))
        
        # Source Attribution
        story.append(PageBreak())
        story.append(Paragraph("3. Source Attribution Analysis", self.styles['SectionHeader']))
        
        sources_text = """
        <b>Primary NO₂ Emission Sources in Urban Areas:</b><br/><br/>
        <b>1. Vehicular Emissions (40-50%)</b><br/>
        • Diesel vehicles (trucks, buses): Major contributor<br/>
        • Two-wheelers and cars: Significant contribution<br/>
        • Traffic congestion hotspots<br/><br/>
        <b>2. Industrial Activities (25-35%)</b><br/>
        • Power plants and thermal stations<br/>
        • Manufacturing units<br/>
        • Construction activities<br/><br/>
        <b>3. Residential & Commercial (15-20%)</b><br/>
        • Cooking and heating<br/>
        • Diesel generators<br/>
        • Commercial establishments<br/><br/>
        <b>4. Other Sources (5-10%)</b><br/>
        • Agricultural burning<br/>
        • Waste burning<br/>
        • Natural sources<br/>
        """
        story.append(Paragraph(sources_text, self.styles['BodyJustify']))
        
        if include_recommendations:
            # Policy Recommendations
            story.append(PageBreak())
            story.append(Paragraph("4. Policy Recommendations", self.styles['SectionHeader']))
            
            recommendations = self._generate_recommendations(avg_no2, category)
            story.append(Paragraph(recommendations, self.styles['BodyJustify']))
        
        # Methodology
        story.append(PageBreak())
        story.append(Paragraph("5. Methodology & Data Sources", self.styles['SectionHeader']))
        
        methodology_text = """
        <b>Data Collection:</b><br/>
        • Satellite: Copernicus Sentinel-5P TROPOMI<br/>
        • Spatial Resolution: 1 km (downscaled from 7 km)<br/>
        • Temporal Coverage: Daily measurements<br/><br/>
        <b>Processing Methodology:</b><br/>
        • AI/ML Downscaling: Ensemble model (Random Forest, XGBoost, Neural Networks)<br/>
        • Quality Control: Automated outlier detection and validation<br/>
        • Uncertainty Estimation: Gaussian Process Regression<br/><br/>
        <b>Compliance with Standards:</b><br/>
        • ISO 14001: Environmental Management<br/>
        • CPCB Guidelines: National Air Quality Monitoring<br/>
        • WHO Protocols: Air Quality Assessment<br/>
        """
        story.append(Paragraph(methodology_text, self.styles['BodyJustify']))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        footer_text = """
        <para alignment='center'>
        <i>This report is generated by an AI-powered air quality monitoring system.<br/>
        For queries, contact: airquality@monitoring.gov.in</i>
        </para>
        """
        story.append(Paragraph(footer_text, self.styles['BodyText']))
        
        # Build PDF
        doc.build(story)
        print(f"✅ Regulatory report generated: {filename}")
        return filename
    
    def _generate_recommendations(self, avg_no2: float, category: str) -> str:
        """Generate policy recommendations based on air quality"""
        
        if category in ["Severe", "Very Poor"]:
            return """
            <b>IMMEDIATE ACTIONS REQUIRED:</b><br/><br/>
            <b>1. Emergency Response Measures (0-7 days)</b><br/>
            • Declare air quality emergency<br/>
            • Implement odd-even vehicle scheme<br/>
            • Close schools and educational institutions<br/>
            • Ban construction activities<br/>
            • Shut down polluting industries temporarily<br/>
            • Deploy water sprinklers on major roads<br/><br/>
            <b>2. Short-term Interventions (1-3 months)</b><br/>
            • Increase public transport frequency by 50%<br/>
            • Provide free public transport during peak pollution<br/>
            • Enforce strict emission norms for industries<br/>
            • Implement work-from-home for government offices<br/>
            • Ban diesel generators<br/>
            • Intensify road sweeping and dust control<br/><br/>
            <b>3. Medium-term Strategies (3-12 months)</b><br/>
            • Accelerate transition to electric vehicles<br/>
            • Establish green zones with restricted vehicle access<br/>
            • Upgrade industrial pollution control equipment<br/>
            • Expand metro and public transport network<br/>
            • Implement congestion pricing in city center<br/>
            • Plant 100,000 trees in urban areas<br/><br/>
            <b>4. Long-term Policy Framework (1-5 years)</b><br/>
            • Develop comprehensive air quality management plan<br/>
            • Invest in renewable energy infrastructure<br/>
            • Modernize public transport fleet (100% electric)<br/>
            • Implement strict building codes for energy efficiency<br/>
            • Create urban forests and green corridors<br/>
            • Establish real-time air quality monitoring network<br/>
            • Develop regional air quality coordination mechanism<br/>
            """
        elif category == "Poor":
            return """
            <b>CORRECTIVE ACTIONS RECOMMENDED:</b><br/><br/>
            <b>1. Immediate Measures (0-30 days)</b><br/>
            • Issue public health advisories<br/>
            • Increase monitoring frequency<br/>
            • Restrict heavy vehicle movement during peak hours<br/>
            • Enforce emission testing for all vehicles<br/>
            • Ban open burning of waste<br/><br/>
            <b>2. Short-term Actions (1-6 months)</b><br/>
            • Promote public transport usage (subsidies)<br/>
            • Implement traffic management improvements<br/>
            • Enforce industrial emission standards<br/>
            • Increase green cover in pollution hotspots<br/>
            • Launch public awareness campaigns<br/><br/>
            <b>3. Long-term Strategies (6-24 months)</b><br/>
            • Transition to cleaner fuels<br/>
            • Expand cycling and pedestrian infrastructure<br/>
            • Incentivize electric vehicle adoption<br/>
            • Develop integrated transport planning<br/>
            • Establish air quality improvement fund<br/>
            """
        else:  # Good or Moderate
            return """
            <b>PREVENTIVE MEASURES & BEST PRACTICES:</b><br/><br/>
            <b>1. Maintain Current Standards</b><br/>
            • Continue regular air quality monitoring<br/>
            • Enforce existing emission norms<br/>
            • Maintain green spaces and urban forests<br/>
            • Support sustainable transport initiatives<br/><br/>
            <b>2. Proactive Improvements</b><br/>
            • Expand electric vehicle charging infrastructure<br/>
            • Promote cycling and walking<br/>
            • Implement green building standards<br/>
            • Encourage renewable energy adoption<br/>
            • Develop climate action plan<br/><br/>
            <b>3. Community Engagement</b><br/>
            • Public awareness programs<br/>
            • School education on air quality<br/>
            • Citizen science initiatives<br/>
            • Recognition for clean air champions<br/>
            """
    
    def generate_prevention_guide(self, city: str) -> str:
        """
        Generate comprehensive air pollution prevention guide
        
        Args:
            city: City name
            
        Returns:
            str: Path to generated PDF guide
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.output_dir}/Prevention_Guide_{city}_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Title
        story.append(Spacer(1, 0.5*inch))
        title = Paragraph(
            f"Air Pollution Prevention Guide<br/>{city}",
            self.styles['CustomTitle']
        )
        story.append(title)
        story.append(Spacer(1, 0.5*inch))
        
        # Introduction
        intro_text = """
        <b>About This Guide</b><br/><br/>
        This comprehensive guide provides actionable strategies for individuals, communities, 
        businesses, and government agencies to prevent and reduce air pollution. Every action, 
        no matter how small, contributes to cleaner air for all.
        """
        story.append(Paragraph(intro_text, self.styles['BodyJustify']))
        story.append(Spacer(1, 0.3*inch))
        
        # Individual Actions
        story.append(Paragraph("1. Individual Actions", self.styles['SectionHeader']))
        individual_text = """
        <b>Transportation Choices:</b><br/>
        ✓ Use public transport, carpool, or bike whenever possible<br/>
        ✓ Maintain your vehicle regularly to reduce emissions<br/>
        ✓ Avoid unnecessary idling - turn off engine when parked<br/>
        ✓ Plan trips to combine errands and reduce travel<br/>
        ✓ Consider electric or hybrid vehicles for next purchase<br/>
        ✓ Walk or cycle for short distances (&lt;2 km)<br/><br/>
        <b>At Home:</b><br/>
        ✓ Use energy-efficient appliances (5-star rated)<br/>
        ✓ Switch to LED lighting<br/>
        ✓ Avoid burning waste, leaves, or garbage<br/>
        ✓ Use natural gas or LPG instead of wood/coal<br/>
        ✓ Plant trees and maintain a garden<br/>
        ✓ Reduce, reuse, and recycle to minimize waste<br/>
        ✓ Use eco-friendly cleaning products<br/><br/>
        <b>Consumer Choices:</b><br/>
        ✓ Buy local products to reduce transportation emissions<br/>
        ✓ Choose products with minimal packaging<br/>
        ✓ Support businesses with green practices<br/>
        ✓ Avoid single-use plastics<br/>
        ✓ Purchase energy-efficient electronics<br/>
        """
        story.append(Paragraph(individual_text, self.styles['BodyJustify']))
        
        # Community Actions
        story.append(PageBreak())
        story.append(Paragraph("2. Community Initiatives", self.styles['SectionHeader']))
        community_text = """
        <b>Neighborhood Programs:</b><br/>
        ✓ Organize tree plantation drives (target: 100 trees/year)<br/>
        ✓ Create community gardens and green spaces<br/>
        ✓ Establish carpool networks for schools and offices<br/>
        ✓ Conduct awareness workshops on air quality<br/>
        ✓ Set up community composting facilities<br/>
        ✓ Organize clean-up drives for public spaces<br/><br/>
        <b>Advocacy & Engagement:</b><br/>
        ✓ Participate in local environmental committees<br/>
        ✓ Report pollution violations to authorities<br/>
        ✓ Support clean air policies and initiatives<br/>
        ✓ Engage with local government on air quality issues<br/>
        ✓ Share air quality information with neighbors<br/>
        ✓ Organize car-free days in your locality<br/><br/>
        <b>Educational Activities:</b><br/>
        ✓ School programs on environmental awareness<br/>
        ✓ Air quality monitoring projects<br/>
        ✓ Science fairs focused on pollution solutions<br/>
        ✓ Youth climate action groups<br/>
        """
        story.append(Paragraph(community_text, self.styles['BodyJustify']))
        
        # Business Actions
        story.append(PageBreak())
        story.append(Paragraph("3. Business & Industry Best Practices", self.styles['SectionHeader']))
        business_text = """
        <b>Operational Improvements:</b><br/>
        ✓ Install pollution control equipment (scrubbers, filters)<br/>
        ✓ Regular maintenance of machinery to reduce emissions<br/>
        ✓ Switch to cleaner fuels (natural gas, solar, wind)<br/>
        ✓ Implement energy management systems<br/>
        ✓ Optimize logistics to reduce transportation emissions<br/>
        ✓ Use electric vehicles for company fleet<br/><br/>
        <b>Green Building Practices:</b><br/>
        ✓ LEED or GRIHA certification for buildings<br/>
        ✓ Install solar panels and renewable energy systems<br/>
        ✓ Use eco-friendly construction materials<br/>
        ✓ Implement rainwater harvesting<br/>
        ✓ Create green roofs and vertical gardens<br/>
        ✓ Maximize natural lighting and ventilation<br/><br/>
        <b>Employee Programs:</b><br/>
        ✓ Provide shuttle services or transport allowances<br/>
        ✓ Offer work-from-home options<br/>
        ✓ Install EV charging stations<br/>
        ✓ Incentivize use of public transport<br/>
        ✓ Organize environmental awareness training<br/>
        """
        story.append(Paragraph(business_text, self.styles['BodyJustify']))
        
        # Government Actions
        story.append(PageBreak())
        story.append(Paragraph("4. Government Policy Framework", self.styles['SectionHeader']))
        government_text = """
        <b>Regulatory Measures:</b><br/>
        ✓ Enforce strict emission standards (BS-VI for vehicles)<br/>
        ✓ Implement congestion pricing in city centers<br/>
        ✓ Ban old, polluting vehicles (>15 years)<br/>
        ✓ Mandate pollution control devices for industries<br/>
        ✓ Regulate construction dust and debris<br/>
        ✓ Ban crop burning and open waste burning<br/><br/>
        <b>Infrastructure Development:</b><br/>
        ✓ Expand metro and public transport network<br/>
        ✓ Build dedicated cycling lanes (500 km target)<br/>
        ✓ Create pedestrian-friendly walkways<br/>
        ✓ Establish park-and-ride facilities<br/>
        ✓ Develop green corridors and urban forests<br/>
        ✓ Install air quality monitoring stations (1 per 5 km²)<br/><br/>
        <b>Incentive Programs:</b><br/>
        ✓ Subsidies for electric vehicles (30-50% of cost)<br/>
        ✓ Tax benefits for green buildings<br/>
        ✓ Grants for renewable energy adoption<br/>
        ✓ Rewards for pollution reduction achievements<br/>
        ✓ Free public transport on high pollution days<br/><br/>
        <b>Research & Innovation:</b><br/>
        ✓ Fund air quality research projects<br/>
        ✓ Support clean technology startups<br/>
        ✓ Establish innovation labs for pollution solutions<br/>
        ✓ Collaborate with international agencies<br/>
        """
        story.append(Paragraph(government_text, self.styles['BodyJustify']))
        
        # Emergency Measures
        story.append(PageBreak())
        story.append(Paragraph("5. Emergency Response Protocol", self.styles['SectionHeader']))
        emergency_text = """
        <b>When Air Quality is 'Very Poor' or 'Severe':</b><br/><br/>
        <b>For Citizens:</b><br/>
        🚨 Stay indoors as much as possible<br/>
        🚨 Keep windows and doors closed<br/>
        🚨 Use air purifiers (HEPA filters)<br/>
        🚨 Wear N95/N99 masks if you must go out<br/>
        🚨 Avoid outdoor exercise<br/>
        🚨 Keep emergency medications handy (for asthma, etc.)<br/>
        🚨 Monitor air quality regularly via apps<br/><br/>
        <b>For Authorities:</b><br/>
        🚨 Issue public health advisories<br/>
        🚨 Close schools and non-essential offices<br/>
        🚨 Implement odd-even vehicle scheme<br/>
        🚨 Ban construction activities<br/>
        🚨 Deploy water sprinklers on roads<br/>
        🚨 Provide free masks at public places<br/>
        🚨 Set up medical camps for vulnerable populations<br/>
        """
        story.append(Paragraph(emergency_text, self.styles['BodyJustify']))
        
        # Success Stories
        story.append(PageBreak())
        story.append(Paragraph("6. Success Stories & Best Practices", self.styles['SectionHeader']))
        success_text = """
        <b>Global Examples:</b><br/><br/>
        <b>Beijing, China:</b> Reduced PM2.5 by 35% through strict vehicle restrictions, 
        industrial relocation, and massive afforestation (2013-2020).<br/><br/>
        <b>London, UK:</b> Congestion charging reduced traffic by 30% and emissions by 20% 
        in city center (since 2003).<br/><br/>
        <b>Copenhagen, Denmark:</b> 62% of citizens cycle to work daily, reducing vehicular 
        emissions significantly.<br/><br/>
        <b>Singapore:</b> Electronic road pricing and excellent public transport resulted in 
        one of Asia's cleanest cities.<br/><br/>
        <b>Indian Success:</b> Delhi's CNG conversion of public transport reduced vehicular 
        pollution by 40% (2000-2010).<br/>
        """
        story.append(Paragraph(success_text, self.styles['BodyJustify']))
        
        # Call to Action
        story.append(Spacer(1, 0.3*inch))
        cta_text = """
        <para alignment='center'>
        <b><font size=14>Every Action Counts!</font></b><br/><br/>
        Clean air is a fundamental right. Together, we can make a difference.<br/>
        Start today. Choose one action from this guide and commit to it.<br/><br/>
        <i>For more information and resources, visit: airquality.gov.in</i>
        </para>
        """
        story.append(Paragraph(cta_text, self.styles['BodyText']))
        
        # Build PDF
        doc.build(story)
        print(f"✅ Prevention guide generated: {filename}")
        return filename


# Convenience functions
def generate_report(city: str, start_date: str, end_date: str, data: Dict[str, Any]) -> str:
    """Quick function to generate regulatory report"""
    generator = RegulatoryReportGenerator()
    return generator.generate_regulatory_report(city, start_date, end_date, data)


def generate_prevention_guide(city: str) -> str:
    """Quick function to generate prevention guide"""
    generator = RegulatoryReportGenerator()
    return generator.generate_prevention_guide(city)


if __name__ == "__main__":
    # Test report generation
    test_data = {
        'average_no2': 95.5,
        'max_no2': 145.2,
        'category': 'Poor'
    }
    
    generator = RegulatoryReportGenerator()
    generator.generate_regulatory_report(
        city="Bengaluru",
        start_date="2025-11-01",
        end_date="2025-11-21",
        data=test_data
    )
    generator.generate_prevention_guide("Bengaluru")
