from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from flaskext.mysql import MySQL
import pymysql
import pdfkit
import os
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config.from_pyfile('config.py')

app.secret_key = 'ashish'

mysql = MySQL()

UPLOAD_FOLDER = 'static/uploads/'


app.config['UPLOAD_FOLDER'] = "static/files"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor(pymysql.cursors.DictCursor)

# ----------------------Pre Login Page--------------------------


@app.route('/')
def index():
    return render_template('index.html')

# -------------------------Login Page---------------------------


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    # Check if "email" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor.execute(
            'SELECT * FROM login WHERE email = %s AND password = %s', (email, password))
        # Fetch one record and return result
        account = cursor.fetchone()

        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['email'] = account['email']
            # Redirect to home page
            # return 'Logged in successfully!'
            return redirect(url_for('home'))
            
        else:
            # Account doesnt exist or email/password incorrect
            msg = 'Incorrect email/password!'
    return render_template('login.html', msg=msg)
# --####################################### Login End #########################

# --####################################### Forget Password ####################


@app.route('/forget_password1', methods=['GET', 'POST'])
def forget1():
    if request.method == 'POST' and 'email' in request.form:
        # Create variables for easy access
        email = request.form['email']
        # Check if account exists using MySQL
        cursor.execute(
            'SELECT * FROM login WHERE email = %s ', (email))
        # Fetch one record and return result
        account = cursor.fetchone()

        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['email'] = account['email']
            # Redirect to home page
            # return 'Logged in successfully!'
            return redirect(url_for('forget'))
        else:
            # Account doesnt exist or email/password incorrect
            msg = 'Email Not Found or You Entered a Wrong Email Id'
    return render_template('login.html', msg=msg)


@app.route('/forget', methods=['GET', 'POST'])
def forget2():
    msg = ''
    cursor.execute('SELECT * FROM login WHERE email=%s ', [session['email']])
    pro = cursor.fetchone()
    if request.method == 'POST':
        # email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if confirm_password != password:
            msg = "Password Doesn't Match "
            return render_template('personal.html', msg=msg, pro=pro)
        else:
            cursor.execute("UPDATE login SET password=%s,confirm_password=%s WHERE email='" +
                           session['email']+"' ", (password, confirm_password))
            conn.commit()
            msg = 'Password Change Successfully. Please Login to continue.'
            return redirect(url_for('login', msg=msg))
    return render_template('forget.html')


# --######################################### End Forget Password ####################


# --################################## Profile ###############################--


@app.route('/personal', methods=['GET', 'POST'])
def personal():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()

    return render_template('personal.html', pro=pro)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        mobile = request.form['mobile']
        cursor.execute("UPDATE login SET first_name=%s,last_name=%s,mobile=%s WHERE email='" +
                       session['email']+"' ", (first_name, last_name, mobile))
        conn.commit()
        return redirect(url_for('personal'))
    return render_template('personal.html')


@app.route('/upload_photo', methods=['GET', 'POST'])
def upload_photo():
    if request.method == 'POST':

        photo = request.files.getlist('photo[]')

        for files in photo:
            if files and allowed_file(files.filename):
                filename = secure_filename(files.filename)
                files.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cursor.execute(
                    "UPDATE login SET photo=%s WHERE email='"+session['email']+"' ", [filename])
                cursor.fetchall()
                conn.commit()
                return redirect(url_for('personal'))
    return render_template('personal.html')


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    msg = ''
    cursor.execute('SELECT * FROM login WHERE email=%s ', [session['email']])
    pro = cursor.fetchone()
    if request.method == 'POST':
        # email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if confirm_password != password:
            msg = "Password Doesn't Match "
            return render_template('personal.html', msg=msg, pro=pro)
        else:
            cursor.execute("UPDATE login SET password=%s,confirm_password=%s WHERE email='" +
                           session['email']+"' ", (password, confirm_password))
            conn.commit()
            msg = 'Password Change Successfully. Please Login to continue.'
            return render_template('login.html', msg=msg)
    return render_template('personal.html', pro=pro)


