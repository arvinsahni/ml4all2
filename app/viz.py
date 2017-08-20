from __future__ import division

from flask import render_template, request, Response, jsonify,redirect,url_for,flash
from werkzeug.utils import secure_filename

from app import app

import json
import psycopg2
import psycopg2.extras
import os
import pandas as pd
import hashlib
import datetime
from datetime import date
import numpy as np
from subprocess import Popen
import shlex
import sys
import requests
import threading
from json2table import convert

module_path = os.path.abspath(os.path.join('../'))
if module_path not in sys.path:
    sys.path.append(module_path)

from learn import forall as fa
from learn import utils

TRAINING_DATA={}
TESTING_DATA={}


ALLOWED_EXTENSIONS=set(['txt','csv'])
SECRET_KEY='ml4all'
app.secret_key='ml4all'

p="global variable for the vis server"

@app.route('/index')
def index():
	return render_template('home.html')

@app.route('/')
def dataset():
   return render_template('home.html')

@app.route('/method')
def method():
	return render_template('method.html')


def to_csv(d, fields):
	d.insert(0, fields)
	return Response('\n'.join([",".join(map(str, e)) for e in d]), mimetype='text/csv')

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/dataset',methods=['POST'])
def upload_file():
	global p
	train_file_name = 'train'
	test_file_name ='test'
	error=None
	if request.method == 'POST':
		try:
			p.terminate()
			print("Shiny server killed.")
		except Exception as e:
			print(e)
			print("Did not find a Shiny server to kill...")

		# check if the post request has the file part
		if train_file_name not in request.files or test_file_name not in request.files:
			#flash('No file part')
			error='Kindly upload both training and testing files'
			#print("helllllo")
			#print(request.url)
			flash("load files")
			#return redirect(request.url)
			return render_template('home.html',error=error)


		file = request.files[train_file_name]

		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == '':

			print(request.url)
			error='Kindly upload both training and testing files'

			flash('No selected files')
			return redirect(request.url)
			#return render_template('home.html',error=error)

		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			print(filename)
			print(os.path.abspath(os.path.join('app/','uploads/')))
			#file.save(os.path.abspath(os.path.join('app/',app.config['UPLOAD_FOLDER'], filename)))
			file.save(os.path.abspath(os.path.join('app/','uploads/', filename)))
			print("done")
			## convert file to pandas dataframe
			#df_train=pd.read_csv(os.path.join('app/',app.config['UPLOAD_FOLDER'], filename))
			df_train=pd.read_csv(os.path.join('app/','uploads/', filename))

			print("df_train1",df_train.head(5))

			## hash the pd , change to binary --> get fom Jason
			temp_hash=pd.util.hash_pandas_object(df_train)
			hash_train = hashlib.sha256(str(temp_hash).encode('utf-8','ignore')).hexdigest()

			#Save train data in /uploads folder
			os.system("mv app/uploads/" + filename + " " + "app/uploads/" + hash_train + ".csv")
			## update dict ---> key:hash ,value: dataframe
			#TRAINING_DATA[hash_train]=df_train

		## For the test file
		file = request.files[test_file_name]

			# if user does not select file, browser also
			# submit a empty part without filename
		if file.filename == '':
			print(request_url)
			flash('No selected files')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			#file.save(os.path.abspath(os.path.join('app/',app.config['UPLOAD_FOLDER'], filename)))
			file.save(os.path.abspath(os.path.join('app/','uploads/', filename)))

			## convert file to pandas dataframe
			#df_test=pd.read_csv(os.path.join('app/',app.config['UPLOAD_FOLDER'], filename))
			df_test=pd.read_csv(os.path.join('app/','uploads/', filename))
			print("df_test1",df_test.head(5))

			## hash the pd , change to binary --> get fom Jason
			temp_hash=pd.util.hash_pandas_object(df_test)
			hash_test = hashlib.sha256(str(temp_hash).encode('utf-8','ignore')).hexdigest()

			# Save test data in /uploads folder
			os.system("mv app/uploads/" + filename + " " + "app/uploads/" + hash_test + ".csv")

		# Pass datasets to Shiny app
		p = Popen(shlex.split("Rscript ~/shiny.R " + hash_train + ".csv " + hash_test + ".csv",posix=False))
		return(jsonify({"hash_train": hash_train, "hash_test": hash_test}))


@app.route('/shiny',methods=['GET'])
def check_shiny():
	# Check if Shiny server is up
	response_code = 0
	import time
	port1 = os.environ["PORT"]
	print("port1 is ",port1)
	while response_code != 200:
		try:
			#r = requests.head("https://ml4all1.herokuapp.com:"+str(port1))
			r=requests.head("http://0.0.0.0:7775")
			response_code = r.status_code
			print(r.status_code)
		except requests.ConnectionError:
			time.sleep(0.1)
			print("Trying to connect to Shiny server.")
			pass

	return("Shiny server is up.")


