from flask import Flask, request, render_template, send_file
import os
import uuid
import zipfile
import shutil
from werkzeug.utils import secure_filename
from generate_pdf import create_multi_task_pdf_report

app = Flask(__name__)
# Get paths from environment variables if available (for cloud deployment)
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['OUTPUT_FOLDER'] = os.environ.get('OUTPUT_FOLDER', 'outputs')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return render_template('index.html', error='No JSON file selected')
        
        json_file = request.files['file']
        if json_file.filename == '':
            return render_template('index.html', error='No JSON file selected')
        
        # Check if JSON file is valid
        if not json_file.filename.endswith('.json'):
            return render_template('index.html', error='Invalid file type. Please upload a JSON file')
            
        # Generate a unique ID for this processing session
        unique_id = str(uuid.uuid4())
        
        # Process JSON file
        json_filename = secure_filename(json_file.filename)
        base_filename = os.path.splitext(json_filename)[0]
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{json_filename}")
        json_file.save(input_path)
        
        # Create a directory for extracted images
        images_dir = os.path.join(app.config['UPLOAD_FOLDER'], f"images_{unique_id}")
        os.makedirs(images_dir, exist_ok=True)
        
        # Process ZIP file if present
        if 'images' in request.files:
            zip_file = request.files['images']
            if zip_file and zip_file.filename != '' and zip_file.filename.endswith('.zip'):
                zip_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_images.zip")
                zip_file.save(zip_path)
                
                # Extract images from ZIP file
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(images_dir)
                    print(f"Extracted ZIP contents to {images_dir}")
                except Exception as e:
                    print(f"Error extracting ZIP file: {str(e)}")
                    return render_template('index.html', error=f"Error extracting ZIP file: {str(e)}")
                
                # Delete the zip file after extraction                try:
                    if os.path.exists(zip_path):
                        os.remove(zip_path)
                except Exception as e:
                    print(f"Error removing ZIP file: {str(e)}")
                    
        output_filename = f"{base_filename}_report_{unique_id}.pdf"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        try:
            # Set a timeout for the process to avoid hanging the server
            import threading
            import time
            from functools import partial
              # Create a flag to track if processing completed
            processing_complete = {"done": False, "error": None}
            
            # Function to run in separate thread
            def process_pdf():
                try:
                    print(f"Starting PDF generation for {json_filename} with {len(os.listdir(images_dir))} images")
                    # Call the PDF generation function with the images directory
                    create_multi_task_pdf_report(input_path, output_path, images_dir)
                    processing_complete["done"] = True
                    print(f"PDF generation completed successfully: {output_path}")
                except Exception as proc_error:
                    import traceback
                    processing_complete["error"] = str(proc_error)
                    print(f"Error in PDF processing thread: {proc_error}")
                    print(f"Traceback: {traceback.format_exc()}")
            
            # Start the processing in a background thread
            process_thread = threading.Thread(target=process_pdf)
            process_thread.daemon = True
            process_thread.start()            # Wait for processing to complete with a timeout
            max_wait_time = 270  # seconds (increased for larger files, but less than Gunicorn's 300s timeout)
            wait_interval = 1   # seconds
            total_waited = 0
            
            while not processing_complete["done"] and total_waited < max_wait_time:
                time.sleep(wait_interval)
                total_waited += wait_interval
            
            # Check if process completed successfully
            if not processing_complete["done"]:
                if process_thread.is_alive():
                    return render_template('index.html', error="PDF generation timed out. Your file might be too large or complex. Try with a smaller file or fewer images.")
                if processing_complete["error"]:
                    return render_template('index.html', error=f"Error generating PDF: {processing_complete['error']}")
                
            # Return the PDF file for download
            response = send_file(output_path, as_attachment=True, download_name=f"{base_filename}_report.pdf")
            
            # Schedule file cleanup after the response is sent
            @response.call_on_close
            def cleanup():
                try:
                    # Delete temporary files to save space
                    if os.path.exists(input_path):
                        os.remove(input_path)
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    if os.path.exists(images_dir):
                        shutil.rmtree(images_dir)                
                except Exception as cleanup_error:
                    print(f"Error during cleanup: {cleanup_error}")
            
            return response
        except Exception as e:
            # Clean up in case of error
            if os.path.exists(images_dir):
                shutil.rmtree(images_dir)
            return render_template('index.html', error=f"Error generating PDF: {str(e)}")
    return render_template('index.html')

if __name__ == '__main__':
    # Use environment variable PORT if available (for Render deployment)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)