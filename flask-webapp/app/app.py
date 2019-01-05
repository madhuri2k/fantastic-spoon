from flask import Flask

app = Flask(__name__)

top_html = """
    <!doctype html>
    <html lang="en"> <head> <title> Flask App </title>
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <!-- Add Bootstrap CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
    </head>
    <body>
        <div class="container">
        <h1> Hello Docker</h1>
        <p> This is an example app to learn how to dockerize a python web app.
        </p><hr>
"""
bot_html = """
        <hr><p> <a href="/">[Home] </a> </p>
        </div>
    </body>
    </html>
"""

@app.route("/")
def index():
    page_content = """
        <p> Follow these links to explore the app:
        </p>
        <ul>
            <li> <a href="/about"> About this app </a> </li>
            <li> <a href="/greeter/User"> Basic Greeter </a> </li>
            <li> <a href="/factorial/3"> Factorial calculator </a> </li>
        </ul>
    """
    index_html = top_html + page_content + bot_html
    return index_html

@app.route('/about')
def about():
    about_html = top_html + """
        <h3> About this app</h3>
        <p> This is an example app to learn how to dockerize a python web app.
        </p>
    """ + bot_html
    return about_html

@app.route('/greeter/<username>')
def greeter(username):
    page_content  = "<h2>Hey there, %s</h2>" %username
    page_content += "<p>Change the last part of URL path to change greeting</p>"
    return top_html + page_content + bot_html

@app.route('/factorial/<int:num>')
def show_post(num):
    # Limit the value for num
    if num > 50:
        num = 50
    page_content = "<h2>Factorial calculator</h2>"
    page_content+= "<p> factorial(%d) = %d" % (num, factorial(num))
    page_content+= "<p>Change the last part of URL path to change input</p>"
    return top_html + page_content + bot_html

# A simple implementation of factorial
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
