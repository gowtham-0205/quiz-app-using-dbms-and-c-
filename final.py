import mysql.connector
import random
import threading

class Question:
    def __init__(self, question_id, question_text, answer_choices, correct_answer, additional_attribute):
        self.question_id = question_id
        self.question_text = question_text
        self.answer_choices = answer_choices
        self.correct_answer = correct_answer
        self.additional_attribute = additional_attribute


class PythonQuestion(Question):
    def __init__(self, question_id, question_text, answer_choices, correct_answer, additional_python_attribute):
        super().__init__(question_id, question_text, answer_choices, correct_answer)
        self.additional_python_attribute = additional_python_attribute

class CppQuestion(Question):
    def __init__(self, question_id, question_text, answer_choices, correct_answer, additional_cpp_attribute):
        super().__init__(question_id, question_text, answer_choices, correct_answer)
        self.additional_cpp_attribute = additional_cpp_attribute

class SqlQuestion(Question):
    def __init__(self, question_id, question_text, answer_choices, correct_answer, additional_sql_attribute):
        super().__init__(question_id, question_text, answer_choices, correct_answer)
        self.additional_sql_attribute = additional_sql_attribute

class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

class Authenticator:
    def __init__(self, database):
        self.database = database
        self.max_login_attempts = 5

    def authenticate(self):
        for _ in range(self.max_login_attempts):
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            if self.check_credentials(username, password):
                return self.get_user(username)
            print("Authentication failed. Please try again.")
        print("Maximum login attempts reached. Exiting.")
        self.database.close() 
        exit(1)

    def check_credentials(self, username, password):
        query = "SELECT username, password FROM users WHERE username = %s AND password = %s"
        self.database.cursor.execute(query, (username, password))
        result = self.database.cursor.fetchone()
        return result is not None

    def get_user(self, username):
        query = "SELECT id, username, password FROM users WHERE username = %s"
        self.database.cursor.execute(query, (username,))
        user_data = self.database.cursor.fetchone()
        if user_data:
            id, username, password = user_data
            return User(id, username, password)
        return None

    def register(self):
        username = input("Enter a new username: ")
        password = input("Enter a new password: ")
        if self.is_username_taken(username):
            print("Username already in use. Please choose another one.")
            return self.register()
        else:
            self.create_user(username, password)
            print("Registration successful. You can now log in.")
            return self.get_user(username)

    def is_username_taken(self, username):
        query = "SELECT username FROM users WHERE username = %s"
        self.database.cursor.execute(query, (username,))
        result = self.database.cursor.fetchone()
        return result is not None

    def create_user(self, username, password):
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        self.database.cursor.execute(query, (username, password))
        self.database.connection.commit()

class Admin:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

