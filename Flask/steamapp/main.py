from flask import Flask, redirect, url_for, request, render_template, session
import pickle
import re

app = Flask(__name__)
app.secret_key = 'dev'
model1 = pickle.load(open('sentiment_analysis_best_model.pkl','rb'))

# Haiyi's
def process_text_1(content):
    sentence = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','', content)
    sentence = re.sub('@[^\s]+','', sentence)
    sentence = sentence.lower().split()
    reformed_sentence = [word for word in sentence]
    reformed_sentence = " ".join(reformed_sentence) 
    sentence = re.sub('&[^\s]+;', '', reformed_sentence)
    sentence = re.sub('[^a-zA-Zа-яА-Я1-9]+', ' ', sentence)
    sentence = re.sub(' +',' ', sentence)
    #text = re.sub(' [\w] ', ' ', text)
    session['process_1_text'] = [sentence.strip()]

# Andre's
def process_text_2(text):
    #\r and \n
    session['process_2_text_1'] = text.replace("\r", " ")
    session['process_2_text_1'] = session['process_2_text_1'].replace("\n", " ")
    session['process_2_text_1'] = session['process_2_text_1'].replace("    ", " ")

    # quotation marks
    session['process_2_text_1'] = session['process_2_text_1'].replace('"', '')

    # Lower casing all words so that upper case words (ex: at the begineeing of a sentence) 
    # are read the same as lower case words
    session['process_2_text_2'] = session['process_2_text_1'].lower()

    # punctuation signs
    punctuation_signs = list("?:!.,;")
    session['process_2_text_3'] = session['process_2_text_2']

    for i in punctuation_signs:
        session['process_2_text_3'] = session['process_2_text_3'].replace(i, '')
    
    # Possesvive pronouns 
    session['process_2_text_4'] = session['process_2_text_3'].replace("'s", "")

def getScores(text):
        process_text_2(text)
        process_text_1(text)
        session['score1'] = (float(model1.predict(session['process_1_text'])[0]))
        session['score2'] = 1.0
        session['score3'] = 1.0
        session['score4'] = 0.0

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
        getScores(user_text)
        return redirect(url_for('success'))

@app.context_processor
def score_processor():
    def scoreColor(score):
        # error handling
        if score < -1 or score > 1:
            return 'DeepPink'
        else:
            # some really funky math to get a good-looking gradient
            # if score is within neutral range, map from rgb(100,100,100)
            # at 0.0 to rgb(200,200,200) at +/-0.1
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
                G = 200
            # if within neutral range, make the color grey
            if score >= -0.1:
                R = B
            # if score below the neutral threshold, max out the red value
            else:
                R = 200
            
            return f'rgb({R},{G},{B})'
        
    return dict(scoreColor=scoreColor)
@app.route('/')
def main():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)