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
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from pypdf import PdfReader, PdfWriter
try:
    from docxtpl import DocxTemplate
except ImportError:
    pass


class RegulatoryReportGenerator:
    """Generate government-compliant air quality reports"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for official documents"""
        # Title Style (Official)
        self.styles.add(ParagraphStyle(
            name='OfficialTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.black,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Times-Bold',
            leading=28
        ))
        
        # Subtitle/Dept Name
        self.styles.add(ParagraphStyle(
            name='OfficialSubtitle',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.black,
            alignment=TA_CENTER,
            fontName='Times-Roman',
            spaceAfter=30,
            textTransform='uppercase',
            letterSpacing=2
        ))
        
        # Section Headers
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1a1a1a'),
            spaceBefore=15,
            spaceAfter=10,
            fontName='Times-Bold',
            borderPadding=5,
            borderWidth=0,
            borderColor=colors.black,
            backColor=None,
            borderBottomWidth=1 # Underline effect manually done via layout if needed, or simple line
        ))
        
        # Body Text (Formal)
        self.styles.add(ParagraphStyle(
            name='FormalBody',
            parent=self.styles['BodyText'],
            alignment=TA_JUSTIFY,
            fontSize=11,
            leading=15,
            fontName='Times-Roman',
            spaceAfter=10
        ))
        
        # Metric Value
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            alignment=TA_CENTER,
            fontSize=12,
            fontName='Helvetica-Bold'
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
        Generate comprehensive regulatory report with official formatting
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.output_dir}/Regulatory_Report_{city}_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        
        story = []
        
        # --- Official Banner Header (Compact) ---
        from reportlab.graphics.shapes import Drawing, Rect, String
        from reportlab.lib import colors as rcolors

        # Blue Banner
        d = Drawing(500, 80)
        d.add(Rect(-50, 0, 600, 80, fillColor=colors.HexColor('#1a237e'), strokeColor=None))
        
        # Header Text inside Banner
        d.add(String(250, 50, "NATIONAL AIR QUALITY MONITORING BUREAU", 
                     textAnchor='middle', fontName='Times-Bold', fontSize=16, fillColor=colors.white))
        d.add(String(250, 30, "MINISTRY OF ENVIRONMENT & FORESTS | GOVT. OF INDIA", 
                     textAnchor='middle', fontName='Times-Roman', fontSize=10, fillColor=colors.white))
        
        story.append(d)
        story.append(Spacer(1, 0.3*inch))
        
        # Title (Normal)
        story.append(Paragraph(f"AIR QUALITY REGULATORY<br/>COMPLIANCE REPORT", self.styles['OfficialTitle']))
        story.append(Paragraph(f"JURISDICTION: {city.upper()}", 
                               ParagraphStyle('Su', parent=self.styles['OfficialSubtitle'], fontSize=10, spaceAfter=10)))
        
        # --- Metadata Table ---
        # 2-column table for aligned metadata
        meta_data = [
            ['REPORT NUMBER:', f'AQI-{timestamp}-{city[:3].upper()}'],
            ['DATE OF ISSUE:', datetime.now().strftime('%B %d, %Y')],
            ['MONITORING PERIOD:', f'{start_date} to {end_date}'],
            ['REPORTING AUTHORITY:', 'Autonomous AI Agent System'],
            ['CONTACT:', 'compliance@naqmb.gov.in']
        ]
        
        meta_table = Table(meta_data, colWidths=[200, 300])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Times-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey) # Light grid
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 0.3*inch))
        
        # --- Dashboard Row (Metrics + Map) ---
        # Prepare Metrics Table
        try:
            aqi = float(data.get('aqi', 0))
            cigarettes = float(data.get('cigarettes', 0))
        except:
            aqi, cigarettes = 0, 0
        category = data.get('category', 'Unknown')
        
        aqi_color = colors.green
        if aqi > 100: aqi_color = colors.orange
        if aqi > 200: aqi_color = colors.red
        if aqi > 400: aqi_color = colors.maroon

        metric_data = [
            ['PARAMETER', 'VALUE', 'STATUS'],
            ['AQI', f'{int(aqi)}', category],
            ['Toxicity', f'{cigarettes:.1f} Cigs/Day', 'CRIT' if cigarettes > 5 else 'MOD']
        ]
        
        metric_table = Table(metric_data, colWidths=[90, 80, 70])
        metric_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#283593')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
            ('TEXTCOLOR', (1, 1), (1, 1), aqi_color),
            ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 1), (1, 1), 12),
        ]))
        
        # Prepare Satellite Image
        viz_flowable = Paragraph("<b>No Data</b>", self.styles['Normal'])
        satellite_image_path = f"agents_downloads/{city}_{start_date}_{end_date}.tif".replace(" ", "_")
        if os.path.exists(satellite_image_path):
            try:
                import rasterio
                import matplotlib
                matplotlib.use('Agg')
                import matplotlib.pyplot as plt
                import numpy as np
                
                with rasterio.open(satellite_image_path) as src:
                    d = src.read(1)
                    d[d == src.nodata] = np.nan
                
                plt.figure(figsize=(5, 3.5)) # Normal figure
                plt.imshow(d, cmap='RdYlGn_r', interpolation='bilinear')
                plt.axis('off')
                plt.tight_layout(pad=0)
                
                png_path = satellite_image_path.replace('.tif', '_viz_small.png')
                plt.savefig(png_path, dpi=120, bbox_inches='tight')
                plt.close()
                viz_flowable = Image(png_path, width=3*inch, height=2*inch)
            except: pass

        # Combine into Parent Table using Nested Tables for vertical stacking in cells
        # Left Cell: Metrics
        # We wrap contents in a sub-table to stack Header + Content vertically
        sub_metrics = [
            [Paragraph("KEY METRICS", self.styles['SectionHeader'])],
            [metric_table]
        ]
        t_metrics = Table(sub_metrics, colWidths=[250])
        t_metrics.setStyle(TableStyle([
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0)
        ]))
        
        # Right Cell: Map
        sub_viz = [
            [Paragraph("SATELLITE DATA", self.styles['SectionHeader'])],
            [viz_flowable]
        ]
        t_viz = Table(sub_viz, colWidths=[250])
        t_viz.setStyle(TableStyle([
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0)
        ]))

        dashboard_data = [[t_metrics, t_viz]]
        
        dashboard_table = Table(dashboard_data, colWidths=[250, 250])
        dashboard_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(dashboard_table)
        story.append(Spacer(1, 0.3*inch))

        # --- Compliance Table ---
        # Extract Pollutant Data
        print(f"DEBUG: Pollutant Data received: {data.get('pollutants')}")
        pollutants = data.get('pollutants', {})
        def get_conc(pollutant, key, factor):
            try:
                val = float(pollutants.get(pollutant, {}).get(key, 0))
                return val * factor
            except:
                return 0.0

        avg_no2 = get_conc('no2', 'mean_mol', 250000)
        max_no2 = get_conc('no2', 'max_mol', 250000)
        avg_so2 = get_conc('so2', 'mean_mol', 250000)
        avg_co  = get_conc('co', 'mean_mol', 90000)
        avg_o3  = get_conc('o3', 'mean_mol', 210000)

        story.append(Paragraph("3. COMPLIANCE DATA TABLE", self.styles['SectionHeader']))
        
        comp_data = [
            ['POLLUTANT', 'STANDARD (µg/m³)', 'OBSERVED (µg/m³)', 'COMPLIANCE'],
            ['Nitrogen Dioxide (NO₂)', '80 (24h)', f'{max_no2:.2f}', 'PASS' if max_no2 <= 80 else 'FAIL'],
            ['Nitrogen Dioxide (NO₂)', '40 (Annual)', f'{avg_no2:.2f}', 'PASS' if avg_no2 <= 40 else 'FAIL'],
            ['Sulfur Dioxide (SO₂)', '50 (Annual)', f'{avg_so2:.2f}', 'PASS' if avg_so2 <= 50 else 'FAIL'],
            ['Carbon Monoxide (CO)', '2000 (8h)', f'{avg_co:.2f}', 'PASS' if avg_co <= 2000 else 'FAIL'],
            ['Ozone (O₃)', '100 (8h)', f'{avg_o3:.2f}', 'PASS' if avg_o3 <= 100 else 'FAIL'],
        ]
        
        c_table = Table(comp_data, colWidths=[180, 100, 100, 100])
        c_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')), # Official Blue
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            
            # Body
            ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            
            # Zebra Striping
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ]))
        story.append(c_table)
        story.append(Spacer(1, 0.6*inch))
        
        # --- Signature Block ---
        # Wrapper to keep title and sigs together
        sig_elements = []
        sig_elements.append(Paragraph("AUTHORIZED SIGNATORY", self.styles['SectionHeader']))
        sig_elements.append(Spacer(1, 0.6*inch))
        
        sig_data = [
            ['__________________________', '__________________________'],
            ['Chief Toxicologist', 'Regulatory Commissioner'],
            ['Natl. Air Quality Bureau', 'Ministry of Environment']
        ]
        sig_table = Table(sig_data, colWidths=[250, 250])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
        ]))
        sig_elements.append(sig_table)
        
        story.append(Spacer(1, 0.6*inch))
        story.append(KeepTogether(sig_elements))
        
        # Footer
        story.append(Spacer(1, 0.1*inch))
        footer_text = f"Report Generated ID: {timestamp} | System: AAMS-v2 | Page 1 of 1"
        story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)))
        
        doc.build(story)
        
        # Merge with template if available
        final_pdf = self._merge_with_template(filename)
        
        print(f"✅ Regulatory report generated: {final_pdf}")
        return final_pdf




    def generate_word_report(
        self,
        city: str,
        start_date: str,
        end_date: str,
        data: Dict[str, Any]
    ) -> str:
        """
        Generate report using a Word template (docxtpl) for easy user modification
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        template_path = "report_template.docx" # Default template
        
        if not os.path.exists(template_path):
            print(f"⚠️ Template {template_path} not found. Skipping Word generation.")
            return ""
            
        try:
            doc = DocxTemplate(template_path)
            
            # Prepare context
            aqi = float(data.get('aqi', 0))
            cigarettes = float(data.get('cigarettes', 0))
            category = data.get('category', 'Unknown')
            
            pollutant_map = {'no2': 'NO2', 'so2': 'SO2', 'co': 'CO', 'o3': 'Ozone'}
            dominant = data.get('dominant_pollutant', 'no2')
            dom_label = pollutant_map.get(dominant, dominant.upper())
            
            # Formatting values for template
            context = {
                'city': city.upper(),
                'timestamp': timestamp,
                'date': datetime.now().strftime('%B %d, %Y'),
                'start_date': start_date,
                'end_date': end_date,
                'category': category.upper(),
                'aqi': int(aqi),
                'cigarettes': f"{cigarettes:.1f}",
                'dominant_pollutant': dom_label,
                'summary_text': f"The air quality in {city} is currently categorized as {category}. The overall AQI is {int(aqi)}.",
                'recommendations': self._generate_recommendations(0, category).replace('<br/>', '\n').replace('<b>', '').replace('</b>', ''), 
                # Note: HTML tags in recommendations won't render in Word plain text. 
                # Ideally we strip them or use RichText, but simple strip is fine for now.
            }
            
            # Add pollutant data
            pollutants = data.get('pollutants', {})
            for pol in ['no2', 'so2', 'co', 'o3', 'pm2_5', 'pm10']:
                key = pol.lower()
                val = pollutants.get(key, {}).get('mean_mol', 0)
                # Quick hack for display values since we don't have full formatting logic here
                if val == 0: val = pollutants.get(key, {}).get('concentration', 0)
                
                std = "N/A"
                status = "N/A"
                
                safe_key = pol.upper().replace('.', '_')
                context[f'{safe_key}_val'] = f"{val:.2f}"
                context[f'{safe_key}_std'] = std
                context[f'{safe_key}_status'] = status
            
            doc.render(context)
            
            output_filename = f"{self.output_dir}/Regulatory_Report_{city}_{timestamp}.docx"
            doc.save(output_filename)
            print(f"✅ Word report generated: {output_filename}")
            return output_filename
            
        except Exception as e:
            print(f"❌ Word generation failed: {e}")
            return ""

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
    
    def generate_prevention_guide(self, city: str, category: str = "General") -> str:
        """Generate a one-page prevention guide PDF (Dynamic based on Category)"""
        filename = os.path.join(self.output_dir, f"Prevention_Guide_{city}_{datetime.now().strftime('%Y%m%d')}.pdf")
        
        doc = SimpleDocTemplate(filename, pagesize=letter,
                              rightMargin=0.5*inch, leftMargin=0.5*inch,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        story = []
        
        # Header (Official)
        d = Drawing(400, 60)
        d.add(Rect(0, 0, 550, 60, fillColor=colors.HexColor('#1a237e'), strokeColor=None))
        d.add(String(20, 25, "NATIONAL AIR QUALITY MONITORING BUREAU", 
                     textAnchor='start', fontName='Times-Bold', fontSize=16, fillColor=colors.white))
        d.add(String(20, 10, "OFFICIAL PREVENTION MANIFESTO", 
                     textAnchor='start', fontName='Times-Roman', fontSize=10, fillColor=colors.white))
        
        story.append(d)
        story.append(Spacer(1, 0.3*inch))
        
        # Title
        story.append(Paragraph(f"AIR POLLUTION PREVENTION GUIDE", self.styles['OfficialTitle']))
        story.append(Paragraph(f"JURISDICTION: {city.upper()} | STATUS: {category.upper()}", self.styles['OfficialSubtitle']))
        
        # Introduction
        intro_text = f"""
        <b>Current Status: {category}</b><br/><br/>
        This guide provides specific actionable strategies tailored to the current air quality level.
        Please follow these official recommendations to protect your health and community.
        """
        story.append(Paragraph(intro_text, self.styles['FormalBody']))
        story.append(Spacer(1, 0.3*inch))
        
        # Helper for Card Style
        def create_card(title, content, color_hex='#1a237e'):
            data = [[title], [Paragraph(content, self.styles['FormalBody'])]]
            t = Table(data, colWidths=[500])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(color_hex)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                
                ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F8F9FA')),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor(color_hex)),
                ('LEFTPADDING', (0, 1), (-1, 1), 10),
                ('RIGHTPADDING', (0, 1), (-1, 1), 10),
                ('TOPPADDING', (0, 1), (-1, 1), 10),
                ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
            ]))
            return t

        # --- Dynamic Content Logic ---
        # Suggestions Map (Mirrored from Notifications for consistency)
        suggestions_map = {
             "Good": [
                "✅ Perfect time for outdoor cardio or marathons.",
                "🏠 VENTILATE: Open all windows to flush out indoor CO2.",
                "👶 Ideal for infants and elderly to soak in sun.",
                "🧘‍♀️ Practice deep breathing exercises outdoors.",
                "⚡ Maximize solar energy usage if applicable."
            ],
            "Moderate": [
                "⚠️ Sensitive groups (asthma/heart conditions) should carry inhalers.",
                "🚘 Close car windows while driving in traffic.",
                "🏃‍♂️ Reduce intensity of outdoor exercise (jog instead of sprint).",
                "🥛 Stay hydrated to keep airways moist.",
                "🔄 Recirculate indoor air during peak traffic hours."
            ],
            "Poor": [
                "🚫 CUT OUTDOOR EXERCISE: Switch to indoor gym/yoga.",
                "😷 COMMUTING: Wear an N95 mask if walking/biking.",
                "🧒 CHILDREN: Limit playground time to <30 mins.",
                "🥗 DIET: Increase intake of antioxidants (Vitamin C/E).",
                "🌬️ PURIFIERS: Run HEPA filters in bedrooms at night.",
                "🧂 STEAM INHALATION: Consider before sleep to clear airways."
            ],
            "Very Poor": [
                "🚨 AVOID OUTDOORS: Walk only if necessary.",
                "😷 MANDATORY N95/N99 MASK: Cloth masks are ineffective.",
                "🏢 WORK FROM HOME: If employer permits.",
                "🚿 Wash face/hands immediately after returning indoors.",
                "🥘 COOKING: Use exhaust fans; avoid frying to reduce indoor PM2.5.",
                "🌱 INDOOR PLANTS: Snake Plant/Areca Palm can help slightly."
            ],
            "Severe": [
                "🆘 HEALTH EMERGENCY: Breathlessness possible even in healthy adults.",
                "🛑 SEAL WINDOWS: Use wet towels in door gaps if drafts enter.",
                "💨 DO NOT EXERCISE: Even indoors, keep activity low.",
                "💊 ASTHMATICS: Keep relief medication immediately accessible.",
                "🩺 CHECK OXYGEN: Monitor SpO2 levels if feeling dizzy.",
                "🌫️ AIR PURIFIER: Run on 'Turbo' mode 24/7."
            ]
        }
        
        # Default fallback
        current_advice = suggestions_map.get(category, suggestions_map["Moderate"])
        advice_html = "<br/>".join(current_advice)

        # 1. Health & Lifestyle (Dynamic)
        is_severe = category in ["Poor", "Very Poor", "Severe"]
        card_color = '#d32f2f' if is_severe else '#2e7d32' # Red vs Green
        card_title = f"1. HEALTH ADVISORY: {category.upper()}"
        
        story.append(create_card(card_title, advice_html, color_hex=card_color))
        story.append(Spacer(1, 0.2*inch))
        
        # 2. Community Initiatives (Static but important)
        community_text = """
        <b>Neighborhood:</b><br/>
        * Organize tree plantation drives<br/>
        * Create community gardens<br/>
        * Carpool networks for schools<br/><br/>
        <b>Advocacy:</b><br/>
        * Report pollution violations<br/>
        * Support clean air policies<br/>
        * Share air quality info<br/>
        """
        story.append(create_card("2. COMMUNITY INITIATIVES", community_text))
        story.append(Spacer(1, 0.2*inch))

        # 3. Business & Industry (Static)
        business_text = """
        <b>Operations:</b><br/>
        * Install pollution control equipment<br/>
        * Regular machinery maintenance<br/>
        * Switch to cleaner fuels<br/><br/>
        <b>Facilities:</b><br/>
        * Install solar panels<br/>
        * Rainwater harvesting<br/>
        * EV charging stations<br/>
        """
        story.append(create_card("3. BUSINESS & INDUSTRY PRACTICES", business_text))
        story.append(Spacer(1, 0.2*inch))
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        footer_text = f"Guide ID: {timestamp} | National Air Quality Monitoring Bureau"
        story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)))
        
        # Build PDF (ONCE!)
        doc.build(story)
        
        # Merge with template if available (Logic handles "No Template" internally)
        final_pdf = self._merge_with_template(filename)
        
        print(f"✅ Prevention guide generated (Dynamic): {final_pdf}")
        return final_pdf

    def _merge_with_template(self, input_pdf_path: str) -> str:
        """Merge the generated report with a background template if it exists"""
        # User requested to disable template overlay ("no template is needed")
        return input_pdf_path
        
        template_path = os.path.join(os.path.dirname(self.output_dir), 'template.pdf')
            
        try:
            reader = PdfReader(input_pdf_path)
            template_reader = PdfReader(template_path)
            writer = PdfWriter()
            
            # Get template page (assume single page template repeated, or 1st page)
            template_page = template_reader.pages[0]
            
            for page in reader.pages:
                # Let's blindly try page.merge_page(template_page) and hope transparency works.
                # My template.pdf uses `c.rect` without fill (default), so it should be transparent.
            
                # Re-implementation for certainty:
                # We want Content on Top.
                # writer.add_page(page)
                # writer.pages[-1].merge_page(template_page) -> Template on Top.
                # If template is transparent, it overlays content.
                # My template has a border and watermark. Watermark is semi-transparent.
                # This is fine.
            
                writer.add_page(page)
                writer.pages[-1].merge_page(template_page)

            # Write to temp file then replace original
            temp_output = input_pdf_path.replace('.pdf', '_temp.pdf')
            with open(temp_output, 'wb') as f:
                writer.write(f)
            
            # Replace original
            import shutil
            shutil.move(temp_output, input_pdf_path)
                
            return input_pdf_path
            
        except Exception as e:
            print(f"Warning: Template merge failed: {e}")
            return input_pdf_path


# Convenience functions
def generate_report(city: str, start_date: str, end_date: str, data: Dict[str, Any]) -> str:
    """Quick function to generate regulatory report (PDF + Word)"""
    generator = RegulatoryReportGenerator()
    pdf_path = generator.generate_regulatory_report(city, start_date, end_date, data)
    # docx_path = generator.generate_word_report(city, start_date, end_date, data) # Disabled by user request
    return pdf_path # Return PDF as primary, but both are generated


def generate_prevention_guide(city: str, category: str = "General") -> str:
    """Quick function to generate prevention guide"""
    generator = RegulatoryReportGenerator()
    return generator.generate_prevention_guide(city, category)


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
    generator.generate_word_report(
        city="Bengaluru",
        start_date="2025-11-01",
        end_date="2025-11-21",
        data=test_data
    )
    generator.generate_prevention_guide("Bengaluru")
