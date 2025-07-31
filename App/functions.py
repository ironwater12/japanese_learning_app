import gradio as gr
import random

from data import hirukana_dict, reverse_hirukana_dict, translation_dict, reverse_translation_dict, question_hirukana, question_reverse_hirukana, question_translation, question_reverse_translation


def reset_score(score):

    """
    Reset the score displayed

    Args:
        score (dict): 

    Returns:
        score (str): string to display with the current score
    """

    score['correct'] = 0
    score['total'] = 0

    return f"Score: {score['correct']} / {score['total']}"


def make_question(base_dict, question_used, num_choice=4):

    """
    Select a random character or word and its traduction along with several wrong traductions to create a question

    Args:
        base_dict (dict): The dict of character/word and traductions to use for questions
        question_used (str): The base text of the question
        num_choice (int): The number of choice for multiple choice mode

    Returns:
        question (str): The full text of the question to show on the interface
        all_answers (list): The list of all suggested answers
        right_answer (str): The correct answer
    """

    character = random.choice(list(base_dict.keys()))
    question = question_used + "<br> **" + character + "**"
    right_answer = base_dict[character]
    other_keys = {k: v for k, v in base_dict.items() if k!= character}

    all_answers = [right_answer]
    all_answers += random.sample(list(other_keys.values()), num_choice-1)
    random.shuffle(all_answers)

    return question, all_answers, right_answer


def new_question(base_dict, question_used, current_question, score):

    """
    Create a new question and return a state for the interface

    Args:
        base_dict (dict): The dict of character/word and traductions to use for questions
        question_used (str): The base text of the question
        current_question (dict): 
        score (dict): 

    Returns:
        tuple:
            - question text
            - empty string for text input
            - empty string for result
            - score string
            - validate button with interactive state turned on (can be clicked)
            - next button with interactive state turned off (can't be clicked)
            - result message turned to non visible

    """

    question, all_answers, right_answer = make_question(base_dict, question_used)
    current_question["question"] = question
    current_question["all_answers"] = all_answers
    current_question["right_answer"] = right_answer

    return (question, 
            gr.update(choices=all_answers, value=None),
            "",  # vide text_input
            "",  # vide result
            f"Score: {score['correct']} / {score['total']}",
            gr.Button(interactive=True),  # Validate button is activate when a new question is create
            gr.Button(interactive=False),    # Next button is deactivate and will be turned on only when an answer is chosen/written 
            gr.update(visible=False)  # Result message is hidden at the start
    )


def check_answer(selected_option, text_answer, mode_libre, mode_no_mistake, current_question, score):

    """
    Checks whether the user's answer is correct based on the quiz mode

    Args:
        selected_option (str): The selected radio button answer (in multiple-choice mode)
        text_answer (str): The answer typed by the user (in free-answer mode)
        mode_libre (bool): Whether free-answer mode is active
        mode_no_mistake (bool): Whether the no-mistake mode is active (score reset when a mistake is made)
        current_question (dict): 
        score (dict):

    Returns:
        tuple:
            - question text
            - all choice of answers updated with the current question and associated answers
            - result string message
            - score string
            - validate button with interactive state
            - next button with interactive state
            - result message with visibility state
            - max score string
    """

    if not (selected_option or text_answer):

        return (current_question["question"], 
                gr.update(choices=current_question["all_answers"]), 
                "Select an answer",
                f"Score: {score['correct']} / {score['total']}",
                gr.Button(interactive=True),  # Valider reste activé
                gr.Button(interactive=False),    # Suivant désactivé
                gr.update(visible=False),
                f"**🏆 Max score: {score['max_score']}**"

        )
    
    score["total"] += 1
    
    if mode_libre:
        right_answers = current_question['right_answer'].split('/')
        correct = False
        for right_answer in right_answers:
            correct = (text_answer.strip().lower() == right_answer.strip().lower()) or (text_answer.split('(')[0].strip().lower() == right_answer.split('(')[0].strip().lower())
    else:
        correct = selected_option == current_question["right_answer"]

    if correct:
        score["correct"] += 1
        message = "✅ Correct !"

        if mode_no_mistake:
            if score['correct'] > score['max_score']:
                score['max_score'] = score['correct'] 
    
    else:
        message = f"❌ Wrong, it was : **{current_question['right_answer']}**"

        if mode_no_mistake:
            if score['correct'] > score['max_score']:
                score['max_score'] = score['correct']
            reset_score(score)
            message += "<br> Your score was reset"
            

    return (current_question["question"], 
            gr.update(choices=current_question["all_answers"]), 
            message,
            f"Score: {score['correct']} / {score['total']}",
            gr.Button(interactive=False),   # Désactiver Valider
            gr.Button(interactive=True),   # Activer Suivant
            gr.update(visible=True),
            f"**🏆 Max score: {score['max_score']}**"
)


def toggle_mode_libre(mode):

    """
    Function called when free text mode is toggled on

    Args:
        mode (bool): state of the free text mode toggle

    Returns:
        result (str): empty string for result (reset result)
        text_input: update the visibility state of text_input (free text) depedending on the mode
        answer_options: update the visibility state of answer_options (multiple choice box) depedending on the mode
    """

    if mode:
        return "", gr.update(visible=True), gr.update(visible=False)
    else:
        return "", gr.update(visible=False), gr.update(visible=True)
    

def toggle_switch_base_dict(mode_lang, mode_words, current_question, score):

    """
    Function called when the translation dict to use is changed (either the mode is change from characters to words or the language is switched)

    Args:
        mode_lang (bool): state of the switch language mode, True when the mode is toggled on and language is switched to fr->jp
        mode_words (bool): state of the full words mode, True when the mode is toggled on and full words need to be translated
        current_question (dict): 
        score (dict):

    Returns:
        base_dict (dict):  The dict of character/word and traductions to use for questions
        base_question (str): The base text of the question
        new_question outputs (check new_question function documentation)
    """

    if mode_lang:
        if mode_words:
            base_dict = reverse_translation_dict
            base_question = question_reverse_translation
        else:
            base_dict = reverse_hirukana_dict
            base_question = question_reverse_hirukana
    else:
        if mode_words:
            base_dict = translation_dict
            base_question = question_translation
        else:
            base_dict = hirukana_dict
            base_question = question_hirukana

    return base_dict, base_question, *new_question(base_dict, base_question, current_question, score)  # a new question is generated when the mode is changed
            

def toggle_no_mistake(mode_no_mistake, score):

    """
    Function called when the no mistake mode is toggled on

    Args:
        mode_no_mistake (bool): state of the no mistake mode, True when the mode is toggled on
        score (dict): 

    Returns:
        new_score (str): score text that is reset automatically when the no mistake mode is toggled on
        max_score: update the visibility of the max score display (visible only in no mistake mode)
    """

    new_score = reset_score(score)

    if mode_no_mistake:
        return new_score, gr.update(visible=True)
    else:
        return new_score, gr.update(visible=False)