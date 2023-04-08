import random
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def load_vocab():
    """Load the vocabulary list from file."""
    with open('nikkei_vocab.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    vocab = []
    for word in data.values():
        vocab.append({
            'word': word['word'],
            'meaning': word['meaning'],
            'reading': word['reading']
        })
    return vocab
    
# Define the quiz data dictionary
quiz_data = {
    'remaining': load_vocab() or [], # Set default value to an empty list
    'completed': [],
    'current_vocab': None
}

# Define the current score dictionary
current_score = {
    'correct': 0,
    'incorrect': 0
}

@app.route('/')
def home():
    """Render the home page."""
    current_score = {'correct': 0, 'incorrect': 0}
    return render_template('home.html', current_score=current_score)

@app.route('/vocab_list')
def vocab_list():
    """Render the vocabulary list page."""
    vocab = load_vocab()
    return render_template('vocab_list.html', vocab=vocab)

@app.route('/quiz', methods=['GET', 'POST'])
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    """Render the quiz page."""
    if request.args.get('restart'):
        # Reset the quiz state and score
        quiz_data['remaining'] = load_vocab() or []
        quiz_data['completed'] = []
        quiz_data['current_vocab'] = None
        current_score['correct'] = 0
        current_score['incorrect'] = 0
        return redirect(url_for('quiz'))

    # Check if quiz is complete
    if len(quiz_data.get('remaining', [])) == 0:
        # Quiz is complete
        return render_template('quiz_complete.html', score=current_score)

    if request.method == 'POST':
        # Check if answer is correct
        answer = request.form.get('choice')
        if quiz_data.get('current_vocab') and quiz_data['current_vocab'].get('meaning') and answer == quiz_data['current_vocab']['meaning']:
            # Answer is correct, add to completed list and update score
            quiz_data['completed'].append(quiz_data['current_vocab'])
            if quiz_data['current_vocab'] in quiz_data['remaining']:
                quiz_data['remaining'].remove(quiz_data['current_vocab'])
            current_score['correct'] += 1
        else:
            # Answer is incorrect, update score
            current_score['incorrect'] += 1

    # Get a new random vocabulary word from the remaining list
    if quiz_data.get('remaining'):
        current_vocab = random.choice(quiz_data['remaining'])
        # Remove the current_vocab from the remaining list
        quiz_data['remaining'].remove(current_vocab)

        # Set the current_vocab in quiz_data
        quiz_data['current_vocab'] = current_vocab

        # Get three random choices for the multiple choice answers
        choices = [current_vocab]
        vocab_remaining = [v for v in quiz_data['remaining'] if v != current_vocab]
        for i in range(3):
            if vocab_remaining:
                choice = random.choice(vocab_remaining)
                if choice not in choices:
                    vocab_remaining.remove(choice)
                    choices.append(choice)

        # Shuffle the choices
        random.shuffle(choices)

        # Pass the data to the template
        return render_template('quiz.html', vocab=current_vocab, choices=choices, score=current_score)
    else:
        return render_template('quiz_complete.html', score=current_score)

if __name__ == '__main__':
    app.run(debug=True)