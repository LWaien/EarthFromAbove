import os
from sentinelhub import SHConfig, SentinelHubRequest, MimeType, CRS, BBox, bbox_to_dimensions, bbox_to_resolution, DataCollection, ResamplingType, MosaickingOrder
from PIL import Image, ImageEnhance

# Sentinel Hub credentials (replace with your own credentials)
CLIENT_ID = ''
CLIENT_SECRET = ''
INSTANCE_ID = ''

# Set up SentinelHub configuration
config = SHConfig()
config.sh_client_id = CLIENT_ID
config.sh_client_secret = CLIENT_SECRET
config.instance_id = INSTANCE_ID

# Create images directory if it doesn't exist
os.makedirs("images", exist_ok=True)

# Function to fetch satellite image based on latitude and longitude
def fetch_satellite_image(latitude, longitude):
    # Define bounding box with small offsets
    lon_offset, lat_offset = 0.15, 0.15
    lon1, lon2 = longitude - lon_offset, longitude + lon_offset
    lat1, lat2 = latitude - lat_offset, latitude + lat_offset

    # Create bounding box
    bbox = BBox(bbox=(lon1, lat1, lon2, lat2), crs=CRS.WGS84)
    resolution = bbox_to_resolution(bbox, width=2500, height=1406)
    dimensions_size = bbox_to_dimensions(bbox, resolution=resolution)

    # Evalscript for true color image
    evalscript_true_color = """
        //VERSION=3
        function setup() {
            return {
                input: [{ bands: ["B02", "B03", "B04"] }],
                output: { bands: 3 }
            };
        }

        function evaluatePixel(sample) {
            return [sample.B04, sample.B03, sample.B02];
        }
    """

    # Create a request to fetch the image
    request_true_color = SentinelHubRequest(
        evalscript=evalscript_true_color,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L1C,
                time_interval=("2020-07-01", "2020-07-30"),
                mosaicking_order=MosaickingOrder.LEAST_CC,
                upsampling=ResamplingType.BILINEAR
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
        bbox=bbox,
        size=dimensions_size,
        config=config,
    )

    # Fetch the image
    true_color_imgs = request_true_color.get_data()
    image_array = true_color_imgs[0]
    image = Image.fromarray(image_array)

    # Enhance brightness and contrast
    enhancer = ImageEnhance.Brightness(image)
    brightened_image = enhancer.enhance(4)
    contrast_enhance = ImageEnhance.Contrast(brightened_image)
    brightened_image = contrast_enhance.enhance(1.2)

    # Generate filename with coordinates (latitude, longitude)
    coordinates_str = f"{latitude:.4f}_{longitude:.4f}"
    filename = f"sat/static/images/{coordinates_str}.png"

    # Save the image
    brightened_image.save(filename)
    print(f"Saved image: {filename}")

    # Keep only the latest 30 images
    MAX_IMAGES = 0
    image_files = sorted(os.listdir('sat/static/images/'))
    if len(image_files) > MAX_IMAGES:
        for old_image in image_files[:-MAX_IMAGES]:
            os.remove(os.path.join('images', old_image))
            print(f"Deleted old image: {old_image}")