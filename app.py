from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Ganti dengan secret key yang lebih aman

# Konfigurasi koneksi MySQL
db_config = {
    'user': 'psrental',         # Ganti dengan nama pengguna MySQL Anda
    'password': 'Admin123',         # Ganti dengan password MySQL Anda
    'host': 'psrental.mysql.database.azure.com',    # Ganti dengan host server MySQL Anda
    'database': 'psrental',  # Ganti dengan nama database MySQL Anda
    'port': 3306
}

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    return mysql.connector.connect(**db_config)

rules = [
   # Aturan berdasarkan budget, tipe game, dan preferensi grafik
{
    "condition": lambda facts: facts["budget"] >= 15000000 and facts["game_type"] == "action" and facts["genre"] == "RPG" and facts["graphics"] == "high", 
    "recommendation": "PS5"
},
{
    "condition": lambda facts: facts["budget"] >= 12000000 and facts["game_type"] == "action" and facts["genre"] == "RPG" and facts["graphics"] == "high", 
    "recommendation": "PS4 Pro"
},
{
    "condition": lambda facts: facts["budget"] >= 10000000 and facts["game_type"] == "adventure" and facts["genre"] == "RPG" and facts["graphics"] == "medium", 
    "recommendation": "PS4 Slim"
},
{
    "condition": lambda facts: facts["budget"] < 10000000 and facts["game_type"] == "adventure" and facts["genre"] == "RPG" and facts["graphics"] == "low", 
    "recommendation": "PS4"
},
{
    "condition": lambda facts: facts["budget"] >= 12000000 and facts["game_type"] == "multiplayer" and facts["genre"] == "RPG" and facts["graphics"] == "high", 
    "recommendation": "PS5"
},
{
    "condition": lambda facts: facts["budget"] < 12000000 and facts["game_type"] == "multiplayer" and facts["genre"] == "RPG" and facts["graphics"] == "low", 
    "recommendation": "PS4"
},
{
    "condition": lambda facts: facts["budget"] >= 15000000 and facts["game_type"] == "action" and facts["genre"] == "Racing" and facts["graphics"] == "high", 
    "recommendation": "PS5"
},
{
    "condition": lambda facts: facts["budget"] >= 12000000 and facts["game_type"] == "action" and facts["genre"] == "Racing" and facts["graphics"] == "medium", 
    "recommendation": "PS4 Pro"
},
{
    "condition": lambda facts: facts["budget"] >= 10000000 and facts["game_type"] == "adventure" and facts["genre"] == "Racing" and facts["graphics"] == "low", 
    "recommendation": "PS4 Slim"
},
{
    "condition": lambda facts: facts["budget"] < 10000000 and facts["game_type"] == "adventure" and facts["genre"] == "Racing" and facts["graphics"] == "low", 
    "recommendation": "PS4"
},
{
    "condition": lambda facts: facts["budget"] >= 12000000 and facts["game_type"] == "multiplayer" and facts["genre"] == "Racing" and facts["graphics"] == "high", 
    "recommendation": "PS5"
},
{
    "condition": lambda facts: facts["budget"] < 12000000 and facts["game_type"] == "multiplayer" and facts["genre"] == "Racing" and facts["graphics"] == "medium", 
    "recommendation": "PS4"
},
{
    "condition": lambda facts: facts["budget"] >= 15000000 and facts["game_type"] == "action" and facts["genre"] == "Sports" and facts["graphics"] == "high", 
    "recommendation": "PS5"
},
{
    "condition": lambda facts: facts["budget"] >= 12000000 and facts["game_type"] == "action" and facts["genre"] == "Sports" and facts["graphics"] == "medium", 
    "recommendation": "PS4 Pro"
},
{
    "condition": lambda facts: facts["budget"] >= 10000000 and facts["game_type"] == "adventure" and facts["genre"] == "Sports" and facts["graphics"] == "low", 
    "recommendation": "PS4 Slim"
},
{
    "condition": lambda facts: facts["budget"] < 10000000 and facts["game_type"] == "adventure" and facts["genre"] == "Sports" and facts["graphics"] == "low", 
    "recommendation": "PS4"
},
{
    "condition": lambda facts: facts["budget"] >= 12000000 and facts["game_type"] == "multiplayer" and facts["genre"] == "Sports" and facts["graphics"] == "high", 
    "recommendation": "PS5"
},
{
    "condition": lambda facts: facts["budget"] < 12000000 and facts["game_type"] == "multiplayer" and facts["genre"] == "Sports" and facts["graphics"] == "medium", 
    "recommendation": "PS4"
},
# Aturan tambahan untuk PS2 dan PS3 dengan genre dan grafik rendah
{
    "condition": lambda facts: facts["budget"] < 5000000 and facts["game_type"] == "action" and facts["genre"] == "RPG" and facts["graphics"] == "low", 
    "recommendation": "PS3"
},
{
    "condition": lambda facts: facts["budget"] < 3000000 and facts["game_type"] == "action" and facts["genre"] == "RPG" and facts["graphics"] == "low", 
    "recommendation": "PS2"
},
{
    "condition": lambda facts: facts["budget"] < 5000000 and facts["game_type"] == "adventure" and facts["genre"] == "RPG" and facts["graphics"] == "low", 
    "recommendation": "PS3"
},
{
    "condition": lambda facts: facts["budget"] < 3000000 and facts["game_type"] == "adventure" and facts["genre"] == "RPG" and facts["graphics"] == "low", 
    "recommendation": "PS2"
},
{
    "condition": lambda facts: facts["budget"] < 5000000 and facts["game_type"] == "multiplayer" and facts["genre"] == "RPG" and facts["graphics"] == "low", 
    "recommendation": "PS3"
},
{
    "condition": lambda facts: facts["budget"] < 3000000 and facts["game_type"] == "multiplayer" and facts["genre"] == "RPG" and facts["graphics"] == "low", 
    "recommendation": "PS2"
},
{
    "condition": lambda facts: facts["budget"] < 5000000 and facts["game_type"] == "action" and facts["genre"] == "Racing" and facts["graphics"] == "low", 
    "recommendation": "PS3"
},
{
    "condition": lambda facts: facts["budget"] < 3000000 and facts["game_type"] == "action" and facts["genre"] == "Racing" and facts["graphics"] == "low", 
    "recommendation": "PS2"
},
{
    "condition": lambda facts: facts["budget"] < 5000000 and facts["game_type"] == "adventure" and facts["genre"] == "Racing" and facts["graphics"] == "low", 
    "recommendation": "PS3"
},
{
    "condition": lambda facts: facts["budget"] < 3000000 and facts["game_type"] == "adventure" and facts["genre"] == "Racing" and facts["graphics"] == "low", 
    "recommendation": "PS2"
},
{
    "condition": lambda facts: facts["budget"] < 5000000 and facts["game_type"] == "multiplayer" and facts["genre"] == "Racing" and facts["graphics"] == "low", 
    "recommendation": "PS3"
},
{
    "condition": lambda facts: facts["budget"] < 3000000 and facts["game_type"] == "multiplayer" and facts["genre"] == "Racing" and facts["graphics"] == "low", 
    "recommendation": "PS2"
},
{
    "condition": lambda facts: facts["budget"] < 5000000 and facts["game_type"] == "action" and facts["genre"] == "Sports" and facts["graphics"] == "low", 
    "recommendation": "PS3"
},
{
    "condition": lambda facts: facts["budget"] < 3000000 and facts["game_type"] == "action" and facts["genre"] == "Sports" and facts["graphics"] == "low", 
    "recommendation": "PS2"
},
{
    "condition": lambda facts: facts["budget"] < 5000000 and facts["game_type"] == "adventure" and facts["genre"] == "Sports" and facts["graphics"] == "low", 
    "recommendation": "PS3"
},
{
    "condition": lambda facts: facts["budget"] < 3000000 and facts["game_type"] == "adventure" and facts["genre"] == "Sports" and facts["graphics"] == "low", 
    "recommendation": "PS2"
},
{
    "condition": lambda facts: facts["budget"] < 5000000 and facts["game_type"] == "multiplayer" and facts["genre"] == "Sports" and facts["graphics"] == "low", 
    "recommendation": "PS3"
},
{
    "condition": lambda facts: facts["budget"] < 3000000 and facts["game_type"] == "multiplayer" and facts["genre"] == "Sports" and facts["graphics"] == "low", 
    "recommendation": "PS2"
}

]

