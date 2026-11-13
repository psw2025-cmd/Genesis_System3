import sys
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Create workbook
wb = openpyxl.Workbook()
# remove default sheet
wb.remove(wb.active)

# Color palettes
NAVY_HEADER = "1B365D"
WHITE_TEXT = "FFFFFF"
LIGHT_GRAY_BORDER = "D3D3D3"
ZEBRA_FILL = "F8FAFC"

# Classification fills
FILL_DASH_ONLY = "E8F4F8"      # Light Cyan
FILL_CONTENT_ONLY = "EDE7F6"   # Light Purple
FILL_BOTH = "E8F5E9"           # Light Mint
FILL_BETTER_DASH = "C8E6C9"    # Soft Green
FILL_BETTER_CONTENT = "BBDEFB" # Soft Blue
FILL_MERGE = "FFF9C4"          # Soft Yellow
FILL_REMOVE = "FFCDD2"         # Soft Red

# Fonts
font_title = Font(name="Segoe UI", size=14, bold=True, color="1B365D")
font_header = Font(name="Segoe UI", size=11, bold=True, color=WHITE_TEXT)
font_data = Font(name="Segoe UI", size=10)
font_bold = Font(name="Segoe UI", size=10, bold=True)
font_winner_dash = Font(name="Segoe UI", size=10, bold=True, color="1B5E20")
font_winner_content = Font(name="Segoe UI", size=10, bold=True, color="0D47A1")
font_winner_merge = Font(name="Segoe UI", size=10, bold=True, color="E65100")
font_winner_remove = Font(name="Segoe UI", size=10, bold=True, color="B71C1C")

header_fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
zebra_fill = PatternFill(start_color=ZEBRA_FILL, end_color=ZEBRA_FILL, fill_type="solid")
white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

thin_side = Side(border_style="thin", color=LIGHT_GRAY_BORDER)
cell_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
header_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=Side(border_style="medium", color="1B365D"))

align_left = Alignment(horizontal="left", vertical="top", wrap_text=True)
align_center = Alignment(horizontal="center", vertical="top", wrap_text=True)
align_header = Alignment(horizontal="center", vertical="center", wrap_text=True)

HEADERS = [
    "Feature Name",
    "Classification",
    "Source File",
    "Destination File",
    "Winner",
    "Reason",
    "Evidence"
]

def add_sheet_data(ws, title, rows_data):
    ws.views.sheetView[0].showGridLines = True
    
    # Header row
    for col_idx, h in enumerate(HEADERS, 1):
        cell = ws.cell(row=1, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = header_fill
        cell.alignment = align_header
        cell.border = header_border
    ws.row_dimensions[1].height = 28
    
    # Data rows
    for r_idx, row in enumerate(rows_data, 2):
        bg = zebra_fill if r_idx % 2 == 0 else white_fill
        
        # Determine classification fill if preferred, or row striping
        classification = row.get("Classification", "")
        winner = row.get("Winner", "")
        
        row_vals = [
            row.get("Feature Name", ""),
            classification,
            row.get("Source File", ""),
            row.get("Destination File", ""),
            winner,
            row.get("Reason", ""),
            row.get("Evidence", "")
        ]
        
        for c_idx, val in enumerate(row_vals, 1):
            cell = ws.cell(row=r_idx, column=c_idx, value=val)
            cell.font = font_data
            cell.fill = bg
            cell.border = cell_border
            
            if c_idx in (2, 5): # Classification and Winner centered
                cell.alignment = align_center
            else:
                cell.alignment = align_left
                
            # Highlight winner font
            if c_idx == 5:
                if "dashboard" in winner.lower():
                    cell.font = font_winner_dash
                    cell.fill = PatternFill(start_color="E8F8F5", end_color="E8F8F5", fill_type="solid")
                elif "content" in winner.lower():
                    cell.font = font_winner_content
                    cell.fill = PatternFill(start_color="EBF5FB", end_color="EBF5FB", fill_type="solid")
                elif "merge" in winner.lower():
                    cell.font = font_winner_merge
                    cell.fill = PatternFill(start_color="FEF9E7", end_color="FEF9E7", fill_type="solid")
                elif "remove" in winner.lower() or "none" in winner.lower():
                    cell.font = font_winner_remove
                    cell.fill = PatternFill(start_color="FDEDEC", end_color="FDEDEC", fill_type="solid")

            # Classification subtle badges
            if c_idx == 2:
                if "Merge required" in classification:
                    cell.fill = PatternFill(start_color="FFF9C4", end_color="FFF9C4", fill_type="solid")
                    cell.font = font_bold
                elif "Safe removal" in classification:
                    cell.fill = PatternFill(start_color="FFCDD2", end_color="FFCDD2", fill_type="solid")
                    cell.font = font_bold
                elif "Better implementation in dashboard" in classification:
                    cell.fill = PatternFill(start_color="C8E6C9", end_color="C8E6C9", fill_type="solid")
                elif "Better implementation in content" in classification:
                    cell.fill = PatternFill(start_color="BBDEFB", end_color="BBDEFB", fill_type="solid")
                elif "Present in dashboard only" in classification:
                    cell.fill = PatternFill(start_color="E8F4F8", end_color="E8F4F8", fill_type="solid")
                elif "Present in content only" in classification:
                    cell.fill = PatternFill(start_color="EDE7F6", end_color="EDE7F6", fill_type="solid")
                elif "Present in both" in classification:
                    cell.fill = PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid")

        ws.row_dimensions[r_idx].height = 45 # generous height for multi-line wrapped text
        
    # Auto-fit column widths with bounds
    col_widths = {
        1: 28, # Feature Name
        2: 24, # Classification
        3: 32, # Source File
        4: 32, # Destination File
        5: 18, # Winner
        6: 45, # Reason
        7: 55  # Evidence
    }
    for c_idx, width in col_widths.items():
        col_letter = get_column_letter(c_idx)
        ws.column_dimensions[col_letter].width = width
        
    # Freeze top row
    ws.freeze_panes = "A2"
    # Enable filter
    ws.auto_filter.ref = f"A1:G{len(rows_data) + 1}"

print("Helper defined")
sys.exit(0)
