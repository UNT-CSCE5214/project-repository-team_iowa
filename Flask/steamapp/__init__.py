from flask import Flask, redirect, url_for, request, render_template, session
app = Flask(__name__)
app.secret_key = 'dev'

def getScores():
        session['score1'] = -0.85
        session['score2'] = -0.31
        session['score3'] = 0.07
        session['score4'] = 0.75

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
        getScores()
        return redirect(url_for('success'))
    else:
        user = request.args.get('user_review')
        return redirect(url_for('success'))

@app.context_processor
def score_processor():
    def scoreColor(score):
        # error handling
        if score < -1 or score > 1:
            return 'DeepPink'
        else:
            # some really funky math to get a good-looking gradient
            
            # if score is within neutral range, map from rgb(100,100,100) at 0.0 to rgb(200,200,200) at +/-0.1
            if score >= -0.1 and score <= 0.1:
                B = 100 + abs(score)*1000
            # otherwise, B=0 at +/-1, and linearly ramps to 135 at +/-0.1
            else:
                B = (1-abs(score))*150
            # if within neutral range, make the color grey
            if score <= 0.1:
                G = B
            # if score above the neutral threshold, max out the green value
            else:
                G = 225
            # if within neutral range, make the color grey
            if score >= -0.1:
                R = B
            # if score below the neutral threshold, max out the red value
            else:
                R = 225
            
            return f'rgb({R},{G},{B})'
        
    return dict(scoreColor=scoreColor)
@app.route('/')
def main():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)