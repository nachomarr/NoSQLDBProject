class Login:
    _instance = None  # Class attribute to store the single instance

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Login, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):  # To prevent reinitialization
            self.username = None
            self.email = None
            self.credentials = {}
            self.initialized = True

    def checklogin(self):
        if self.username is None:
            self.setlogin()
        return self.credentials

    def setlogin(self):
        checked = False
        while not checked:
            email = input("What's your email? ")
            if '@' in email:
                checked = True
                self.username = email.split('@')[0].capitalize()
                self.email = email

        self.credentials = {'username': self.username, 'email': self.email}
        print("Login set successfully!")

    def getLogin(self):
        if self.credentials:
            return self.credentials
        else:
            print("No login information available.")
            return None
