import os
import time
import random
import sqlite3
from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '0FvADmStUdA1wHQXYeZ89uLjUNSpXDCYyqKmEiKt4RYwj6vHxTc9w19y3gPzN'

UPLOAD_FOLDER = ''  # Set a default UPLOAD_FOLDER
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def upload_image(context):
    if context == 'user':
        UPLOAD_FOLDER = 'static/image/user'
    elif context == 'product':
        UPLOAD_FOLDER = 'static/image/products'
    elif context == 'customer':
        UPLOAD_FOLDER = 'static/image/customer'
    else:
        UPLOAD_FOLDER = 'static/image'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    return UPLOAD_FOLDER


# Connect to the SQLite database
conn = sqlite3.connect('database.db')

# Product
create_products_table_sql = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER,
    name TEXT,
    cost DECIMAL(10, 2),
    price DECIMAL(10, 2),
    image TEXT,
    status TEXT
);
"""

# Currency
create_currency_table_sql = """
CREATE TABLE IF NOT EXISTS currency (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    code TEXT,
    symbol TEXT,
    is_default TEXT,
    sell_out_price DECIMAL(10, 2)
);
"""

# Category
create_category_table_sql = """
CREATE TABLE IF NOT EXISTS category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    status TEXT
);
"""

# User
create_user_table_sql = """
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    image TEXT,
    status TEXT
);
"""

# Customer
create_customer_table_sql = """
CREATE TABLE IF NOT EXISTS customer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    image TEXT,
    status TEXT
);
"""

# Execute the SQL statements to create the tables
conn.execute(create_products_table_sql)
conn.execute(create_currency_table_sql)
conn.execute(create_category_table_sql)
conn.execute(create_user_table_sql)
conn.execute(create_customer_table_sql)

# Commit the changes and close the connection
conn.commit()
conn.close()


# Customer
@app.route('/wp-admin/customer')
def customerIndex():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customer;")
    rows = cursor.fetchall()
    conn.close()
    return render_template('admin/customer/index.html', modul='customer', rows=rows)


# End Customer


# Category
@app.route('/wp-admin/category')
def categoryIndex():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM category;")
    rows = cursor.fetchall()
    conn.close()
    return render_template('admin/category/index.html', modul='category', rows=rows)


# End Category


# Product
@app.route('/wp-admin/product')
def productIndex():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products;")
    rows = cursor.fetchall()

    cursor.execute("SELECT * FROM category;")
    categories = cursor.fetchall()
    conn.close()
    return render_template('admin/product/index.html', modul='product', rows=rows, categories=categories)


# End product


# currency
@app.route('/wp-admin/currency')
def currencyIndex():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM currency;")
    rows = cursor.fetchall()
    conn.close()
    return render_template('admin/currency/index.html', modul='currency', rows=rows)


# End currency


# user
@app.route('/wp-admin/user')
def userIndex():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user;")
    rows = cursor.fetchall()
    conn.close()
    return render_template('admin/user/index.html', modul='user', rows=rows)


# End user


@app.route('/wp-admin')
def adminIndex():
    return render_template('admin/dashboard.html', modul='dashboard')


# CRUD FUNCTION

# CREATE
@app.route('/wp-admin/insert-data/<string:table_name>', methods=['POST'])
def insertData(table_name):
    if table_name == 'products':
        return insertIntoProduct()
    elif table_name == 'currency':
        return insertIntoCurrency()
    elif table_name == 'user':
        return insertIntoUser()
    elif table_name == 'customer':
        return insertIntoCustomer()
    elif table_name == 'category':
        return insertIntoCategory()
    else:
        flash(f"Error: Table {table_name} not found.", "error")
        return redirect(request.referrer)


# DELETE
@app.route('/wp-admin/delete-record/<string:table_name>', methods=['POST'])
def removeRecord(table_name):
    try:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row  # Set row factory to access columns by name
        cursor = conn.cursor()
        recordID = request.form['recordID']
        cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (recordID,))
        existing_record = cursor.fetchall()
        if existing_record:
            for row in existing_record:
                if 'image' in row.keys():
                    file_path = os.path.join(f'static/image/{table_name}', row['image'])
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            flash(f"Error removing the file: {str(e)}", "error")
            cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (recordID,))
            conn.commit()
            flash("Success: Your data has been removed successfully.", "success")
        else:
            flash("Error: The record you tried to remove was not found.", "error")
    except Exception as e:
        conn.rollback()
        flash(f"Error: {str(e)}", "error")
    finally:
        conn.close()
    # Redirect back
    return redirect(request.referrer)


# Update
@app.route('/wp-admin/update-data/<string:table_name>', methods=['POST'])
def updateRecord(table_name):
    if table_name == 'products':
        return updateProduct()
    elif table_name == 'currency':
        return updateCurrency()
    elif table_name == 'user':
        return updateUser()
    elif table_name == 'customer':
        return updateCustomer()
    elif table_name == 'category':
        return updateCategory()
    else:
        flash(f"Error: Table {table_name} not found.", "error")
        return redirect(request.referrer)


# END CRUD FUNCTION


# Split Function for Insert operation
def insertIntoCategory():
    try:
        name = request.form['category_name']
        status = request.form['status']
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        insert_query = "INSERT INTO category (name, status) VALUES (?, ?)"
        cursor.execute(insert_query, (name, status))
        flash("Success: Your data has been saved successfully.", "success")
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        flash("Database error: " + str(e), "error")
    except Exception as e:
        conn.rollback()
        flash("Error: " + str(e), "error")
    finally:
        if conn is not None:
            conn.close()
    return redirect(url_for('categoryIndex'))


def insertIntoCustomer():
    try:
        conn = sqlite3.connect("database.db")
        name = request.form['name']
        status = request.form['status']
        image = request.files['customer_image']
        if not image:
            flash("Error: Please upload customer Image!", "error")
            return redirect(url_for('customerIndex'))
        if image.filename == '':
            flash("Error: Please upload customer Image!", "error")
            return redirect(url_for('customerIndex'))

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            unique_filename = generate_unique_filename(filename)
            file_path = os.path.join(upload_image('customer'), unique_filename)
            image.save(file_path)
            if filename != unique_filename:
                os.rename(file_path, os.path.join(upload_image('customer'), unique_filename))
        else:
            flash("Error: File not supported!", "error")
            return redirect(request.referrer)
        cursor = conn.cursor()
        insert_query = "INSERT INTO customer (name, image, status) VALUES (?, ?, ?)"
        cursor.execute(insert_query, (name, unique_filename, status))
        flash("Success: Your data has been saved successfully.", "success")
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        flash("Database error: " + str(e), "error")
    except Exception as e:
        flash("Error: " + str(e), "error")
    return redirect(url_for('customerIndex'))


def insertIntoUser():
    try:
        conn = sqlite3.connect("database.db")
        name = request.form['name']
        status = request.form['status']
        image = request.files['profileImage']
        if not image:
            flash("Error: Please upload user Image!", "error")
            return redirect(url_for('userIndex'))
        if image.filename == '':
            flash("Error: Please upload user Image!", "error")
            return redirect(url_for('userIndex'))

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            unique_filename = generate_unique_filename(filename)
            file_path = os.path.join(upload_image('user'), unique_filename)
            image.save(file_path)
            if filename != unique_filename:
                os.rename(file_path, os.path.join(upload_image('user'), unique_filename))
        else:
            flash("Error: File not supported!", "error")
            return redirect(request.referrer)
        cursor = conn.cursor()
        insert_query = "INSERT INTO user (name, image, status) VALUES (?, ?, ?)"
        cursor.execute(insert_query, (name, unique_filename, status))
        flash("Success: Your data has been saved successfully.", "success")
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        flash("Database error: " + str(e), "error")
    except Exception as e:
        flash("Error: " + str(e), "error")
    return redirect(url_for('userIndex'))


def insertIntoCurrency():
    conn = None
    try:
        conn = sqlite3.connect("database.db")
        name = request.form['name']
        code = request.form['code']
        symbol = request.form['symbol']
        is_default = request.form['is_default']
        sell_out_price = request.form['sell_out_price']
        cursor = conn.cursor()
        insert_query = "INSERT INTO currency (name, code, symbol, is_default, sell_out_price) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(insert_query, (name, code, symbol, is_default, sell_out_price))
        flash("Success: Your data has been saved successfully.", "success")
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        flash("Database error: " + str(e), "error")
    except Exception as e:
        conn.rollback()
        flash("Error: " + str(e), "error")
    finally:
        if conn is not None:
            conn.close()
    return redirect(url_for('currencyIndex'))


def insertIntoProduct():
    try:
        conn = sqlite3.connect("database.db")
        name = request.form['product_name']
        status = request.form['status']
        cost = request.form['product_cost']
        price = request.form['product_price']
        category_id = request.form['category_id']
        image = request.files['productImage']
        if not image:
            flash("Error: Please upload product Image!", "error")
            return redirect(url_for('productIndex'))
        if image.filename == '':
            flash("Error: Please upload product Image!", "error")
            return redirect(url_for('productIndex'))

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            unique_filename = generate_unique_filename(filename)
            file_path = os.path.join(upload_image('product'), unique_filename)
            image.save(file_path)
            if filename != unique_filename:
                os.rename(file_path, os.path.join(upload_image('product'), unique_filename))
        else:
            flash("Error: File not supported!", "error")
            return redirect(request.referrer)
        cursor = conn.cursor()
        insert_query = "INSERT INTO products (name, image, status, cost, price, category_id) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(insert_query, (name, unique_filename, status, cost, price, category_id))
        flash("Success: Your data has been saved successfully.", "success")
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        flash("Database error: " + str(e), "error")
    except Exception as e:
        flash("Error: " + str(e), "error")
    return redirect(url_for('productIndex'))


# End Split Function for Insert operation

# Split Function for Update operation
def updateProduct():
    try:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row  # Set row factory to access columns by name
        cursor = conn.cursor()
        product_id = request.form['edit_product_id']
        product_name = request.form['edit_product_name']
        cost = request.form['edit_product_cost']
        price = request.form['edit_product_price']
        category_id = request.form['edit_category_id']
        status = request.form['edit_status']
        image = request.files['edit_productImage']
        # Check if the product exists
        cursor.execute("SELECT id, image FROM products WHERE id = ?", (product_id,))
        existing_record = cursor.fetchall()
        if existing_record:
            if image:
                # Remove the old image file if it exists
                for row in existing_record:
                    if 'image' in row.keys():
                        file_path = os.path.join(f'static/image/products', row['image'])
                        if os.path.exists(file_path):
                            try:
                                os.remove(file_path)
                            except Exception as e:
                                flash(f"Error removing the file: {str(e)}", "error")
                # Save the new image
                filename = secure_filename(image.filename)
                unique_filename = generate_unique_filename(filename)
                file_path = os.path.join(upload_image('product'), unique_filename)
                image.save(file_path)

                # Update the product with the new image
                update_query = "UPDATE products SET name=?, category_id=?, cost=?, price=?, status=?, image=? WHERE id=?"
                cursor.execute(update_query,
                               (product_name, category_id, cost, price, status, unique_filename, product_id))
                conn.commit()
                flash("Success: Product updated with a new image.", "success")
            else:
                # Update the product without changing the image
                update_query = "UPDATE products SET name=?, category_id=?, cost=?, price=?, status=? WHERE id=?"
                cursor.execute(update_query, (product_name, category_id, cost, price, status, product_id))
                conn.commit()
                flash("Success: Product updated.", "success")
        else:
            flash("Error: Product not found.", "error")
            return redirect(request.referrer)
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
    finally:
        conn.close()
    return redirect(url_for('productIndex'))


def updateCategory():
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        category_id = request.form['edit_category_id']
        name = request.form['edit_category_name']
        status = request.form['edit_status']
        cursor.execute("SELECT id FROM category WHERE id = ?", (category_id,))
        existing_record = cursor.fetchone()
        if existing_record:
            update_query = "UPDATE category SET name=?, status=? WHERE id=?"
            cursor.execute(update_query, (name, status, category_id))
            conn.commit()
            flash("Success: Category updated!.", "success")
        else:
            flash("Error: Record not found!.", "error")
    except Exception as e:
        flash(f"Error: {str(e)}.", "error")
    finally:
        conn.close()
    return redirect(url_for('categoryIndex'))


def updateUser():
    try:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        user_id = request.form['edit_user_id']
        user_name = request.form['edit_name']
        status = request.form['edit_status']
        image = request.files['edit_profileImage']
        # Check if the product exists
        cursor.execute("SELECT id, image FROM user WHERE id = ?", (user_id,))
        existing_record = cursor.fetchall()
        if existing_record:
            if image:
                # Remove the old image file if it exists
                for row in existing_record:
                    if 'image' in row.keys():
                        file_path = os.path.join(f'static/image/user', row['image'])
                        if os.path.exists(file_path):
                            try:
                                os.remove(file_path)
                            except Exception as e:
                                flash(f"Error removing the file: {str(e)}", "error")
                # Save the new image
                filename = secure_filename(image.filename)
                unique_filename = generate_unique_filename(filename)
                file_path = os.path.join(upload_image('user'), unique_filename)
                image.save(file_path)

                # Update the product with the new image
                update_query = "UPDATE user SET name=?, status=?, image=? WHERE id=?"
                cursor.execute(update_query, (user_name, status, unique_filename, user_id))
                conn.commit()
                flash("Success: User updated with a new image.", "success")
            else:
                update_query = "UPDATE user SET name=?, status=? WHERE id=?"
                cursor.execute(update_query, (user_name, status, user_id))
                conn.commit()
                flash("Success: User updated.", "success")
        else:
            flash("Error: User not found.", "error")
            return redirect(request.referrer)
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
    finally:
        conn.close()
    return redirect(url_for('userIndex'))


def updateCustomer():
    try:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        customer_id = request.form['edit_customer_id']
        user_name = request.form['edit_name']
        status = request.form['edit_status']
        image = request.files['edit_profileImage']
        # Check if the product exists
        cursor.execute("SELECT id, image FROM customer WHERE id = ?", (customer_id,))
        existing_record = cursor.fetchall()
        if existing_record:
            if image:
                # Remove the old image file if it exists
                for row in existing_record:
                    if 'image' in row.keys():
                        file_path = os.path.join(f'static/image/customer', row['image'])
                        if os.path.exists(file_path):
                            try:
                                os.remove(file_path)
                            except Exception as e:
                                flash(f"Error removing the file: {str(e)}", "error")
                # Save the new image
                filename = secure_filename(image.filename)
                unique_filename = generate_unique_filename(filename)
                file_path = os.path.join(upload_image('customer'), unique_filename)
                image.save(file_path)

                # Update the product with the new image
                update_query = "UPDATE customer SET name=?, status=?, image=? WHERE id=?"
                cursor.execute(update_query, (user_name, status, unique_filename, customer_id))
                conn.commit()
                flash("Success: Customer updated with a new image.", "success")
            else:
                update_query = "UPDATE customer SET name=?, status=? WHERE id=?"
                cursor.execute(update_query, (user_name, status, customer_id))
                conn.commit()
                flash("Success: Customer updated.", "success")
        else:
            flash("Error: Customer not found.", "error")
            return redirect(request.referrer)
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
    finally:
        conn.close()
    return redirect(url_for('customerIndex'))


def updateCurrency():
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        currency_id = request.form['edit_currency_id']
        name = request.form['edit_name']
        code = request.form['edit_code']
        symbol = request.form['edit_symbol']
        is_default = request.form['edit_is_default']
        sell_out_price = request.form['edit_sell_out_price']
        cursor.execute("SELECT id FROM currency WHERE id = ?", (currency_id,))
        existing_record = cursor.fetchone()
        if existing_record:
            update_query = "UPDATE currency SET name=?, code=?, symbol=?, is_default=?, sell_out_price=? WHERE id=?"
            cursor.execute(update_query, (name, code, symbol, is_default, sell_out_price, currency_id))
            conn.commit()
            flash("Success: Currency updated!.", "success")
        else:
            flash("Error: Record not found!.", "error")
    except Exception as e:
        flash(f"Error: {str(e)}.", "error")
    finally:
        conn.close()
    return redirect(url_for('currencyIndex'))


# End Split Function for Update operation

# check file Ext
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# generate unique name
def generate_unique_filename(filename):
    timestamp = int(time.time() * 100)
    # Add a random component to ensure uniqueness
    random_suffix = random.randint(1, 10000)
    _, file_extension = os.path.splitext(filename)
    unique_filename = f"{timestamp}_{random_suffix}{file_extension}"
    return unique_filename


@app.route('/')
def hello_world():
    data = []
    name = ['Coca', 'Pessi', 'Fanta', 'Tiger', 'Angkor', 'Cambodia']
    for item in range(15):
        data.append({
            'name': random.choice(name),
            'price': random.randint(10, 20),
            'qty': random.randint(1, 10),
            'discount': 10
        },
        )
    return render_template('index.html', data=data)


@app.errorhandler(404)
def pageNotFound(e):
    return render_template('errorPage/pageNotFound.html')


@app.errorhandler(500)
def internalServerError(e):
    return render_template('errorPage/500Page.html')


if __name__ == '__main__':
    app.run()
