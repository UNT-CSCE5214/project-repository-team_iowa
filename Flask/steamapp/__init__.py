from flask import Flask, redirect, url_for, request, render_template, session
app = Flask(__name__)
app.secret_key = 'dev'
 
@app.route('/success/')
def success():
    if(session.get('user_text', None)):
        return render_template('output.html')
    else:
        return render_template('emptyReview.html')


@app.route('/home', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        user_text = request.form['user_review']
        session['user_text'] = user_text
        return redirect(url_for('success'))
    else:
        user = request.args.get('user_review')
        return redirect(url_for('success'))

@app.context_processor
def getScores():
    return {'score1':0.5,'score2':-0.6,'score3':-0.2,'score4':0.9}

@app.route('/')
def main():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)