from flask import Flask, jsonify, request, send_file
import requests
import json
import os
from flask_cors import CORS
from Markdown2docx import Markdown2docx
app = Flask(__name__)
CORS(app)
# Initializing the App and Gemini API
working_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = f"{working_dir}/config.json"
config_data = json.load(open(config_file_path))
GOOGLE_API_KEY = config_data["GOOGLE_API_KEY"]
class RolePlayCreator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + self.api_key
    @staticmethod
    def construct_prompt(data):
        prompt_parts = [
            "Generate a role-play exercise with the following specifications:\n",
            f"**Industry:** {data['industry']}\n",
            f"**Learning Objective:** {data['learningObjective']}\n",
            "**Roles:**\n"
        ]
        prompt_parts.extend([f"- {role}\n" for role in data['roles']])
        prompt_parts.append("**Required Skills:**\n")
        prompt_parts.extend([f"- {skill}\n" for skill in data['skills']])
        if 'complexity' in data:
            prompt_parts.append(f"**Complexity:** {data['complexity']}\n")
        if 'experience' in data:
            prompt_parts.append(f"**Experience Level:** {data['experience']}\n")
        if 'industryContext' in data:
            prompt_parts.append(f"**Industry Context:** {data['industryContext']}\n")
        if 'scenarioSettings' in data:
            prompt_parts.append(f"**Scenario Settings:** {data['scenarioSettings']}\n")
        return ''.join(prompt_parts)
rolePlayCreator_service = RolePlayCreator(api_key=GOOGLE_API_KEY)
@app.route('/role_play_creator', methods=['POST'])
def rolePlayCreator():
    try:
        headers = {'Content-Type': 'application/json'}
        request_data = request.json
        prompt = rolePlayCreator_service.construct_prompt(request_data)
        generation_config = {
            'temperature': 0.9,
            'topK': 1,
            'topP': 1,
            'maxOutputTokens': 2048,
            'stopSequences': []
        }
        request_body = {
            'contents': [{'parts': [{'text': prompt}]}],
            'generationConfig': generation_config
        }
        response = requests.post(rolePlayCreator_service.base_url, json=request_body, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        rolePlayExercie = [candidate['content']['parts'][0]['text'] for candidate in response_data['candidates']]
        return jsonify(rolePlayExercie)
    except Exception as e:
        print("Service Exception:", str(e))
        raise Exception("Error in getting response from Gemini API")
@app.route('/download-docx', methods=['POST'])
def download_docx():
    markdown_content = request.json['markdown_content']
    file_path = working_dir+"/RolePlay.md"
    create_md_file(markdown_content, file_path)
    # output = aw.Document()
    # output.remove_all_children()
    project = Markdown2docx(working_dir+"/RolePlay")
    project.eat_soup()
    project.save()
    return send_file("RolePlay.docx", as_attachment=True, download_name="role-play.docx", mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
def create_md_file(text_content, file_path):
    try:
        # Open the file in write mode
        with open(file_path, 'w') as f:
            # Write the text content to the file
            f.write(text_content)
        print(f"Markdown file '{file_path}' created successfully.")
    except Exception as e:
        print("Error:", str(e))
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")