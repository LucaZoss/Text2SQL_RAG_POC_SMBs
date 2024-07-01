from flask import Flask
from ui.upload_interface import app
from config.settings import Config

app.config.from_object(Config)

if __name__ == '__main__':
    app.run(debug=True)