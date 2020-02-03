from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "tessa"


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
        return "Webhoook"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)