@app.route('/upload_sign', methods=['GET', 'POST'])
def upload_sign():
    if request.method == 'POST':

        sign = request.files.getlist('sign[]')

        for files in sign:
            if files and allowed_file(files.filename):
                filename = secure_filename(files.filename)
                files.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cursor.execute(
                    "UPDATE login SET sign=%s WHERE email='"+session['email']+"' ", [filename])
                cursor.fetchall()
                conn.commit()
                return redirect(url_for('personal'))
    return render_template('personal.html')
# ------------------------home-----------------------------


@app.route('/home', methods=['GET', 'POST'])
def home():
    cursor.execute('SELECT * FROM login WHERE email=%s ', [session['email']])
    pro = cursor.fetchone()

    cursor.execute("SELECT * FROM home")
    img = cursor.fetchall()

    if request.method == 'POST':

        photo = request.files.getlist('photo[]')

        for files in photo:
            if files and allowed_file(files.filename):
                filename = secure_filename(files.filename)
                files.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cursor.execute(
                    "UPDATE home SET photo=%s WHERE name='companyimage' ", [filename])
                cursor.fetchall()
                conn.commit()
        return redirect('home')
    return render_template('home.html', img=img, pro=pro)

# ----------------------Inventory--------------------------------


@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()

    cursor.execute('SELECT DISTINCT item_id,item_name,item_cata FROM inventory')
    table = cursor.fetchall()
    cursor.execute(
        "SELECT SUM(total_stock_price) as total_stock_value FROM inventory")
    stock = cursor.fetchone()

    msg = ''
    if request.method == 'POST':
        item_id = request.form['item_id']
        item_name = request.form['item_name']
        item_cata = request.form['item_cata']
        current_stock = request.form['current_stock']
        unit = request.form['unit']
        price = request.form['price']
        item_type = request.form['item_type']
        tax = request.form['tax']
        min_stock = request.form['min_stock']
        max_stock = request.form['max_stock']
        c_party_code = request.form['c_party_code']
        added_on = request.form['added_on']

        cursor.execute('INSERT INTO inventory(item_id,item_name,item_cata,current_stock,unit,price,item_type,tax,min_stock,max_stock,c_party_code,added_on) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ',
                       (item_id, item_name, item_cata, current_stock, unit, price, item_type, tax, min_stock, max_stock, c_party_code,added_on))
        if request.method == 'POST':
            cursor.execute(
                'UPDATE inventory SET `total_stock_price`=(current_stock*price) ')
        conn.commit()
        msg = 'Item Added Successfully'
        return redirect(url_for('inventory'))

    return render_template('inventory.html', msg=msg, table=table, pro=pro, stock=stock)

@app.route('/product_edit/<string:id>', methods=['GET', 'POST'])
def product_edit(id):
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()

    cursor.execute('SELECT * FROM inventory WHERE id=%s',(id))
    table = cursor.fetchall()
    cursor.execute(
        "SELECT SUM(total_stock_price) as total_stock_value FROM inventory")
    stock = cursor.fetchone()

    msg = ''
    if request.method == 'POST':
        item_id = request.form['item_id']
        item_name = request.form['item_name']
        item_cata = request.form['item_cata']
        current_stock = request.form['current_stock']
        unit = request.form['unit']
        price = request.form['price']
        item_type = request.form['item_type']
        tax = request.form['tax']
        min_stock = request.form['min_stock']
        max_stock = request.form['max_stock']
        c_party_code = request.form['c_party_code']
        added_on = request.form['added_on']
        dispatch_on =request.form['dispatch_on']

        cursor.execute('UPDATE  inventory SET item_id=%s,item_name=%s,item_cata=%s,current_stock=%s,unit=%s,price=%s,item_type=%s,tax=%s,min_stock=%s,max_stock=%s,c_party_code=%s,added_on=%s,dispatch_on=%s WHERE id = %s ',
                       (item_id, item_name, item_cata, current_stock, unit, price, item_type, tax, min_stock, max_stock, c_party_code,added_on,dispatch_on,id))
        if request.method == 'POST':
            cursor.execute(
                'UPDATE inventory SET `total_stock_price`=(current_stock*price) ')
        conn.commit()
        msg = 'Item Updated Successfully'
        return redirect(url_for('inventory'))

    return render_template('product_edit.html', msg=msg, table=table, pro=pro, stock=stock)

