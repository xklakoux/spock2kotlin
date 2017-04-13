from enum import Enum

from context import ParsingContext


class UnrollerState(Enum):
    START = 0
    NAMES = 1
    VALUES = 2
    END = 3


class Unroller(object):
    def __init__(self):
        self.brackets_stack = []
        self.names = []
        self.values = []
        self.recorded_lines = []
        self.state = UnrollerState.START

    def record(self, line):

        if self.state == UnrollerState.NAMES:
            self.names = [var.strip() for var in line.split('|')]
            self.state = UnrollerState.VALUES
            return False

        elif self.state == UnrollerState.VALUES:
            if '|' in line:
                self.values.append([var.strip() for var in line.split('|')])
            else:
                self.state = UnrollerState.END
            return False

        if 'where:' in line:
            self.state = UnrollerState.NAMES
            return False

        self.recorded_lines.append(line)

        if self.state == UnrollerState.START or self.state == UnrollerState.END:
            for char in line:
                if char == '{':
                    self.brackets_stack.append('{')
                if char == '}':
                    self.brackets_stack.pop()
                    if not len(self.brackets_stack):
                        return True

        return False

    def unroll_tests(self):
        new_tests = []
        for set_index, value_set in enumerate(self.values):
            method_name = self.recorded_lines[0]
            for name_index, name in enumerate(self.names):
                method_name = method_name.replace("#{}".format(name), value_set[name_index].strip('"'))
            new_tests.append(method_name)
            for line in self.recorded_lines[1:]:

                for name_index, name in enumerate(self.names):
                    line = line.replace(name, value_set[name_index])
                new_tests.append(line)
            new_tests.append('')
        return new_tests

    @staticmethod
    def parse(spock):
        state = ParsingContext.INDETERMINATE
        unroller = Unroller()
        new_lines = []
        for line in spock:
            if '@Unroll' in line:
                state = ParsingContext.UNROLLING
                continue

            if state == ParsingContext.UNROLLING:
                if unroller.record(line):
                    new_tests = unroller.unroll_tests()
                    state = ParsingContext.INDETERMINATE
                    new_lines.extend(new_tests)
                    unroller = Unroller()
                continue

            new_lines.append(line)
        return new_lines
