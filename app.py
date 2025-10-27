from flask import Flask, render_template, request, jsonify
import os
import random
import time
from werkzeug.utils import secure_filename
from PIL import Image
import cv2
import numpy as np

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'static/uploads'
DATASET_FOLDER = 'static/dataset'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATASET_FOLDER'] = DATASET_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATASET_FOLDER, exist_ok=True)

# Disease database with solutions
DISEASE_DATABASE = {
    'healthy': {
        'solution': 'Your plant is healthy! Continue with regular watering and proper sunlight. Maintain good soil nutrition and monitor for any changes.',
        'confidence': 0.95,
        'prevention': 'Continue current care routine, ensure proper spacing between plants.'
    },
    'powdery_mildew': {
        'solution': 'Apply sulfur-based fungicide every 7-10 days. Remove severely infected leaves. Improve air circulation around plants.',
        'confidence': 0.87,
        'prevention': 'Avoid overhead watering, plant in sunny locations, use resistant varieties.'
    },
    'leaf_spot': {
        'solution': 'Remove and destroy infected leaves. Apply copper-based fungicide weekly. Avoid watering foliage.',
        'confidence': 0.82,
        'prevention': 'Water at base of plants, ensure good drainage, rotate crops annually.'
    },
    'blight': {
        'solution': 'Apply chlorothalonil or mancozeb fungicide. Remove infected plants immediately. Sterilize gardening tools.',
        'confidence': 0.89,
        'prevention': 'Use disease-free seeds, practice crop rotation, avoid working with wet plants.'
    },
    'rust': {
        'solution': 'Apply fungicide containing myclobutanil. Remove infected leaves. Ensure proper plant spacing.',
        'confidence': 0.85,
        'prevention': 'Plant resistant varieties, clean garden debris, water early in day.'
    },
    'root_rot': {
        'solution': 'Improve soil drainage. Reduce watering frequency. Apply phosphorous acid fungicide to soil.',
        'confidence': 0.91,
        'prevention': 'Use well-draining soil, avoid overwatering, plant in raised beds.'
    },
    'aphid_infestation': {
        'solution': 'Spray with insecticidal soap or neem oil weekly. Introduce ladybugs or lacewings. Use strong water spray to dislodge.',
        'confidence': 0.88,
        'prevention': 'Encourage beneficial insects, use reflective mulch, inspect plants regularly.'
    },
    'nutrient_deficiency': {
        'solution': 'Apply balanced fertilizer (NPK 10-10-10). Test soil pH and adjust. Add compost or specific nutrient supplements.',
        'confidence': 0.84,
        'prevention': 'Regular soil testing, use slow-release fertilizers, maintain proper pH levels.'
    }
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_random_dataset_image():
    """Get a random image from the dataset folder"""
    try:
        if not os.path.exists(DATASET_FOLDER):
            create_sample_dataset()

        images = [f for f in os.listdir(DATASET_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        if not images:
            create_sample_dataset()
            images = [f for f in os.listdir(DATASET_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        if images:
            random_image = random.choice(images)
            return os.path.join(DATASET_FOLDER, random_image), random_image
        else:
            return None, None
    except Exception as e:
        print(f"Error getting random image: {e}")
        return None, None


def create_sample_dataset():
    """Create sample dataset images for demonstration"""
    try:
        # Create more realistic sample images
        plant_types = ['Tomato', 'Potato', 'Corn', 'Wheat', 'Rice', 'Soybean']
        conditions = ['Healthy', 'Diseased', 'Early_Stage', 'Advanced']

        for i in range(12):  # Create 12 sample images
            # Generate random color based on condition
            if i % 4 == 0:  # Healthy - vibrant green
                color = (random.randint(30, 80), random.randint(150, 200), random.randint(30, 80))
            elif i % 4 == 1:  # Early disease - yellowish
                color = (random.randint(100, 150), random.randint(150, 200), random.randint(50, 100))
            else:  # Diseased - brownish
                color = (random.randint(50, 100), random.randint(100, 150), random.randint(150, 200))

            # Create image with plant-like pattern
            img = np.zeros((400, 400, 3), dtype=np.uint8)

            # Create a plant-like shape (oval/circle)
            center_x, center_y = 200, 200
            radius_x, radius_y = 150, 180

            # Draw main plant body
            for y in range(400):
                for x in range(400):
                    dx = (x - center_x) / radius_x
                    dy = (y - center_y) / radius_y
                    if dx * dx + dy * dy <= 1:
                        # Add some texture variation
                        variation = random.randint(-20, 20)
                        img[y, x] = [
                            max(0, min(255, color[0] + variation)),
                            max(0, min(255, color[1] + variation)),
                            max(0, min(255, color[2] + variation))
                        ]

            # Add some spots for diseased look
            if i % 4 != 0:  # Not healthy
                for _ in range(random.randint(5, 15)):
                    spot_x = random.randint(50, 350)
                    spot_y = random.randint(50, 350)
                    spot_radius = random.randint(5, 20)
                    spot_color = (random.randint(100, 200), random.randint(50, 100), random.randint(50, 100))
                    cv2.circle(img, (spot_x, spot_y), spot_radius, spot_color, -1)

            plant_type = random.choice(plant_types)
            condition = conditions[i % 4]
            filename = f"{plant_type}_{condition}_{i + 1}.jpg"
            cv2.imwrite(os.path.join(DATASET_FOLDER, filename), img)

        print("Sample dataset created successfully")
    except Exception as e:
        print(f"Error creating sample dataset: {e}")


def analyze_image(image_path):
    """Analyze the image and predict disease with realistic processing simulation"""
    try:
        # Simulate AI processing time
        time.sleep(2)

        img = cv2.imread(image_path)
        if img is None:
            return 'healthy', DISEASE_DATABASE['healthy']['solution'], DISEASE_DATABASE['healthy']['prevention'], 0.95

        # More sophisticated mock analysis
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        avg_color = np.mean(hsv, axis=(0, 1))

        # Calculate color distribution
        green_ratio = np.sum((hsv[:, :, 0] > 30) & (hsv[:, :, 0] < 90)) / (hsv.shape[0] * hsv.shape[1])
        brown_ratio = np.sum((hsv[:, :, 0] > 10) & (hsv[:, :, 0] < 25)) / (hsv.shape[0] * hsv.shape[1])
        yellow_ratio = np.sum((hsv[:, :, 0] > 25) & (hsv[:, :, 0] < 35)) / (hsv.shape[0] * hsv.shape[1])

        # Determine disease based on color ratios
        if green_ratio > 0.6:
            disease = 'healthy'
            confidence = random.uniform(0.85, 0.98)
        elif brown_ratio > 0.3:
            disease = 'blight'
            confidence = random.uniform(0.80, 0.95)
        elif yellow_ratio > 0.4:
            disease = 'nutrient_deficiency'
            confidence = random.uniform(0.75, 0.90)
        else:
            # Random selection from other diseases
            other_diseases = ['powdery_mildew', 'leaf_spot', 'rust', 'root_rot', 'aphid_infestation']
            disease = random.choice(other_diseases)
            confidence = random.uniform(0.70, 0.88)

        disease_data = DISEASE_DATABASE.get(disease, DISEASE_DATABASE['healthy'])

        return (disease.replace('_', ' ').title(),
                disease_data['solution'],
                disease_data['prevention'],
                round(confidence, 2))

    except Exception as e:
        print(f"Error analyzing image: {e}")
        return 'Unknown', 'Unable to analyze image. Please try again.', 'Consult with agricultural expert.', 0.0


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/scan_crop', methods=['GET', 'POST'])
def scan_crop():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file selected')

        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='No file selected')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Show processing page before analysis
            return render_template('processing.html',
                                   image_path=f'uploads/{filename}',
                                   source='upload')

    return render_template('scan.html')


@app.route('/process_scan')
def process_scan():
    """Process the scan and return results"""
    source = request.args.get('source', 'random')
    image_path = request.args.get('image_path', '')

    if source == 'upload':
        full_path = os.path.join('static', image_path)
        disease, solution, prevention, confidence = analyze_image(full_path)

        return render_template('result.html',
                               img_name=image_path,
                               disease=disease,
                               solution=solution,
                               prevention=prevention,
                               confidence=confidence,
                               source='upload')

    else:  # random scan
        random_image_path, random_filename = get_random_dataset_image()

        if random_image_path:
            disease, solution, prevention, confidence = analyze_image(random_image_path)

            return render_template('result.html',
                                   img_name=f'dataset/{random_filename}',
                                   disease=disease,
                                   solution=solution,
                                   prevention=prevention,
                                   confidence=confidence,
                                   source='random')
        else:
            return render_template('error.html', error='No dataset images available')


@app.route('/scan_random')
def scan_random():
    """Show processing page for random scan"""
    random_image_path, random_filename = get_random_dataset_image()

    if random_image_path:
        return render_template('processing.html',
                               image_path=f'dataset/{random_filename}',
                               source='random')
    else:
        return render_template('error.html', error='No dataset images available')


@app.route('/auto_scan')
def auto_scan():
    """Automatically scan a random image (for Scan Another Crop button)"""
    random_image_path, random_filename = get_random_dataset_image()

    if random_image_path:
        return render_template('processing.html',
                               image_path=f'dataset/{random_filename}',
                               source='random')
    else:
        return render_template('error.html', error='No dataset images available')


if __name__ == '__main__':
    create_sample_dataset()
    app.run(debug=True, port=5000)