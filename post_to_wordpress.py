import json
import requests
from requests.auth import HTTPBasicAuth
from config import WORDPRESS_URL, WORDPRESS_USERNAME, WORDPRESS_PASSWORD
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_valid_image_url(url):
    """Check if the URL points to a valid image"""
    if not url:
        return False
        
    try:
        # Check if URL is accessible
        response = requests.head(url, timeout=5)
        if response.status_code != 200:
            return False
            
        # Check if content type is an image
        content_type = response.headers.get('Content-Type', '')
        return content_type.startswith('image/')
    except requests.exceptions.RequestException:
        return False

def upload_image(image_url):
    """Upload image to WordPress with improved error handling"""
    if not is_valid_image_url(image_url):
        logging.warning(f"Invalid or inaccessible image URL: {image_url}")
        return None
        
    try:
        image_data = requests.get(image_url, timeout=10).content
        filename = image_url.split("/")[-1]
        
        # Handle potential non-standard filenames
        if '.' not in filename:
            filename = f"image-{hash(image_url)}.jpg"
            
        headers = {
            'Content-Disposition': f'attachment; filename={filename}',
            'Content-Type': 'image/jpeg',  # Assuming JPEG as default
        }
        
        response = requests.post(
            f"{WORDPRESS_URL}/wp-json/wp/v2/media",
            auth=HTTPBasicAuth(WORDPRESS_USERNAME, WORDPRESS_PASSWORD),
            headers=headers,
            data=image_data,
            timeout=30  # Longer timeout for uploads
        )
        
        response.raise_for_status()
        logging.info(f"Image uploaded successfully: {image_url}")
        return response.json()['source_url']
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to upload image: {e}")
        return None

def post_to_wordpress(title, content, image_url=None):
    """Post content to WordPress with graceful image failure handling"""
    image_content = ""
    
    if image_url:
        try:
            image_src = upload_image(image_url)
            if image_src:
                image_content = f'<img src="{image_src}" alt="{title}"><br>'
        except Exception as e:
            logging.error(f"Image processing error: {e}")
            # Continue without the image
    
    # Combine image (if available) with the rest of the content
    full_content = f"{image_content}{content}"
    
    post = {
        'title': title,
        'content': full_content,
        'status': 'publish'
    }
    
    response = requests.post(
        f"{WORDPRESS_URL}/wp-json/wp/v2/posts",
        auth=HTTPBasicAuth(WORDPRESS_USERNAME, WORDPRESS_PASSWORD),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(post),
        timeout=15
    )
    
    response.raise_for_status()
    logging.info(f"Post created successfully: {title}")
    return response.json()