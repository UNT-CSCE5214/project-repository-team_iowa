from flask import Flask, redirect, url_for, request, render_template, session
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
import pickle
import re
import logging
from tensorflow import keras


app = Flask(__name__)
app.secret_key = 'dev'
model1 = pickle.load(open('sentiment_analysis_svm.pkl','rb'))
model2 = pickle.load(open('sentiment_analysis_random_forest.pkl','rb'))
# This would be part of the app, but google's free tier has memory limits
#model3 = keras.models.load_model("kerasClassificationModel.h5")

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

# Google cloud functions
def predict_text_classification_single_label_sample(
    project: str,
    endpoint_id: str,
    content: str,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
    instance = predict.instance.TextClassificationPredictionInstance(
        content=content,
    ).to_value()
    instances = [instance]
    parameters_dict = {}
    parameters = json_format.ParseDict(parameters_dict, Value())
    endpoint = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )
    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters
    )
    print("response")
    print(" deployed_model_id:", response.deployed_model_id)

    predictions = response.predictions
    print(predictions)
    for prediction in predictions:
        #print(prediction)
        print(" prediction:", dict(prediction))
        #print(dict(prediction))
        #print(dict(prediction)['confidences'])
        #print(dict(prediction)['confidences'][0])
        return dict(prediction)['confidences'][0]
# [END aiplatform_predict_text_classification_single_label_sample]

def predict_text_sentiment_analysis_sample(
    project: str,
    endpoint_id: str,
    content: str,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
    instance = predict.instance.TextSentimentPredictionInstance(
        content=content,
    ).to_value()
    instances = [instance]
    parameters_dict = {}
    parameters = json_format.ParseDict(parameters_dict, Value())
    endpoint = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )
    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters
    )
    print("response")
    print(" deployed_model_id:", response.deployed_model_id)
    # See gs://google-cloud-aiplatform/schema/predict/prediction/text_sentiment_1.0.0.yaml for the format of the predictions.
    predictions = response.predictions
    for prediction in predictions:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(prediction)
        print(" prediction:", dict(prediction))
        print(dict(prediction)['sentiment'])
        return dict(prediction)['sentiment']
# [END aiplatform_predict_text_sentiment_analysis_sample]

def getScores(text):
        process_text_2(text)
        process_text_1(text)
        session['score1'] = round(predict_text_classification_single_label_sample(
                                project="47224200977",
                                endpoint_id="1634424034689024000",
                                location="us-central1",
                                content=session['process_2_text_4']
                            ),2)
        session['score2'] = round(predict_text_sentiment_analysis_sample(
                                project="47224200977",
                                endpoint_id="9119969565332209664",
                                location="us-central1",
                                content=session['process_2_text_4']
                            ),2)
        session['score3'] = float(model1.predict(session['process_1_text'])[0])
        session['score4'] = float(model2.predict(session['process_1_text'])[0])
        # This would be part of the app, but google's free tier has memory limits
        #session['score5'] = float(model3.predict(session['process_1_text'])[0])

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
        # outputs are in range [0,1]. Project to [-1,1] because I already did that math
        score = score*2-1
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