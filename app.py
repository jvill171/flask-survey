from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import *

RESPONSE_KEY = "response"
app = Flask(__name__)

survey = satisfaction_survey

app.config['SECRET_KEY']="survey-secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

@app.route("/")
def home_page():
    '''Starting page, to begin survey'''
    return render_template("survey_home.html", survey=survey)



@app.route("/begin-survey", methods=['POST'])
def begin_survey():
    '''Begins the survey'''
    session[RESPONSE_KEY]=[]
    #redirect to first question
    return redirect(f'/question/1')

 

@app.route("/answer", methods=['POST'])
def do_answer():
    '''Append user's response to response[] and proceed to next questions/completed survey'''
    #Collect response to the question
    ans_resp=request.form['answer']
    
    #Add collected response to session
    response=session[RESPONSE_KEY]
    response.append(ans_resp)
    session[RESPONSE_KEY] = response

    if(len(response) == len(survey.questions)):
        #All questions answered, redirect to survey-complete
        return redirect("/survey-complete")
    else:
        #Proceed to next question
        return redirect(f'/question/{len(response)+1}')



@app.route('/question/<int:qid>')
def question_page(qid):
    '''Display the next un-answered question'''
    response = session.get(RESPONSE_KEY)

    if len(response)==len(survey.questions):
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
    return render_template("survey_complete.html", survey_title=survey.title, survey_questions=survey.questions)
  