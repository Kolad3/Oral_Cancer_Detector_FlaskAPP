from flask import Flask
from pkg.config import Config 



app = Flask(__name__)
app.config.from_object(Config)

from pkg import routes