@app.route('/inventory_table_details/<string:item_id>')
def inventory_table_details(item_id):
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()
        cursor.execute('SELECT * FROM inventory WHERE item_id=%s',(item_id))
        details = cursor.fetchall()
    return render_template('inventory_table_details.html', pro=pro, details=details)

@app.route('/checkreport')
def checkreport():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()
        cursor.execute('SELECT * FROM check_list')
        check = cursor.fetchall()

        return render_template('checkreport.html', pro=pro,check=check)
@app.route('/check_upload', methods=['GET', 'POST'])
def check_upload():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()

    if request.method == 'POST':
        check_no = request.form['check_no']
        photo = request.files.getlist('photo[]')

        for files in photo:
            if files and allowed_file(files.filename):
                filename = secure_filename(files.filename)
                files.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cursor.execute(
                    "INSERT INTO check_list(check_no,photo) VALUES(%s,%s) ", [check_no,filename])
                cursor.fetchall()
                conn.commit()
        return redirect('inventory')
    return render_template('inventory.html', pro=pro, stock=stock)

@app.route('/update_stock', methods=['GET', 'POST'])
def update_stock():
    msg = ''
    if request.method == 'POST':
        item_id = request.form['item_id']
        current_stock = request.form['current_stock']
        price = request.form['price']

        cursor.execute("UPDATE inventory SET current_stock=%s,price=%s,`total_stock_price`=(current_stock*price) WHERE item_id=%s",
                       (current_stock, price, item_id))

        conn.commit()
        msg = 'Updated Successfully'

        return redirect(url_for('inventory'))
    return render_template('inventory.html', msg=msg)

#   ------------------------- Delete item -----------------


@app.route('/delete/<string:id>', methods=['GET', 'POST'])
def delete(id):
    cursor.execute("DELETE FROM inventory WHERE id={0}".format(id))
    conn.commit()
    return redirect(url_for('inventory'))
    #   -------------------------  End Delete item -----------------
# ------------------------------------- Inventory Excel ----------------------------------


@app.route('/inventory_excel', methods=['GET', 'POST'])
def inventory_excel():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()
        cursor.execute(
            "SELECT SUM(total_stock_price) as total_stock_value FROM inventory")
    stock = cursor.fetchone()

    cursor.execute("SHOW DATABASES")

    for x in cursor:
        print(x)
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_path = os.path.join(
                app.config['UPLOAD_FOLDER'], uploaded_file.filename)

            uploaded_file.save(file_path)
            parseCSV(file_path)
        return redirect('inventory')
    return render_template('inventory.html', pro=pro, stock=stock)


def parseCSV(filePath):
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()
        cursor.execute(
            "SELECT SUM(total_stock_price) as total_stock_value FROM inventory")
    stock = cursor.fetchone()

    col_names = ['item_id', 'item_name', 'item_cata', 'current_stock', 'unit',
                 'price', 'item_type', 'tax', 'min_stock', 'max_stock', 'c_party_code']

    csvData = pd.read_csv(filePath, names=col_names, skiprows=1, header=None)

    for i, row in csvData.iterrows():
        sql = "INSERT INTO inventory (item_id,item_name,item_cata,current_stock,unit,price,item_type,tax,min_stock,max_stock,c_party_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        value = (row['item_id'], row['item_name'], row['item_cata'], row['current_stock'], row['unit'],
                 row['price'], row['item_type'], row['tax'], row['min_stock'], row['max_stock'], row['c_party_code'])

        cursor.execute(sql, value)
        if request.method == 'POST':
            cursor.execute(
                'UPDATE inventory SET `total_stock_price`=(current_stock*price) ')
        conn.commit()
    return render_template('inventory.html', pro=pro, stock=stock)


