"""
Quiz models for reading comprehension questions.
"""

from datetime import datetime
from lute.db import db


class QuizQuestion(db.Model):
    """
    Quiz question for reading comprehension.
    """
    __tablename__ = "quiz_questions"

    id = db.Column("QQID", db.Integer, primary_key=True)
    text_id = db.Column("QQTxID", db.Integer, db.ForeignKey("texts.TxID"), nullable=False)
    book_id = db.Column("QQBkID", db.Integer, db.ForeignKey("books.BkID"), nullable=False)
    question_text = db.Column("QQQuestion", db.String(500), nullable=False)
    correct_answer = db.Column("QQCorrectAnswer", db.String(200), nullable=False)
    option_a = db.Column("QQOptionA", db.String(200), nullable=False)
    option_b = db.Column("QQOptionB", db.String(200), nullable=False)
    option_c = db.Column("QQOptionC", db.String(200), nullable=False)
    option_d = db.Column("QQOptionD", db.String(200), nullable=False)
    created_at = db.Column("QQCreatedAt", db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    text = db.relationship("Text", backref="quiz_questions")
    book = db.relationship("Book", backref="quiz_questions")
    answers = db.relationship("QuizAnswer", back_populates="question", cascade="all, delete-orphan")

    def __init__(self, text_id, book_id, question_text, correct_answer, option_a, option_b, option_c, option_d):
        self.text_id = text_id
        self.book_id = book_id
        self.question_text = question_text
        self.correct_answer = correct_answer
        self.option_a = option_a
        self.option_b = option_b
        self.option_c = option_c
        self.option_d = option_d

    def __repr__(self):
        return f"<QuizQuestion {self.id} for Text {self.text_id}>"

    def get_options(self):
        """Return all options as a list."""
        return [self.option_a, self.option_b, self.option_c, self.option_d]

    def get_correct_option_index(self):
        """Return the index of the correct answer (0-3)."""
        options = self.get_options()
        return options.index(self.correct_answer)


class QuizAnswer(db.Model):
    """
    Student's answer to a quiz question.
    """
    __tablename__ = "quiz_answers"

    id = db.Column("QAID", db.Integer, primary_key=True)
    question_id = db.Column("QAQuestionID", db.Integer, db.ForeignKey("quiz_questions.QQID"), nullable=False)
    selected_answer = db.Column("QASelectedAnswer", db.String(200), nullable=False)
    is_correct = db.Column("QAIsCorrect", db.Boolean, nullable=False)
    answered_at = db.Column("QAAnsweredAt", db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    question = db.relationship("QuizQuestion", back_populates="answers")

    def __init__(self, question_id, selected_answer, is_correct):
        self.question_id = question_id
        self.selected_answer = selected_answer
        self.is_correct = is_correct

    def __repr__(self):
        return f"<QuizAnswer {self.id} for Question {self.question_id}>"


class QuizSession(db.Model):
    """
    A quiz session for tracking student progress through questions.
    """
    __tablename__ = "quiz_sessions"

    id = db.Column("QSID", db.Integer, primary_key=True)
    text_id = db.Column("QSTxID", db.Integer, db.ForeignKey("texts.TxID"), nullable=False)
    book_id = db.Column("QSBkID", db.Integer, db.ForeignKey("books.BkID"), nullable=False)
    started_at = db.Column("QSStartedAt", db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column("QSCompletedAt", db.DateTime, nullable=True)
    total_questions = db.Column("QSTotalQuestions", db.Integer, nullable=False)
    correct_answers = db.Column("QSCorrectAnswers", db.Integer, default=0, nullable=False)
    
    # Relationships
    text = db.relationship("Text", backref="quiz_sessions")
    book = db.relationship("Book", backref="quiz_sessions")

    def __init__(self, text_id, book_id, total_questions):
        self.text_id = text_id
        self.book_id = book_id
        self.total_questions = total_questions

    def __repr__(self):
        return f"<QuizSession {self.id} for Text {self.text_id}>"

    def mark_completed(self):
        """Mark the quiz session as completed."""
        self.completed_at = datetime.utcnow()

    def increment_correct_answers(self):
        """Increment the correct answers count."""
        self.correct_answers += 1

    def get_score_percentage(self):
        """Get the quiz score as a percentage."""
        if self.total_questions == 0:
            return 0
        return (self.correct_answers / self.total_questions) * 100