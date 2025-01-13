import os, cloudinary
import cloudinary.uploader
# from cloudinary.utils import cloudinary_url

from dotenv import load_dotenv
load_dotenv()

CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
API_KEY = os.getenv('CLOUDINARY_API_KEY')
API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

cloudinary.config(
    cloud_name = CLOUD_NAME,
    api_key = API_KEY,
    api_secret = API_SECRET,
    secure=True
)

"""
Upload a local image to Cloudinary

Args:
    image_path (str): Path to local image file
    public_id (str, optional): Custom public ID for the image
    
Returns:
    dict: Cloudinary upload response
"""
def upload_local_image(image_path, public_id=None):
    try:
        upload_result = cloudinary.uploader.upload(
            image_path,
            public_id=public_id,
            unique_filename=True
        )
        return upload_result
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        return None

if os.path.isdir('images'):
    for image in os.listdir('images'):
        image_path = os.path.join('images', image)
        result = upload_local_image(image_path)
        print(f'Url = {result['secure_url']}')
else:
    print('Cannot find images folder, aborting')

# DEMO CODE
# # Upload an image
# upload_result = cloudinary.uploader.upload("https://res.cloudinary.com/demo/image/upload/getting-started/shoes.jpg",
#                                            public_id="shoes")
# print(upload_result["secure_url"])

# # Optimize delivery by resizing and applying auto-format and auto-quality
# optimize_url, _ = cloudinary_url("shoes", fetch_format="auto", quality="auto")
# print(optimize_url)

# # Transform the image: auto-crop to square aspect_ratio
# auto_crop_url, _ = cloudinary_url("shoes", width=500, height=500, crop="auto", gravity="auto")
# print(auto_crop_url)