def forward_chaining(facts):
    recommendations = []
    
    # Iterasi semua aturan
    for rule in rules:
        if rule["condition"](facts):
            recommendations.append(rule["recommendation"])
    
    return recommendations

@app.route("/index", methods=["GET", "POST"])
def index():
    recommendations = []  # Default empty list for recommendations
    budget = game_type = genre = graphics = ""
    
    if request.method == "POST":
        # Ambil input dari form, pastikan budget diubah menjadi integer
        try:
            budget = int(request.form["budget"])  # Handle the budget field safely
        except ValueError:
            budget = 0  # If the value is invalid, default to 0

        game_type = request.form["game_type"]
        genre = request.form["genre"]  # Ambil genre dari form
        graphics = request.form["graphics"]  # Ambil preferensi grafik
        
        # Buat dictionary untuk fakta
        facts = {
            "budget": budget,
            "game_type": game_type,
            "genre": genre,  # Menambahkan genre ke dalam fakta
            "graphics": graphics  # Menambahkan preferensi grafik ke dalam fakta
        }
        
        # Panggil forward chaining untuk mendapatkan rekomendasi
        recommendations = forward_chaining(facts)
    
    # Kirim rekomendasi ke template HTML
    return render_template("index.html", recommendations=recommendations, budget=budget, game_type=game_type, genre=genre, graphics=graphics)


