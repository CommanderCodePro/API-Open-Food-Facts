import requests
from flask import Flask, render_template, request

# Initialize the Flask app
app = Flask(__name__)

# List of barcodes to display - these are valid products from OpenFoodFacts
barcodes = ["9300652010374", "9310055536333"]

def fetch_product_data(barcode):
    """Fetch product data for a single barcode"""
    url = f"https://world.openfoodfacts.net/api/v2/product/{barcode}"
    
    nutrient_keys_per_100g = {
        "energy-kj": "Energy (kJ)",
        "proteins": "Protein",
        "carbohydrates": "Carbohydrates",
        "fat": "Fat",
        "saturated-fat": "Saturated Fat",
        "sugars": "Sugars",
        "fiber": "Dietary Fibre",
        "sodium": "Sodium",
        "salt": "Salt",
        "iron": "Iron"
    }
    
    nutrient_keys_per_serving = {
        "energy-kj_serving": "Energy (kJ)",
        "proteins_serving": "Protein",
        "carbohydrates_serving": "Carbohydrates",
        "fat_serving": "Fat",
        "saturated-fat_serving": "Saturated Fat",
        "sugars_serving": "Sugars",
        "fiber_serving": "Dietary Fibre",
        "sodium_serving": "Sodium",
        "salt_serving": "Salt",
        "iron_serving": "Iron"
    }
    
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Check if product exists
        if data.get('status') != 1:
            return {
                'barcode': barcode,
                'name': 'Product not found',
                'image': '',
                'nutrients_per_100g': {label: "Not available" for label in nutrient_keys_per_100g.values()},
                'nutrients_per_serving': {label: "Not available" for label in nutrient_keys_per_serving.values()},
                'nutrient_levels': {},
                'ingredients': [],
                'allergens': [],
                'nutri_score': 'Not available',
                'eco_score': 'Not available',
                'nova_group': 'Not available',
                'error': True
            }
        
        product_info = data.get('product', {})
        
        product_name = product_info.get('product_name', 'Name not found')
        image_url = product_info.get('image_front_url', '')
        
        # Get nutrient info per 100g
        nutriments = product_info.get("nutriments", {})
        nutrients_per_100g = {}
        for key, label in nutrient_keys_per_100g.items():
            value = nutriments.get(key, "Not available")
            if isinstance(value, (int, float)):
                nutrients_per_100g[label] = round(value)
            else:
                nutrients_per_100g[label] = value
        
        # Get nutrient info per serving
        nutrients_per_serving = {}
        for key, label in nutrient_keys_per_serving.items():
            value = nutriments.get(key, "Not available")
            if isinstance(value, (int, float)):
                nutrients_per_serving[label] = round(value)
            else:
                nutrients_per_serving[label] = value
        
        # Get nutrient levels
        nutrient_levels = product_info.get("nutrient_levels", {})
        
        # Get ingredients
        ingredients_data = product_info.get("ingredients", [])
        ingredients = [ingredient.get('text', '').title() for ingredient in ingredients_data] if ingredients_data else []
        
        # Get allergens
        allergens_data = product_info.get("allergens", "")
        allergens = allergens_data.split(", ") if allergens_data else []
        
        # Get Nutri-Score
        nutri_score = product_info.get("nutriscore_grade", "").upper() or "Not available"
        
        # Get Eco-Score (Green Score)
        eco_score = product_info.get("ecoscore_grade", "").upper() or "Not available"
        
        # Get NOVA processing level
        nova_group = product_info.get("nova_group", "") or "Not available"
        
        return {
            'barcode': barcode,
            'name': product_name,
            'image': image_url,
            'nutrients_per_100g': nutrients_per_100g,
            'nutrients_per_serving': nutrients_per_serving,
            'nutrient_levels': nutrient_levels,
            'ingredients': ingredients,
            'allergens': allergens,
            'nutri_score': nutri_score,
            'eco_score': eco_score,
            'nova_group': nova_group,
            'error': False
        }
        
    except requests.exceptions.RequestException as e:
        print(f"API request failed for barcode {barcode}: {e}")
        return {
            'barcode': barcode,
            'name': 'Error fetching data',
            'image': '',
            'nutrients_per_100g': {label: "Not available" for label in nutrient_keys_per_100g.values()},
            'nutrients_per_serving': {label: "Not available" for label in nutrient_keys_per_serving.values()},
            'nutrient_levels': {},
            'ingredients': [],
            'allergens': [],
            'nutri_score': 'Not available',
            'eco_score': 'Not available',
            'nova_group': 'Not available',
            'error': True
        }

#define a route for home page
@app.route('/')
def home():
  return render_template('home.html')

# Define a route for our product page
@app.route('/product')
def show_product():
    """Display multiple products based on the barcodes list"""
    # Check if barcodes are provided via URL parameters
    url_barcodes = request.args.get('barcodes')
    
    if url_barcodes:
        # Split comma-separated barcodes from URL
        barcode_list = [barcode.strip() for barcode in url_barcodes.split(',')]
    else:
        # Use default barcodes
        barcode_list = barcodes
    
    products = []
    
    # Fetch data for each barcode
    for barcode in barcode_list:
        product_data = fetch_product_data(barcode)
        products.append(product_data)
    
    # Pass the list of products to the template
    return render_template('product.html', products=products)

# Route to display a single product by barcode
@app.route('/product/<barcode>')
def show_single_product(barcode):
    """Display a  single product by barcode"""
    product_data = fetch_product_data(barcode)
    return render_template('product.html', products=[product_data])

if __name__ == '__main__':
  # Add the port argument here
  app.run(debug=True, host='0.0.0.0', port=8080)