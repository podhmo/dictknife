def setup(app):
    # monkey patch
    import os.path
    from difflib import unified_diff
    from sphinx.directives.code import LiteralIncludeReader

    def show_diff(self, location=None):
        new_lines = self.read_file(self.filename)
        old_filename = self.options.get('diff')
        old_lines = self.read_file(old_filename)
        diff = unified_diff(old_lines, new_lines, os.path.basename(old_filename), os.path.basename(self.filename))
        return list(diff)

    LiteralIncludeReader.show_diff = show_diff

    return {"version": "0.0"}