class AdminInterface:
    def __init__(self, database):
        self.database = database
        self.admin = None

    def authenticate_admin(self):
        username = input("Enter your admin username: ")
        password = input("Enter your admin password: ")
        if self.check_admin_credentials(username, password):
            self.admin = self.get_admin(username)
        else:
            print("Authentication failed. Access denied.")
            return

    def check_admin_credentials(self, username, password):
        query = "SELECT username, password FROM admins WHERE username = %s AND password = %s"
        self.database.cursor.execute(query, (username, password))
        result = self.database.cursor.fetchone()
        return result is not None

    def get_admin(self, username):
        query = "SELECT id, username, password FROM admins WHERE username = %s"
        self.database.cursor.execute(query, (username,))
        admin_data = self.database.cursor.fetchone()
        if admin_data:
            id, username, password = admin_data
            return Admin(id, username, password)
        return None

    def add_question(self, topic_id, question_text, answer_choices, correct_answer):
        topic = self.get_topic_name_by_id(topic_id)
        if not topic:
            print("Invalid topic ID.")
            return

        table_name = f"{topic.lower()}_questions"  
        query = f"INSERT INTO {table_name} (question_text, answer_choices, correct_answer) VALUES (%s, %s, %s)"
        self.database.cursor.execute(query, (question_text, answer_choices, correct_answer))
        self.database.connection.commit()

    def get_topic_name_by_id(self, topic_id):
        query = "SELECT topic_name FROM topics WHERE topic_id = %s"
        self.database.cursor.execute(query, (topic_id,))
        result = self.database.cursor.fetchone()
        if result:
            return result[0]
        return None

    def remove_question(self, topic_id):
        topic = self.get_topic_name_by_id(topic_id)
        if not topic:
            print("Invalid topic ID.")
            return

        table_name = f"{topic.lower()}_questions"  
        self.list_questions(topic)
        question_id = input("Enter the question ID to remove: ")
        query = f"DELETE FROM {table_name} WHERE question_id = %s"
        self.database.cursor.execute(query, (question_id,))
        self.database.connection.commit()
    

    def list_questions(self, topic):
        query = f"SELECT question_id, question_text FROM {topic}_questions"
        self.database.cursor.execute(query)
        questions = self.database.cursor.fetchall()
        print(f"Questions for {topic}:\n")
        for question in questions:
            question_id, question_text = question
            print(f"ID: {question_id}, Text: {question_text}")
    def add_topic(self, topic_name):
    
        query = "INSERT INTO topics (topic_name) VALUES (%s)"
        self.database.cursor.execute(query, (topic_name,))
        self.database.connection.commit()
    
        query = f"CREATE TABLE IF NOT EXISTS {topic_name}_questions (question_id INT AUTO_INCREMENT PRIMARY KEY, question_text VARCHAR(255), answer_choices VARCHAR(255), correct_answer INT)"
        self.database.cursor.execute(query)
        self.database.connection.commit()
    def get_topics(self):
        query = "SELECT topic_id, topic_name FROM topics"
        self.database.cursor.execute(query)
        topics = self.database.cursor.fetchall()
        return topics


    def remove_topic(self):
        self.list_topics()
        topic_id = input("Enter the topic ID to remove: ")

        topic_name = self.get_topic_name_by_id(topic_id)
        if not topic_name:
            print("Invalid topic ID.")
            return

        self.delete_questions_table(topic_name)

        query = "DELETE FROM topics WHERE topic_id = %s"
        self.database.cursor.execute(query, (topic_id,))
        self.database.connection.commit()
        print(f"Topic '{topic_name}' and its questions have been removed.")

    def delete_questions_table(self, topic_name):
        table_name = f"{topic_name.lower()}_questions"
        query = f"DROP TABLE IF EXISTS {table_name}"
        self.database.cursor.execute(query)
        self.database.connection.commit()


    def list_topics(self):
        query = "SELECT topic_id, topic_name FROM topics"
        self.database.cursor.execute(query)
        topics = self.database.cursor.fetchall()
        return topics

def admin_menu(admin_interface):
    while True:
        print("\nAdmin Menu:")
        print("1. Add Question")
        print("2. Remove Question")
        print("3. Add Topic")
        print("4. Remove Topic")
        print("5. Log Out")
        choice = input("Enter your choice: ")

        if choice == "1":
            topics = admin_interface.list_topics()
            print("Available Topics:")
            for topic in topics:
                topic_id, topic_name = topic
                print(f"{topic_id}. {topic_name}")

            topic_id = input("Enter the topic ID: ")
            question_text = input("Enter the question text: ")
            answer_choices = input("Enter answer choices separated by ';': ")
            correct_answer = input("Enter the correct answer (as a number): ")
            admin_interface.add_question(topic_id, question_text, answer_choices, correct_answer)
        elif choice == "2":
            topics = admin_interface.list_topics()
            print("Available Topics:")
            for topic in topics:
                topic_id, topic_name = topic
                print(f"{topic_id}. {topic_name}")

            topic_id = input("Enter the topic ID: ")
            admin_interface.remove_question(topic_id)
        elif choice == "3":
            topic_name = input("Enter the new topic name: ")
            admin_interface.add_topic(topic_name)
        elif choice == "4":
            topics = admin_interface.list_topics()
            print("Available Topics:")
            for topic in topics:
                topic_id, topic_name = topic
                print(f"{topic_id}. {topic_name}")

            admin_interface.remove_topic()
        elif choice == "5":
            print("Logging out as admin.")
            break
        else:
            print("Invalid choice. Please enter a valid option (1-5).")

        topics = admin_interface.list_topics()
        print("Available Topics:")
        for topic in topics:
            topic_id, topic_name = topic
            print(f"{topic_id}. {topic_name}")

class Database:
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()

    def get_questions_by_topic(self, topic_name):
        topic = f"{topic_name.lower()}_questions"

        if not self.check_if_topic_exists(topic_name):
            raise ValueError("Invalid topic")

        query = f"SELECT question_id, question_text, answer_choices, correct_answer FROM {topic}"

        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        questions = []

        question_class = globals().get(f"{topic_name}Question", Question)

        for row in rows:
            question_id, question_text, answer_choices, correct_answer = row
            answer_choices = answer_choices.split(';')
            questions.append(question_class(question_id, question_text, answer_choices, correct_answer, f"Additional {topic_name} attribute"))

        return questions


    def check_if_topic_exists(self, topic_name):
        query = "SELECT topic_id FROM topics WHERE topic_name = %s"
        self.cursor.execute(query, (topic_name,))
        result = self.cursor.fetchone()
        return result is not None
    
