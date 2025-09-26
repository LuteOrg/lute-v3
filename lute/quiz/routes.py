"""
Quiz routes for reading comprehension questions.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from lute.db import db
from lute.quiz.service import QuizService
from lute.read.service import Service as ReadService
from lute.models.book import Book, Text
from lute.models.quiz import QuizQuestion, QuizAnswer, QuizSession

bp = Blueprint("quiz", __name__, url_prefix="/quiz")


@bp.route("/start/<int:text_id>")
def start_quiz(text_id):
    """
    Start a quiz for the given text.
    Generate questions if they don't exist.
    """
    quiz_service = QuizService(db.session)
    
    # Check if questions already exist for this text
    existing_questions = quiz_service.get_quiz_questions(text_id)
    
    if not existing_questions:
        # Get text and book information
        text = db.session.query(Text).filter_by(id=text_id).first()
        if not text:
            return redirect(url_for("index"))
        
        # Generate questions
        questions = quiz_service.generate_questions_for_text(text_id, text.bk_id)
        
        if not questions:
            # If no questions could be generated, redirect back to reading
            return redirect(url_for("read.read", bookid=text.bk_id))
        
        # Create quiz session
        quiz_service.create_quiz_session(text_id, text.bk_id, questions)
    else:
        questions = existing_questions
    
    # Get the first question
    first_question = questions[0] if questions else None
    
    return render_template("quiz/quiz.html", 
                         text_id=text_id,
                         question=first_question,
                         question_number=1,
                         total_questions=len(questions))


@bp.route("/question/<int:question_id>")
def show_question(question_id):
    """
    Show a specific quiz question.
    """
    question = db.session.query(QuizQuestion).filter_by(id=question_id).first()
    if not question:
        return redirect(url_for("index"))
    
    # Get all questions for this text to calculate progress
    all_questions = db.session.query(QuizQuestion).filter_by(text_id=question.text_id).all()
    question_number = next((i + 1 for i, q in enumerate(all_questions) if q.id == question_id), 1)
    
    return render_template("quiz/quiz.html",
                         text_id=question.text_id,
                         question=question,
                         question_number=question_number,
                         total_questions=len(all_questions))


@bp.route("/submit_answer", methods=["POST"])
def submit_answer():
    """
    Submit an answer to a quiz question.
    """
    data = request.get_json()
    question_id = data.get('question_id')
    selected_answer = data.get('selected_answer')
    
    if not question_id or not selected_answer:
        return jsonify({'error': 'Missing required data'}), 400
    
    quiz_service = QuizService(db.session)
    result = quiz_service.submit_answer(question_id, selected_answer)
    
    if result is None:
        return jsonify({'error': 'Question not found'}), 404
    
    return jsonify(result)


@bp.route("/next_question/<int:text_id>/<int:current_question_id>")
def next_question(text_id, current_question_id):
    """
    Navigate to the next question.
    """
    # Get all questions for this text
    questions = db.session.query(QuizQuestion).filter_by(text_id=text_id).order_by(QuizQuestion.id).all()
    
    # Find current question index
    current_index = next((i for i, q in enumerate(questions) if q.id == current_question_id), -1)
    
    if current_index == -1:
        return redirect(url_for("index"))
    
    # Check if there's a next question
    if current_index + 1 < len(questions):
        next_question_obj = questions[current_index + 1]
        return redirect(url_for("quiz.show_question", question_id=next_question_obj.id))
    else:
        # No more questions, show results
        return redirect(url_for("quiz.quiz_results", text_id=text_id))


@bp.route("/results/<int:text_id>")
def quiz_results(text_id):
    """
    Show quiz results for a text.
    """
    quiz_service = QuizService(db.session)
    results = quiz_service.get_quiz_results(text_id)
    
    # Calculate score
    total_questions = len(results)
    correct_answers = sum(1 for r in results if r['is_correct'])
    score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    
    # Get text information
    text = db.session.query(Text).filter_by(id=text_id).first()
    book_id = text.bk_id if text else None
    
    return render_template("quiz/results.html",
                         text_id=text_id,
                         book_id=book_id,
                         results=results,
                         score=score,
                         total_questions=total_questions,
                         correct_answers=correct_answers)


@bp.route("/skip/<int:text_id>")
def skip_quiz(text_id):
    """
    Skip the quiz and return to reading.
    """
    text = db.session.query(Text).filter_by(id=text_id).first()
    if text:
        return redirect(url_for("read.read", bookid=text.bk_id))
    return redirect(url_for("index"))