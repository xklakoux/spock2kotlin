import re
from enum import Enum

from context import ParsingContext


class UnrollerState(Enum):
    START = 0
    NAMES = 1
    VALUES = 2
    END = 3


class Unroller(object):
    unroll_big = False

    def __init__(self, unroll_big):
        self.brackets_stack = []
        self.names = []
        self.values = []
        self.recorded_lines = []
        self.givens = []
        self.state = UnrollerState.START
        self.all_lines = []
        Unroller.unroll_big = unroll_big

    def record(self, line):
        self.all_lines.append(line)
        if self.state == UnrollerState.NAMES:
            line = line.replace('||', '|')
            self.names = [var.strip() for var in line.split('|')]
            self.all_lines.pop()
            self.state = UnrollerState.VALUES
            return False

        elif self.state == UnrollerState.VALUES:
            if '|' in line:
                line = line.replace('||', '|')
                self.values.append([var.strip() for var in line.split('|')])
                self.all_lines.pop()
                return False
            elif '=' in line:
                self.givens.append(line)
                return False
            else:
                self.state = UnrollerState.END

        if 'where:' in line:
            if not re.search('\S', self.recorded_lines[-1]):
                self.recorded_lines.pop()

            if not re.search('\S', self.all_lines[-1]):
                self.all_lines.pop()

            self.state = UnrollerState.NAMES
            self.all_lines.pop()
            return False

        self.recorded_lines.append(line)

        if self.state == UnrollerState.START or self.state == UnrollerState.END:
            if '}' in line:
                return True

        return False

    def unroll_tests(self):

        if len(self.values) > 3 and not Unroller.unroll_big:
            return self.get_parameterized_template()

        self.givens = ['val ' + given for given in self.givens]

        new_tests = []
        for set_index, _set in enumerate(self.values):
            method_name = self.recorded_lines[0]
            for name_index, name in enumerate(self.names):
                method_name = method_name.replace("#{}".format(name), _set[name_index].strip().strip('"'))
                method_name = self.replace_invalid_chars(method_name)
            new_tests.append(method_name)

            new_givens = []
            for given in self.givens:
                for name_index, name in enumerate(self.names):
                    given = re.sub(r'([^.]){}(\b)'.format(name), '\g<1>' + _set[name_index] + '\g<2>', given)
                new_tests.append(given)
            new_tests.extend(new_givens)

            for line in self.recorded_lines[1:]:
                for name_index, name in enumerate(self.names):
                    line = re.sub(r'([^.]){}(\b)'.format(name), '\g<1>' + _set[name_index] + '\g<2>', line)
                new_tests.append(line)
            new_tests.append('')
        return new_tests

    def replace_invalid_chars(self, method_name):
        method_name = method_name.replace(',', '[coma]')
        method_name = method_name.replace('.', '[dot]')
        method_name = method_name.replace('[', '(')
        method_name = method_name.replace(']', ')')
        method_name = method_name.replace(':', '')
        method_name = method_name.replace('\\n', ' newline ')
        method_name = method_name.replace('\\', ' [slash] ')

        return method_name

    @staticmethod
    def parse(spock):
        state = ParsingContext.INDETERMINATE
        unroller = Unroller(Unroller.unroll_big)
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
                    unroller = Unroller(Unroller.unroll_big)
                continue

            new_lines.append(line)
        return new_lines

    def get_parameterized_template(self):
        class_name = re.search('`(.*)`', self.all_lines[0]).group(1)

        coma_separator = ',\n'
        parameters = coma_separator.join(["private val " + name + ": " for name in self.names])
        values = coma_separator.join(['{ arrayOf(' + ', '.join(vals) + ') }' for vals in self.values])

        pipe_whitespace = ' |\n' + ' ' * 48
        names = pipe_whitespace.join([name + ' {' + str(index) + '}' for index, name in enumerate(self.names)])

        parameterized_template = '''
        @RunWith(Parameterized::class)
class `{}`({}) : Setup() {{

    companion object {{
        @JvmStatic
        @Parameterized.Parameters(name = """{}
                                            """)
        fun data() = createData({})
    }}         
        '''.format(class_name, parameters, names, values)
        self.all_lines.insert(0, parameterized_template)
        self.all_lines.append("}")
        return self.all_lines