@app.route('/')
def home():
    if 'user' in session:
        return render_template('home.html')
    else:
        return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']  # Bisa email atau username
        password = request.form['password']
        
        # Cek apakah yang dimasukkan adalah username atau email
        conn = get_db_connection()
        cursor = conn.cursor()

        # Cek apakah admin yang login (gunakan username untuk admin)
        cursor.execute(
            "SELECT * FROM admin WHERE username = %s AND password = %s",
            (username_or_email, password)
        )
        admin = cursor.fetchone()

        if admin:
            # Jika admin ditemukan, set session dengan peran admin
            session['user'] = {
                'id': admin[0],
                'username': admin[1],
                'role': 'admin'
            }
            cursor.close()
            conn.close()
            return redirect(url_for('admin_dashboard'))  # Redirect ke admin dashboard

        # Jika bukan admin, cek apakah user biasa dengan email
        cursor.execute(
            "SELECT * FROM users WHERE email = %s AND password = %s",
            (username_or_email, password)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            # Jika user ditemukan, set session dengan peran user
            session['user'] = {
                'id': user[0],
                'email': user[1],
                'role': 'user'
            }
            return redirect(url_for('home'))  # Redirect ke halaman utama user

        else:
            # Jika tidak ditemukan admin maupun user
            return render_template('login.html', error='Email/Username atau password salah.')

    return render_template('login.html')


@app.route('/logout')
def logout():
    # Hapus session dan arahkan ke halaman login
    session.pop('user', None)
    return redirect(url_for('home'))  # Arahkan ke halaman utama setelah logout

@app.route('/ps')
def ps():
    return render_template('ps.html')  # Halaman Detail Produk PS

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/registrasi', methods=['GET', 'POST'])
def registrasi():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        password = request.form['password']
        
        # Koneksi ke database dan masukkan pengguna baru
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, phone, address, password) VALUES (%s, %s, %s, %s, %s)",
            (name, email, phone, address, password)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('login'))  # Arahkan ke halaman login setelah registrasi berhasil
    return render_template('registrasi.html')

