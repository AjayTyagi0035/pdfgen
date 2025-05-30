"""
Script version: v6

This script generates a PDF visualizing the tasks for a collected app and all its steps, actions, and screenshots. It is much easier to spot check and review collected data this way rather than by inspecting the raw JSON file.

Installation:
1. Ensure you have Python 3.7 or later installed.
2. Install the required packages using pip:
   pip install reportlab Pillow

Usage:
python generate_pdf.py <path_to_input_json> [-o <output_pdf_path>]

Arguments:
  <path_to_input_json>  : Path to the JSON file containing task data
  -o <output_pdf_path>  : (Optional) Path where the output PDF should be saved. By default, saves the PDF to the directory this python file is in.

Example usage:
1. Generate a report with default output location (default is the directory where this python file is saved in):
   python generate_pdf.py ~/com.panerabread/com.panerabread.json

2. Generate a report with a specified output location:
   python generate_pdf.py ~/com.panerabread/com.panerabread.json -o reports/panera.pdf
"""

import json
import argparse
import math
import os
import tempfile

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from PIL import Image as PILImage
from PIL import ImageDraw


def convert_to_pixels(image, float_x, float_y):
    """
    Convert relative coordinates to pixel coordinates based on image size.
    """
    width, height = image.size
    return round(float_x * width), round(float_y * height)


def draw_bounding_boxes_and_annotations(image_path, targets, taps, swipes, output_path):
    """
    Draw bounding boxes, crosses for taps, and arrows for swipes on the image.
    """
    try:
        with PILImage.open(image_path) as img:
            draw = ImageDraw.Draw(img)
            width, height = img.size

            # Draw bounding boxes
            for target in targets:
                x, y, w, h = target['x'], target['y'], target['width'], target['height']
                draw.rectangle([x, y, x + w, y + h], outline='red', width=2)

            # Draw crosses for tap actions
            for tap in taps:
                tap_x, tap_y = convert_to_pixels(img, tap['x'], tap['y'])
                cross_size = 40
                draw.line((tap_x - cross_size, tap_y, tap_x + cross_size, tap_y), fill='red', width=5)
                draw.line((tap_x, tap_y - cross_size, tap_x, tap_y + cross_size), fill='red', width=5)

            # Draw arrows for swipe actions
            for swipe in swipes:
                start_x, start_y = convert_to_pixels(img, swipe['startX'], swipe['startY'])
                end_x, end_y = convert_to_pixels(img, swipe['endX'], swipe['endY'])
                draw_arrow(draw, start_x, start_y, end_x, end_y, fill='red', width=5)

            img.save(output_path)
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None
    return output_path


def draw_arrow(draw, x1, y1, x2, y2, fill='red', width=5):
    """Draw an arrow from (x1, y1) to (x2, y2)."""
    draw.line((x1, y1, x2, y2), fill=fill, width=width)

    # Calculate the angle of the line
    angle = math.atan2(y2 - y1, x2 - x1)

    # Calculate the points for the arrowhead
    arrow_length = 20
    arrow_angle = math.pi / 6  # 30 degrees

    x3 = x2 - arrow_length * math.cos(angle - arrow_angle)
    y3 = y2 - arrow_length * math.sin(angle - arrow_angle)
    x4 = x2 - arrow_length * math.cos(angle + arrow_angle)
    y4 = y2 - arrow_length * math.sin(angle + arrow_angle)

    # Draw the arrowhead
    draw.polygon([(x2, y2), (x3, y3), (x4, y4)], fill=fill)


