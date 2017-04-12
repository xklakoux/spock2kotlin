from enum import Enum
import re


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
        for set_index, set in enumerate(self.values):
            method_name = self.recorded_lines[0]
            for name_index, name in enumerate(self.names):
                method_name = method_name.replace("#{}".format(name), set[name_index].strip('"'))
            new_tests.append(method_name)
            for line in self.recorded_lines[1:]:

                for name_index, name in enumerate(self.names):
                    line = line.replace(name, set[name_index])
                new_tests.append(line)
            new_tests.append('')
        return new_tests