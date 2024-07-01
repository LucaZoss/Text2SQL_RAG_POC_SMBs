from flask import Flask, request, render_template, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import os
from future_enhancements.loaders import DataLoader
from rag_system.llama_index_integration import LlamaIndexIntegration  # type: ignore
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin  # type: ignore
from config.settings import verify_id_token

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQL_CONNECTIONS'] = {}


class User(UserMixin):
    def __init__(self, id):
        self.id = id


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.request_loader
def load_user_from_request(request):
    id_token = request.headers.get('Authorization')
    if id_token:
        user_info = verify_id_token(id_token)
        if user_info:
            user = User(user_info['uid'])
            return user
    return None


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files and 'sql_connection_string' not in request.form:
        return 'No file part or SQL connection string provided'

    file = request.files.get('file')
    sql_connection_string = request.form.get('sql_connection_string')
    # Assuming client_id is provided to distinguish clients
    client_id = request.form.get('client_id')

    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        data = None

        if filename.endswith('.csv'):
            data = DataLoader.load_csv(file_path)
        elif filename.endswith('.json'):
            data = DataLoader.load_json(file_path)
        elif filename.endswith('.pdf'):
            data = DataLoader.load_pdf(file_path)
        elif filename.endswith('.docx'):
            data = DataLoader.load_word(file_path)
        elif filename.endswith(('.png', '.jpg', '.jpeg')):
            data = DataLoader.load_image(file_path)

        if data:
            index = LlamaIndexIntegration()
            index.add_data(data)
            return 'File uploaded and data indexed successfully'
        else:
            return 'Unsupported file type'

    elif sql_connection_string and client_id:
        app.config['SQL_CONNECTIONS'][client_id] = sql_connection_string
        return 'SQL connection string stored successfully'

    return 'No valid data provided'


@app.route('/query', methods=['GET', 'POST'])
@login_required
def query_index():
    if request.method == 'POST':
        query_text = request.form['query']
        client_id = request.form['client_id']
        index = LlamaIndexIntegration()
        response = index.query(query_text, client_id)
        return render_template('query.html', query=query_text, response=response)
    return render_template('query.html')


if __name__ == '__main__':
    app.run(debug=True)
