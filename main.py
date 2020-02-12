from flask import Flask, request
import sys
import csv
import pickle
import pandas as pd
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
import requests
from requests.auth import HTTPBasicAuth
import json

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
  return """
        <html>
        <head>
        <title>Incident Prioritization</title>
        </head>
        <body>
        Hello, World!<br>
        This is a web service written in Python using <a href=""http://flask.pocoo.org/"">Flask</a> module for incident prioritization by 23519006.<br>
        </body>
        </html>
        """

@app.route("/webhook", methods=["GET", "POST"])
def tracking():
  """Endpoint for receiving webhook from bitbucket."""
  if request.method == "POST":
    data = request.get_json()
    if data["webhookEvent"] == "jira:issue_created":
      summary = data["issue"]["fields"]["summary"]
      description = data["issue"]["fields"]["description"]
      idIssue = data["issue"]["id"]
      key = data["issue"]["key"]
      print("Summary          :",summary)
      print("Description      :",description)
      print("Issue ID         :",idIssue)
      print("Issue Key        :",key)
      return "OK"
    else:
      return "Webhook"

@app.route("/predict", methods=["GET", "POST"])
def predict():
  classifier = 'D3'

  # Loading models
  model_summary_impact = pickle.load(open('./pickle/xtremax/text_'+classifier+'_title_impact_model.pickle',"rb"))
  model_description_impact = pickle.load(open('./pickle/xtremax/text_'+classifier+'_body_impact_model.pickle',"rb"))
  model_summary_urgency = pickle.load(open('./pickle/xtremax/text_'+classifier+'_title_urgency_model.pickle',"rb"))
  model_description_urgency = pickle.load(open('./pickle/xtremax/text_'+classifier+'_body_urgency_model.pickle',"rb"))
  priority_model = pickle.load(open('./pickle/xtremax/'+classifier+'_priority_model.pickle',"rb"))

  data = request.get_json()
  summary = data["issue"]["fields"]["summary"]
  description = data["issue"]["fields"]["description"]
  idIssue = data["issue"]["id"]
  key = data["issue"]["key"]

  summary =  {"title":[summary]}
  description = {"body":[description]}

  # Predict impact
  impact_model = pickle.load(open('./pickle/xtremax/'+classifier+'_impact_weight_model.pickle',"rb"))
  summary_impact = model_summary_impact.predict(summary)
  description_impact = model_description_impact.predict(description)
  impact_data = {"title" : [summary_impact],"body" : [description_impact],"result" : None}
  impact_df = pd.DataFrame(impact_data)
  impact_vars = impact_df.iloc[:,:-1]
  predicted_impact = impact_model.predict(impact_vars)

  # Predict urgency
  urgency_model = pickle.load(open('./pickle/xtremax/'+classifier+'_impact_weight_model.pickle',"rb"))
  summary_urgency = model_summary_urgency.predict(summary)
  description_urgency = model_description_urgency.predict(description)
  urgency_data = {"title" : [summary_urgency],"body" : [description_urgency],"result" : None}
  urgency_df = pd.DataFrame(urgency_data)
  urgency_vars = urgency_df.iloc[:,:-1]
  predicted_urgency = urgency_model.predict(urgency_vars)

  # Predict priority
  priority_data = {"urgency" : predicted_urgency,"impact" : predicted_impact,"result" : None}   
  priority_df = pd.DataFrame(priority_data)
  priority_vars = priority_df.iloc[:,:-1]
  predicted_priority = priority_model.predict(priority_vars)

  # Final variables
  final_summary = summary["title"][0].lower()
  final_description = description["body"][0].lower()
  symbols = ["/","?","<",".","!",",","[","]","(",")","{","}","`","/","*","-","+"]
  for symbol in symbols:
    final_summary = final_summary.replace(symbol,"")
    final_description = final_description.replace(symbol,"")
  final_urgency = priority_data["urgency"][0]
  final_impact = priority_data["impact"][0]
  final_priority = predicted_priority[0]

  # Print
  print("Issue ID         :",idIssue)
  print("Issue Key        :",key)
  print("Summary          :",final_summary)
  print("Description      :",final_description)
  print("Urgency          :",final_urgency)
  print("Impact           :",final_impact)
  print("Priority         :",final_priority)

  # Update the ticket
  headers = {"Accept": "application/json", "Content-Type": "application/json"}
  payload = json.dumps({"fields":{"priority" : {"name" : final_priority}, "customfield_10091" : {"value" : final_urgency},"customfield_10004" : {"value" : final_impact}}})
  url = "https://tesang.atlassian.net/rest/api/3/issue/"+idIssue
  auth = HTTPBasicAuth("23519006@std.stei.itb.ac.id","m7qO60tWTnrssvCX6iIu4C2B")
  response = requests.request("PUT",url,data=payload,headers=headers,auth=auth)
  print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))

  return "Predict"

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)