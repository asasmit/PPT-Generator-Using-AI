import gradio as gr
import os
from app import rag_engine
from app.slide_generator import create_ppt

import traceback

def generate_lesson_plan(curriculum_pdf, grade, subject, topic, subtopic):
    print("generate_lesson_plan_hit")

    if not curriculum_pdf:
        return "Please upload the curriculum.", "", "", None

    try:
        # creating vectorstore
        pdf_path = curriculum_pdf
        index_name = os.path.basename(pdf_path).split(".")[0]

        docs = rag_engine.load_and_split_pdf(pdf_path)
        vectordb = rag_engine.build_vectorstore(docs, index_name)
        result = rag_engine.query_vectorstore(subject, topic, subtopic, grade, vectordb)

        if "error" in result:
            return f"Error: {result['error']}", result.get("raw", ""), "", None

        slides = result.get("slides", [])
        if not slides:
            return "No slides found in the response.", "", "", None

        title_slide = next((s for s in slides if s["type"] == "title"), None)
        content_slides = [s for s in slides if s["type"] == "content"]
        quiz_slide = next((s for s in slides if s["type"] == "quiz"), None)

        # Title
        title = title_slide.get("title", "Generated Lesson Title") if title_slide else "Generated Lesson Title"

        # Body: using loop for generating body content
        body_parts = []
        for slide in content_slides:
            slide_title = slide.get("title", "")
            points = slide.get("points", [])
            bullet_points = "\n".join([f" {p}" for p in points])
            body_parts.append(f"{slide_title}\n{bullet_points}\n")
        body = "\n".join(body_parts)

        # Quiz formatting for gradio interfce (not for ppt)
        quiz_str = ""
        if quiz_slide:
            quiz = quiz_slide.get("quiz", {})
            if quiz.get("type") == "mcq":
                options = "\n".join([f"- {opt}" for opt in quiz.get("options", [])])
                quiz_str = f"**Question:** {quiz['question']}\n\n{options}"
            elif quiz.get("type") == "fill-in-the-blank":
                quiz_str = f"**Fill in the blank:** {quiz['question']}"

        # from slide_generator.py
        pptx_path = create_ppt(result)

        return title, body, quiz_str, pptx_path

    except Exception as e:
        return f"Exception occurred: {str(e)}", "", "", None

    except Exception as e:
        print("Exception occurred:")
        traceback.print_exc()
        return f"Error: {str(e)}", "", "", None


with gr.Blocks(title="AI Lesson Plan Generator") as demo:
    gr.Markdown("## AI Lesson Plan Generator")

    with gr.Row():
        curriculum_pdf = gr.File(label="Upload Curriculum PDF", file_types=[".pdf"])
        grade = gr.Textbox(label="Grade/Class", placeholder="e.g., 7")

    with gr.Row():
        subject = gr.Textbox(label="Subject", placeholder="e.g., Science")
        topic = gr.Textbox(label="Topic/Chapter", placeholder="e.g., Temperature")
        subtopic = gr.Textbox(label="Subtopic", placeholder="e.g., Measurse heat")

    submit_btn = gr.Button("Generate Lesson Plan")

    with gr.Row():
        title_output = gr.Textbox(label="Lesson Title", interactive=False)
        body_output = gr.Textbox(label="Lesson Body", lines=5, interactive=False)

    quiz_output = gr.Markdown(label="Quiz")

    pptx_output = gr.File(label="Download Slides", interactive=False)

    submit_btn.click(
        fn=generate_lesson_plan,
        inputs=[curriculum_pdf, grade, subject, topic, subtopic],
        outputs=[title_output, body_output, quiz_output, pptx_output]
    )

if __name__ == "__main__":
    demo.launch(share=True)