@app.route('/pemesanan', methods=['GET', 'POST'])
def pemesanan():
    if request.method == 'POST':
        ps_kode = request.form['ps']
        tv = request.form.get('tv', None)  # Mengambil nilai TV dari radio button
        if 'no_tv' in request.form:
            tv = None  # Set nilai TV menjadi None jika checkbox "Tanpa TV" dipilih

        delivery_date = datetime.strptime(request.form['delivery'], '%Y-%m-%d')
        return_date = datetime.strptime(request.form['return'], '%Y-%m-%d')

        # Pastikan return_date tidak lebih awal dari delivery_date
        if return_date < delivery_date:
            flash('Tanggal pengembalian tidak boleh lebih awal dari tanggal pengiriman.', 'error')
            return redirect(url_for('pemesanan'))

        payment_method = request.form['payment']

        # Hitung harga sewa berdasarkan tanggal
        total_days = (return_date - delivery_date).days
        conn = get_db_connection()
        cursor = conn.cursor()

        # Ambil data harga sewa PS dan kurangi stok PS
        cursor.execute("SELECT harga_sewa, stok FROM ps WHERE kode_ps = %s", (ps_kode,))
        ps_data = cursor.fetchone()
        ps_price = ps_data[0]
        ps_stok = ps_data[1]

        if ps_stok > 0:  # Pastikan stok cukup sebelum memproses pesanan
            cursor.execute(
                "UPDATE ps SET stok = %s WHERE kode_ps = %s",
                (ps_stok - 1, ps_kode)
            )

            # Jika menggunakan TV, tambahkan harga sewa TV dan kurangi stok TV
            if tv:
                cursor.execute("SELECT harga_sewa, stok FROM tv WHERE kode_tv = %s", (tv,))
                tv_data = cursor.fetchone()
                tv_price = tv_data[0]
                tv_stok = tv_data[1]

                if tv_stok > 0:  # Pastikan stok cukup sebelum memproses pesanan
                    cursor.execute(
                        "UPDATE tv SET stok = %s WHERE kode_tv = %s",
                        (tv_stok - 1, tv)
                    )
                    total_price = (ps_price + tv_price) * total_days
                else:
                    flash('TV yang dipilih tidak tersedia saat ini.', 'error')
                    return redirect(url_for('pemesanan'))
            else:
                total_price = ps_price * total_days

            # Ambil nama pengguna dari session
            user_id = session['user']['id']  # Mengakses 'id' dari session yang berbentuk dictionary
            cursor.execute("SELECT name FROM users WHERE id = %s", (user_id,))
            user_name = cursor.fetchone()[0]

            # Masukkan data pemesanan baru ke database
            cursor.execute(
                "INSERT INTO pemesanan (ps_kode, tv, delivery_date, return_date, payment_method, total_price, user_name) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (ps_kode, tv, delivery_date, return_date, payment_method, total_price, user_name)
            )
            conn.commit()
            cursor.close()
            conn.close()

            # Redirect ke halaman nota dengan membawa total harga
            return render_template('nota.html', ps_kode=ps_kode, tv=tv, delivery_date=delivery_date, return_date=return_date, payment_method=payment_method, total_price=total_price, user_name=user_name)
        else:
            flash('PlayStation yang dipilih tidak tersedia saat ini.', 'error')
            return redirect(url_for('pemesanan'))

    elif request.method == 'GET':
        # Ambil data PS dan TV dari database untuk ditampilkan di form
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT kode_ps, nama, stok, harga_sewa, foto FROM ps")
        ps_data = cursor.fetchall()
        
        cursor.execute("SELECT kode_tv, nama, stok, harga_sewa, gambar FROM tv")
        tv_data = cursor.fetchall()
        
        cursor.close()
        conn.close()

        return render_template('pemesanan.html', ps_data=ps_data, tv_data=tv_data)

    # Redirect jika tidak ada method yang cocok
    return redirect(url_for('home'))


# Route untuk unggah foto
@app.route('/upload_foto', methods=['POST'])
def upload_foto():
    if 'foto' not in request.files:
        return 'Tidak ada file yang diunggah', 400
    
    file = request.files['foto']
    if file.filename == '':
        return 'Tidak ada file yang dipilih', 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        kode_ps = request.form['kode_ps']
        
        # Update database dengan nama file foto
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE ps SET foto = %s WHERE kode_ps = %s", (filename, kode_ps))
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('admin_dashboard'))
    
    return 'File tidak diperbolehkan', 400

@app.route('/upload_gambar_tv', methods=['POST'])
def upload_gambar_tv():
    if 'gambar' not in request.files:
        return 'Tidak ada file yang diunggah', 400
    
    file = request.files['gambar']
    if file.filename == '':
        return 'Tidak ada file yang dipilih', 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        kode_tv = request.form['kode_tv']
        
        # Update database dengan nama file gambar
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE tv SET gambar = %s WHERE kode_tv = %s", (filename, kode_tv))
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('admin_dashboard'))
    
    return 'File tidak diperbolehkan', 400


