import os


class XMLHelper:
    @staticmethod
    def read(file_path):
        curdir = os.getcwd()
        with open(f"{curdir}{file_path}") as xml:
            return xml.read()
