# 📚 Lesson Plan PPT Generator

An AI-powered Gradio web application that generates PowerPoint presentations from structured JSON files. It automatically pulls relevant images using the SerpAPI Google Images search and adds content, titles, and quiz slides to your deck.

---

## 🚀 Features

- 📝 Upload a lesson plan JSON file
- 🖼️ Auto-fetch relevant images via SerpAPI
- 🎯 Supports:
  - Title slides
  - Content slides with bullet points
  - Quiz slides (MCQs and Fill-in-the-blanks)
- 💾 Download ready-to-use `.pptx` presentations

---

## 🖼 Sample Slide Types

1. **Title Slide**
2. **Content Slide with Bullet Points**
3. **Quiz Slide (with answer on separate slide)**

---

## 🧪 Sample JSON Format

```json
{
  "slides": [
    {
      "type": "title",
      "title": "Photosynthesis",
      "subtitle": "Understanding how plants make food",
      "keyword": "photosynthesis diagram"
    },
    {
      "type": "content",
      "title": "Key Points",
      "points": [
        "Takes place in chloroplasts",
        "Uses sunlight, CO2, and water",
        "Produces oxygen and glucose"
      ],
      "keyword": "chloroplast"
    },
    {
      "type": "quiz",
      "title": "Photosynthesis Quiz",
      "quiz": {
        "type": "mcq",
        "question": "What is a by-product of photosynthesis?",
        "options": ["Oxygen", "Carbon Dioxide", "Water", "Nitrogen"],
        "answer": "Oxygen"
      }
    }
  ]
}
```

---

## 🛠 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/lesson-plan-ppt-generator.git
   cd lesson-plan-ppt-generator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your [SerpAPI](https://serpapi.com/) key:
   ```env
   SERP_API_KEY=your_api_key_here
   ```

---

## 🧠 Usage

```bash
python app.py
```

This will launch the Gradio interface in your browser. Upload your JSON file and download your generated PPT!

---

## 📦 Requirements

- `gradio`
- `python-pptx`
- `requests`
- `python-dotenv`

Install all using:
```bash
pip install gradio python-pptx requests python-dotenv
```

---

## 📂 Output

A downloadable `.pptx` file with auto-generated slides and relevant images.

---

## 🙌 Credits

Created by [Your Name]. Powered by:
- [Gradio](https://gradio.app/)
- [SerpAPI](https://serpapi.com/)
- [python-pptx](https://python-pptx.readthedocs.io/)

---

## 📄 License

MIT License