# Admin routes
# @app.route('/admin/login', methods=['GET', 'POST'])
# def admin_login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         # Koneksi ke database dan cek apakah admin ada dengan username dan password yang diberikan
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute(
#             "SELECT * FROM admin WHERE username = %s AND password = %s",
#             (username, password)
#         )
#         admin = cursor.fetchone()
        
#         if admin:
#             # Admin ada, set session admin
#             session['user'] = {
#                 'id': admin[0],
#                 'username': admin[1],
#                 'role': 'admin'  # Set peran admin
#             }
#             cursor.close()
#             conn.close()
#             return redirect(url_for('admin_dashboard'))  # Arahkan ke dashboard admin
        
#         # Jika admin tidak ditemukan atau password salah, tangani sesuai kebutuhan
#         cursor.close()
#         conn.close()
#         return render_template('admin_login.html', error='Username atau password salah.')

#     return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user' in session:
        # Pastikan hanya admin yang dapat mengakses dashboard
        if session['user']['role'] == 'admin':
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Fetch user data
            cursor.execute("SELECT * FROM users")
            users_data = cursor.fetchall()
            
            # Ambil data pemesanan
            cursor.execute("SELECT * FROM pemesanan")
            pemesanan = cursor.fetchall()
            
            # Ambil data PS
            cursor.execute("SELECT * FROM ps")
            ps_data = cursor.fetchall()
            
            # Ambil data TV
            cursor.execute("SELECT * FROM tv")
            tv_data = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return render_template('admin_dashboard.html', pemesanan=pemesanan, ps_data=ps_data, tv_data=tv_data, users_data=users_data)
        else:
            return redirect(url_for('home'))  # Redirect jika bukan admin
    else:
        return redirect(url_for('admin_login'))  # Redirect jika belum login sebagai admin

@app.route('/admin/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        password = request.form['password']
        
        # Koneksi ke database dan masukkan pengguna baru
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, phone, address, password) VALUES (%s, %s, %s, %s, %s)",
            (name, email, phone, address, password)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('admin_dashboard'))  # Arahkan ke dashboard admin setelah berhasil tambah user
    
    return render_template('add_user.html')  # Tampilkan form tambah user

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        password = request.form['password']
        
        # Koneksi ke database dan update data pengguna
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET name = %s, email = %s, phone = %s, address = %s, password = %s WHERE id = %s",
            (name, email, phone, address, password, user_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('admin_dashboard'))  # Arahkan ke dashboard admin setelah berhasil edit user
    
    # Ambil data user dari database untuk ditampilkan di form edit
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user:
        return render_template('edit_user.html', user=user)  # Tampilkan form edit dengan data user
    else:
        return 'User tidak ditemukan', 404

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    # Hapus user dari database berdasarkan ID
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))  # Arahkan kembali ke dashboard admin setelah berhasil hapus user

@app.route('/admin/ps/add', methods=['GET', 'POST'])
def add_ps():
    if request.method == 'POST':
        kode_ps = request.form['kode_ps']
        nama = request.form['nama']
        stok = request.form['stok']
        harga_sewa = request.form['harga_sewa']
        
        # Koneksi ke database dan masukkan data PS baru
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ps (kode_ps, nama, stok, harga_sewa) VALUES (%s, %s, %s, %s)",
            (kode_ps, nama, stok, harga_sewa)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('admin_dashboard'))  # Arahkan ke dashboard admin setelah berhasil tambah PS
    
    return render_template('add_ps.html')  # Tampilkan form tambah PS
@app.route('/admin/ps/edit/<string:ps_kode>', methods=['GET', 'POST'])
def edit_ps(ps_kode):
    if request.method == 'POST':
        kode_ps = request.form['kode_ps']
        nama = request.form['nama']
        stok = request.form['stok']
        harga_sewa = request.form['harga_sewa']
        
        # Koneksi ke database dan update data PS
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE ps SET kode_ps = %s, nama = %s, stok = %s, harga_sewa = %s WHERE kode_ps = %s",
            (kode_ps, nama, stok, harga_sewa, ps_kode)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('admin_dashboard'))  # Arahkan ke dashboard admin setelah berhasil edit PS
    
    # Ambil data PS dari database untuk ditampilkan di form edit
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ps WHERE kode_ps = %s", (ps_kode,))
    ps = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if ps:
        return render_template('edit_ps.html', ps=ps)  # Tampilkan form edit dengan data PS
    else:
        return 'PS tidak ditemukan', 404

