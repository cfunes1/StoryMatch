# app.py
from flask import Flask, render_template, jsonify, request
import pandas as pd
import random
from pathlib import Path

app = Flask(__name__)

def try_read_csv(filename):
    """Try reading CSV with different encodings"""
    encodings = ['utf-8', 'cp1252', 'iso-8859-1', 'latin1']
    
    for encoding in encodings:
        try:
            return pd.read_csv(filename, encoding=encoding)
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error reading {filename}: {str(e)}")
            return None
    
    print(f"Failed to read {filename} with any of the attempted encodings")
    return None

# Load data
def load_data():
    stories_df = try_read_csv('Stories.csv')
    questions_df = try_read_csv('questions.csv')  # Updated filename
    matches_df = try_read_csv('Questions_Stories.csv')
    
    if any(df is None for df in [stories_df, questions_df, matches_df]):
        raise Exception("Failed to load one or more required CSV files")
    
    return stories_df, questions_df, matches_df

# Get random question
def get_random_question(questions_df):

        # Filter questions to only include those with Story count > 0
    valid_questions = questions_df[questions_df['Story count'] > 0]
    
    if valid_questions.empty:
        raise Exception("No questions found with valid story matches")
    
    question = valid_questions.sample(n=1).iloc[0]
    return {
        'id': int(question['ID']),
        'text': question['Question'],
        'category': question['Category'],
        'short_version': question['short version'],
        'story_count': int(question['Story count'])


    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get-game-data')
def get_game_data():
    try:
        stories_df, questions_df, _ = load_data()
        question = get_random_question(questions_df)
        stories = stories_df['Story'].tolist()
        
        return jsonify({
            'question': question,
            'stories': stories
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-answers', methods=['POST'])
def check_answers():
    try:
        data = request.json
        selected_stories = data.get('selected_stories', [])
        question_id = data.get('question_id')
        
        _, questions_df, matches_df = load_data()
        
        # Get all matches for this question with their strengths
        question_matches = matches_df[matches_df['Question ID'] == question_id].copy()
        
        # Get the question details
        question_info = questions_df[questions_df['ID'] == question_id].iloc[0]
        
        # Evaluate each story
        results = []
        for story_index, story_data in enumerate(selected_stories):
            story_text = story_data['text']
            is_selected = story_data['selected']
            
            # Find if this story is a match for the question
            match_info = question_matches[question_matches['Story'] == story_text]
            should_have_selected = not match_info.empty
            
            # Get match strength and rationale if available
            match_strength = None
            rationale = None
            if should_have_selected:
                match_strength = int(match_info['Match strength'].iloc[0])
                rationale = match_info['Rationale'].iloc[0]
            
            is_correct = (should_have_selected and is_selected) or \
                        (not should_have_selected and not is_selected)
            
            results.append({
                'story_index': story_index,
                'is_correct': is_correct,
                'should_have_selected': should_have_selected,
                'match_strength': match_strength,
                'rationale': rationale
            })
        
        return jsonify({
            'results': results,
            'question_category': question_info['Category'],
            'expected_story_count': int(question_info['Story count'])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)