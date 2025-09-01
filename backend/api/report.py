from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import FileResponse
from typing import Dict, Any, List, Optional
import json
import os
import tempfile
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

# Import services

# Create router
router = APIRouter()

@router.post("/generate_report")
async def generate_report(
    data: Dict[str, Any]
):
    """
    Generate a PDF report with maps, charts, and tabular data.
    
    Parameters:
    - data: Dictionary containing polygon, vector data, and raster data
    
    Returns:
    - PDF file
    """
    try:
        # Extract data from request
        polygon = data.get("polygon")
        if not polygon:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Polygon must be provided"
            )
        
        # In a real app, this would fetch data from the database and generate charts
        # For now, create a simple mock PDF report
        
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            # Create PDF document
            doc = SimpleDocTemplate(tmp.name, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            
            # Add title
            elements.append(Paragraph("Agricultural Intelligence Report", styles["Title"]))
            elements.append(Spacer(1, 12))
            
            # Add date
            elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
            elements.append(Spacer(1, 12))
            
            # Add area information
            elements.append(Paragraph("Selected Area Information", styles["Heading2"]))
            elements.append(Paragraph("Area Type: Polygon", styles["Normal"]))
            elements.append(Paragraph("Approximate Size: 25 hectares", styles["Normal"]))
            elements.append(Spacer(1, 12))
            
            # Add soil data table
            elements.append(Paragraph("Soil Data", styles["Heading2"]))
            soil_data = [
                ["Property", "Value"],
                ["Soil Type", "Alluvial"],
                ["pH Level", "6.8"],
                ["Organic Matter", "2.3%"],
                ["Nitrogen", "Medium"],
                ["Phosphorus", "Low"],
                ["Potassium", "High"]
            ]
            soil_table = Table(soil_data, colWidths=[200, 200])
            soil_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.green),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(soil_table)
            elements.append(Spacer(1, 12))
            
            # Add rainfall data table
            elements.append(Paragraph("Rainfall Data", styles["Heading2"]))
            rainfall_data = [
                ["Property", "Value"],
                ["Annual Average", "1200mm"],
                ["Monsoon Average", "850mm"],
                ["Dry Season Average", "120mm"],
                ["Rainfall Zone", "High Rainfall Zone"]
            ]
            rainfall_table = Table(rainfall_data, colWidths=[200, 200])
            rainfall_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.blue),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(rainfall_table)
            elements.append(Spacer(1, 12))
            
            # Add crop suitability information
            elements.append(Paragraph("Crop Suitability", styles["Heading2"]))
            elements.append(Paragraph("Suitable Crops: Rice, Wheat, Sugarcane, Vegetables", styles["Normal"]))
            elements.append(Paragraph("Recommended Crop: Rice", styles["Normal"]))
            elements.append(Paragraph("Growing Season: June - November", styles["Normal"]))
            elements.append(Spacer(1, 12))
            
            # In a real app, we would generate and add charts here
            # For now, just add a placeholder message
            elements.append(Paragraph("NDVI and Rainfall charts would be included here", styles["Italic"]))
            
            # Build the PDF
            doc.build(elements)
            
            # Return the file path
            return {
                "report_url": f"/report/download_report?filename={os.path.basename(tmp.name)}",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating report: {str(e)}"
        )

@router.get("/download_report")
async def download_report(filename: str):
    """
    Download a generated report by filename.
    
    Parameters:
    - filename: Name of the report file
    
    Returns:
    - PDF file
    """
    try:
        # In a real app, this would check if the file exists and return it
        # For now, return a mock response
        return {"message": f"This endpoint would return the report file: {filename}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading report: {str(e)}"
        )