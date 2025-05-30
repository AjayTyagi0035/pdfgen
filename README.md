# PDF Generator Web Application

This is a web application that generates PDF reports from JSON task data. It visualizes tasks for a collected app and all its steps, actions, and screenshots.

## Features

- Upload JSON files with app task data
- Generate comprehensive PDF reports with visualizations
- Automatic processing of screenshots and annotations
- Web interface for easy uploading

## Deployment on Render

This application is configured for deployment on Render.com.

### Deployment Steps

1. Create a new Git repository and push this code to it
2. Sign up for a Render account at https://render.com
3. In the Render dashboard, click "New" and select "Blueprint"
4. Connect your Git repository
5. Render will automatically detect the `render.yaml` file and configure the deployment
6. Click "Apply" to deploy the application

Alternatively, you can deploy manually:

1. In the Render dashboard, click "New" and select "Web Service"
2. Connect your Git repository
3. Configure the deployment with these settings:
   - Name: pdf-generator
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. Add the following environment variables:
   - PYTHON_VERSION: 3.9.0
   - UPLOAD_FOLDER: /opt/render/project/src/data/uploads
   - OUTPUT_FOLDER: /opt/render/project/src/data/outputs
5. Add a disk resource:
   - Name: data
   - Mount Path: /opt/render/project/src/data
   - Size: 1 GB
6. Click "Create Web Service"
5. Use the following settings:
   - Name: pdf-generator (or any name you prefer)
   - Runtime: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
6. Click "Create Web Service"

## Local Development

1. Install requirements:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

3. Open your browser to http://localhost:5000

## Application Structure

- `app.py`: Main Flask application
- `generate_pdf.py`: Core PDF generation logic
- `templates/index.html`: Web interface template
- `uploads/`: Directory for uploaded JSON files
- `outputs/`: Directory for generated PDF reports

## Notes

- The application expects JSON files with specific structure including tasks and references to image files
- Make sure your JSON file paths are correctly structured if you're using the application locally
