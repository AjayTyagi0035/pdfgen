# PDF Generator Web Application

This is a web application that generates PDF reports from JSON task data. It visualizes tasks for a collected app and all its steps, actions, and screenshots.

## Features

- Upload JSON files with app task data
- Generate comprehensive PDF reports with visualizations
- Automatic processing of screenshots and annotations
- Web interface for easy uploading

## Deployment on Render

This application is configured for deployment on Render.com's free tier.

### Deployment Steps

1. Create a new Git repository and push this code to it
2. Sign up for a free Render account at https://render.com
3. In the Render dashboard, click "New" and select "Web Service"
4. Connect your Git repository
5. Configure the deployment with these settings:
   - Name: pdf-generator (or any name you prefer)
   - Environment: Python
   - Region: Choose the region closest to your users
   - Branch: main (or your default branch)
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Instance Type: Free
6. Add the following environment variables (click "Advanced" → "Add Environment Variable"):
   - PYTHON_VERSION: 3.9.0
   - UPLOAD_FOLDER: /tmp/uploads
   - OUTPUT_FOLDER: /tmp/outputs
7. Click "Create Web Service"

### Important Notes for Free Tier

- The free tier doesn't support persistent disk storage
- Files will be stored temporarily and may be lost when the service restarts
- Uploaded files and generated PDFs will be stored in `/tmp` directories
- If you need persistent storage, consider upgrading to a paid plan

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
- If your JSON references image files, you'll need to ensure those images are uploaded to the same server
- For the free tier deployment, you can manually upload images to the `/tmp/uploads` directory, but be aware they will be removed when the instance restarts

### Handling Image References

For the PDF generator to work correctly with images:

1. Upload your JSON file through the web interface
2. If your JSON references images that aren't included with the upload:
   - Those images need to be present on the server
   - For local development, place them in the `uploads` folder
   - For Render deployment on the free tier, the app will look in `/tmp/uploads`
   - Consider building a more comprehensive solution with an image upload feature for production use
