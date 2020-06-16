from train import predict, train_model, load_model
from flask_ngrok import run_with_ngrok
from flask import Flask, jsonify, request

load_model()

app = Flask(__name__)
run_with_ngrok(app)

@app.route('/')
def home():
	return 'Hello world! - Sadmanda'

@app.route('/api/chat', methods = ['GET'])
def chat():
  msg_dict = request.get_json()
  speaker = msg_dict['speaker']
  msg = msg_dict['msg']
  
  output = predict(msg)
  
  if output is not None:
    return jsonify({'status': 'success', 'data': {'output': output}})
  else:
    return jsonify({'status': 'fail', 'data': {}})

app.run()