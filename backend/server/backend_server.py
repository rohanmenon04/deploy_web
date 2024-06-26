from flask import Flask, request, jsonify, send_file, render_template, session
from flask_cors import CORS
from flask_session import Session
import os
import json
import requests
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management
CORS(app)

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'  # Store sessions in the filesystem
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True  # To protect the cookie from being tampered
app.config['SESSION_KEY_PREFIX'] = 'myapp_'

# Initialize the session
Session(app)

# In-memory data store
player_data = {}

def date_suffix(day: int) -> str:
    if 4 <= day <= 20 or 24 <= day <= 30:
        return "th"
    else:
        return ["st", "nd", "rd"][day % 10 - 1]

def format_date(date: str) -> str:
    date_parts = date.split()
    month, day, year = date_parts[0].split('/')
    hour, minute, second = date_parts[1].split(':')
    if date_parts[2] == "PM" and int(hour) != 12:
        hour = int(hour) + 12
    date = datetime.datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute), second=int(second))
    if datetime.datetime.now() - date < timedelta(days=1):
        format = "Today at %H:%M"
    else:
        format = f"%d{date_suffix(int(day))} %B %Y"
    return date.strftime(format)

def change_to_datetime(date: str) -> datetime:
    input_format = "%m/%d/%Y %I:%M:%S %p"
    date_obj = datetime.datetime.strptime(date, input_format)
    return date_obj

def cleaning_dates(INP):
    input_format = "%Y-%m-%dT%H:%M:%S.%f"
    output_format = "%d/%m/%Y %H:%M"
    date_obj = datetime.datetime.strptime(INP, input_format)
    formatted_date = date_obj.strftime(output_format)
    return formatted_date

def extract_top_scores(user_scores):
    top_scores = sorted(user_scores, key=lambda x: x['score'], reverse=True)
    return top_scores

OPENAI_KEY = os.getenv('OPENAI_KEY')
if not OPENAI_KEY:
    raise ValueError("No OpenAI API Key Found")
API_URL = 'https://api.openai.com/v1/chat/completions'

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {OPENAI_KEY}'
}

system_prompt = """
You are a helpful and knowledgeable assistant for the game "Lines." Your role is to provide players with useful information, tips, and strategies to help them improve their gameplay. NEVER DEVIATE FROM SPEAKING ABOUT THE GAME. Here is what you should keep in mind:

1. Game Overview:
   - Explain the basic principle of the game: "Lines" involves avoiding lines coming at you from various angles. The goal is to survive as long as possible to earn points.
   - Mention the control mechanism: The player controls their character using the mouse.

2. Difficulty Levels:
   - Easy: Fewer lines, slower movement.
   - Medium: More lines, faster movement.
   - Hard: Maximum number of lines, fastest movement.

3. Gameplay Strategies:
   - Emphasize the importance of observing patterns, such as lines always converging into the middle of the screen.
   - Suggest staying near the edges of the screen when lines are sparse and moving towards the middle only when necessary to avoid collisions.
   - Recommend practicing smooth and controlled mouse movements to improve reaction time and accuracy.

4. Scoring and Progression:
   - Explain how points are accumulated over time based on survival duration.
   - Highlight any milestones or achievements players can aim for to stay motivated.

5. Troubleshooting and Common Issues:
   - Provide solutions for common problems, such as lagging or unresponsive controls.
   - Offer tips for improving performance, like adjusting game settings or ensuring a stable internet connection.

6. Encouragement and Motivation:
   - Encourage players by recognizing their progress and offering positive reinforcement.
   - Suggest setting personal goals and gradually increasing difficulty to improve skills.

7. FAQs:
   - Prepare answers for frequently asked questions, such as "How do I pause the game?" or "Can I customize my character?"

8. Feedback and Support:
   - Invite players to provide feedback on the game and report any bugs or issues they encounter.
   - Direct them to additional resources or support channels if needed.

By providing clear, concise, and helpful responses, you aim to enhance the players' experience and help them enjoy "Lines" to the fullest. 
Keep responses as short as possible while capturing all the meaning that is necessary. Only elaborate if it is absolutely necessary.
Do not provide tactics for the game or game controls unless that is what the user is asking for explicitly.
"""

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_data = response.json()
        bot_message = response_data['choices'][0]['message']['content']
        return jsonify({"response": bot_message})
    else:
        return jsonify({"error": f"Request failed with status code {response.status_code}"}), 500

@app.route('/save_playerdata', methods=['POST'])
def save_playerdata():
    data = request.get_json()
    time = datetime.datetime.now().isoformat()
    username = data['username']
    data['time'] = time

    try:
        requests.get(f"http://dreamlo.com/lb/LhmhwO4BDUmmx1c6mpVcJQaIOAKMEaV0ydc-7N3WQrow/add/{username}/{data['score']}")
    except:
        if username not in player_data:
            player_data[username] = []
        player_data[username].append(data)
        session['player_data'] = player_data
        return jsonify({"message": "Data saved successfully, to session but not sent to Dreamlo"}), 200

    if username not in player_data:
        player_data[username] = []
    player_data[username].append(data)
    session['player_data'] = player_data

    return jsonify({"message": "Data saved successfully"}), 200

@app.route('/api/leaderboard-all-time', methods=['GET'])
def get_all_time_leaderboard():
    response = requests.get("http://dreamlo.com/lb/65bcfe73778d3df3f065b921/json")
    leaderboard_data = response.json()
    leaderboard_all_time = leaderboard_data['dreamlo']['leaderboard']['entry']
    for entry in leaderboard_all_time:
        entry['date'] = format_date(entry['date'])
    return jsonify(leaderboard_all_time)

@app.route('/api/leaderboard-24h', methods=['GET'])
def get_24h_leaderboard():
    response = requests.get("http://dreamlo.com/lb/65bcfe73778d3df3f065b921/json")
    leaderboard_data = response.json()
    leaderboard_all_time = leaderboard_data['dreamlo']['leaderboard']['entry']
    leaderboard_24h = [
        entry for entry in leaderboard_all_time
        if datetime.datetime.now() - change_to_datetime(entry["date"]) <= timedelta(days=1)
    ]
    for entry in leaderboard_24h:
        entry["date"] = format_date(entry["date"])
    return jsonify(leaderboard_24h)

@app.route('/api/get-graph-data', methods=['GET'])
def get_top_scores():
    username = request.args.get('username')
    player_data = session.get('player_data', {})
    if not username or username not in player_data:
        return jsonify({"labels": [], "values": []})

    try:
        user_scores = player_data[username]
        top_scores = extract_top_scores(user_scores)
        if not top_scores:
            chart_data = {
                "labels": [],
                "values": []
            }
            return jsonify(chart_data)

        labels = [cleaning_dates(score['time']) for score in top_scores]
        values = [score['score'] for score in top_scores]
        chart_data = {
            "labels": labels,
            "values": values
        }
        return jsonify(chart_data)
    except Exception as e:
        app.logger.error(f"Error in /api/get-graph-data: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

def delete_from_playerdata(username, score_to_delete):
    if username in player_data:
        player_data[username] = [entry for entry in player_data[username] if entry['score'] != int(score_to_delete)]
    session['player_data'] = player_data

@app.route('/api/delete-score', methods=['POST'])
def delete_score():
    data = request.json
    score_to_delete = data.get('score')
    username = data.get('username')

    if not score_to_delete or not username:
        return jsonify({"error": "No score or username provided"}), 400

    delete_from_playerdata(username, score_to_delete)

    return jsonify({"message": "Score deleted successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)  # Ensure this port matches the Render service port
