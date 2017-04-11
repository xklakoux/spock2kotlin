import codecs
import re
import sys
from unroller import Unroller

SUPPRESS_ILLEGAL_IDENTIFIER = '@file:Suppress("IllegalIdentifier")\n'
NEWLINE = "§"


class SpockParser(object):
    spock = []
    configuration = ''
    rules = []

    def __init__(self, spock_path, conf_path):
        with open(spock_path) as g, open(conf_path) as c:
            self.spock = g.read().splitlines()
            self.configuration = conf_path
            self.parse_configuration()

    def parse_spock(self):
        new_lines = []
        new_lines.append(SUPPRESS_ILLEGAL_IDENTIFIER)
        record_lines = False
        unroller = Unroller()

        for (pattern, replace) in self.rules:
            for line in self.spock:

                new_line = re.sub(pattern, replace, line)
                new_lines.append(new_line)
                if new_line != line:
                    print("found match with " + pattern + " on line: " + line)
            self.spock = new_lines
            new_lines = []

        new_lines = []
        for line in self.spock:
            if '@Unroll' in line:
                record_lines = True
                continue

            if record_lines:
                if unroller.record(line):
                    new_tests = unroller.unroll_tests()
                    record_lines = False
                    new_lines.extend(new_tests)
                    unroller = Unroller()
                continue
            new_lines.append(line)

        self.spock = new_lines
        return self.spock

    def parse_configuration(self):
        with codecs.open(self.configuration, 'r', 'utf-8') as conf_file:
            for rule in conf_file.readlines():
                if not rule.startswith('#'):
                    pattern, replace = rule.split('§')[0:2]
                    self.rules.append((pattern, replace.strip('\n')))


if __name__ == '__main__':
    spock_file = sys.argv[1]
    configuration = 'rules.conf'
    kotlin_path = ''.join(sys.argv[1].split('\\')[:-1]) + sys.argv[1].split('\\')[-1].split('.')[0] + ".kt"

    parser = SpockParser(spock_file, configuration)
    kotlin_lines = parser.parse_spock()

    with open(kotlin_path, "w+") as kotlin_file:

        for line in kotlin_lines:
            kotlin_file.write(line + '\n')