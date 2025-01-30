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
    rfid = data.get('rfid')
    sets = data.get('sets', {})

    if not rfid:
        return jsonify({'error': 'RFID is required'}), 400

    existing_rfid = db.execute("SELECT rfid_id FROM rfid WHERE rfid_id = ?", (rfid,)).fetchone()

    if not existing_rfid:
        db.execute("INSERT INTO rfid (rfid_id) VALUES (?)", (rfid,))
        db.commit()

    if not sets:
        return jsonify({'message': 'RFID added successfully!', 'rfid': rfid}), 201

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
    return jsonify({'message': 'RFID and sets assigned successfully!', 'rfid': rfid}), 201

@app.route('/rfid/<rfid>/sets', methods=['GET'])
def get_sets_by_rfid(rfid):
    db = get_db()
    
    # Fetch all sets associated with the given RFID
    sets = db.execute("""
        SELECT zestawy.zestaw_name, product_zestaw.product_id, products.name AS product_name,products.price AS product_price,
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
            'name': row['product_name'], # changed to name and price to match function "add_to_cart" function in controller.
            'price': row['product_price'],
            'quantity': row['quantity']
        })

    return jsonify(response), 200

@app.route('/delete_set',methods=["POST"])
def delete_set_by_name_and_rfid():
    db = get_db()
    data = request.json

    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    set_name = data['set_name']
    rfid = data['rfid']

    try:
        cursor = db.cursor()

        # Wyszukanie zestawu na podstawie nazwy i RFID
        cursor.execute("""
                SELECT z.zestaw_id FROM zestawy z
                JOIN rfid r ON z.rfid_id = r.rfid_id
                WHERE z.zestaw_name = ? AND r.rfid_id = ?
            """, (set_name, rfid))
        row = cursor.fetchone()

        if not row:
            return jsonify({'error': 'Set not found'}), 404

        zestaw_id = row['zestaw_id']

        # Rozpoczęcie transakcji
        db.execute('BEGIN')

        # Usunięcie powiązanych rekordów z tabeli product_zestaw
        cursor.execute("""
                DELETE FROM product_zestaw WHERE zestaw_id = ?
            """, (zestaw_id,))

        # Usunięcie samego zestawu z tabeli zestawy
        cursor.execute("""
                DELETE FROM zestawy WHERE zestaw_id = ?
            """, (zestaw_id,))

        # Zatwierdzenie zmian w bazie danych
        db.commit()

        return jsonify({'success': True, 'message': 'Set deleted successfully'}), 200



    except Exception as e:
        # Obsługa innych nieprzewidzianych błędów
        db.rollback()
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500

    finally:
        db.close()


@app.route('/rename_set',methods=["POST"])
def rename_set_by_name_and_rfid():
    db = get_db()
    data = request.json

    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    set_name_old = data['set_name_old']
    rfid = data['rfid']
    set_name_new = data["set_name_new"]

    if not set_name_old or not rfid or not set_name_new:
        return jsonify({'error': 'Missing set_name_old, rfid, or set_name_new in request'}), 400

    try:
        cursor = db.cursor()

        # Wyszukanie zestawu na podstawie starej nazwy i RFID
        cursor.execute("""
                SELECT zestaw_id FROM zestawy
                WHERE zestaw_name = ? AND rfid_id = ?
            """, (set_name_old, rfid))
        row = cursor.fetchone()

        if not row:
            return jsonify({'error': 'Set not found'}), 404

        zestaw_id = row['zestaw_id']

        # Aktualizacja nazwy zestawu
        cursor.execute("""
                UPDATE zestawy
                SET zestaw_name = ?
                WHERE zestaw_id = ?
            """, (set_name_new, zestaw_id))

        # Zatwierdzenie zmian w bazie danych
        db.commit()

        return jsonify({'success': True, 'message': 'Set renamed successfully'}), 200



    except Exception as e:
        # Obsługa innych nieprzewidzianych błędów
        db.rollback()
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500

    finally:
        db.close()

@app.route('/add_set', methods=["POST"])
def add_set_by_name_cart_and_rfid():
    db = get_db()
    data = request.json

    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    set_name = data['set_name']
    rfid = data['rfid']
    cart = data["cart"]
    print(cart)

    try:
        connection = get_db()
        cursor = connection.cursor()

        # Sprawdź, czy RFID istnieje w tabeli rfid, jeśli nie, dodaj
        cursor.execute("SELECT rfid_id FROM rfid WHERE rfid_id = ?", (rfid,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO rfid (rfid_id) VALUES (?)", (rfid,))

        # Dodaj nowy zestaw
        cursor.execute("""
                INSERT INTO zestawy (zestaw_name, rfid_id) VALUES (?, ?)
            """, (set_name, rfid))
        zestaw_id = cursor.lastrowid

        # Dodaj produkty do zestawu
        for product_name,quantity_price_dict in cart.items():

            quantity = quantity_price_dict['quantity']
            cursor.execute("SELECT product_id FROM products WHERE name = ?", (product_name,))
            row = cursor.fetchone()
            if row:
                product_id = row['product_id']
                cursor.execute("""
                        INSERT INTO product_zestaw (product_id, zestaw_id, quantity) VALUES (?, ?, ?)
                    """, (product_id, zestaw_id, quantity))
            else:
                # Jeśli produkt nie istnieje, pomiń lub zwróć błąd
                return jsonify({'error': f"Produkt '{product_name}' nie istnieje."}), 400

        connection.commit()
        connection.close()
        return jsonify({'success': True, 'message': f"Zestaw '{set_name}' został zapisany."}), 200

    except Exception as e:
        # Obsługa innych nieprzewidzianych błędów
        db.rollback()
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500

    finally:
        db.close()


@app.route('/overwrite_set', methods=["POST"])
def overwrite_set_by_name_cart_and_rfid():
    db = get_db()
    data = request.json

    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    set_name_old = data['set_name_old']
    set_name_new = data['set_name_new']
    rfid = data['rfid']
    cart = data["cart"]

    try:
        connection = get_db()
        cursor = connection.cursor()

        # Znajdź zestaw do nadpisania
        cursor.execute("""
                SELECT zestaw_id FROM zestawy WHERE zestaw_name = ? AND rfid_id = ?
            """, (set_name_old, rfid))
        row = cursor.fetchone()
        if not row:
            return jsonify({'error': 'Set not found'}), 404
        zestaw_id = row['zestaw_id']

        # Jeśli podano nową nazwę, zaktualizuj ją
        if set_name_new and set_name_new != set_name_old:
            cursor.execute("""
                    UPDATE zestawy SET zestaw_name = ? WHERE zestaw_id = ?
                """, (set_name_new, zestaw_id))


        # Usuń istniejące produkty w zestawie
        cursor.execute("""
                DELETE FROM product_zestaw WHERE zestaw_id = ?
            """, (zestaw_id,))

        # Dodaj nowe produkty do zestawu
        for product_name,quantity_price_dict in cart.items():

            quantity = quantity_price_dict['quantity']
            cursor.execute("SELECT product_id FROM products WHERE name = ?", (product_name,))
            row = cursor.fetchone()
            if row:
                product_id = row['product_id']
                cursor.execute("""
                        INSERT INTO product_zestaw (product_id, zestaw_id, quantity) VALUES (?, ?, ?)
                    """, (product_id, zestaw_id, quantity))
            else:
                return jsonify({'error': f"Produkt '{product_name}' nie istnieje."}), 400

        connection.commit()
        connection.close()
        return jsonify({'success': True, 'message': f"Zestaw '{set_name_old}' został nadpisany."}), 200


    except Exception as e:

        # Obsługa innych nieprzewidzianych błędów

        db.rollback()

        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500


    finally:

        db.close()






if __name__ == '__main__':
    db = get_db()
    seed_database(db)
    app.run(debug=True, host="127.0.0.1")