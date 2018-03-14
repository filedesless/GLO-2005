from flask import Flask, render_template, request
#import pymysql, pymysql.cursors

app = Flask(__name__)
@app.route("/")

def main():
    return render_template('template_html/page_principale.html')



if __name__ == "__main__":
    app.run(debug=True, port=3000)