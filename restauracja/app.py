from flask import Flask, jsonify, request
from init_database import init_db, get_db
from seeder import seed_database

app = Flask(__name__)

init_db()

@app.route('/categories', methods=['GET', 'POST'])
def categories():
    db = get_db()
    if request.method == 'GET':
        categories = db.execute("SELECT category_id, name FROM categories").fetchall()
        return jsonify([{'category_id': row[0], 'name': row[1]} for row in categories])
    elif request.method == 'POST':
        data = request.json
        db.execute("INSERT INTO categories (category_id, name) VALUES (?, ?)", (data['category_id'], data['name']))
        db.commit()
        return jsonify({'message': 'Category added successfully!'}), 201

@app.route('/products', methods=['GET', 'POST'])
def products():
    db = get_db()
    
    if request.method == 'GET':
        category = request.args.get('category')  # Fetch category ID from query parameters
        
        if category:
            try:
                # If category_id is provided, filter products by that category
                products = db.execute("""
                    SELECT product_id, p.name, price, p.category_id
                    FROM products p
                    JOIN categories c ON p.category_id = c.category_id
                    WHERE c.name = ?
                """, (category,)).fetchall()
            except ValueError:
                return jsonify({'error': 'Invalid category ID'}), 400
        else:
            # Fetch all products if no category filter is applied
            products = db.execute("""
                SELECT product_id, name, price, category_id
                FROM products
            """).fetchall()
        
        return jsonify([{'product_id': row[0], 'name': row[1], 'price': row[2], 'category_id': row[3]} for row in products])
    
    elif request.method == 'POST':
        data = request.json
        db.execute("""
            INSERT INTO products (product_id, name, price, category_id)
            VALUES (?, ?, ?, ?)
        """, (data['product_id'], data['name'], data['price'], data['category_id']))
        db.commit()
        return jsonify({'message': 'Product added successfully!'}), 201

@app.route('/rfid', methods=['POST'])
def assign_rfid():
    db = get_db()
    data = request.json
    rfid = data['rfid']
    sets = data['sets']
    db.execute("INSERT OR IGNORE INTO rfid (rfid_id) VALUES (?)", (rfid,))
    for set_name, products in sets.items():
        db.execute("INSERT INTO zestawy (zestaw_name, rfid_id) VALUES (?, ?)", (set_name, rfid))
        zestaw_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        for product_name, quantity in products.items():
            product = db.execute("SELECT product_id FROM products WHERE name = ?", (product_name,)).fetchone()
            if product:
                product_id = product[0]
                db.execute("INSERT INTO product_zestaw (product_id, zestaw_id, quantity) VALUES (?, ?, ?)",
                           (product_id, zestaw_id, quantity))
    db.commit()
    return jsonify({'message': 'RFID and sets assigned successfully!'}), 201

@app.route('/rfid/<rfid>/sets', methods=['GET'])
def get_sets_by_rfid(rfid):
    db = get_db()
    
    # Fetch all sets associated with the given RFID
    sets = db.execute("""
        SELECT zestawy.zestaw_name, product_zestaw.product_id, products.name AS product_name, 
               product_zestaw.quantity
        FROM zestawy
        JOIN product_zestaw ON zestawy.zestaw_id = product_zestaw.zestaw_id
        JOIN products ON product_zestaw.product_id = products.product_id
        WHERE zestawy.rfid_id = ?
    """, (rfid,)).fetchall()
    
    if not sets:
        return jsonify({'error': 'No sets found for the given RFID'}), 404
    
    response = {}
    for row in sets:
        set_name = row['zestaw_name']
        if set_name not in response:
            response[set_name] = []
        
        response[set_name].append({
            'product_id': row['product_id'],
            'product_name': row['product_name'],
            'quantity': row['quantity']
        })

    return jsonify(response), 200

if __name__ == '__main__':
    db = get_db()
    seed_database(db)
    app.run(debug=True, host="127.0.0.1")