@app.route('/admin/ps/delete/<string:ps_kode>', methods=['POST'])
def delete_ps(ps_kode):
    # Hapus PS dari database berdasarkan kode_ps
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ps WHERE kode_ps = %s", (ps_kode,))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('admin_dashboard'))  # Redirect kembali ke dashboard admin

@app.route('/admin/tv/add', methods=['GET', 'POST'])
def add_tv():
    if request.method == 'POST':
        kode_tv = request.form['kode_tv']
        nama = request.form['nama']
        stok = request.form['stok']
        harga_sewa = request.form['harga_sewa']
        
        # Koneksi ke database dan masukkan data TV baru
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tv (kode_tv, nama, stok, harga_sewa) VALUES (%s, %s, %s, %s)",
            (kode_tv, nama, stok, harga_sewa)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('admin_dashboard'))  # Arahkan ke dashboard admin setelah berhasil tambah TV
    
    return render_template('add_tv.html')  # Tampilkan form tambah TV

@app.route('/admin/tv/edit/<string:tv_kode>', methods=['GET', 'POST'])
def edit_tv(tv_kode):
    if request.method == 'POST':
        nama = request.form['nama']
        stok = request.form['stok']
        harga_sewa = request.form['harga_sewa']
        
        # Koneksi ke database dan update data TV
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tv SET nama = %s, stok = %s, harga_sewa = %s WHERE kode_tv = %s",
            (nama, stok, harga_sewa, tv_kode)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('admin_dashboard'))  # Arahkan ke dashboard admin setelah berhasil edit TV
    
    # Ambil data TV dari database untuk ditampilkan di form edit
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tv WHERE kode_tv = %s", (tv_kode,))
    tv = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if tv:
        return render_template('edit_tv.html', tv=tv)  # Tampilkan form edit dengan data TV
    else:
        return 'TV tidak ditemukan', 404


@app.route('/admin/tv/delete/<string:tv_kode>', methods=['POST'])
def delete_tv(tv_kode):
    # Hapus TV dari database berdasarkan kode_tv
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tv WHERE kode_tv = %s", (tv_kode,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/pemesanan/edit/<int:pemesanan_id>', methods=['GET', 'POST'])
def edit_pemesanan(pemesanan_id):
    if request.method == 'POST':
        ps_kode = request.form['ps_kode']
        tv = request.form.get('tv', None)
        if 'no_tv' in request.form:
            tv = None
        
        delivery_date = datetime.strptime(request.form['delivery_date'], '%Y-%m-%d')
        return_date = datetime.strptime(request.form['return_date'], '%Y-%m-%d')
        payment_method = request.form['payment_method']
        total_price = request.form['total_price']
        
        # Update data pemesanan di database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE pemesanan SET ps_kode = %s, tv = %s, delivery_date = %s, return_date = %s, payment_method = %s, total_price = %s WHERE id = %s",
            (ps_kode, tv, delivery_date, return_date, payment_method, total_price, pemesanan_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('admin_dashboard'))  # Arahkan ke dashboard admin setelah berhasil edit pemesanan
    
    # Ambil data pemesanan dari database untuk ditampilkan di form edit
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pemesanan WHERE id = %s", (pemesanan_id,))
    pemesanan = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if pemesanan:
        return render_template('edit_pemesanan.html', pemesanan=pemesanan)  # Tampilkan form edit dengan data pemesanan
    else:
        return 'Pemesanan tidak ditemukan', 404

@app.route('/admin/pemesanan/delete/<int:pemesanan_id>', methods=['POST'])
def delete_pemesanan(pemesanan_id):
    # Hapus pemesanan dari database berdasarkan ID
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pemesanan WHERE id = %s", (pemesanan_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))  # Arahkan kembali ke dashboard admin setelah berhasil hapus pemesanan


if __name__ == '__main__':
    app.run(debug=True)
