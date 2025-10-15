import os

from openai import OpenAI
from dotenv import load_dotenv
import gradio as gr

# Load environment variables from the .env file
load_dotenv()

# Retrieve the OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

print("OpenAI API Key loaded successfully.")
# Let's view the first few characters to confirm it's loaded (DO NOT print the full key)
print(f"Key starts with: {openai_api_key[:10]}...")

# Configure the OpenAI Client using the loaded key
openai_client = OpenAI(api_key=openai_api_key)
print("OpenAI client configured.")

explanation_levels = {
    1: "like I'm five",
    2: "like I'm a high school student",
    3: "like I'm a college student",
    4: "like I'm a graduate student",
    5: "like I'm an expert in the field"
}

def stream_ai_tutor_response_with_level(user_question, explanation_level):
    
    level_desc = explanation_levels.get(explanation_level, "clear and concise")
    
    system_prompt = f"Your are a helpful AI tutor. Explain the following concepts {level_desc}"
    
    try:
        stream = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content":system_prompt},
                {"role": "user", "content": user_question}
            ],
            temperature=0.7,
            stream=True
        )
        
        full_response = ""
        
        #Now we iterate through the stream and print each chunk as it arrives
        for chunk in stream:
            if 'choices' in chunk and len(chunk['choices']):
                text_chunk = chunk.choices[0].delta.content
                
                #Add this chucnk to the full response
                full_response += text_chunk
                
                #yeild makes the text appear to be typing in real time
                yield full_response
                
    except Exception as e:
        print(f"An error occurred: {e}")
        yield f"Sorry, something went wrong {e}"
        
        
# Next we make the Gradio UI

ai_tutor_interface_slider = gr.Interface(
    fn=stream_ai_tutor_response_with_level,
    inputs=[
        gr.Textbox(lines=3, placeholder="Ask me anything", label="Your Question"),
        gr.Slider(
            minimum=1,
            maximum=5,
            step=1,
            label="Explanation Level",
            value=3,
        ),
        ],
    outputs= gr.Textbox(label="AI Tutor Response (streaming)", container=True, lines=10),
    title="Advanced AI Tutor with Explanation Levels",
    description="Ask questions and get explanations tailored to your level of understanding.",
    allow_flagging="never",
)

print("Launching Gradio interface...")
ai_tutor_interface_slider.launch()