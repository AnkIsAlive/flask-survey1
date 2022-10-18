# IMPORT TOOLS AND TOOLS
from flask import Flask, render_template, request, redirect, flash, session, make_response
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey

CUURENT_SURVEY_KEY = 'current_survey'
RESPONSE_KEY = "responses"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Springboard123'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


@app.route('/')
def show_survey_start():
    """user selects survey"""

    return render_template('survey_start.html', survey=surveys)


@app.route("/", methods=["POST"])
def pick_survey():
    """User can choose survey"""

    survey_id = request.form['survey_code']

    # not letting user re-take survey until cookie is cleared/times out.
    if request.cookies.get(f"completed_{survey_id}"):
        return render_template("already-done.html")

    survey = surveys[survey_id]
    session[CURRENT_SURVEY_KEY] = survey_id

    return render_template("survey_start.html", survey=surveys)


@app.route("/begin", methods=['POST'])
def start_survey():

    session[RESPONSE_KEY] = []

    return redirect("/questions/0")


@app.route('/answer', methods=["POST"])
def handle_question():

    choice = request.form['answer']

    # add response to list in session
    responses = session[RESPONSE_KEY]
    responses.append(choice)

    # add repsonse to session
    session[RESPONSE_KEY] = responses
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    if (len(responses) == len(survey.questions)):
        # once they have answered all questions
        return redirect("/complete")
    else:
        return redirect(f"/questions/{len(responses)}")


@app.route('/questions/<int:qid>')
def show_question(qid):
    responses = session.get(RESPONSE_KEY)
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    if (responses is None):
        # trying to access questions too fast
        return redirect('/')

    if (len(responses) == len(survey.questions)):
        # completing the survey fully
        return redirect("/complete")

    if (len(responses) != qid):
        # accessing questions out of order
        flash(f"Invalid question id: {qid}.")
        return redirect(f"/questions/{len(responses)}")

    question = survey.questions[qid]

    return render_template(
        "question.html", question_num=qid, question=question)


@app.route("/complete")
def say_thanks():
    """Thank you message and respond with list"""

    survey_id = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_id]
    responses = session[RESPONSE_KEY]

    html = render_template(
        "completion.html", survey=survey, responses=responses)

    # set cookie nothing so user cannot retake surveys
    response = make_response(html)
    response.set_cookie(f"completed_{survey_id}", "yes", max_age=60)
    return response
