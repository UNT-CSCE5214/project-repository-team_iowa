from flask import Flask, redirect, url_for, request
app = Flask(__name__)
 
 
@app.route('/success/<text>')
def success(text):
    return 'Your Review: %s' % text
 
 
@app.route('/home', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        user_text = request.form['user_review']
        return redirect(url_for('success', text=user_text))
    else:
        user = request.args.get('user_review')
        return redirect(url_for('success', text=user_text))
 
 
if __name__ == '__main__':
    app.run(debug=True)