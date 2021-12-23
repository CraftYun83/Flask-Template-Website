from flask import Flask, request, render_template, redirect
from pymongo import MongoClient
from cryptography.fernet import Fernet

cluster = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000")
collection = cluster.get_database("FlaskTest").get_collection("credentials")
app = Flask(__name__)
key = Fernet.generate_key()
cipher_suite = Fernet(key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    try:
        username = cipher_suite.decrypt(request.cookies.get('un').encode("utf-8")).decode("utf-8")
        password = cipher_suite.decrypt(request.cookies.get('pw').encode("utf-8")).decode("utf-8")

        if collection.count_documents({"username": username, "password": password}) == 0:
            return "Did you really try forge cookies????"
        elif collection.count_documents({"username": username, "password": password}) == 1:
            return redirect("/home")
    except Exception:
        return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_request():
    username = request.form['username']
    password = request.form['password']
    if collection.count_documents({"username": username}) == 0:
        return "This account does not exist!"
    if collection.find_one({"username": username})["password"] == password:
        response = redirect("/home")
        response.set_cookie("li", bytes(True))
        response.set_cookie("hb", "aGFtYnVyZ2Vy".encode("utf-8"))
        response.set_cookie("ck", "Y29va2ll".encode("utf-8"))
        response.set_cookie("un", cipher_suite.encrypt(username.encode("utf-8")).decode("utf-8"))
        response.set_cookie("pw", cipher_suite.encrypt(password.encode("utf-8")).decode("utf-8"))
        return response
    else:
        return "Wrong credentials!"

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_request():
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    posts = collection.find({"username": username})
    if collection.count_documents({"username": username}) == 1:
        return "An account with this username already exists!"
    collection.insert_one({"email": email, "username": username, "password": password})
    response = redirect("/home")
    response.set_cookie("li", bytes(True))
    response.set_cookie("hb", "aGFtYnVyZ2Vy".encode("utf-8"))
    response.set_cookie("ck", "Y29va2ll".encode("utf-8"))
    response.set_cookie("un", cipher_suite.encrypt(username.encode("utf-8")))
    response.set_cookie("pw", cipher_suite.encrypt(password.encode("utf-8")))
    return response

@app.route('/home')
def home():
    try:
        username = cipher_suite.decrypt(request.cookies.get('un').encode("utf-8")).decode("utf-8")
        password = cipher_suite.decrypt(request.cookies.get('pw').encode("utf-8")).decode("utf-8")

        if collection.count_documents({"username": username, "password": password}) == 0:
            return "Did you really try forge cookies????"
        elif collection.count_documents({"username": username, "password": password}) == 1:
            return f"Hello! {username}, you are now signed in!"
    except Exception as e:
        return "You are NOT logged in!"

@app.route("/logout")
def logout():
    try:
        username = cipher_suite.decrypt(request.cookies.get('un').encode("utf-8")).decode("utf-8")
        password = cipher_suite.decrypt(request.cookies.get('pw').encode("utf-8")).decode("utf-8")

        if collection.count_documents({"username": username, "password": password}) == 0:
            return "Did you really try forge cookies????"
        elif collection.count_documents({"username": username, "password": password}) == 1:
            response = redirect("/")
            response.set_cookie("li", b"", expires=0)
            response.set_cookie("hb", b"", expires=0)
            response.set_cookie("ck", b"", expires=0)
            response.set_cookie("un", b"", expires=0)
            response.set_cookie("pw", b"", expires=0)
            return response
    except Exception:
        return "You aren't even signed in..."

@app.route("/delete")
def delete():
    try:
        username = cipher_suite.decrypt(request.cookies.get('un').encode("utf-8")).decode("utf-8")
        password = cipher_suite.decrypt(request.cookies.get('pw').encode("utf-8")).decode("utf-8")

        if collection.count_documents({"username": username, "password": password}) == 0:
            return "Did you really try forge cookies????"
        elif collection.count_documents({"username": username, "password": password}) == 1:
            collection.delete_one({"username": username, "password": password})
            response = redirect("/")
            response.set_cookie("li", b"", expires=0)
            response.set_cookie("hb", b"", expires=0)
            response.set_cookie("ck", b"", expires=0)
            response.set_cookie("un", b"", expires=0)
            response.set_cookie("pw", b"", expires=0)
            return response
    except Exception:
        return "You aren't even signed in..."

app.run(debug=True)