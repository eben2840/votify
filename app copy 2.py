from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory user storage
users = []


# User SignUp
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    full_name = data.get('full_name')
    password = data.get('password')
    
    print("Registration attempt for email:", email)

    # if not all([email, full_name, service, password]):
    if not all([email, full_name, password]):
        return jsonify({'message': 'All fields are required'}), 400

    if any(user['email'] == email for user in users):
        return jsonify({'message': 'Email already registered'}), 409

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    users.append({
        'email': email,
        'full_name': full_name,
        'password': hashed_password
    })
    print("Successfully registered user:", email)
    return jsonify({'message': 'User registered successfully'}), 201


# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = next((u for u in users if u['email'] == email), None)
    if user and check_password_hash(user['password'], password):
        return jsonify({
            'status': 200,
            'message': 'Login successful'
        }), 200
    return jsonify({
        'status': 200,
        'message': 'Invalid email or password'
    }), 401








# service dropdown
services = [
    'plumber',
    'electrician',
    'carpenter',
    'painter',
    'cleaner',
    'mason',
    'welder',
    'tailor',
    'barber',
    'beautician',
    'cook',
    'driver',
    'gardener',
    'laundry',
    'mechanic',
    'photographer',
    'programmer',
    'tutor',
    'others'
]


# Business Signup
@app.route('/business_sign_up', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    name_of_business = data.get('name_of_business')
    services_selected = data.get('services_selected')
    number = data.get('number')
    location = data.get('location')
    full_name = data.get('full_name')
    password = data.get('password')
    

    print("Registration attempt for email:", email)

    # if not all([email, full_name, service, password]):
    if not all([email, full_name, password, name_of_business,services, location,number ]):
        return jsonify({'message': 'All fields are required'}), 400

    # make the others an input field when the user clicks on it
    if services_selected == 'others':
        services_selected = data.get('others')

    # add service to the services
    if services_selected not in services:
        return jsonify({'message': 'Please select a valid service from the dropdown', 'available_services': services}), 400   


    # email verification
    if any(user['email'] == email for user in users):
        return jsonify({'message': 'Email already registered'}), 409

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    users.append({
        'email': email,
        'name_of_business': name_of_business,
        'location':location,
        'number': number,
        'service': services_selected,
        'full_name': full_name,
        'password': hashed_password
    })
    print("Successfully registered user:", email)
    return jsonify({'message': 'User registered successfully'}), 201




# Business Login
@app.route('/business_login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = next((u for u in users if u['email'] == email), None)
    if user and check_password_hash(user['password'], password):
        return jsonify({
            'status': 200,
            'message': 'Login successful'
        }), 200
    return jsonify({
        'status': 200,
        'message': 'Invalid email or password'
    }), 401



# Search endpoint for user
@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', '').lower()
    if not keyword:
        return jsonify({'message': 'Keyword is required'}), 400

    matched_users = [
        {
            'email': u['email'],
            'full_name': u['full_name'],
            'services': u['services']
        }
        for u in users if keyword in u['services']
    ]

    return jsonify({'results': matched_users}), 200


if __name__ == '__main__':
    app.run(port=4000, debug=True, host= '0.0.0.0')