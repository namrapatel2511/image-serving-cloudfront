from flask import Flask, request, redirect, url_for, render_template
import boto3
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration
S3_BUCKET = 'namra-2511'
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')
S3_REGION = 'ap-south-1'
CLOUDFRONT_DOMAIN = 'd2w9tagpxi2byr.cloudfront.net'  # Replace with your CloudFront distribution domain

# Initialize S3 client
s3 = boto3.client('s3',
                  aws_access_key_id=S3_ACCESS_KEY,
                  aws_secret_access_key=S3_SECRET_KEY,
                  region_name=S3_REGION)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        file_name = request.form['file_name']
        
        if file and file_name:
            file_name = secure_filename(file_name) + os.path.splitext(file.filename)[1]
            s3.upload_fileobj(file, S3_BUCKET, file_name)  # Removed ACL
            return redirect(url_for('index'))

    # Fetch all stored images
    images = s3.list_objects_v2(Bucket=S3_BUCKET).get('Contents', [])
    image_urls = [f"https://{CLOUDFRONT_DOMAIN}/{img['Key']}" for img in images]

    return render_template('index.html', image_urls=image_urls)

if __name__ == '__main__':
    app.run(debug=True)
