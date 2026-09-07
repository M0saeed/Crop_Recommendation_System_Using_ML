import os
import pickle
import numpy as np
from flask import Flask, request, render_template, jsonify

# Initialize Flask Application
app = Flask(__name__)

# Load Trained Models and Scalers
MODEL_PATH = 'model.pkl'
STAND_SCALER_PATH = 'standscaler.pkl'
MINMAX_SCALER_PATH = 'minmaxscaler.pkl'

model = pickle.load(open(MODEL_PATH, 'rb'))[cite: 1]
sc = pickle.load(open(STAND_SCALER_PATH, 'rb'))[cite: 1]
ms = pickle.load(open(MINMAX_SCALER_PATH, 'rb'))[cite: 1]

# Crop Mapping Dictionary
CROP_DICT = {
    1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya", 7: "Orange",
    8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
    14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean", 18: "Mothbeans",
    19: "Pigeonpeas", 20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"
}[cite: 1]

def predict_crop_with_confidence(feature_list):
    """
    Transforms input features, predicts the crop, 
    and calculates prediction confidence score if available.
    """
    # Convert input string features to floating-point numbers
    float_features = [float(x) for x in feature_list]
    single_pred = np.array(float_features).reshape(1, -1)[cite: 1]

    # Preprocess and scale input features
    scaled_features = ms.transform(single_pred)[cite: 1]
    final_features = sc.transform(scaled_features)[cite: 1]

    # Perform prediction
    prediction = model.predict(final_features)[0][cite: 1]

    # Calculate confidence percentage
    confidence = None
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(final_features)[0]
        confidence = round(float(np.max(probabilities)) * 100, 2)

    crop_name = CROP_DICT.get(prediction, None)[cite: 1]
    return crop_name, confidence


@app.route('/')
def index():
    return render_template("index.html")[cite: 1]


@app.route("/predict", methods=['POST'])[cite: 1]
def predict():
    try:
        # Handle input data from both JSON API requests and Web Forms
        if request.is_json:
            data = request.get_json()
            features = [
                data.get('Nitrogen'), data.get('Phosporus'), data.get('Potassium'),
                data.get('Temperature'), data.get('Humidity'), data.get('Ph'), data.get('Rainfall')
            ][cite: 1]
        else:
            features = [
                request.form['Nitrogen'], request.form['Phosporus'], request.form['Potassium'],
                request.form['Temperature'], request.form['Humidity'], request.form['Ph'], request.form['Rainfall']
            ][cite: 1]

        # Execute prediction pipeline
        crop, confidence = predict_crop_with_confidence(features)

        # Construct response message
        if crop:
            if confidence is not None:
                result = f"The best crop for cultivation is: {crop} (Confidence: {confidence}%)"
            else:
                result = f"{crop} is the best crop to be cultivated right there."[cite: 1]
        else:
            result = "Sorry, we could not determine the best crop with the provided data."[cite: 1]

        # Return JSON response for API calls
        if request.is_json:
            return jsonify({
                'status': 'success',
                'crop': crop,
                'confidence': confidence,
                'result_message': result
            })

        # Render HTML template with result for Web Forms
        return render_template('index.html', result=result)[cite: 1]

    except ValueError:
        error_msg = "Error: Please ensure valid numerical values are entered in all fields."
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        return render_template('index.html', result=error_msg)

    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 500
        return render_template('index.html', result=error_msg)


if __name__ == "__main__":
    # Run the Flask local development server
    app.run(debug=True)[cite: 1]