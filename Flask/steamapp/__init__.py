from flask import Flask, redirect, url_for, request, render_template, session
import pickle
import re

app = Flask(__name__)
app.secret_key = 'dev'
model1 = pickle.load(open('sentiment_analysis_best_model.pkl','rb'))

def getScores(text):
        # model outputs 0 or 1. Multiply by 2 and subtract 1 to normalize to range [-1, 1]
        session['score1'] = (float(model1.predict(process_text1(text))[0])*2.0)-1.0
        session['score2'] = -0.11
        session['score3'] = 0.07
        session['score4'] = 0.75

def process_text1(content):
    sentence = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','', content)
    sentence = re.sub('@[^\s]+','', sentence)
    sentence = sentence.lower().split()
    reformed_sentence = [word for word in sentence]
    reformed_sentence = " ".join(reformed_sentence) 
    sentence = re.sub('&[^\s]+;', '', reformed_sentence)
    sentence = re.sub('[^a-zA-Zа-яА-Я1-9]+', ' ', sentence)
    sentence = re.sub(' +',' ', sentence)
    #text = re.sub(' [\w] ', ' ', text)
    return [sentence.strip()]

@app.route('/success/')
def success():
    return render_template('output.html')

@app.route('/noresponse/')
def noresponse():
    return render_template('emptyReview.html')

@app.route('/home', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        user_text = request.form['user_review']
        if(not user_text):
            return redirect(url_for('noresponse'))
        session['user_text'] = user_text
        session['processed_text'] = process_text1(user_text)
        getScores(user_text)
        return redirect(url_for('success'))
    #else:
    #    user = request.args.get('user_review')
    #    return redirect(url_for('success'))

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
                B = (1-abs(score))*175
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