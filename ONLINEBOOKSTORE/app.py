from flask import Flask, request, render_template, redirect
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Panda123",
    database="books"
)
cursor = db.cursor()

@app.route('/')
def index():
    # Fetch recent orders
    cursor.execute("""
        SELECT o.OrderID, CONCAT(c.FirstName, ' ', c.LastName) as CustomerName, o.OrderDate, o.TotalPrice
        FROM orders o
        JOIN customers c ON o.CustomerID = c.CustomerID
        ORDER BY o.OrderDate DESC
        LIMIT 5
    """)
    orders = cursor.fetchall()
    
    # Fetch recent customers
    cursor.execute("""
        SELECT CustomerID, FirstName, LastName, Email
        FROM customers
        ORDER BY RegistrationDate DESC
        LIMIT 5
    """)
    customers = cursor.fetchall()

    return render_template('index.html', orders=orders, customers=customers)

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['PhoneNumber']
        address = request.form['address']
        registration_date = datetime.today().strftime('%Y-%m-%d')  # auto-fill today

        cursor.execute("""
            INSERT INTO customers (FirstName, LastName, Email, PhoneNumber, Address, RegistrationDate)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (first_name, last_name, email, phone_number, address, registration_date))

        db.commit()
        return redirect('/customers')
    return render_template('add_customer.html')

@app.route('/customers')
def customers():
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    return render_template('customer_list.html', customers=customers)

@app.route('/books')
def books():
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    return render_template('books_list.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre_id = request.form['genre_id']
        supplier_id = request.form['supplier_id']
        price = request.form['price']
        stock_quantity = request.form['stock_quantity']

        cursor.execute("""
            INSERT INTO books (Title, Author, GenreID, SupplierID, Price, StockQuantity)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, author, genre_id, supplier_id, price, stock_quantity))
        db.commit()
        return redirect('/books')

    # Get suppliers list for dropdown
    cursor.execute("SELECT SupplierID, Name FROM suppliers")
    suppliers = cursor.fetchall()
    
    # Get genres list for dropdown
    cursor.execute("SELECT GenreID, GenreName FROM genres")
    genres = cursor.fetchall()
    
    return render_template('add_book.html', suppliers=suppliers, genres=genres)

# --- Add Order ---
@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    if request.method == 'POST':
        customer_id = request.form['CustomerID']
        order_date = datetime.today().strftime('%Y-%m-%d')
        total_price = request.form['TotalPrice']
        payment_status = request.form['PaymentStatus']
        order_status = request.form['OrderStatus']

        cursor.execute("""
            INSERT INTO orders (CustomerID, OrderDate, TotalPrice, PaymentStatus, OrderStatus)
            VALUES (%s, %s, %s, %s, %s)
        """, (customer_id, order_date, total_price, payment_status, order_status))
        db.commit()
        return redirect('/orders')
        
    # Get customers for dropdown
    cursor.execute("SELECT CustomerID, CONCAT(FirstName, ' ', LastName) as Name FROM customers")
    customers = cursor.fetchall()
    
    return render_template('add_order.html', customers=customers)

@app.route('/orders')
def orders():
    cursor.execute("""
        SELECT o.*, CONCAT(c.FirstName, ' ', c.LastName) as CustomerName 
        FROM orders o
        JOIN customers c ON o.CustomerID = c.CustomerID
    """)
    orders = cursor.fetchall()
    return render_template('orders_list.html', orders=orders)

# --- Add Order Details ---
@app.route('/add_order_detail', methods=['GET', 'POST'])
def add_order_detail():
    if request.method == 'POST':
        order_id = request.form['OrderID']
        book_id = request.form['BookID']
        quantity = request.form['Quantity']

        # Check if OrderDetailID is auto-increment in your DB
        # If not, you'll need to include it in the insert
        cursor.execute("""
            INSERT INTO orderdetails (OrderID, BookID, Quantity)
            VALUES (%s, %s, %s)
        """, (order_id, book_id, quantity))
        db.commit()
        return redirect('/order_details')
        
    # Get orders for dropdown
    cursor.execute("SELECT OrderID FROM orders")
    orders = cursor.fetchall()
    
    # Get books for dropdown
    cursor.execute("SELECT BookID, Title FROM books")
    books = cursor.fetchall()
    
    return render_template('add_order_detail.html', orders=orders, books=books)

@app.route('/order_details')
def order_details():
    cursor.execute("""
        SELECT od.*, o.OrderDate, b.Title as BookTitle 
        FROM orderdetails od
        JOIN orders o ON od.OrderID = o.OrderID
        JOIN books b ON od.BookID = b.BookID
    """)
    details = cursor.fetchall()
    return render_template('order_details_list.html', details=details)

# --- Add Supplier ---
@app.route('/add_supplier', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        name = request.form['Name']
        phone_number = request.form['PhoneNumber']
        address = request.form['Address']
        order_date = datetime.today().strftime('%Y-%m-%d')

        cursor.execute("""
            INSERT INTO suppliers (Name, PhoneNumber, Address, OrderDate)
            VALUES (%s, %s, %s, %s)
        """, (name, phone_number, address, order_date))
        db.commit()
        return redirect('/suppliers')
    return render_template('add_supplier.html')

@app.route('/suppliers')
def suppliers():
    cursor.execute("SELECT * FROM suppliers")
    suppliers = cursor.fetchall()
    return render_template('suppliers_list.html', suppliers=suppliers)

# --- Edit and Delete Routes ---

# Edit Customer
@app.route('/edit_customer/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['PhoneNumber']
        address = request.form['address']

        cursor.execute("""
            UPDATE customers SET FirstName=%s, LastName=%s, Email=%s, PhoneNumber=%s, Address=%s
            WHERE CustomerID=%s
        """, (first_name, last_name, email, phone_number, address, customer_id))
        db.commit()
        return redirect('/customers')
        
    cursor.execute("SELECT * FROM customers WHERE CustomerID=%s", (customer_id,))
    customer = cursor.fetchone()
    return render_template('edit_customer.html', customer=customer)

# Delete Customer
@app.route('/delete_customer/<int:customer_id>')
def delete_customer(customer_id):
    cursor.execute("DELETE FROM customers WHERE CustomerID=%s", (customer_id,))
    db.commit()
    return redirect('/customers')

# Edit Book
@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre_id = request.form['genre_id']
        supplier_id = request.form['supplier_id']
        price = request.form['price']
        stock_quantity = request.form['stock_quantity']

        cursor.execute("""
            UPDATE books SET Title=%s, Author=%s, GenreID=%s, SupplierID=%s, Price=%s, StockQuantity=%s
            WHERE BookID=%s
        """, (title, author, genre_id, supplier_id, price, stock_quantity, book_id))
        db.commit()
        return redirect('/books')
        
    cursor.execute("SELECT * FROM books WHERE BookID=%s", (book_id,))
    book = cursor.fetchone()
    
    cursor.execute("SELECT SupplierID, Name FROM suppliers")
    suppliers = cursor.fetchall()
    
    cursor.execute("SELECT GenreID, GenreName FROM genres")
    genres = cursor.fetchall()
    
    return render_template('edit_book.html', book=book, suppliers=suppliers, genres=genres)

# Delete Book
@app.route('/delete_book/<int:book_id>')
def delete_book(book_id):
    cursor.execute("DELETE FROM books WHERE BookID=%s", (book_id,))
    db.commit()
    return redirect('/books')

if __name__ == '__main__':
    app.run(debug=True)
