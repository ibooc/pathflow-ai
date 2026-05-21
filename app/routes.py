from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, Response, stream_with_context
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User
from app import bcrypt, limiter
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
API_URL = 'https://openrouter.ai/api/v1/chat/completions'

MODELS = [
    'google/gemma-4-26b-a4b-it:free',
    'meta-llama/llama-3.2-3b-instruct:free',
    'mistralai/mistral-7b-instruct:free',
]

def ask_ai(prompt):
    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://pathflow-ai.onrender.com',
        'X-Title': 'PathFlow AI'
    }

    for model in MODELS:
        try:
            print(f"Trying: {model}")
            body = {
                'model': model,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 1500,
            }
            response = requests.post(
                API_URL,
                headers=headers,
                json=body,
                timeout=30
            )

            if response.status_code == 429:
                print(f"Rate limited: {model}")
                continue

            if response.status_code != 200:
                print(f"Bad status {response.status_code}: {model}")
                continue

            data = response.json()

            if 'error' in data:
                print(f"API Error: {data['error'].get('message', '')}")
                continue

            if 'choices' not in data or len(data['choices']) == 0:
                print(f"No choices: {model}")
                continue

            message = data['choices'][0]['message']

            # Content None ho toh reasoning se lo
            content = (
                message.get('content') or
                message.get('reasoning') or
                message.get('reasoning_content') or
                ''
            )

            content = content.strip() if content else ''

            if len(content) > 20:
                print(f"Success: {model} — {len(content)} chars")
                return content
            else:
                print(f"Too short from {model}: '{content}'")
                continue

        except requests.exceptions.Timeout:
            print(f"Timeout: {model}")
            continue
        except Exception as e:
            print(f"Exception {model}: {str(e)}")
            continue

    raise Exception("Saare models busy hain — thodi der baad try karo!")

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/generate-roadmap', methods=['POST'])
def generate_roadmap():
    data = request.get_json()
    career_goal = data.get('career', '')

    if not career_goal:
        return jsonify({'error': 'Career goal missing'}), 400

    prompt = f"""
You are an expert career counselor for students in India.
A student wants to become: {career_goal}

Give a detailed response in this EXACT format:

REQUIRED SKILLS:
- List 6-8 must-have skills

MISSING SKILLS TO LEARN:
- List 5-6 skills most beginners lack

LEARNING ROADMAP:
- Month 1-2: What to learn first
- Month 3-4: What to learn next
- Month 5-6: Advanced topics
- Month 7-8: Projects and portfolio

RECOMMENDED TOOLS & TECHNOLOGIES:
- List 6-8 specific tools

TOP CERTIFICATIONS:
- List 3-4 best certifications

SALARY RANGE IN INDIA:
- Fresher: X to Y LPA
- Mid-level: X to Y LPA
- Senior: X to Y LPA

BEGINNER PROJECTS:
- List 3 beginner projects

INTERVIEW TIPS:
- List 3-4 key tips

Keep it practical and beginner-friendly for Indian students.
"""

    try:
        result = ask_ai(prompt)
        return jsonify({'roadmap': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/analyze-skills', methods=['POST'])
def analyze_skills():
    data = request.get_json()
    skills = data.get('skills', '')
    target_role = data.get('role', '')

    prompt = f"""
A student has these skills: {skills}
They want to become: {target_role}

Analyze and respond in this EXACT format:

CURRENT SKILLS ASSESSMENT:
- Rate each skill mentioned

MISSING CRITICAL SKILLS:
- List skills they MUST learn

JOB READINESS SCORE: X/10

IMPROVEMENT PLAN:
- Week 1-2: Focus on...
- Week 3-4: Focus on...
- Month 2: Focus on...

Keep advice practical for Indian job market.
"""

    try:
        result = ask_ai(prompt)
        return jsonify({'analysis': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/generate-interview', methods=['POST'])
def generate_interview():
    data = request.get_json()
    role = data.get('role', '')

    prompt = f"""
Generate interview questions for: {role}

TECHNICAL QUESTIONS:
Q1: [Question]
A1: [Beginner-friendly answer]

Q2: [Question]
A2: [Answer]

Q3: [Question]
A3: [Answer]

HR QUESTIONS:
Q1: [HR Question]
A1: [Sample answer]

Q2: [HR Question]
A2: [Sample answer]

INTERVIEW TIPS:
- Tip 1
- Tip 2
- Tip 3
"""

    try:
        result = ask_ai(prompt)
        return jsonify({'questions': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@main.route('/resume-scanner')
def resume_scanner():
    return render_template('resume_scanner.html')

@main.route('/interview')
def interview():
    return render_template('interview.html')

@main.route('/projects')
def projects():
    return render_template('projects.html')

@main.route('/generate-projects', methods=['POST'])
def generate_projects():
    data = request.get_json()
    role = data.get('role', '')
    level = data.get('level', 'beginner')

    prompt = f"""
You are an expert mentor for Indian CS students.
Generate project ideas for: {role} at {level} level.

Respond in this EXACT format:

BEGINNER PROJECTS:
Project 1: [Name]
Description: [2 lines]
Skills Used: [list]
Time: [duration]

Project 2: [Name]
Description: [2 lines]
Skills Used: [list]
Time: [duration]

Project 3: [Name]
Description: [2 lines]
Skills Used: [list]
Time: [duration]

INTERMEDIATE PROJECTS:
Project 1: [Name]
Description: [2 lines]
Skills Used: [list]
Time: [duration]

Project 2: [Name]
Description: [2 lines]
Skills Used: [list]
Time: [duration]

ADVANCED PROJECTS:
Project 1: [Name]
Description: [2 lines]
Skills Used: [list]
Time: [duration]

Project 2: [Name]
Description: [2 lines]
Skills Used: [list]
Time: [duration]

RESUME TIPS:
- Tip 1
- Tip 2
- Tip 3

Keep projects practical and impressive for Indian job market.
"""

    try:
        result = ask_ai(prompt)
        return jsonify({'projects': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

import re

@main.route('/register', methods=['GET', 'POST'])
@limiter.limit("20 per minute")
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        # Name validation
        if len(name) < 2:
            flash('Naam kam se kam 2 characters ka hona chahiye!', 'error')
            return redirect(url_for('main.register'))

        if not name.replace(' ', '').isalpha():
            flash('Naam mein sirf letters hone chahiye!', 'error')
            return redirect(url_for('main.register'))

        # Email validation — proper regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash('Valid email daalo! Jaise: rahul@gmail.com', 'error')
            return redirect(url_for('main.register'))

        # Common fake email domains block karo
        blocked_domains = [
            'gmai.com', 'gmial.com', 'gamil.com',
            'yaho.com', 'yahooo.com', 'hotmal.com',
            'test.com', 'fake.com', 'abc.com'
        ]
        email_domain = email.split('@')[1]
        if email_domain in blocked_domains:
            flash('Valid email provider use karo! (Gmail, Yahoo, etc.)', 'error')
            return redirect(url_for('main.register'))

        # Password validation
        if len(password) < 6:
            flash('Password kam se kam 6 characters ka hona chahiye!', 'error')
            return redirect(url_for('main.register'))

        if not any(c.isdigit() for c in password):
            flash('Password mein kam se kam 1 number hona chahiye!', 'error')
            return redirect(url_for('main.register'))

        # Check karo email already hai ya nahi
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash('Ye email already registered hai! Login karo.', 'error')
            return redirect(url_for('main.register'))

        # User banao
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(name=name, email=email, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('main.setup'))

    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Galat email ya password!', 'error')

    return render_template('login.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@main.route('/setup', methods=['GET', 'POST'])
@login_required
def setup():
    if request.method == 'POST':
        current_user.target_role = request.form.get('target_role', '')
        current_user.skills = request.form.get('skills', '')
        current_user.python_level = int(request.form.get('python_level', 0))
        current_user.web_level = int(request.form.get('web_level', 0))
        current_user.data_level = int(request.form.get('data_level', 0))
        current_user.ml_level = int(request.form.get('ml_level', 0))
        current_user.sql_level = int(request.form.get('sql_level', 0))
        db.session.commit()
        return redirect(url_for('main.dashboard'))

    return render_template('setup.html', user=current_user)


@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)


@main.route('/update-stats', methods=['POST'])
@login_required
def update_stats():
    data = request.get_json()
    stat_type = data.get('type')

    if stat_type == 'roadmap':
        current_user.roadmaps_count += 1
    elif stat_type == 'scan':
        current_user.scans_count += 1
    elif stat_type == 'interview':
        current_user.interviews_count += 1
    elif stat_type == 'project':
        current_user.projects_count += 1

    db.session.commit()
    return jsonify({'success': True})

@main.route('/analyze-dashboard', methods=['POST'])
@login_required
def analyze_dashboard():
    data = request.get_json()
    
    prompt = f"""
You are an expert AI career counselor analyzing a student's profile.

Student Name: {current_user.name}
Target Role: {current_user.target_role or 'Not set'}
Current Skills: {current_user.skills or 'Not mentioned'}
Skill Levels:
- Python: {current_user.python_level}%
- Web Development: {current_user.web_level}%
- Data Analysis: {current_user.data_level}%
- Machine Learning: {current_user.ml_level}%
- SQL & Database: {current_user.sql_level}%

Analyze this student's profile and respond in EXACTLY this format:

JOB_READINESS_SCORE: [number between 0-100]

STRENGTHS:
- [strength 1]
- [strength 2]
- [strength 3]

MISSING_SKILLS:
- [missing skill 1]
- [missing skill 2]
- [missing skill 3]
- [missing skill 4]

NEXT_STEPS:
- [action 1 - specific and actionable]
- [action 2]
- [action 3]
- [action 4]

SALARY_ESTIMATE:
Fresher: [X to Y LPA]
Mid-level: [X to Y LPA]
Senior: [X to Y LPA]

TOP_COURSES:
- [course 1 with platform name]
- [course 2]
- [course 3]

CAREER_ADVICE:
[2-3 lines of personalized advice for this specific student]

TIME_TO_JOB_READY:
[Estimated months needed to be job ready]

Be specific, practical and encouraging for Indian students.
"""

    try:
        result = ask_ai(prompt)
        return jsonify({'insights': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@main.route('/salary')
def salary():
    return render_template('salary.html')


@main.route('/get-salary', methods=['POST'])
def get_salary():
    data = request.get_json()
    role = data.get('role', '')
    experience = data.get('experience', 'fresher')

    prompt = f"""
You are a salary expert for Indian job market.
Role: {role}
Experience Level: {experience}

IMPORTANT: Give REALISTIC and ACCURATE salary data.
- For medical/healthcare roles: mention hospitals, clinics, pharma companies
- For trade/craft roles: mention relevant industries, NOT IT companies
- For IT roles: mention tech companies
- Do NOT mention irrelevant companies

Give salary information in this EXACT format:

SALARY_IN_INDIA:
Fresher (0-1 yr): X to Y LPA
Junior (1-3 yr): X to Y LPA
Mid-level (3-5 yr): X to Y LPA
Senior (5+ yr): X to Y LPA

TOP_PAYING_CITIES:
- City 1: X to Y LPA
- City 2: X to Y LPA
- City 3: X to Y LPA

TOP_COMPANIES:
- Company 1: X to Y LPA
- Company 2: X to Y LPA
- Company 3: X to Y LPA

SKILLS_THAT_INCREASE_SALARY:
- Skill 1: +X LPA impact
- Skill 2: +X LPA impact
- Skill 3: +X LPA impact

GLOBAL_SALARY:
USA: $X to $Y per year
UK: £X to £Y per year
Canada: $X to $Y per year
Australia: $X to $Y per year

SALARY_TIPS:
- Tip 1
- Tip 2
- Tip 3

Keep data realistic for 2024-2025 Indian market.
"""

    try:
        result = ask_ai(prompt)
        return jsonify({'salary': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500   
    
    from flask import render_template

@main.app_errorhandler(429)
def too_many_requests(e):
    return render_template('429.html'), 429

@main.app_errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404