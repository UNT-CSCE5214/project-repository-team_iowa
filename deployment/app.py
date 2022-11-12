from flask import Flask,request,jsonify,render_template
import pickle
import re

app = Flask(__name__)
model = pickle.load(open('sentiment_analysis_best_model.pkl','rb'))

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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    text = request.form['words']
    prediction = model.predict(process_text1(text))[0]
    
    if prediction==0:
        output = 'Negative'
    else:
        output = 'Positive'
        
    return render_template('index.html', prediction_text='The best sentiment analysis model predict:{}'.format(output))
 
 
    
if __name__ == "__main__":
    app.run(debug=True)