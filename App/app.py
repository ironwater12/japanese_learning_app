### Setup

# import
import gradio as gr
import json

# local import
from functions import new_question, check_answer, toggle_mode_libre, toggle_switch_base_dict, reset_score, toggle_no_mistake

# CSS loading
with open("styles.css", "r", encoding="utf-8") as f:
    css_code = f.read()

# translation data loading
with open("app_data.json", "r", encoding="utf-8") as f:
    app_data = json.load(f)

hiragana_dict = app_data['translation_data']['hiragana']
question_hiragana = app_data['question']['question_hiragana']


### App code

with gr.Blocks(css=css_code) as interface:

    with gr.Column(elem_id="app-container"):

        # Title
        gr.Markdown("## 🏯 Japanese Quiz 🏯", elem_id="title")

        # Settings
        with gr.Row(elem_id="settings_row"):
            mode_libre = gr.Checkbox(label="📝 Type your answer", value=False)
            mode_full_words = gr.Checkbox(label="🔡 Full words", value=False)
            mode_switch_language = gr.Checkbox(label="🔁 Switch language", value=False)
            mode_no_mistake = gr.Checkbox(label="❌✍️ No mistake", value=False)

        # Quiz content
        with gr.Column(elem_id="quiz-box"):
            question_text = gr.Markdown("", elem_id="question_markdown", elem_classes="question_text")
            answer_options = gr.Radio(choices=[], label="", elem_id="options_radio")
            text_input = gr.Textbox(placeholder="Write your answer:", label="", visible=False, interactive=True, elem_id="text_input_box")
            result = gr.Markdown("", elem_id="result_box")

            # Score section
            with gr.Row(elem_id="score_section"):
                score_box = gr.Markdown("", elem_id="score_box")
                max_score = gr.Markdown(f"**🏆 Max score: 0**", visible=False, elem_id="max_score")
                reset_score_btn = gr.Button("Reset Score", elem_id="reset_score_btn")

        # Action buttons
        with gr.Row(elem_id="buttons_row"):
            check_btn = gr.Button("☑️ Validate", elem_id="check_btn")
            next_btn = gr.Button("➡️ Next", elem_id="next_btn")

        # States
        next_btn.disabled = True
        dict_used = gr.State(hiragana_dict)
        question_used = gr.State(question_hiragana)
        current_question = gr.State({"question": "", "all-answers": [], "right_answer": ""})
        score = gr.State({"correct": 0, "total": 0, "max_score": 0})

        # Event logic
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
        
        reset_score_btn.click(fn=reset_score,
                              inputs=score,
                              outputs=score_box)
        
        check_btn.click(fn=check_answer,
                        inputs=[answer_options, text_input, mode_libre, mode_no_mistake, current_question, score],
                        outputs=[question_text, answer_options, result, score_box, check_btn, next_btn, result, max_score])
        
        next_btn.click(fn=new_question,
                       inputs=[dict_used, question_used, current_question, score],
                       outputs=[question_text, answer_options, text_input, result, score_box, check_btn, next_btn, result])
        
        interface.load(fn=new_question,
                       inputs=[dict_used, question_used, current_question, score],
                       outputs=[question_text, answer_options, text_input, result, score_box, check_btn, next_btn, result])

if __name__ == "__main__":
    interface.launch()