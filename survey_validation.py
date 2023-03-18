def make_survey_key(resp_key, survey_code):
    '''Returns a new key, combining the response key and survey code'''
    return f'{resp_key}_{survey_code}'

def is_complete(q, r):
    '''
    Returns bool of if a survey is complete
    by comparing the amount of quesitons in a survey (q) to the 
    total received responses (r)
    
    if (q and r) are the same length, return true
    else return false
    '''
    if(len(q) == len(r)):
        return True
    return False