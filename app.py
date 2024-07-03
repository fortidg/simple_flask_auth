from utils import auth_required                                                                                                          
from flask import Flask
from flask import request
from flask import render_template
from flask import make_response
from flask import jsonify
import subprocess


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template("home.html")

@app.route('/hello')
def hello():
    return "Hello, World!"


@app.route('/user')
def get_user():
    name = request.args.get('name')
    return "Requested for name = %s" % name

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    return "Login successful for %s:%s" % (username, password)


@app.route('/save', methods=['POST'])
def save_user():
    user_data = request.json
    return 'Saving user with id = %d' % (user_data.get('id'))


@app.route('/secret')
@auth_required
def secret_view():
    return render_template("secret.html")

@app.route('/feedback', methods=['GET', 'POST'])
@auth_required
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        feedback = request.form['feedback']
        with open('templates/view_feedback.html', 'a') as f:
            f.write ("<html>")
            f.write ("<body>")
            f.write ("<h3>" f'{name}' "</h3>")
            f.write ("<p>" f'{feedback}' "</p>")
            f.write ("</body>")
            f.write ("</html>" '\n')
            f.close()
        response = make_response(render_template('thanks.html'))
        response.set_cookie('name', name)
        return response
    else:
        return render_template('feedback.html')
    
@app.route('/view_feedback')
def view_feedback():
    return render_template("view_feedback.html")

# Add API endpoints
@app.route('/api/v1/systeminfo', methods=['GET'])
def get_command():
    if 'cmd' not in request.args:
        return jsonify({"systeminfo": subprocess.check_output('uname -a', shell=True).decode(),"message": "Or use ?cmd=<command> to run any command."}), 200
    else:
        cmd = request.args.get('cmd')
        result = subprocess.check_output(cmd, shell=True)
        return jsonify({"output": result.decode()}), 200

@app.route('/api/v1/calculate', methods=['POST'])
def calculate():
    data = request.json
    if 'num1' not in data or 'num2' not in data:
        return jsonify({"message": "ERROR: Missing parameter - Please provide num1 and num2 in the request body as json."}), 400
    if 'operation' not in data:
        return jsonify(
            {"message": "ERROR: Missing parameter - Please provide operation in the request body as json."}), 400
    if data['operation'] not in ['add', 'subtract', 'multiply', 'divide']:
        return jsonify(
            {"message": "ERROR: Missing parameter - Invalid operation. Please provide add, subtract, multiply or divide."}), 400
    num1 = data['num1']
    num2 = data['num2']
    if data['operation'] == 'add':
        return jsonify({"result": str(num1 + num2)}), 200
    elif data['operation'] == 'subtract':
        return jsonify({"result": str(num1 - num2)}), 200
    elif data['operation'] == 'multiply':
        return jsonify({"result": str(num1 * num2)}), 200
    elif data['operation'] == 'divide':
        if num2 == 0:
            return jsonify({"message": "ERROR: Division by zero."}), 500
        return jsonify({"result": str(num1 / num2)}), 200

    return str(num1 + num2)

@app.route('/api/v1/protected', methods=['POST'])
def protected():
    if 'X-API-KEY' in request.headers and request.headers['X-API-KEY'] != 'VGhpcyBpcyBhIFNzZWNyZXQgdG9rZW4gd2hpY2ggc2hvdWxkIGJlIGhhbmRsZWQgdmVyeSBjYXJlZnVsbHkh':
        return jsonify({"message": "ERROR: Unauthorized - This is a protected resource. Specify the secret token in the header to access it."}), 403
    elif request.headers.get('X-API-KEY') != 'VGhpcyBpcyBhIFNzZWNyZXQgdG9rZW4gd2hpY2ggc2hvdWxkIGJlIGhhbmRsZWQgdmVyeSBjYXJlZnVsbHkh':
        return jsonify({"message": "ERROR: Unauthorized -  Please provide the secret token in the header."}), 403
    elif request.headers['X-API-KEY'] == 'VGhpcyBpcyBhIFNzZWNyZXQgdG9rZW4gd2hpY2ggc2hvdWxkIGJlIGhhbmRsZWQgdmVyeSBjYXJlZnVsbHkh':
        return jsonify({"message": "OK: Authorized"}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
