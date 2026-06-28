from flask_login import UserMixin

class User(UserMixin):
    """
    Represents a user in the application, integrating Flask-Login's UserMixin 
    for session management and authentication.
    """
    def __init__(self, id, name, surname, email, role, languages=None):
        self.id = id
        self.name = name
        self.surname = surname
        self.email = email
        self.role = role
        # Stores the list of languages spoken by the user (primarily for guides)
        self.languages = languages