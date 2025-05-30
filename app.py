from flask import Flask, request, render_template, send_file
import os
import uuid
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
            return render_template('index.html', error='No file part')
        
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='No selected file')
        
        if file and file.filename.endswith('.json'):
            # Generate a unique filename to prevent collisions
            unique_id = str(uuid.uuid4())
            filename = secure_filename(file.filename)
            base_filename = os.path.splitext(filename)[0]
            
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{filename}")
            file.save(input_path)
            
            output_filename = f"{base_filename}_report_{unique_id}.pdf"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
              try:
                # Call your PDF generation function
                create_multi_task_pdf_report(input_path, output_path)
                
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
                    except Exception as cleanup_error:
                        print(f"Error during cleanup: {cleanup_error}")
                
                return response
            except Exception as e:
                return render_template('index.html', error=f"Error generating PDF: {str(e)}")
        
        return render_template('index.html', error='Invalid file type. Please upload a JSON file.')
    
    return render_template('index.html')

if __name__ == '__main__':
    # Use environment variable PORT if available (for Render deployment)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)