@app.route('/predict/<hash_train>_<hash_test>', methods=['GET'])
def run_prediction(hash_train, hash_test):
	train_file=hash_train + ".csv"
	test_file=hash_test + ".csv"

	# Make predictions
	df_train=pd.read_csv(os.path.join('app/','uploads/', train_file))
	df_test=pd.read_csv(os.path.join('app/','uploads/', test_file))
	X, y = utils.X_y_split(X_train=df_train, X_test=df_test)
	model = fa.All()
	model.fit(X, y)

	# Append prediction column to test set
	predictions = model.predict(df_test)
	df_test['prediction'] = predictions
	# Save output file in /downloads folder
	df_test.to_csv("app/downloads/" + hash_train + "_" + hash_test + ".csv", index=False)

	# Add model.display_score to JSON and round values
	model.all_metrics = {k:round(v, 3) for k, v in model.all_metrics.items()}
	model.all_metrics['Overall score']=model.display_score

	# Build HTML table
	build_direction = "LEFT_TO_RIGHT"
	table_attributes = {"style" : "width:30%"}
	display_score = convert(model.all_metrics, build_direction=build_direction, table_attributes=table_attributes)

	# if df_train.shape[1]==(df_test.shape[1]-1):
	# 	temp=hash_test
	# 	hash_test=hash_train
	# 	hash_train=temp
	# 	temp_df=df_test
	# 	df_test=df_train
	# 	df_train=temp_df
	#
	# TESTING_DATA[hash_test]=df_test
	# TRAINING_DATA[hash_train]=df_train
	# #print("hash_train2",hash_train)
	# #print("hash_test2",hash_test)
	# #print("df_train2",df_train)
	# #print("df_test2",df_test)
	# flash("Uploaded files all training")
	# return redirect('home.html')
	# return jsonify({"hash":hash})
	# return redirect(request.url)
	# return redirect(url_for('dataset'))
	return(jsonify({"hashid": hash_train + "_" + hash_test, "performance": display_score}))

## may look to add another app.route for test data hash but later

#@app.route('/dataset_test',methods=['POST'])
#def upload_testfile():


#        file_name = 'test[]'
#
#        if request.method == 'POST':
#
#                # check if the post request has the file part
#                if file_name not in request.files:
#                        print(request.files)
#                        flash('No file part')
#                        return redirect(request.url)
#
#                file = request.files[file_name]
#
#                print (file.filename)
#                # if user does not select file, browser also
#                # submit a empty part without filename
#                if file.filename == '':
#
#                        flash('No selected files')
#                        return redirect(request.url)
#                if file and allowed_file(file.filename):
#
#                        filename = secure_filename(file.filename)
#
#                        print(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#                        print(os.getcwd())
#                        file.save(os.path.join('app/',app.config['UPLOAD_FOLDER'], filename))
#
#                        ## convert file to pandas dataframe
#
#                        df_test=pd.read_csv(os.path.join('app/',app.config['UPLOAD_FOLDER'], filename))
#                        print(df_test.head(5))

#                        ## hash the pd , change to binary --> get fom Jason
#                        temp_hash_test=hash_pandas_object(df_test)

#                        print(temp_hash_test)
#                        testing_data_hash = hashlib.sha256(str(temp_hash_test).encode('utf-8','ignore')).hexdigest()
#                        print(testing_data_hash)
#                        ## update dict ---> key:hash ,value: dataframe
#                        TESTING_DATA[temp_hash_test]=df_test

#                        return jsonify({"test_data_hash":testing_data_hash})


BASIC_STATS = {}
##replace with actual function
def jacky_function(df):
	return date.today(),1,len(list(df))

@app.route('/basic-stats/<hash>',methods=['GET'])
def basic_stat(hash):
	## step 1 if hash in BASIC_STATS return jsonify(BASIC_STATS[hash])
	## else step 2
	## pull in training data
        ## compute basic stats(basically call Jacky's function)  add results to dictionary BASIC_STATS, return jsonify(BASIC_STATS[hash])
        ## which is basically {"metadata": {"date": <ISO Format>, "version": <int>}, "data": {<data collection 1>: {}, <data collection 2>: {}, ...}}
	print(TRAINING_DATA)

	if hash in BASIC_STATS:
		return jsonify({BASIC_STATS[hash]})
		# error can be sent the same way jsonify(BASIC_STATS[error])
	else:
		#for key,value in TRAINING_DATA.items():
			#print (key,value)
		train_df=TRAINING_DATA[hash_train]
		date_fn,version_fn,stats=jacky_function(train_df)
		BASIC_STATS[hash_train]=stats
		return jsonify({"metadata":{"date":str(date_fn),"version":version_fn},"data":stats})


## Prediction stats work the same way as basic stats except i need to call Jason's function instead of Jacky's function
## this would need a MODELS dictionary - key is the hash value, value is the model we train
## input to a function that Jason will write ---> model ( from the MODELS dictionary)
## output would be {"metadata": {"date": <ISO Format>, "version": <int>}, "data": {"technical_scores": [{"name": "AUC", "value": .867}, {"name": "Accuracy", "value": "79%"}], <data collection 2>: {}, ...}}
# ( inform JAcky of the structure --how its returned)

MODELS={}
##replace with actual function
sample={}
temp={}
temp
sample["technical_scores"]=[]
def jason_function(df):
        return date.today(),100,len(list(df))

@app.route('/prediction-stats/<hash>',methods=['GET'])
def prediction_stat(hash):
	print(TRAINING_DATA)
	if hash in MODELS:
        	return jsonify({MODELS[hash]})
	else:
		train_df=TRAINING_DATA[hash]
		date_fn,version_fn,pred_stats=jason_function(train_df)
		MODELS[hash]=pred_stats
		return jsonify({"metadata":{"date":str(date_fn),"version":version_fn},"data":pred_stats})



## test data prediction

#replace by actual code
def jason_model_creation(hash):
	return 100
def jason_prediction(model_saved,hash,testing_data_hash):
	return 200

## this one should return a df
def jason_add_pred_to_test(pred,testing_data_hash,hash):
	return pd.DataFrame(np.random.randn(10, 5))

from flask import send_from_directory
MODELS_SAVED={}
## the below is for checking stuff only
#TESTING_DATA["e0d47420dd0157af6af54d64b14f348f1fada3c050a73cd50fad2716a38fc2b2"]=1234
@app.route('/download/<hashid>',methods=['GET'])
def prediction_test(hashid):
	return send_from_directory(directory=os.path.abspath(os.path.join('app/downloads/')), filename=hashid + ".csv")
