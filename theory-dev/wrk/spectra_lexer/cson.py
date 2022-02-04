from io import StringIO
from typing import TextIO


class CommentRemover(StringIO):
    def __init__(self, source: TextIO, comment_prefix="#"):
        super().__init__()
        self._comment_prefix = comment_prefix
        for line in source:
            # Only take content that does not start with comment
            if not line.strip().startswith(self._comment_prefix):
                self.write(line)
        self.seek(0)
