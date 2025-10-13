import requests
from flask import Flask, render_template, request

# Initialize the Flask app
app = Flask(__name__)

# List of barcodes to display - these are valid products from OpenFoodFacts
barcodes = ["3168930000020", "3017620422003", "3270190127512", "8000500037560"]

def fetch_product_data(barcode):
    """Fetch product data for a single barcode"""
    url = f"https://world.openfoodfacts.net/api/v2/product/{barcode}"
    
    nutrient_keys = {
        "carbohydrates": "Carbohydrates",
        "proteins": "Proteins",
        "fat": "Fat",
        "sugars": "Sugars",
        "salt": "Salt"
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
                'nutrients': {label: "Not available" for label in nutrient_keys.values()},
                'error': True
            }
        
        product_info = data.get('product', {})
        
        product_name = product_info.get('product_name', 'Name not found')
        image_url = product_info.get('image_front_url', '')
        
        # Get nutrient info
        nutriments = product_info.get("nutriments", {})
        nutrients = {}
        for key, label in nutrient_keys.items():
            nutrients[label] = nutriments.get(key, "Not available")
        
        return {
            'barcode': barcode,
            'name': product_name,
            'image': image_url,
            'nutrients': nutrients,
            'error': False
        }
        
    except requests.exceptions.RequestException as e:
        print(f"API request failed for barcode {barcode}: {e}")
        return {
            'barcode': barcode,
            'name': 'Error fetching data',
            'image': '',
            'nutrients': {label: "Not available" for label in nutrient_keys.values()},
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
    """Display a single product by barcode"""
    product_data = fetch_product_data(barcode)
    return render_template('product.html', products=[product_data])

if __name__ == '__main__':
  # Add the port argument here
  app.run(debug=True, host='0.0.0.0', port=8080)