def create_multi_task_pdf_report(json_file_path, output_pdf_path=None, images_dir=None):
    """
    Generate a PDF report from a JSON file containing task data.
    
    Args:
        json_file_path: Path to the JSON file
        output_pdf_path: Path where the output PDF will be saved
        images_dir: Directory containing image files referenced in the JSON
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory: {temp_dir}")
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        app_name = data.get('app', 'Unknown App')
        bundle_id = data.get('bundle', 'unknown_bundle')
        app_version = data.get('app-version', 'Unknown Version')
        tasks = data.get('tasks', [])

        if output_pdf_path is None:
            current_directory = os.getcwd()
            sanitized_app_name = ''.join(c for c in app_name if c.isalnum() or c in (' ', '_'))
            output_pdf_path = os.path.join(current_directory, f"{sanitized_app_name}_tasks_report.pdf")
        doc = SimpleDocTemplate(output_pdf_path, pagesize=A4,
                                leftMargin=0.5 * inch, rightMargin=0.5 * inch,
                                topMargin=0.5 * inch, bottomMargin=0.5 * inch)

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontSize=16,
            leading=20,
            alignment=1,  # Center align
            spaceAfter=12
        )
        subtitle_style = ParagraphStyle(
            'SubTitle',
            parent=styles['Title'],
            fontSize=9,
            leading=20,
            alignment=1,  # Center align
            spaceAfter=12
        )
        header_style = ParagraphStyle(
            'Header',
            fontSize=12,
            leading=14,
            alignment=1,  # Center align
            spaceAfter=6
        )
        small_header_style = ParagraphStyle(
            'SmallHeader',
            fontSize=12,
            leading=14,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold',
            spaceAfter=6
        )
        step_id_style = ParagraphStyle(
            'StepID',
            fontSize=7,
            leading=14,
            fontName='Helvetica-Bold',
            spaceAfter=6
        )
        normal_style = ParagraphStyle(
            'Normal',
            fontSize=9,
            leading=11,
            spaceAfter=2
        )

        elements = []

        # Add app information header
        elements.append(Paragraph(app_name, title_style))
        elements.append(Paragraph(f"Bundle ID: {bundle_id}", header_style))
        elements.append(Paragraph(f"Version: {app_version}", header_style))
        elements.append(Spacer(1, 24))

        # Process each task
        for task in tasks:
            task_elements = []
            task_elements.append(Paragraph(f"Task: {task['phrases']}", title_style))
            task_elements.append(Paragraph(f"Task id: {task['id']}", subtitle_style))

            # Add prerequisites table if available
            prereq_info = task.get('prereq-info', {})
            if prereq_info:
                task_elements.append(Paragraph("Prerequisites:", small_header_style))
                prerequisites = [['Key', 'Value']] + [[key, value] for key, value in prereq_info.items()]
                table = Table(prerequisites, colWidths=[2 * inch, 4 * inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                task_elements.append(table)
                task_elements.append(Spacer(1, 12))

            # Prepare step content for two-column grid
            step_data = []
            steps = task.get('steps', [])
            success_description = None
            is_text = None

            for i, step in enumerate(steps):
                step_header = Paragraph(f"Step {i + 1}", small_header_style)
                step_id = Paragraph(f"id: {step['id']}", step_id_style)

                if 'action' in step:
                    action = step['action']
                    action_type = action.get('action', {}).get('type', 'No action type')
                    action_phrase = action.get('phrases', ['No phrase available'])[0]

                    if action_type == 'success':
                        success_description = action['action'].get('successDescription', 'No description available')
                        is_text = action['action'].get('isText', False)
                        action_type_para = Paragraph("<b>Action type:</b> Success", normal_style)
                        success_desc_para = Paragraph(f"<b>Success description:</b> {success_description}",
                                                      normal_style)
                        is_text_para = Paragraph(f"<b>isText:</b> {is_text}", normal_style)

                        step_content = [
                            [step_header],
                            [step_id],
                            [action_type_para],
                            [success_desc_para],
                            [is_text_para]
                        ]
                    elif action_type == 'textEntry' and 'key' in action['action']:
                        prereq_key = action['action']['key']
                        action_type_para = Paragraph(f"<b>Action type:</b> Prerequisite", normal_style)
                        prereq_key_para = Paragraph(f"<b>Prerequisite key:</b> {prereq_key}", normal_style)
                        action_phrase_para = Paragraph(f"<b>Action phrase:</b> {action_phrase}", normal_style)
                        step_content = [
                            [step_header],
                            [step_id],
                            [action_type_para],
                            [prereq_key_para],
                            [action_phrase_para]
                        ]
                    elif action_type == 'textEntry':
                        entered_text = action['action'].get('text', 'No text entered')
                        action_type_para = Paragraph(f"<b>Action type:</b> {action_type}", normal_style)
                        entered_text_para = Paragraph(f"<b>Entered text:</b> {entered_text}", normal_style)
                        action_phrase_para = Paragraph(f"<b>Action phrase:</b> {action_phrase}", normal_style)
                        step_content = [
                            [step_header],
                            [step_id],
                            [action_type_para],
                            [entered_text_para],
                            [action_phrase_para]
                        ]
                    else:
                        action_type_para = Paragraph(f"<b>Action type:</b> {action_type}", normal_style)
                        action_phrase_para = Paragraph(f"<b>Action phrase:</b> {action_phrase}", normal_style)
                        step_content = [
                            [step_header],
                            [step_id],
                            [action_type_para],
                            [action_phrase_para]
                        ]                    # Image processing
                    # Try multiple possible locations for the image
                    image_id = step['image']['id']
                    # Check for multiple image extensions
                    image_extensions = ['.png', '.jpg', '.jpeg']
                    
                    possible_paths = []
                    
                    # First look in the uploaded images directory if provided
                    if images_dir:
                        # Look for images in the root of the extracted directory
                        for ext in image_extensions:
                            possible_paths.append(os.path.join(images_dir, f"{image_id}{ext}"))
                        
                        # Also check for nested folders in the ZIP
                        for root, dirs, files in os.walk(images_dir):
                            for file in files:
                                basename, ext = os.path.splitext(file)
                                if basename == image_id or file.startswith(f"{image_id}."):
                                    possible_paths.append(os.path.join(root, file))
                    
                    # Add other possible locations as fallbacks
                    for ext in image_extensions:
                        possible_paths.extend([
                            os.path.join(os.path.dirname(json_file_path), f"{image_id}{ext}"),  # Same directory as JSON
                            os.path.join(os.path.dirname(json_file_path), 'images', f"{image_id}{ext}"),  # images subfolder
                            os.path.join('uploads', f"{image_id}{ext}"),  # uploads folder
                            os.path.join('/tmp/uploads', f"{image_id}{ext}"),  # Render free tier tmp folder
                            os.path.join(os.environ.get('UPLOAD_FOLDER', 'uploads'), f"{image_id}{ext}")  # Environment variable path
                        ])
                    
                    image_path = None
                    for path in possible_paths:
                        if os.path.exists(path):
                            image_path = path
                            break
                    
                    # Log image path search results for debugging
                    if image_path:
                        print(f"Found image at: {image_path}")
                    else:
                        print(f"Could not find image for ID {image_id}. Searched paths: {possible_paths}")
                    
                    img_element = None
                    if image_path and os.path.exists(image_path):
                        output_image_path = os.path.join(temp_dir, f"temp_{step['image']['id']}.png")
                        targets = [action['target']] if 'target' in action else []
                        taps = []
                        swipes = []

                        if action_type == 'tap':
                            taps.append({'x': action['action']['x'], 'y': action['action']['y']})
                        elif action_type == 'swipe':
                            swipes.append(action['action'])

                        image_with_annotations = draw_bounding_boxes_and_annotations(image_path, targets, taps, swipes,
                                                                                     output_image_path)
                        if image_with_annotations:
                            img_element = Image(image_with_annotations)
                            img_element._restrictSize(3.5 * inch, 3.5 * inch)

                    if img_element:
                        step_content.append([img_element])

                    step_table = Table(step_content, colWidths=[3.7 * inch])
                    step_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 2),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 2)
                    ]))

                    step_data.append(step_table)

            # Add success condition section after processing all steps
            task_elements.append(Paragraph("Success Condition:", small_header_style))
            if success_description is not None:
                task_elements.append(Paragraph(f"Description: {success_description}", normal_style))
                task_elements.append(Paragraph(f"isText: {is_text}", normal_style))
            else:
                task_elements.append(Paragraph("No success condition found", normal_style))
            task_elements.append(Spacer(1, 12))

            # Create a two-column grid for steps
            step_grid_data = []
            for i in range(0, len(step_data), 2):
                if i + 1 < len(step_data):
                    step_grid_data.append([step_data[i], step_data[i + 1]])
                else:
                    step_grid_data.append([step_data[i], ''])

            grid_table = Table(step_grid_data, colWidths=[3.75 * inch, 3.75 * inch])
            grid_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5)
            ]))

            task_elements.append(grid_table)

            # Add all task elements to the main elements list
            elements.extend(task_elements)
            elements.append(PageBreak())

        # Build the PDF document
        doc.build(elements)
    print(f"PDF report successfully created: {output_pdf_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate PDF report from JSON task data")
    parser.add_argument("input_json", help="Path to the input JSON file")
    parser.add_argument("-o", "--output", help="Path to save the output PDF (optional)")
    parser.add_argument("-i", "--images", help="Path to directory containing image files (optional)")

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.input_json):
        print(f"Error: Input file '{args.input_json}' does not exist.")
        return

    output_path = args.output
    images_dir = args.images

    # Validate images directory if provided
    if images_dir and not os.path.exists(images_dir):
        print(f"Warning: Images directory '{images_dir}' does not exist.")
        images_dir = None

    try:
        create_multi_task_pdf_report(args.input_json, output_path, images_dir)
    except Exception as e:
        print(f"An error occurred while generating the report: {str(e)}")


if __name__ == "__main__":
    main()