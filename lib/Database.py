import shelve

class Database ():
    def __init__(self, relativePath):
        self.__database = shelve.open(relativePath)

    def get (self, key):
        return self.__database[key]

    def set (self, key, value):
        self.__database[key] = value
        self.__database.sync()

    def delete (self, key):
        del self.__database[key]
        self.__database.sync()

    def close (self):
        self.__database.close()
        self.__database = None
