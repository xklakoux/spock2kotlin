from enum import Enum


class ListState(Enum):
    START = 0
    END = 1


class ListParser(object):
    def __init__(self):
        self.brackets_stack = []
        self.recorded_lines = []
        self.state = ListState.START

    def record(self, line):
        if '[' in line:
            line = line.replace('[', 'listOf(')
        if ']' in line:
            line = line.replace(']', ')')
            self.state = ListState.END
        self.recorded_lines.append(line)
        if self.state == ListState.END:
            return True
        return False

    def get_lines(self):
        return self.recorded_lines
