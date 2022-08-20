import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.username = "postgres"
        self.password = "postgres"
        self.database_path = "postgresql://{}:{}@{}/{}".format(self.username, self.password,'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_getting_all_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['status'], True)
        self.assertTrue(data['categories'])


    def test_getting_all_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['status'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['categories'])
        self.assertTrue(data['current_category'])


    def test_getting_out_of_range_questions(self):
        res = self.client().get("/questions?page=100000000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['status'], False)


    def test_delete_a_question(self):
        questions = Question.query
        id = questions.first()

        if id is not None:
            id = id.id
            res = self.client().delete(f"/questions/{id}")
            data = json.loads(res.data)

            question = questions.filter(Question.id == id).one_or_none()

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['status'], True)
            self.assertTrue(data['deleted'])
            self.assertEqual(question, None)


    def test_delete_a_non_existing_question(self):
        res = self.client().delete("/questions/100000000")
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 100000000).one_or_none()

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['status'], False)
        self.assertEqual(question, None)

    def test_create_a_question(self):
        res = self.client().post("/questions", json={
            "question": "Who are you?", 
            "answer": "I am me", 
            "difficulty": 1, 
            "category": 1
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['status'], True)
        self.assertTrue(data['created'])

    def test_create_a_question_not_valid(self):
        res = self.client().post("/questions", json={
            "questions": "Who are you?", 
            "category": "1"
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)

    def test_search_questions_by_searchterm(self):
        res = self.client().post("/questions/search", json={"searchTerm": "title"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_get_category_questions(self):
        categories = Category.query
        id = categories.first()

        if id is not None:
            id = id.id
            res = self.client().get(f"/categories/{id}/questions")
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['questions'])
            self.assertTrue(data['total_questions'])
            self.assertTrue(data['current_category'])

    def test_get_category_questions_not_valid(self):
        res = self.client().get(f"/categories/100/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)

    def test_quiz_questions(self):
        res = self.client().post("/quizzes", json={
            "previous_questions": [],
            "quiz_category": 1
        })
        data = res.get_json()
        
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['status'], True)
        self.assertTrue(data['question'])




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()