# ---------------------------- Buyer & Suppliers --------------------------


@app.route('/buyer_supplier_edit/<string:id>', methods=['GET', 'POST'])
def buyer_supplier_edit(id):
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()
    cursor.execute("SELECT * FROM buyer WHERE id=%s ", (id))
    edit = cursor.fetchall()
    return render_template('buyer_supplier_edit.html', edit=edit, pro=pro)


@app.route('/buyer_supplier', methods=['GET', 'POST'])
def buyer_supplier():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()
    cursor.execute('SELECT * FROM buyer')
    buyer = cursor.fetchall()
    msg = ''
    if request.method == 'POST':
        type = request.form['type']
        c_name = request.form['c_name']
        gst_in = request.form['gst_in']
        c_email = request.form['c_email']
        mobile = request.form['mobile']
        address1 = request.form['address1']
        address2 = request.form['address2']
        pin = request.form['pin']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        tags = request.form['tags']
        date = request.form['date']
        name = request.form['name']
        email = request.form['email']

        cursor.execute("INSERT INTO buyer(type,c_name,gst_in,c_email,mobile,address1,address2,pin,city,state,country,tags,date,name,email) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ",
                       (type, c_name, gst_in, c_email, mobile, address1, address2, pin, city, state, country, tags, date, name, email))
        conn.commit()
        msg = 'Company Added Successfully'
        return redirect(url_for('buyer_supplier'))

    return render_template('buyer_supplier.html', buyer=buyer, msg=msg, pro=pro)


@app.route('/delete_buyer/<string:id>', methods=['GET', 'POST'])
def delete_buyer(id):
    msg = ''
    cursor.execute("DELETE FROM buyer WHERE id={0}".format(id))
    conn.commit()
    msg = 'Company Deleted Successfully'
    return redirect(url_for('buyer_supplier', msg=msg))


@app.route('/payment')
def payment():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()
    return render_template('payment.html', pro=pro)


@app.route('/tranzaction', methods=['GET', 'POST'])
def tranzaction():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()

    cursor.execute('SELECT * FROM documents')
    doc = cursor.fetchall()
    return render_template('tranzaction.html', doc=doc, pro=pro)


