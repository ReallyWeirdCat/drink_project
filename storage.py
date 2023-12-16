import os
import time
from pathlib import Path
from ast import literal_eval
import exceptions

class Database:

    def __init__(self, path=None, template=None):
    
        self._data = None
        self._file = None
        self._template = None

        self.__location__ = os.getcwd()
        
        if path == None:
            path = os.path.join(self.__location__, "data")
        else:
            path = os.path.join(self.__location__, path)
        self._file = path
        
        self._template = self.getTemplate(template)
                    
        self._readData()

    def __del__(self):
    
        """
        Destructor. Tries to commit database on exit
        
        EDIT: decided that this is a dangerous practice,
        better leave it off for now
        """
    
        """
        if not self._file: return
        
        try:
            open(self._file, encoding="utf-8")
        except Exception as err:
            print("Failed to save database before exit", err, sep="\n")
            return
        
        self.commit()
        """
        pass

    def commit(self):
    
        """
        Applies changes to the database
        """
    
        with open(self._file, "w+", encoding="utf-8") as file:
            file.write(str(self._data))
    
    def exists(self, *args):
        
        """
        Checks if key exists in the database
        """
        
        try:
            keys = args
            rv = self._data
            for key in keys:
                rv = rv[key]
            return True
        except KeyError as err:
            return False
    
    
    def get(self, *args):
    
        """
        Gets the value from the database.
        *args are the dictionary keys to follow
        """
    
        keys = args
        rv = self._data
        for key in keys:
            rv = rv[key]
        return rv
    
    def set(self, *keys, val):
    
        """
        Writes value to the requested key
        """
    
        current = self._data
        #print(current, type(current))

        for key in keys[:-1]:
            current = current.setdefault(key, {})

        current[keys[-1]] = val

    
    def getTemplate(self, template=None):
    
        """
        Gets database template which is used to create a new
        database if the storage file is empty.
        """
    
        t = {}
    
        if template != None and template != "":
            t = literal_eval(open(os.path.join(self.__location__, template), encoding="utf-8").read())
    
        return t
        
    
    def _readData(self):
    
        """
        Reads the data from file and converts it to dictionary.
        Tries to create database from template if file is empty
        Doesn't allow to continue
        """
    
        buffer = ""
        try:
            with open(self._file, encoding="utf-8") as file:
                buffer = file.read()
        except FileNotFoundError:
            open(self._file, "w+")
        try:
        
            if buffer == "":
                raise exceptions.DatabaseEmptyError
            try:
                buffer = literal_eval(buffer)
                #if type(buffer) != "dict":
                #    raise TypeError
                self._data = buffer
            except Exception as err:
                print(err)
                raise exceptions.DatabaseSyntaxError
                
        except exceptions.DatabaseEmptyError:
            self._data = self._template
            self.commit()
            print("Database was empty. Created from template")
            pass
            
        except exceptions.DatabaseSyntaxError:
            self._file = None
            print("Database is damaged!")