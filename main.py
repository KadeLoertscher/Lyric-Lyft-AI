# Imports
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from transformers import pipeline
import string
from better_profanity import profanity
pf = profanity

# Set up flask application
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db = SQLAlchemy(app)

# Load in lyric lyft ai
spotifyModel = pipeline("text-generation", model="KadeLoertscher/Lyric-Lyft-Model", max_new_tokens=30)
# spotifyModel = pipeline("text-generation", model="rautsrijana/Joyous_Jackals_Lyriclyft", max_new_tokens=30)
# spotifyModel = pipeline("text-generation", model="RobertGCucu/LyricLift", max_new_tokens=30)

# Stores the current output of the ai
curOutput = ""


# Filters a given prompt to only contain certain characters to prevent errors
def filterPrompt(prompt):
    filteredPrompt = ""
    # Keeps alpha characters, spaces, and punctuation
    for char in prompt:
        if (char.isalpha()) or (char == " ") or (char in string.punctuation):
            filteredPrompt += char
    # Makes sure the ai isn't submitted an empty prompt (if the user submitted a prompt with only prohibited chars)
    if filteredPrompt == "":
        filteredPrompt = "Null"
    return filteredPrompt


# Main index webpage
@app.route("/", methods=["POST", "GET"])
def index():
    # User posts an input
    if request.method == "POST":
        try:
            # Gets the text the user typed and filters it
            userPrompt = request.form["content"]
            filteredPrompt = filterPrompt(userPrompt)
            # Redirects to submit with the user's prompt and makes sure it is clean
            return redirect(f"/submit/{pf.censor(filteredPrompt, '')}")
        except Exception as e:
            # An error occurred
            return "There was an error submitting the prompt ---> " + repr(e)
    else:
        # Displays the ai's output
        return render_template("index.html", response=curOutput.strip(" ") + " " if curOutput != "" else "")


# Submits the user's input to the ai
@app.route("/submit/<string:text>", methods=["POST", "GET"])
def submit(text):
    global curOutput
    try:
        # Generates ai response
        output = spotifyModel(text)[0]["generated_text"]
        # Updates the current output
        curOutput = output
        # Makes sure ai's output is clean
        curOutput = pf.censor(curOutput, "")
        # Redirects user to index
        return redirect("/")
    except Exception as e:
        # An error occurred
        return "There was an error returning the prompt ---> " + repr(e)


# Clears the ai's output from the index page
@app.route("/clear", methods=["POST", "GET"])
def clear():
    try:
        global curOutput
        if request.method == "POST":
            # Resets current output
            curOutput = ""

        # Redirects user to index
        return redirect("/")
    except Exception as e:
        # An error occurred
        return "There was an error clearing the output ---> " + repr(e)


# Resubmits the ai's output back into the submit route to continue its prompt
@app.route("/continue", methods=["POST", "GET"])
def continueOutPut():
    try:
        if request.method == "POST":
            # Filters then submits the ai's output
            return redirect(f"submit/{filterPrompt(curOutput)}")
        else:
            return redirect("/")
    except Exception as e:
        # An error occurred
        return "There was an error continuing the output ---> " + repr(e)


# Runs the application
if __name__ == "__main__":
    app.run(host="127.0.0.9", port=8080)