@app.route('/POrder', methods=['GET', 'POST'])
def POrder():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()

    if request.method == 'POST':
        buyer_name = request.form['buyer_name']
        buyer_address = request.form['buyer_address']
        buyer_email = request.form['buyer_email']
        buyer_phone = request.form['buyer_phone']
        buyer_gstin = request.form['buyer_gstin']
        buyer_state = request.form['buyer_state']
        buyer_country = request.form['buyer_country']

        del_name = request.form['del_name']
        del_address = request.form['del_address']
        del_pin = request.form['del_pin']
        del_city = request.form['del_city']
        del_state = request.form['del_state']
        del_country = request.form['del_country']

        sup_name = request.form['sup_name']
        sup_address = request.form['sup_address']
        sup_email = request.form['sup_email']
        sup_phone = request.form['sup_phone']
        sup_gstin = request.form['sup_gstin']
        sup_state = request.form['sup_state']
        sup_country = request.form['sup_country']

        ps_name = request.form['ps_name']
        ps_address = request.form['ps_address']
        ps_email = request.form['ps_email']
        ps_phone = request.form['ps_phone']
        ps_gstin = request.form['ps_gstin']
        ps_state = request.form['ps_state']
        ps_country = request.form['ps_country']
        pridoc_title = request.form['pridoc_title']
        pridoc_docno = request.form['pridoc_docno']
        pridoc_date = request.form['pridoc_date']
        pridoc_amendment = request.form['pridoc_amendment']
        pridoc_deliverydate = request.form['pridoc_deliverydate']
        pridoc_store = request.form['pridoc_store']

        item_id = request.form['item_id']
        item_desc = request.form['item_desc']
        hsn_code = request.form['hsn_code']
        quantity = request.form['quantity']
        unit = request.form['unit']
        price = request.form['price']
        tax = request.form['tax']

        cursor.execute('INSERT INTO documents(buyer_name,buyer_address,buyer_email,buyer_phone,buyer_gstin,buyer_state,buyer_country,del_name,del_address,del_pin,del_city,del_state,del_country,sup_name,sup_address,sup_email,sup_phone,sup_gstin,sup_state,sup_country,ps_name,ps_address,ps_email,ps_phone,ps_gstin,ps_state,ps_country,pridoc_title,pridoc_docno,pridoc_date,pridoc_amendment,pridoc_deliverydate,pridoc_store,item_id,item_desc,hsn_code,quantity,unit,price,tax) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                       (buyer_name, buyer_address, buyer_email, buyer_phone, buyer_gstin, buyer_state, buyer_country, del_name, del_address, del_pin, del_city, del_state, del_country, sup_name, sup_address, sup_email, sup_phone, sup_gstin, sup_state, sup_country, ps_name, ps_address, ps_email, ps_phone, ps_gstin, ps_state, ps_country, pridoc_title, pridoc_docno, pridoc_date, pridoc_amendment, pridoc_deliverydate, pridoc_store, item_id, item_desc, hsn_code, quantity, unit, price, tax))

        if request.method == 'POST':
            cursor.execute(
                'UPDATE documents SET `total_before_tax`=(quantity*price) ')
        if request.method == 'POST':
            cursor.execute(
                'UPDATE documents SET `total_after_tax`=(`total_before_tax` + `tax`/100*`total_before_tax`) ')
        conn.commit()
        return redirect(url_for('tranzaction'))

    return render_template('POrder.html', pro=pro)


@app.route('/view/<string:id>', methods=['GET', 'POST'])
def view(id):
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()

        cursor.execute("SELECT * FROM documents WHERE id=%s", (id))
        view = cursor.fetchall()

    if request.method == 'POST':
        buyer_name = request.form['buyer_name']
        buyer_address = request.form['buyer_address']
        buyer_email = request.form['buyer_name']
        buyer_phone = request.form['buyer_phone']
        buyer_gstin = request.form['buyer_gstin']
        buyer_state = request.form['buyer_state']
        buyer_country = request.form['buyer_country']

        del_name = request.form['del_name']
        del_address = request.form['del_address']
        del_pin = request.form['del_pin']
        del_city = request.form['del_city']
        del_state = request.form['del_state']
        del_country = request.form['del_country']

        sup_name = request.form['sup_name']
        sup_address = request.form['sup_address']
        sup_email = request.form['sup_email']
        sup_phone = request.form['sup_phone']
        sup_gstin = request.form['sup_gstin']
        sup_state = request.form['sup_state']
        sup_country = request.form['sup_country']

        ps_name = request.form['ps_name']
        ps_address = request.form['ps_address']
        ps_email = request.form['ps_email']
        ps_phone = request.form['ps_phone']
        ps_gstin = request.form['ps_gstin']
        ps_state = request.form['ps_state']
        ps_country = request.form['ps_country']
        pridoc_title = request.form['pridoc_title']
        pridoc_docno = request.form['pridoc_docno']
        pridoc_date = request.form['pridoc_date']
        pridoc_amendment = request.form['pridoc_amendment']
        pridoc_deliverydate = request.form['pridoc_deliverydate']
        pridoc_store = request.form['pridoc_store']

        item_id = request.form['item_id']
        item_desc = request.form['item_desc']
        hsn_code = request.form['hsn_code']
        quantity = request.form['quantity']
        unit = request.form['unit']
        price = request.form['price']
        tax = request.form['tax']

        cursor.execute('UPDATE documents SET buyer_name=%s,buyer_address=%s,buyer_email=%s,buyer_phone=%s,buyer_gstin=%s,buyer_state=%s,buyer_country=%s,del_name=%s,del_address=%s,del_pin=%s,del_city=%s,del_state=%s,del_country=%s,sup_name=%s,sup_address=%s,sup_email=%s,sup_phone=%s,sup_gstin=%s,sup_state=%s,sup_country=%s,ps_name=%s,ps_address=%s,ps_email=%s,ps_phone=%s,ps_gstin=%s,ps_state=%s,ps_country=%s,pridoc_title=%s,pridoc_docno=%s,pridoc_date=%s,pridoc_amendment=%s,pridoc_deliverydate=%s,pridoc_store=%s,item_id=%s,item_desc=%s,hsn_code=%s,quantity=%s,unit=%s,price=%s,tax=%s WHERE id=%s',
                       (buyer_name, buyer_address, buyer_email, buyer_phone, buyer_gstin, buyer_state, buyer_country, del_name, del_address, del_pin, del_city, del_state, del_country, sup_name, sup_address, sup_email, sup_phone, sup_gstin, sup_state, sup_country, ps_name, ps_address, ps_email, ps_phone, ps_gstin, ps_state, ps_country, pridoc_title, pridoc_docno, pridoc_date, pridoc_amendment, pridoc_deliverydate, pridoc_store, item_id, item_desc, hsn_code, quantity, unit, price, tax, id))

        if request.method == 'POST':
            cursor.execute(
                'UPDATE documents SET `total_before_tax`=(quantity*price) ')
        if request.method == 'POST':
            cursor.execute(
                'UPDATE documents SET `total_after_tax`=(`total_before_tax` + `tax`/100*`total_before_tax`) ')
        conn.commit()
        return redirect(url_for('tranzaction'))

    return render_template('view.html', pro=pro, view=view)


@app.route('/bill/<string:id>')
def bill(id):
    cursor.execute('SELECT * FROM login WHERE email=%s ', [session['email']])
    pro = cursor.fetchone()
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdfkit.from_url("http://google.com", "out.pdf", configuration=config)

    cursor.execute("SELECT * FROM documents WHERE id=%s", (id,))
    bill = cursor.fetchall()
    conn.commit()
    res = render_template('bill.html', bill=bill, pro=pro)
    responsestring = pdfkit.from_string(res, False)
    response = make_response(responsestring)

    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline;filename=invoice.pdf'
    return response


@app.route('/business_intelligence')
def business_intelligence():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()

        return render_template('business_intelligence.html', pro=pro)

# --################################ Employee ####################### --#


@app.route('/employee', methods=['GET', 'POST'])
def employee():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()

        cursor.execute("SELECT SUM(salary) as total_salary FROM employee")
        salary = cursor.fetchone()

        cursor.execute("SELECT * FROM employee")
        employee = cursor.fetchall()

    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        emergency_phone = request.form['emergency_phone']
        dob = request.form['dob']
        job_title = request.form['job_title']
        manager_name = request.form['manager_name']
        department = request.form['department']
        hired_date = request.form['hired_date']
        salary = request.form['salary']
        qualification = request.form['qualification']
        status = request.form['status']

        cursor.execute("INSERT INTO employee(name,address,phone,emergency_phone,dob,job_title,manager_name,department,hired_date,salary,qualification,status) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ",
                       (name, address, phone, emergency_phone, dob, job_title, manager_name, department, hired_date, salary, qualification, status))
        conn.commit()
        return redirect('employee')

    return render_template('employee.html', pro=pro, employee=employee, salary=salary)


@app.route('/employee_edit/<string:id>', methods=['GET', 'POST'])
def employee_edit(id):

    cursor.execute('SELECT * FROM login WHERE email=%s ',
                   [session['email']])
    pro = cursor.fetchone()
    cursor.execute("SELECT * FROM employee WHERE id=%s", (id))
    edit = cursor.fetchall()
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        emergency_phone = request.form['emergency_phone']
        dob = request.form['dob']
        job_title = request.form['job_title']
        manager_name = request.form['manager_name']
        department = request.form['department']
        hired_date = request.form['hired_date']
        salary = request.form['salary']
        qualification = request.form['qualification']
        status = request.form['status']

        cursor.execute("UPDATE employee SET name=%s,address=%s,phone=%s,emergency_phone=%s,dob=%s,job_title=%s,manager_name=%s,department=%s,hired_date=%s,salary=%s,qualification=%s,status=%s WHERE id=%s ",
                       (name, address, phone, emergency_phone, dob, job_title, manager_name, department, hired_date, salary, qualification, status, id))
        conn.commit()
        return redirect(url_for('employee'))

    return render_template('employee_edit.html', pro=pro, edit=edit)


@app.route('/employee_delete/<string:id>', methods=['GET', 'POST'])
def employee_delete(id):
    cursor.execute('DELETE FROM employee WHERE id={0}'.format(id))
    conn.commit()
    return redirect(url_for('employee'))





@app.route('/sales')
def sales():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()

        cursor.execute("SELECT * FROM sales")
        sale = cursor.fetchall()

        return render_template('sales.html', pro=pro, sale=sale)


@app.route('/All_document')
def All_document():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()

        cursor.execute("SELECT * FROM documents ")
        doc = cursor.fetchall()

        return render_template('All_document.html', pro=pro, doc=doc)


@app.route('/Nav_sidemodal', methods=['POST'])
def Nav_sidemodal():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()

    return render_template('Nav_sidemodal.html', pro=pro)


@app.route('/forget')
def forget():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()

        return render_template('forget.html', pro=pro)

# #######################################-----Bill Generated----########################################


@app.route('/add', methods=['POST'])
def add_product_to_cart():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()

        _current_stock = int(request.form['current_stock'])
        _item_id = request.form['item_id']
        if _current_stock and _item_id and request.method == 'POST':

            cursor.execute(
                "SELECT * FROM inventory WHERE item_id=%s", _item_id)
            row = cursor.fetchone()
            if float(row['current_stock']) >= float(_current_stock):
                itemArray = {row['item_id']: {'item_name': row['item_name'], 'item_id': row['item_id'],
                                              'current_stock': _current_stock, 'price': row['price'], 'total_price': _current_stock * row['price']}}
                all_total_price = 0
                all_total_quantity = 0
                session.modified = True
                if 'cart_item' in session:
                    if row['item_id'] in session['cart_item']:
                        for key, value in session['cart_item'].items():
                            if row['item_id'] == key:
                                old_quantity = session['cart_item'][key]['current_stock']
                                total_quantity = old_quantity + _current_stock
                                session['cart_item'][key]['current_stock'] = total_quantity
                                session['cart_item'][key]['total_price'] = total_quantity * row['price']
                    else:
                        session['cart_item'] = array_merge(
                            session['cart_item'], itemArray)
                    for key, value in session['cart_item'].items():
                        individual_quantity = int(
                            session['cart_item'][key]['current_stock'])
                        individual_price = float(
                            session['cart_item'][key]['total_price'])
                        all_total_quantity = all_total_quantity + individual_quantity
                        all_total_price = all_total_price + individual_price
                else:
                    session['cart_item'] = itemArray
                    all_total_quantity = all_total_quantity + _current_stock
                    all_total_price = all_total_price + \
                        _current_stock * row['price']
                session['all_total_quantity'] = all_total_quantity
                session['all_total_price'] = all_total_price
                return redirect(url_for('.products'))
            else:
                cursor.execute("SELECT * FROM inventory")
                rows = cursor.fetchall()
                return render_template('addtocart.html', products=rows, status='stock_error', pro=pro)


@app.route('/addtocart')
def products():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()
    cursor.execute("SELECT * FROM inventory")
    rows = cursor.fetchall()
    return render_template('addtocart.html', products=rows, pro=pro)


@app.route('/empty')
def empty_cart():
    try:
        session.pop('all_total_quantity')
        session.pop('all_total_price')
        session.pop('cart_item')
        return redirect(url_for('.displaycart'))
    except Exception as e:
        print(e)


@app.route('/delete1/<string:item_id>')
def delete_product(item_id):
    try:
        all_total_price = 0
        all_total_quantity = 0
        session.modified = True
        for item in session['cart_item'].items():
            if item[0] == item_id:
                session['cart_item'].pop(item[0], None)
                if 'cart_item' in session:
                    for key, value in session['cart_item'].items():
                        individual_quantity = int(
                            session['cart_item'][key]['current_stock'])
                        individual_price = float(
                            session['cart_item'][key]['total_price'])
                        all_total_quantity = all_total_quantity + individual_quantity
                        all_total_price = all_total_price + individual_price
                break
        if all_total_quantity == 0:
            session.pop('all_total_quantity')
            session.pop('all_total_price')
            session.pop('cart_item')
        else:
            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price
        return redirect(url_for('.displaycart'))
    except Exception as e:
        print(e)


def array_merge(first_array, second_array):
    if isinstance(first_array, list) and isinstance(second_array, list):
        return first_array + second_array
    elif isinstance(first_array, dict) and isinstance(second_array, dict):
        return dict(list(first_array.items()) + list(second_array.items()))
    elif isinstance(first_array, set) and isinstance(second_array, set):
        return first_array.union(second_array)
    return False


@app.route('/search', methods=['POST'])
def search():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()
    _search = (request.form['search'])

    cursor.execute("SELECT * FROM inventory WHERE item_name LIKE %s OR item_type LIKE %s",
                   ("%" + _search + "%", "%" + _search + "%",))
    rows = cursor.fetchall()
    if not rows:
        return redirect(url_for('.products'))
    else:
        return render_template('addtocart.html', products=rows, pro=pro)


@app.route('/transact', methods=['POST', 'GET'])
def transact():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()
    for key, value in session['cart_item'].items():
        item_id = session['cart_item'][key]['item_id']
        cursor.execute(
            "SELECT current_stock FROM inventory WHERE item_id=%s", item_id)
        row = cursor.fetchone()
        db_quantity = row['current_stock']
        session_quantity = session['cart_item'][key]['current_stock']
        new_quantity = int(db_quantity) - int(session_quantity)
        cursor.execute(
            'UPDATE inventory SET `total_stock_price`=(current_stock*price) ')
        cursor.execute("UPDATE inventory SET current_stock=%s WHERE item_id=%s",
                       (str(new_quantity), item_id))
        if request.method == 'POST':
            customer_name = request.form['customer_name']
            customer_mobile = request.form['customer_mobile']
            date = request.form['date']
            itemname = request.form['itemname']
            itemid = request.form['itemid']
            quantity = request.form['quantity']
            unitprice = request.form['unitprice']
            total_price = request.form['total_price']
            all_quantity = request.form['all_quantity']
            all_price = request.form['all_price']

            cursor.execute("INSERT INTO sales(customer_name,customer_mobile,date,itemname,itemid,quantity,unitprice,total_price,all_quantity,all_price) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ",
                           (customer_name, customer_mobile, date, itemname, itemid, quantity, unitprice, total_price, all_quantity, all_price))

            conn.commit()
            session.pop('all_total_quantity')
            session.pop('all_total_price')
            session.pop('cart_item')
            return redirect('sales')
    return render_template('sales.html', status='success', pro=pro)


@app.route('/bill_item/<string:id>')
def bill_item(id):
    cursor.execute('SELECT * FROM login WHERE email=%s ', [session['email']])
    pro = cursor.fetchone()
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdfkit.from_url("http://google.com", "out.pdf", configuration=config)

    cursor.execute("SELECT * FROM sales WHERE id=%s", (id,))
    sale_bill = cursor.fetchall()
    conn.commit()
    res = render_template('bill_item.html', sale_bill=sale_bill, pro=pro)
    responsestring = pdfkit.from_string(res, False)
    response = make_response(responsestring)

    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline;filename=invoice.pdf'
    return response


@app.route('/view_cart')
def displaycart():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM login WHERE email=%s ',
                       [session['email']])
        pro = cursor.fetchone()
    return render_template('cart.html', pro=pro)





# #####################################################################################################
if __name__ == '__main__':
    app.run(debug=True, port=5004)
