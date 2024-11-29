"""
MIT License

Copyright (c) 2023 Shiva Vara Prasad Kandhagatla, Prateek Singamsetty, Laasya Choudary Nandamuri, Jayanth Ramanidharan
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from flask import Flask, request, render_template, make_response
from flask_restful import Resource, Api

# from Login.login import login_route
from Controller.application_controller import Application
from Controller.user_controller import User
from Controller.home import home_route


app = Flask(__name__)
api = Api(app)
app.config["SECRET_KEY"] = "Sample"  # os.environ.get('SECRET_KEY')
api.add_resource(User, "/user")
api.add_resource(Application, "/application")
app.register_blueprint(home_route, name="login", url_prefix="/login")
app.register_blueprint(home_route, name="home", url_prefix="/")
app.register_blueprint(home_route, name="auth", url_prefix="/auth")
app.register_blueprint(home_route, url_prefix="/")

app.app_context().push()


if __name__ == "__main__":
    app.run(debug=True)
