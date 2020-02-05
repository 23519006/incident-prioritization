from flask import Flask, request
import sys
import pickle
import pandas as pd

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
      print "Summary:"
      print summary
      print "Description:"
      print description
      print "Id issue:"
      print idIssue
      print "Key issue:"
      print key
      return "OK"
    else:
      return "Webhook"

@app.route("/predict", methods=["POST"])
def predict():
    # Download models
    from models.download_models import download_file, download_models
    download_models()

    classifier = SVM

    # Loading models
    model_summary_impact = pickle.load(open('./pickle/xtremax/text_'+classifier+'_title_impact_model.pickle',"rb"))
    model_description_impact = pickle.load(open('./pickle/xtremax/text_'+classifier+'_body_impact_model.pickle',"rb"))
    model_summary_urgency = pickle.load(open('./pickle/xtremax/text_'+classifier+'_title_urgency_model.pickle',"rb"))
    model_description_urgency = pickle.load(open('./pickle/xtremax/text_'+classifier+'_body_urgency_model.pickle',"rb"))
    priority_model = pickle.load(open('./pickle/xtremax/'+classifier+'_priority_model.pickle',"rb"))

    summary = request.json['summary']
    description = request.json['description']

    # Predict impact
    summary_impact = model_summary_impact.predict(summary)
    description_impact = model_description_impact.predict(description)
    impact_data = {"title" : summary_impact,"body" : description_impact,"result" : None}
    impact_df = pd.DataFrame(impact_data)
    impact_vars = impact_df.iloc[:,:-1]
    predicted_impact = impact_model.predict([impact_vars])
    print("predicted impact: "+str(predicted_impact))

    # Predict urgency
    summary_urgency = model_summary_urgency.predict(summary)
    description_urgency = model_description_urgency.predict(description)
    urgency_data = {"title" : summary_urgency,"body" : description_urgency,"result" : None}
    urgency_df = pd.DataFrame(urgency_data)
    urgency_vars = urgency_df.iloc[:,:-1]
    predicted_impact = impact_model.predict([impact_vars])
    print("predicted urgency: "+str(predicted_urgency))

    # Predict priority
    predicted_priority = model_priority.predict(description)
    print("predicted priority: "+str(predicted_priority))
    priority_data = {"urgency" : predicted_urgency,"impact" : predicted_impact,"result" : None}   
    priority_df = pd.DataFrame(priority_data)
    priority_vars = priority_df.iloc[:,:-1]
    predicted_priority = priority_model.predict(priority_vars)

    final_summary = summary.lower()
    final_description = description.lower()
    for symbol in symbols:
        final_summary = final_summary.replace(symbol,"")
        final_description = final_description.replace(symbol,"")
    final_urgency = priority_data["urgency"][0]
    final_impact = priority_data["impact"][0]
    final_priority = predicted_priority[0]
    print("Summary          :",final_summary)
    print("Description      :",final_description)
    print("Urgency          :",final_urgency)
    print("Impact           :",final_impact)
    print("Priority         :",final_priority)

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)