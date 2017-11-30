import io
import os
import sys
import nbformat

# Base file (relative path)
BASE_FILE = "templates/00_base.ipynb"

# Indent for docker-compose.yml
INDENT = 2

# Cell number for each component
SETTINGS = 1
DOCKER_COMPOSE = 3
PERMANENT_DIR = 5

# TODO(yushiro): Move to consts.py or opts.py
# Configuration definitions
JENKINS = "jenkins"
GITLAB = "gitlab"
GITBUCKET = "gitbucket"
_DOCKER_COMPOSE = "docker-compose"
_PERMANENT_DIR = "permanent-dir"
_PARAMETERS = "parameters"

TARGETS = [_DOCKER_COMPOSE, _PERMANENT_DIR, _PARAMETERS]


class NbMerger(object):

    def __init__(self, project, ipaddr):
        self.initialize(project, ipaddr)

    def initialize(self, project, ipaddr):
        self.init = {}
        with io.open(BASE_FILE, 'r', encoding='utf-8') as f:
            self.merged = nbformat.read(f, as_version=4)
            settings = (
                'project = "%s"\ntarget_host = "%s"\n' % (project, ipaddr))
            self._set_into_cell(self.merged, SETTINGS, settings)
        for target in [DOCKER_COMPOSE, PERMANENT_DIR]:
            self.init[target] = True

    def _get_cell(self, nb, target):
        """Get cell description which is matched with tag information

        If multiple cells found, this method will return 1st matches.
        :param nb: A dictionary for notebook
        :param target: A string of tag description
        :returns: A dict of cell description or None
        :raises: None
        """
        if target not in TARGETS:
            return None
        target_cells = [
            c for c in nb.cells if c.metadata.get("tag") == target]
        return target_cells[0].source if target_cells else None

    def _get_cell_id(self, notebook, target):
        """Return an ID of cell

        :param nb: A dictionary for notebook
        :param target: A string of tag description
        :returns: A dict of cell description or None
        :raises: None
        """
        cell_id = None
        for idx, c in enumerate(notebook.cells):
            if c.metadata.get("tag") == target:
                cell_id = idx
                break
        return cell_id

    def _set_cell(self, notebook, target, src):
        notebook.cells[self._get_cell_id(notebook, target)].source = src

    def _get_tag(self, nb, cell=None):
        if cell is None:
            meta = nb.metadata
        else:
            try:
                in_cell = nb.cells[cell]
            except IndexError as e:
                meta = {}
            else:
                meta = in_cell.metadata
        return meta.get("tag")

    def _get_from_cell(self, notebook, cell):
        return notebook.cells[cell].source

    def _set_into_cell(self, notebook, cell, src):
        notebook.cells[cell].source = src

    def _insert_indent(self, src):
        return ("\n").join([" "*INDENT +s for s in src.split("\n")])


    def merge(self, filenames):
        """Merge definitions in specified files

        :param filenames: A list of string with filename
        :returns: A nbformat.notebooknode.NotebookNode object
        :raises: None
        """
        for filename in filenames:
            with io.open(filename, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
                for target in [_DOCKER_COMPOSE, _PERMANENT_DIR]:
                    self._format(nb, target)
        return self.merged

    def _format(self, nb, target):
        """Return formatted value with specified target cell from notebook

        This method updates an instance value 'self.merged instance value'.

        :param nb: A dictionary for notebook
        :param target: An integer value of cell to read from notebook
        :returns: None
        :raises: None
        """
        if target == _DOCKER_COMPOSE:
            src = self._insert_indent(self._get_cell(nb, target))
        elif target == _PERMANENT_DIR:
            src = self._get_cell(nb, target)
        else:
            src = self._get_cell(nb, target)

        formatted = (
            "%s\n%s" % (self._get_cell(self.merged, target), src))
        self._set_cell(self.merged, target, formatted)

    def write(self, path):
        """Output notebook with specified path

        :param path: A string of output filename
        :returns: None
        :raises: None
        """
        nbformat.write(self.merged, path)