def generate_quiz(database, topic, user_id):
    questions = database.get_questions_by_topic(topic)
    random.shuffle(questions)  
    quiz = Quiz(questions, topic, user_id)
    return quiz

def start_quiz(quiz, database):
    print("\n<============================================>\n")
    print("\t Let's begin the Quiz!\n")
    print("\t You have 5 minutes\n")
    print("\n<============================================>\n\n")

    while not quiz.is_quiz_over():
        question = quiz.get_current_question()
        print(f"Question {quiz.current_question_index + 1}/{len(quiz.questions)}:\n\n")
        print(question.question_text)
        for i, answer_choice in enumerate(question.answer_choices, 1):
            print(f"{i}. {answer_choice}")

        user_answer = input("\nEnter the number of your answer: ").strip().lower()

        try:
            user_answer = int(user_answer)
            correct_answer = int(question.correct_answer)
            if user_answer == correct_answer:
                print("\nCorrect!\n")
                quiz.update_score(True)
            else:
                print(f"\nSorry, that's incorrect. The correct answer is: {correct_answer}\n")
        except ValueError:
            print("\nInvalid input. Please enter a number as your answer.")

        quiz.next_question()

    quiz.print_result(database)
    database.close()  

def update_topic_high_score(database, topic, new_high_score, user_id):
    query = "INSERT INTO topic_high_scores (topic, high_score, user_id) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE high_score = %s, user_id = %s"



    database.cursor.execute(query, (topic, new_high_score, user_id, new_high_score, user_id))
    database.connection.commit()

def get_topic_high_score(database, topic):
    query = "SELECT high_score FROM topic_high_scores WHERE topic = %s"
    database.cursor.execute(query, (topic,))
    result = database.cursor.fetchone()
    if result:
        return result[0]
    return 0
class Quiz:
    def __init__(self, questions, topic, user_id):
        self.questions = questions
        self.current_question_index = 0
        self.score = 0  
        self.timer_thread = None
        self.maximum_score = len(questions)  
        self.topic = topic
        self.user_id = user_id

    def get_current_question(self):
        return self.questions[self.current_question_index]

    def is_quiz_over(self):
        return self.current_question_index >= len(self.questions)

    def next_question(self):
        if self.timer_thread:
            self.timer_thread.cancel()  
        self.current_question_index += 1
        if not self.is_quiz_over():
            self.start_question_timer()  

    def update_score(self, is_correct):
        if is_correct:
            self.score += 1

    def start_question_timer(self):
        self.timer_thread = threading.Timer(300, self.timer_expired)
        self.timer_thread.start()

    def timer_expired(self):
        print("\nTime is up!\n")
        self.current_question_index = len(self.questions)

    def print_result(self, database):
        print("\nQuiz Results:")
        print(f"Score: {self.score}/{self.maximum_score}")

        previous_high_score = get_topic_high_score(database, self.topic)

        if self.score > previous_high_score:
            update_topic_high_score(database, self.topic, self.score, self.user_id)
            print(f"Congratulations! You achieved a new high score for this topic.")
        else:
            print(f"High score for this topic: {previous_high_score}")


if __name__ == "__main__":
    database = Database("localhost", "root", "sk@200545", "sk")
    authenticator = Authenticator(database)

    while True:
        print("\n<============================================>\n")
        print("\tWelcome to the Python Quiz App")
        print("\n<============================================>\n\n")
        print("1. Log in\n")
        print("2. Register\n")
        print("3. Admin Login\n")
        choice = input("Enter your choice (1/2/3): ")

        if choice == "1":
            user = authenticator.authenticate()
            if user.username == "admin":
                admin_interface = AdminInterface(database)
                admin_interface.authenticate_admin()
                if admin_interface.admin:
                    admin_menu(admin_interface)
            elif user:
                print("\n<============================================>\n")
                print("\n\tSelect a topic for the quiz:")
                print("\n<============================================>\n\n")

                user_interface = AdminInterface(database)

                topics = user_interface.get_topics()
                for topic_id, topic_name in topics:
                    print(f"{topic_id}. {topic_name}")
    
                topic = input("Enter the number of your chosen topic: ")
                quiz = generate_quiz(database, topic, user.id)
                start_quiz(quiz, database)
            break
        elif choice == "2":
            user = authenticator.register()
            if user:
                break
        elif choice == "3":
            admin_interface = AdminInterface(database)
            admin_interface.authenticate_admin()
            if admin_interface.admin:
                admin_menu(admin_interface)
        else:
            print("Invalid choice. Please enter 1 to log in, 2 to register, or 3 for admin login.")
