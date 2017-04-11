
class Unroller(object):
    brackets_stack = []
    names = []
    values = []
    recorded_lines = []
    in_names = False
    in_values = False

    def record(self, line):

        if self.in_names:
            self.names = [var.strip() for var in line.split('|')]
            self.in_values = True
            self.in_names = False
            return False

        elif self.in_values:
            if '|' in line:
                self.values.append([var.strip() for var in line.split('|')])
            else:
                self.in_values = False
            return False

        if 'where:' in line:
            self.in_names = True
            return False

        self.recorded_lines.append(line)

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
