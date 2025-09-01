#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Agricultural Report Generator

This script generates a PDF report with agricultural data for a selected area,
including soil information, rainfall data, crop suitability, and NDVI analysis.

Usage:
    python generate_report.py --geojson area.geojson --output report.pdf
"""

import argparse
import datetime
import json
import os
import sys
from typing import Dict, Any, List, Optional

# Import ReportLab for PDF generation
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    from reportlab.graphics.charts.piecharts import Pie
except ImportError:
    print("ReportLab is required for PDF generation. Install it with: pip install reportlab")
    sys.exit(1)

# Try to import matplotlib for chart generation
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    print("Matplotlib not found. Charts will be simpler.")
    HAS_MATPLOTLIB = False

def load_geojson(geojson_path: str) -> Dict[str, Any]:
    """
    Load GeoJSON file and return as dictionary.
    
    Args:
        geojson_path: Path to GeoJSON file
        
    Returns:
        GeoJSON as dictionary
    """
    try:
        with open(geojson_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading GeoJSON file: {str(e)}")
        sys.exit(1)

def get_mock_soil_data() -> Dict[str, Any]:
    """
    Get mock soil data for the report.
    In a real application, this would query the database or API.
    
    Returns:
        Dictionary with soil data
    """
    return {
        "soil_type": "Black Cotton Soil",
        "ph_value": 7.2,
        "nitrogen_kgha": 280.5,
        "phosphorus_kgha": 12.8,
        "potassium_kgha": 190.3,
        "organic_carbon_pct": 0.75,
        "texture": "Clay Loam",
        "drainage": "Moderate",
        "depth_cm": 120
    }

def get_mock_rainfall_data() -> Dict[str, Any]:
    """
    Get mock rainfall data for the report.
    In a real application, this would query the database or API.
    
    Returns:
        Dictionary with rainfall data
    """
    return {
        "annual_rainfall_mm": 1200,
        "monsoon_rainfall_mm": 950,
        "winter_rainfall_mm": 150,
        "rainfall_zone": "Medium Rainfall",
        "drought_prone": False,
        "monthly_rainfall": [
            {"month": "Jan", "rainfall_mm": 10},
            {"month": "Feb", "rainfall_mm": 5},
            {"month": "Mar", "rainfall_mm": 8},
            {"month": "Apr", "rainfall_mm": 12},
            {"month": "May", "rainfall_mm": 25},
            {"month": "Jun", "rainfall_mm": 180},
            {"month": "Jul", "rainfall_mm": 350},
            {"month": "Aug", "rainfall_mm": 320},
            {"month": "Sep", "rainfall_mm": 180},
            {"month": "Oct", "rainfall_mm": 80},
            {"month": "Nov", "rainfall_mm": 20},
            {"month": "Dec", "rainfall_mm": 10}
        ]
    }

def get_mock_crop_suitability() -> List[Dict[str, Any]]:
    """
    Get mock crop suitability data for the report.
    In a real application, this would query the database or API.
    
    Returns:
        List of dictionaries with crop suitability data
    """
    return [
        {
            "crop_name": "Rice",
            "suitability_score": 8,
            "yield_potential_tonha": 4.5,
            "water_requirement_mm": 1200,
            "growing_season": "Kharif"
        },
        {
            "crop_name": "Wheat",
            "suitability_score": 6,
            "yield_potential_tonha": 3.2,
            "water_requirement_mm": 450,
            "growing_season": "Rabi"
        },
        {
            "crop_name": "Cotton",
            "suitability_score": 9,
            "yield_potential_tonha": 2.8,
            "water_requirement_mm": 700,
            "growing_season": "Kharif"
        },
        {
            "crop_name": "Soybean",
            "suitability_score": 7,
            "yield_potential_tonha": 2.0,
            "water_requirement_mm": 600,
            "growing_season": "Kharif"
        },
        {
            "crop_name": "Chickpea",
            "suitability_score": 8,
            "yield_potential_tonha": 1.5,
            "water_requirement_mm": 350,
            "growing_season": "Rabi"
        }
    ]

def get_mock_ndvi_data() -> Dict[str, Any]:
    """
    Get mock NDVI data for the report.
    In a real application, this would come from Earth Engine or Sentinel Hub.
    
    Returns:
        Dictionary with NDVI data
    """
    return {
        "ndvi_min": 0.15,
        "ndvi_max": 0.85,
        "ndvi_mean": 0.65,
        "ndvi_stdDev": 0.12,
        "health_status": "Excellent",
        "description": "Excellent vegetation health. Crops are likely at peak growth with optimal conditions.",
        "time_series": [
            {"date": "2023-01-15", "ndvi": 0.25},
            {"date": "2023-02-15", "ndvi": 0.30},
            {"date": "2023-03-15", "ndvi": 0.45},
            {"date": "2023-04-15", "ndvi": 0.60},
            {"date": "2023-05-15", "ndvi": 0.75},
            {"date": "2023-06-15", "ndvi": 0.85},
            {"date": "2023-07-15", "ndvi": 0.80},
            {"date": "2023-08-15", "ndvi": 0.70},
            {"date": "2023-09-15", "ndvi": 0.65},
            {"date": "2023-10-15", "ndvi": 0.55},
            {"date": "2023-11-15", "ndvi": 0.40},
            {"date": "2023-12-15", "ndvi": 0.30}
        ]
    }

def create_matplotlib_chart(output_path: str, data: Dict[str, Any], chart_type: str):
    """
    Create a chart using matplotlib and save it as an image.
    
    Args:
        output_path: Path to save the chart image
        data: Data for the chart
        chart_type: Type of chart to create ('rainfall', 'ndvi', 'crop')
    """
    if not HAS_MATPLOTLIB:
        return None
    
    plt.figure(figsize=(8, 4))
    
    if chart_type == 'rainfall':
        # Create rainfall bar chart
        months = [item['month'] for item in data['monthly_rainfall']]
        rainfall = [item['rainfall_mm'] for item in data['monthly_rainfall']]
        
        plt.bar(months, rainfall, color='skyblue')
        plt.title('Monthly Rainfall Distribution')
        plt.xlabel('Month')
        plt.ylabel('Rainfall (mm)')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
    elif chart_type == 'ndvi':
        # Create NDVI time series line chart
        dates = [item['date'] for item in data['time_series']]
        ndvi_values = [item['ndvi'] for item in data['time_series']]
        
        plt.plot(range(len(dates)), ndvi_values, marker='o', linestyle='-', color='green')
        plt.title('NDVI Time Series')
        plt.xlabel('Date')
        plt.ylabel('NDVI Value')
        plt.xticks(range(len(dates)), [d.split('-')[1] + '/' + d.split('-')[0][2:] for d in dates], rotation=45)
        plt.grid(True, alpha=0.3)
        
    elif chart_type == 'crop':
        # Create crop suitability bar chart
        crops = [item['crop_name'] for item in data]
        scores = [item['suitability_score'] for item in data]
        
        plt.bar(crops, scores, color='lightgreen')
        plt.title('Crop Suitability Scores')
        plt.xlabel('Crop')
        plt.ylabel('Suitability Score (1-10)')
        plt.ylim(0, 10)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    
    return output_path

def create_reportlab_chart(data: Dict[str, Any], chart_type: str) -> Drawing:
    """
    Create a chart using ReportLab.
    
    Args:
        data: Data for the chart
        chart_type: Type of chart to create ('rainfall', 'ndvi', 'crop')
        
    Returns:
        ReportLab Drawing object
    """
    drawing = Drawing(400, 200)
    
    if chart_type == 'rainfall':
        # Create rainfall bar chart
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 50
        chart.width = 300
        chart.height = 125
        
        rainfall = [item['rainfall_mm'] for item in data['monthly_rainfall']]
        chart.data = [rainfall]
        
        chart.categoryAxis.categoryNames = [item['month'] for item in data['monthly_rainfall']]
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = max(rainfall) * 1.1
        chart.bars[0].fillColor = colors.skyblue
        
        drawing.add(chart)
        
    elif chart_type == 'ndvi':
        # Create NDVI time series line chart
        chart = HorizontalLineChart()
        chart.x = 50
        chart.y = 50
        chart.width = 300
        chart.height = 125
        
        ndvi_values = [item['ndvi'] for item in data['time_series']]
        chart.data = [ndvi_values]
        
        chart.categoryAxis.categoryNames = [item['date'].split('-')[1] + '/' + item['date'].split('-')[0][2:] for item in data['time_series']]
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = 1.0
        chart.lines[0].strokeColor = colors.green
        
        drawing.add(chart)
        
    elif chart_type == 'crop':
        # Create crop suitability bar chart
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 50
        chart.width = 300
        chart.height = 125
        
        scores = [item['suitability_score'] for item in data]
        chart.data = [scores]
        
        chart.categoryAxis.categoryNames = [item['crop_name'] for item in data]
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = 10
        chart.bars[0].fillColor = colors.lightgreen
        
        drawing.add(chart)
    
    return drawing

def generate_pdf_report(geojson_dict: Dict[str, Any], output_path: str):
    """
    Generate a PDF report with agricultural data.
    
    Args:
        geojson_dict: GeoJSON data for the area
        output_path: Path to save the PDF report
    """
    # Get data for the report
    soil_data = get_mock_soil_data()
    rainfall_data = get_mock_rainfall_data()
    crop_data = get_mock_crop_suitability()
    ndvi_data = get_mock_ndvi_data()
    
    # Create a PDF document
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Create content for the PDF
    content = []
    
    # Add title
    content.append(Paragraph("Agricultural Analysis Report", title_style))
    content.append(Spacer(1, 0.5*inch))
    
    # Add date and location
    location_name = geojson_dict['features'][0]['properties'].get('name', 'Selected Area')
    content.append(Paragraph(f"Location: {location_name}", normal_style))
    content.append(Paragraph(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}", normal_style))
    content.append(Spacer(1, 0.5*inch))
    
    # Add soil data section
    content.append(Paragraph("Soil Information", heading_style))
    content.append(Spacer(1, 0.1*inch))
    
    soil_table_data = [
        ["Parameter", "Value"],
        ["Soil Type", soil_data['soil_type']],
        ["pH Value", f"{soil_data['ph_value']:.1f}"],
        ["Nitrogen", f"{soil_data['nitrogen_kgha']:.1f} kg/ha"],
        ["Phosphorus", f"{soil_data['phosphorus_kgha']:.1f} kg/ha"],
        ["Potassium", f"{soil_data['potassium_kgha']:.1f} kg/ha"],
        ["Organic Carbon", f"{soil_data['organic_carbon_pct']:.2f}%"],
        ["Texture", soil_data['texture']],
        ["Drainage", soil_data['drainage']],
        ["Depth", f"{soil_data['depth_cm']} cm"]
    ]
    
    soil_table = Table(soil_table_data, colWidths=[2*inch, 2*inch])
    soil_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgreen),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(soil_table)
    content.append(Spacer(1, 0.3*inch))
    
    # Add rainfall data section
    content.append(Paragraph("Rainfall Information", heading_style))
    content.append(Spacer(1, 0.1*inch))
    
    rainfall_table_data = [
        ["Parameter", "Value"],
        ["Annual Rainfall", f"{rainfall_data['annual_rainfall_mm']} mm"],
        ["Monsoon Rainfall", f"{rainfall_data['monsoon_rainfall_mm']} mm"],
        ["Winter Rainfall", f"{rainfall_data['winter_rainfall_mm']} mm"],
        ["Rainfall Zone", rainfall_data['rainfall_zone']],
        ["Drought Prone", "Yes" if rainfall_data['drought_prone'] else "No"]
    ]
    
    rainfall_table = Table(rainfall_table_data, colWidths=[2*inch, 2*inch])
    rainfall_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(rainfall_table)
    content.append(Spacer(1, 0.3*inch))
    
    # Add rainfall chart
    if HAS_MATPLOTLIB:
        chart_path = os.path.join(os.path.dirname(output_path), "rainfall_chart.png")
        create_matplotlib_chart(chart_path, rainfall_data, 'rainfall')
        content.append(Paragraph("Monthly Rainfall Distribution", styles['Heading3']))
        content.append(Image(chart_path, width=6*inch, height=3*inch))
    else:
        content.append(Paragraph("Monthly Rainfall Distribution", styles['Heading3']))
        content.append(create_reportlab_chart(rainfall_data, 'rainfall'))
    content.append(Spacer(1, 0.3*inch))
    
    # Add crop suitability section
    content.append(Paragraph("Crop Suitability", heading_style))
    content.append(Spacer(1, 0.1*inch))
    
    crop_table_data = [["Crop", "Suitability (1-10)", "Yield Potential", "Water Requirement", "Season"]]
    for crop in crop_data:
        crop_table_data.append([
            crop['crop_name'],
            str(crop['suitability_score']),
            f"{crop['yield_potential_tonha']:.1f} t/ha",
            f"{crop['water_requirement_mm']} mm",
            crop['growing_season']
        ])
    
    crop_table = Table(crop_table_data, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    crop_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(crop_table)
    content.append(Spacer(1, 0.3*inch))
    
    # Add crop suitability chart
    if HAS_MATPLOTLIB:
        chart_path = os.path.join(os.path.dirname(output_path), "crop_chart.png")
        create_matplotlib_chart(chart_path, crop_data, 'crop')
        content.append(Paragraph("Crop Suitability Scores", styles['Heading3']))
        content.append(Image(chart_path, width=6*inch, height=3*inch))
    else:
        content.append(Paragraph("Crop Suitability Scores", styles['Heading3']))
        content.append(create_reportlab_chart(crop_data, 'crop'))
    content.append(Spacer(1, 0.3*inch))
    
    # Add NDVI data section
    content.append(Paragraph("Vegetation Health (NDVI Analysis)", heading_style))
    content.append(Spacer(1, 0.1*inch))
    
    ndvi_table_data = [
        ["Parameter", "Value"],
        ["NDVI Minimum", f"{ndvi_data['ndvi_min']:.2f}"],
        ["NDVI Maximum", f"{ndvi_data['ndvi_max']:.2f}"],
        ["NDVI Mean", f"{ndvi_data['ndvi_mean']:.2f}"],
        ["NDVI Standard Deviation", f"{ndvi_data['ndvi_stdDev']:.2f}"],
        ["Health Status", ndvi_data['health_status']]
    ]
    
    ndvi_table = Table(ndvi_table_data, colWidths=[2*inch, 2*inch])
    ndvi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgreen),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(ndvi_table)
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph(f"Description: {ndvi_data['description']}", normal_style))
    content.append(Spacer(1, 0.3*inch))
    
    # Add NDVI chart
    if HAS_MATPLOTLIB:
        chart_path = os.path.join(os.path.dirname(output_path), "ndvi_chart.png")
        create_matplotlib_chart(chart_path, ndvi_data, 'ndvi')
        content.append(Paragraph("NDVI Time Series", styles['Heading3']))
        content.append(Image(chart_path, width=6*inch, height=3*inch))
    else:
        content.append(Paragraph("NDVI Time Series", styles['Heading3']))
        content.append(create_reportlab_chart(ndvi_data, 'ndvi'))
    content.append(Spacer(1, 0.3*inch))
    
    # Add recommendations section
    content.append(Paragraph("Recommendations", heading_style))
    content.append(Spacer(1, 0.1*inch))
    
    # Sort crops by suitability score
    sorted_crops = sorted(crop_data, key=lambda x: x['suitability_score'], reverse=True)
    top_crop = sorted_crops[0]['crop_name']
    
    recommendations = [
        f"1. Based on soil and climate conditions, {top_crop} is the most suitable crop for this area.",
        f"2. The soil pH of {soil_data['ph_value']} is optimal for most crops. No pH adjustment is needed.",
        f"3. Nitrogen content is {soil_data['nitrogen_kgha']:.1f} kg/ha, which is moderate. Consider applying nitrogen fertilizer for nitrogen-demanding crops.",
        f"4. The area receives {rainfall_data['annual_rainfall_mm']} mm of annual rainfall, which is sufficient for most crops with proper water management.",
        f"5. NDVI analysis shows {ndvi_data['health_status'].lower()} vegetation health, indicating good growing conditions."
    ]
    
    for rec in recommendations:
        content.append(Paragraph(rec, normal_style))
        content.append(Spacer(1, 0.1*inch))
    
    # Add footer
    content.append(Spacer(1, 0.5*inch))
    content.append(Paragraph("Generated by Sustainable Agriculture Geospatial Web Application", 
                            ParagraphStyle(name='Footer', parent=normal_style, alignment=1)))
    
    # Build the PDF
    doc.build(content)
    print(f"Report generated and saved to {output_path}")

def main():
    """
    Main function to generate agricultural report.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate agricultural PDF report')
    parser.add_argument('--geojson', required=True, help='Path to GeoJSON file')
    parser.add_argument('--output', required=True, help='Output PDF path')
    
    args = parser.parse_args()
    
    # Load GeoJSON
    geojson_dict = load_geojson(args.geojson)
    
    # Generate PDF report
    generate_pdf_report(geojson_dict, args.output)

if __name__ == '__main__':
    main()