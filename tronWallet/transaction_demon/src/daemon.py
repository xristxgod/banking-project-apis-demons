class Daemon:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Daemon, cls).__new__(cls)
        return cls.instance

