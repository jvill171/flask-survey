from flask import Flask, request, render_template, redirect, flash, session, make_response
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys
from survey_validation import *

RESPONSE_KEY = "response"
SURVEY_KEY = "current_survey"
app = Flask(__name__)

app.config['SECRET_KEY']="survey-secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

@app.route("/")
def home_page():
    '''Starting page, to select survey'''
    return render_template("select_survey.html", surveys=surveys)

@app.route("/", methods=['POST'])
def survey_selected():
    '''Starting page, after survey selected'''
    survey_code = request.form['survey_code']

    survey=surveys[survey_code]
    session[SURVEY_KEY]=survey_code

    if request.cookies.get(f"{survey_code}_completed"):
        surv_resp_key = make_survey_key(RESPONSE_KEY, survey_code)
        my_survey_resp=session[surv_resp_key]
        
        flash("You have already completed this survey!")
        return render_template("survey_complete.html", survey_title=survey.title, survey_questions=survey.questions, my_survey=my_survey_resp)
    
    return render_template("survey_home.html", survey=survey)

@app.route("/begin-survey", methods=['POST'])
def begin_survey():
    '''Begins the survey'''
    survey_code=session[SURVEY_KEY]
    surv_resp_key = make_survey_key(RESPONSE_KEY, survey_code)

    session[surv_resp_key] = []
    #redirect to first question
    return redirect(f'/question/1')

@app.route("/answer", methods=['POST'])
def do_answer():
    '''Append user's response to response[] and proceed to next questions/completed survey'''
    #Collect response to the question
    ans_resp=request.form['answer']
    text_ans_resp=request.form.get('text')
    
    # Get specific survey ID (survey_code) and specify survey
    survey_code=session[SURVEY_KEY]
    survey=surveys[survey_code]

    # Set up response variable
    surv_resp_key = make_survey_key(RESPONSE_KEY, survey_code)
    response=session[surv_resp_key]

    # Add to responses
    response.append({'answer': ans_resp, 'long_answer': text_ans_resp})
    session[surv_resp_key]=response

    if(len(response) == len(survey.questions)):
        #All questions answered, redirect to survey-complete
        return redirect("/survey-complete")
    else:
        #Proceed to next question
        return redirect(f'/question/{len(response)+1}')

@app.route('/question/<int:qid>')
def question_page(qid):
    '''Display the next un-answered question'''
    survey_code = session.get(SURVEY_KEY)
    
    if survey_code is None:
        # No survey selected, but tried entering a question
        flash("Choose a survey before proceeding to the questions!")
        return redirect ("/")

    surv_resp_key = make_survey_key(RESPONSE_KEY, survey_code)
    response = session.get(surv_resp_key)
    survey = surveys[survey_code]

    if is_complete(survey.questions, response):
        #prevent jumping into non-existent question after survey-completion
        flash("Redirected: Survey has been completed! ")
        return redirect('/survey-complete')
    elif len(response)+1 == qid:
        #Display next unanswered question
        return render_template("question.html", sat_quest=survey.questions[qid-1],qid=qid)
    else:
        #prevent skipping forward/back questions, redirect to current question
        flash("Redirected: Tried accessing invalid question!")
        return redirect(f'/question/{len(response)+1}')
 
@app.route('/survey-complete')
def survey_complete():
    '''Display survey completed page, specifying which survey was completed'''
    survey_code = session.get(SURVEY_KEY)
    
    if survey_code is None or session.get(make_survey_key(RESPONSE_KEY, survey_code)) is None:
        # Tried accessing survey completion before selecting a survey
        flash("Redirect: Please select a survey")
        return redirect("/")
    
    survey = surveys[survey_code]
    surv_resp_key = make_survey_key(RESPONSE_KEY, survey_code)
    my_survey_resp=session[surv_resp_key]

    if is_complete(survey.questions, my_survey_resp):
        # survey was completed        
        html = render_template("survey_complete.html", survey_title=survey.title, survey_questions=survey.questions, my_survey=my_survey_resp)

        # Add cookie with a 60 second TTL to response, corrsponding to current survey
        response = make_response(html)
        response.set_cookie(f"{survey_code}_completed", "yes", max_age=60)
        return response

    else:
        # Tried accessing completion screen before completing the survey
        flash("Redirected: Survey has NOT been completed! ")
        return redirect(f'/question/{len(my_survey_resp)+1}')
