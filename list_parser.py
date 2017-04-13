import re
from enum import Enum

from context import ParsingContext


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

    @staticmethod
    def parse(spock):
        pattern = re.compile('\[\D{.*}\]')
        state = ParsingContext.INDETERMINATE
        list_parser = ListParser()
        new_lines = []
        for line in spock:
            if line:
                if 'List<' in line or 'List(' in line or len(re.findall(pattern, line)):
                    if list_parser.record(line):
                        state = ParsingContext.INDETERMINATE
                        new_lines.extend(list_parser.get_lines())
                    else:
                        state = ParsingContext.UNROLLING
                    continue

                if state == ParsingContext.UNROLLING:
                    if list_parser.record(line):
                        list = list_parser.get_lines()
                        state = ParsingContext.INDETERMINATE
                        new_lines.extend(list)
                        list_parser = ListParser()
                    continue

            new_lines.append(line)
        return new_lines