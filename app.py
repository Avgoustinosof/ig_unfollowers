from flask import Flask, render_template, request
import instaloader
import os
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'sessions'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_unfollowers(session_file_path):
    L = instaloader.Instaloader()
    username = os.path.basename(session_file_path).replace('.session', '')

    # Load session from uploaded file
    L.load_session_from_file(username, session_file_path)

    profile = instaloader.Profile.from_username(L.context, username)
    followees = set(user.username for user in profile.get_followees())
    followers = set(user.username for user in profile.get_followers())

    unfollowers = followees - followers
    return sorted(unfollowers)

@app.route('/', methods=['GET', 'POST'])
def index():
    unfollowers = []
    error = None
    if request.method == 'POST':
        if 'session_file' not in request.files:
            error = "No file uploaded"
        else:
            file = request.files['session_file']
            if file.filename.endswith('.session'):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)

                try:
                    unfollowers = get_unfollowers(filepath)
                except Exception as e:
                    error = f"Error: {str(e)}"

                # Optional: Clean up file
                time.sleep(1)
                os.remove(filepath)
            else:
                error = "Please upload a valid .session file"
    return render_template('index.html', unfollowers=unfollowers, error=error)

if __name__ == '__main__':
    app.run(debug=True)
