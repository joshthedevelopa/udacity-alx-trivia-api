import math
import os
import re
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate(request, data):
    page_number = request.args.get("page", 1, type=int)
    start = (page_number - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    if start > len(data):
        return []

    return [item.format() for item in data[start:end]]

def get_random_item(array):
    if len(array) == 0:  
        return None
    index = random.Random.randint(0, len(array) - 1)
    return array[index]

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')

        return response
    
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=['GET'])
    def get_categories():
        categories = {}
        
        for category in Category.query.all():
            categories[category.id] = category.type
            
        return jsonify({
            'status': True,
            'categories': categories
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions", methods=['GET'])
    def get_questions():
        questions = Question.query.all()
        categories = {}
        questions_paginated = paginate(request, questions)

        if len(questions_paginated) == 0:
            abort(404)
        
        for category in Category.query.all():
            categories[category.id] = category.type

        return jsonify({
            'status': True,
            "questions": questions_paginated,
            "total_questions": len(questions),
            "categories": categories,
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:id>", methods=['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.filter(Question.id == id).one_or_none()

            if question is None:
                abort(404)
            
            question.delete()
            return jsonify({
                "status": True,
                "deleted": id
            })

        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=['POST'])
    def add_question():
        required_fields = ["question", "answer", "difficulty", "category"]
        data = request.get_json()

        for field in required_fields:
            if field not in data:
                abort(400)
            
        question = Question(
            question=data['question'],
            answer=data['answer'],
            difficulty=data['difficulty'],
            category=data['category']
        )

        question.insert()
        return jsonify({
            "status": True,
            "created": question.id
        })

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions/search", methods=['POST'])
    def search_question():
        data = request.get_json()
        search_term = data['searchTerm']
        questions = paginate(request, Question.query.filter(Question.question.ilike(f"%{search_term}%")).all())
        
        return jsonify({
            "questions": questions,
            "total_questions": len(questions),
        })
        

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:id>/questions", methods=['GET'])
    def get_category_questions(id):
        category = Category.query.filter_by(id = id).one_or_none()

        if category is None:
            abort(404)

        questions = paginate(request, Question.query.filter_by(category = id).all())

        return jsonify({
            "questions": questions,
            "total_questions": len(questions),
            "current_category": category.type
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def quiz_questions():
        data = request.get_json()

        previous_questions = data['previous_questions']
        quiz_category = data['quiz_category']

        if quiz_category == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category = quiz_category['id']).all()

        for question in questions:
            if question.id not in previous_questions:
                return jsonify({
                    "status": True,
                    "question": question.format()
                })

        return jsonify({
            "status": True,
            "question": None
        })


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "status": False,
            "message": "server_error",
            "code": 500
        }), 500

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "status": False,
            "message": "not_found",
            "code": 404
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "status": False,
            "message": "bad_request",
            "code": 400
        }), 400

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "status": False,
            "message": "unprocessable",
            "code": 422
        }), 422

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "status": False,
            "message": "method_not_allowed",
            "code": 405
        }), 405


    return app

