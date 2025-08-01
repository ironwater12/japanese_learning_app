import gradio as gr

from functions import new_question, check_answer, toggle_mode_libre, toggle_switch_base_dict, reset_score, toggle_no_mistake
from data import hiragana_dict, question_hiragana


with gr.Blocks(css="""
    #quiz-container {
        /*max-width: 1000px;*/
        max-width: 60%;
        width: 100%;
        padding: 5vw;
        margin: auto; 
        padding: 30px; 
        background: #f9f9f9; 
        border-radius: 12px; 
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    #title {
        text-align: center;
        font-size: 2.8em;     
        font-weight: 700;
        margin-bottom: 25px;
        color: #2c3e50;
    }
    #settings_row {
        max-width: 60%;
        width: 100%;
        padding: 5vw;
        margin: auto; 
        padding: 30px; 
        display: flex;
        justify-content: center;
        margin-bottom: 25px;
    }
    #question_markdown {
        text-align: center;
        font-size: 3em;       
        margin-bottom: 20px;
        color: #34495e;
        min-height: 110px;
    }
    #options_radio {
        display: flex !important;
        flex-direction: column !important;
        gap: 12px;
    }
    #options_radio > label {
        font-size: 1.4em;      
        margin-bottom: 12px;
        cursor: pointer;
    }
    #result_box {
        text-align: center;
        font-weight: 700;
        margin-top: 18px;
        min-height: 40px;
        font-size: 1.3em;
    }
    #score_box {
        text-align: center;
        margin-top: 15px;
        font-size: 1.3em;
        color: #34495e;
    }
    #max_score {
        text-align: center;
        margin-top: 15px;
        font-size: 1.3em;
        color: #34495e;
    }
    #reset_score_btn {
        width: 120px;        
        height: 30px;
        text-align: center;
        /*margin: 0 auto;*/  /*Not used, can be used to center the reset button*/
        margin-left: auto;
        margin-right: 0;       
        background-color: #FF4136;
        color: white;
    }
    #reset_score_btn:hover{
        background-color: #E03A30;
    }
    #buttons_row {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 30px;
    }
    #buttons_row button {
        width: 140px;        
        height: 50px;          
        font-weight: 700;
        font-size: 1.2em;      
        border-radius: 12px;
        padding: 0;
        cursor: pointer;
        border: none;
        background-color: #2980b9;
        color: white;
        transition: background-color 0.3s ease;
    }
    #buttons_row button:disabled {
        background-color: #95a5a6;
        cursor: not-allowed;
    }
    #buttons_row button:hover:not(:disabled) {
        background-color: #3498db;
    }
""") as interface:
    
    # Title
    gr.Markdown("## 🏯 Japanese Quiz 🏯", elem_id="title")

    # Settings
    with gr.Row(elem_id="settings_row"):
        mode_libre = gr.Checkbox(label="📝 Type your answer", value=False)
        mode_full_words = gr.Checkbox(label="🔡 Full words", value=False)
        mode_switch_language = gr.Checkbox(label="🔁 Switch language", value=False)
        mode_no_mistake = gr.Checkbox(label="❌✍️ No mistake", value=False)

    # Quiz
    with gr.Row(elem_id="quiz-container"):

        # Question and user input
        question_text = gr.Markdown("", elem_id="question_markdown")
        answer_options = gr.Radio(choices=[], label="", elem_id="options_radio")
        text_input = gr.Textbox(placeholder="Write your answer: ", label="", visible=False, interactive=True)
        result = gr.Markdown("", elem_id="result_box")
        
        # Results and score
        with gr.Column():
            reset_score_btn = gr.Button("Reset Score", elem_id="reset_score_btn")
            
            score_box = gr.Markdown("", elem_id="score_box")
            max_score = gr.Markdown(f"**🏆 Max score: 0**", visible=False, elem_id="max_score")

        # Validate and next button    
        with gr.Row(elem_id="buttons_row"):
                check_btn = gr.Button("☑️ Validate", elem_id="check_btn")
                next_btn = gr.Button("➡️ Next", elem_id="next_btn")

        # Initial state
        next_btn.disabled = True
        dict_used = gr.State(hiragana_dict)
        question_used = gr.State(question_hiragana)
        current_question = gr.State({"question": "", "all-answers": [], "right_answer": ""})
        score = gr.State({"correct": 0, "total": 0, "max_score": 0})

        # Toggle different setting modes
        mode_libre.change(fn=toggle_mode_libre, 
                          inputs=mode_libre,
                          outputs=[result, text_input, answer_options])
        
        mode_switch_language.change(fn=toggle_switch_base_dict,
                               inputs=[mode_switch_language, mode_full_words, current_question, score],
                               outputs=[dict_used, question_used, question_text, answer_options, text_input, result, score_box, check_btn, next_btn, result])
        
        mode_full_words.change(fn=toggle_switch_base_dict,
                               inputs=[mode_switch_language, mode_full_words, current_question, score],
                               outputs=[dict_used, question_used, question_text, answer_options, text_input, result, score_box, check_btn, next_btn, result])
        
        mode_no_mistake.change(fn=toggle_no_mistake,
                               inputs=[mode_no_mistake, score],
                               outputs=[score_box, max_score])
        
        # Buttons click
        reset_score_btn.click(fn=reset_score,
                              inputs=score,
                              outputs=score_box)
                
        check_btn.click(fn=check_answer, 
                        inputs=[answer_options, text_input, mode_libre, mode_no_mistake, current_question, score], 
                        outputs=[question_text, answer_options, result, score_box, check_btn, next_btn, result, max_score])
        
        next_btn.click(fn=new_question, 
                       inputs=[dict_used, question_used, current_question, score], 
                       outputs=[question_text, answer_options, text_input, result, score_box, check_btn, next_btn, result])

        # Interface setup
        interface.load(fn=new_question, 
                       inputs=[dict_used, question_used, current_question, score], 
                       outputs=[question_text, answer_options, text_input, result, score_box, check_btn, next_btn, result])


if __name__ == "__main__":
    interface.launch()  #share=True)