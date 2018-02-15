import io
import os
import sys
import nbformat


class NbHandler(object):

    def __init__(self, notebook):
        self.path = notebook
        self.note = None
        with io.open(self.path, 'r', encoding='utf-8') as f:
            self.target = nbformat.read(f, as_version=4)

    def get_from_cell(self, cell):
        return self.target.cells[cell].source
    
    def set_into_cell(self, cell, msg):
        self.target.cells[cell].source = msg
        
    def write(self):
        nbformat.write(self.target, self.path)