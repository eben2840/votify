from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
CORS(app)  


CSV_FILE = 'students.csv'
ELECTION_FILE = 'election.csv'
CATEGORY_FILE = 'categories.csv'
CANDIDATE_FILE = 'election_candidates.csv'
VOTE_FILE = 'votes.csv'

# Load students into memory (optional)
students = {}
def load_students():
    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            students[row['student_id']] = row['password']

# Read CSV as list of dicts
def read_students():
    with open(CSV_FILE, mode='r') as f:
        return list(csv.DictReader(f))

def write_students(data):
    with open(CSV_FILE, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['student_id', 'password', 'voted'])
        writer.writeheader()
        writer.writerows(data)

# @app.route('/login', methods=['POST'])
# def login():
#     data = request.json
#     student_id = data.get('student_id')
#     password = data.get('password')

#     students = read_students()
#     for student in students:
#         if student['student_id'] == student_id and student['password'] == password:
#             return jsonify({'status':'success','message': 'Login successful'})
#     return jsonify({'status': '\failed','message': 'Invalid credentials'})


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username') or data.get('student_id')
    password = data.get('password')

    # Check if admin login
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin123"
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return jsonify({
            'status': 'success',
            'message': 'Admin login successful',
            'isAdmin': True
        })

    # Check student login
    students = read_students()
    for student in students:
        if student['student_id'] == username and student['password'] == password:
            return jsonify({
                'status': 'success',
                'message': 'Login successful',
                'isAdmin': False,
                'student_id': student['student_id']
            })

    return jsonify({
        'status': 'failed',
        'message': 'Invalid credentials'
    })


# @app.route('/vote', methods=['POST'])
# def vote():
#     data = request.json
#     student_id = data.get('student_id')
#     ballot = data.get('ballot')

#     if not ballot:
#         return jsonify({'success': False, 'message': 'Ballot not dropped'})

#     students = read_students()
#     updated = False

#     for student in students:
#         if student['student_id'] == student_id:
#             if student.get('voted', 'false').lower() == 'true':
#                 return jsonify({'success': False, 'message': 'Already voted'})
#             student['voted'] = 'true'
#             updated = True
#             break

#     if updated:
#         write_students(students)
#         return jsonify({'success': True, 'message': 'Vote recorded'})
#     else:
#         return jsonify({'success': False, 'message': 'Student not found'})




# Read all votes
def read_votes():
    with open(VOTE_FILE, mode='r') as f:
        return list(csv.DictReader(f))

# Write votes to CSV
def write_votes(data):
    with open(VOTE_FILE, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['student_id', 'category_id', 'candidate_name'])
        writer.writeheader()
        writer.writerows(data)

        
@app.route('/vote', methods=['POST'])
def vote():
    data = request.json
    student_id = data.get('student_id')
    ballot = data.get('ballot')  # expecting a dict like {"1": "Ama", "2": "Kofi"}

    if not ballot or not isinstance(ballot, dict):
        return jsonify({'success': False, 'message': 'Invalid ballot format'})

    votes = read_votes()
    already_voted = set((v['student_id'], v['category_id']) for v in votes)

    new_votes = []
    for category_id, candidate_name in ballot.items():
        if not category_id or not candidate_name:
            continue

        if (student_id, category_id) in already_voted:
            return jsonify({'success': False, 'message': f'You have already voted for a candidate in category'})

        new_votes.append({
            'student_id': student_id,
            'category_id': category_id,
            'candidate_name': candidate_name
        })

    if not new_votes:
        return jsonify({'success': False, 'message': 'No valid votes recorded'})

    votes.extend(new_votes)
    write_votes(votes)
    return jsonify({'success': True, 'message': 'Votes recorded'})


# Load categories from CSV
def load_categories():
    categories = []
    with open(CATEGORY_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            categories.append({
                "id": row['id'],
                "name": row['name']
            })
    return categories

# Load candidates by category
def load_candidates():
    candidates_by_category = {}
    with open(CANDIDATE_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cat_id = row['category_id']
            candidate = {
                "name": row['name'],
                "about": row['about'],
                "contact": row['contact'],
                "category_id": row['category_id']
            }
            if cat_id not in candidates_by_category:
                candidates_by_category[cat_id] = []
            candidates_by_category[cat_id].append(candidate)
    return candidates_by_category

# Load election metadata
def load_election():
    with open(ELECTION_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            return {
                "title": row['title'],
                "start_date": row['start_date'],
                "end_date": row['end_date']
            }
    return {}

@app.route('/election')
def get_election_data():
    election = load_election()
    categories = load_categories()
    candidates = load_candidates()

    for category in categories:
        category_id = category['id']
        category['candidates'] = candidates.get(category_id, [])

    election['categories'] = categories
    return jsonify(election)


from flask import request, jsonify

@app.route('/search_new')
def search_new():
    search_query = request.args.get('q', '').lower()

    election = load_election()
    categories = load_categories()
    candidates = load_candidates()

    filtered_categories = []

    for category in categories:
        category_id = category['id']
        category_name = category['name'].lower()

        if search_query in category_name:
            category['candidates'] = candidates.get(category_id, [])
            filtered_categories.append(category)

    # If no search query, return all
    if not search_query:
        for category in categories:
            category_id = category['id']
            category['candidates'] = candidates.get(category_id, [])
        election['categories'] = categories
    else:
        election['categories'] = filtered_categories

    return jsonify(election)




@app.route('/results', methods=['GET'])
def get_results():
    # Load candidates
    candidates_by_category = {}
    with open(CANDIDATE_FILE, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cat_id = row['category_id']
            candidate_name = row['name']
            if cat_id not in candidates_by_category:
                candidates_by_category[cat_id] = {'category_name': row['position'], 'candidates': {}}
            candidates_by_category[cat_id]['candidates'][candidate_name] = 0

    # Count votes
    with open(VOTE_FILE, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cat_id = row['category_id']
            candidate_name = row['candidate_name']
            if cat_id in candidates_by_category and candidate_name in candidates_by_category[cat_id]['candidates']:
                candidates_by_category[cat_id]['candidates'][candidate_name] += 1

    # Format response
    result = []
    for cat_id, data in candidates_by_category.items():
        candidate_list = [
            {'name': name, 'votes': votes}
            for name, votes in data['candidates'].items()
        ]
        # sort descending
        candidate_list.sort(key=lambda x: x['votes'], reverse=True)
        result.append({
            'category': data['category_name'],
            'candidates': candidate_list
        })

    return jsonify({'results': result})





# numbers = [23, 324, 4, 6, 7, 8, 43]
# numbers.sort()
# print('number sorting')
# print(numbers)

if __name__ == '__main__':
    load_students()
    app.run(debug=True, host="0.0.0.0", port=4000)
