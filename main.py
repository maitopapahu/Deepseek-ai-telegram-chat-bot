from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)
generator = pipeline('text-generation', model='distilgpt2')

@app.route('/generate', methods=['POST'])
def generate():
    input_text = request.json.get('text', '')
    output = generator(input_text, max_length=50, num_return_sequences=1)
    return jsonify(output)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
  
