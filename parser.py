import codecs
import re
import sys
from unroller import Unroller
from map_parser import MapParser
from list_parser import ListParser
from enum import Enum

SUPPRESS_ILLEGAL_IDENTIFIER = '@file:Suppress("IllegalIdentifier")\n'
NEWLINE = "§"
TYPE = '[A-Z][a-zA-Z_0-9<>,]+(, )*[a-zA-Z_0-9<>,]+'  # 2 groups
VAR_NAME = '[a-zA-Z_0-9<>,]+'
VAR_RULE = '^(\s+)(' + TYPE + ')\s+(' + VAR_NAME + ')\s*$§\\1private lateinit var \\4: \\2§'
VAL_RULE = '^(\s+)(' + TYPE + ')\s+(' + VAR_NAME + ')\s*=(.*)§\\1private val \\4: \\2 =\\5§'


class ParsingContext(Enum):
    IMPORTS = 0
    UNROLLING = 1
    MEMBERS = 2
    FUNCTION = 3
    INDETERMINATE = 4


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
        self.replace_rules()
        self.unroll()
        self.replace_var()
        self.replace_val()

        self.replace_maps()
        self.replace_lists()

        return self.spock

    def replace_var(self, ):
        state = ParsingContext.INDETERMINATE
        new_lines = []
        for line in self.spock:
            if 'class' in line:
                state = ParsingContext.MEMBERS
                new_lines.append(line)
                continue

            if state == ParsingContext.MEMBERS:
                print("VARS")
                if len(re.findall(re.compile('^\s*(fun `.*?`\(\)\s*{|@Before)'), line)):
                    new_lines.append(line)
                    state = ParsingContext.INDETERMINATE
                    continue

                pattern, replace = VAR_RULE.split('§')[0:2]
                new_line = re.sub(pattern, replace, line)
                new_lines.append(new_line)
                if new_line != line:
                    print("found match with " + pattern + " on line: " + line + " to " + new_line)
                continue
            new_lines.append(line)
        self.spock = new_lines

    def replace_val(self):
        compiled_pattern = re.compile('^\s*(fun `.*?`\(\)\s*{|@Before)')
        state = ParsingContext.INDETERMINATE
        new_lines = []
        for line in self.spock:
            if 'class' in line:
                state = ParsingContext.MEMBERS
                new_lines.append(line)
                continue

            if state == ParsingContext.MEMBERS:
                print("VALS")
                if len(re.findall(compiled_pattern, line)):
                    new_lines.append(line)
                    state = ParsingContext.INDETERMINATE
                    continue

                pattern, replace = VAL_RULE.split('§')[0:2]
                new_line = re.sub(pattern, replace, line)
                new_lines.append(new_line)
                if new_line != line:
                    print("found match with " + pattern + " on line: " + line + " to " + new_line)
                continue
            new_lines.append(line)
        self.spock = new_lines

    def unroll(self):
        state = ParsingContext.INDETERMINATE
        unroller = Unroller()
        new_lines = []
        for line in self.spock:
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
        self.spock = new_lines

    def replace_maps(self):
        state = ParsingContext.INDETERMINATE
        map_parser = MapParser()
        new_lines = []
        for line in self.spock:
            if 'Map<' in line or 'Map(' in line:
                if map_parser.record(line):
                    state = ParsingContext.INDETERMINATE
                    new_lines.extend(map_parser.get_lines())
                    map_parser = MapParser()
                else:
                    state = ParsingContext.UNROLLING
                continue

            if state == ParsingContext.UNROLLING:
                if map_parser.record(line):
                    state = ParsingContext.INDETERMINATE
                    new_lines.extend(map_parser.get_lines())
                    map_parser = MapParser()
                continue

            new_lines.append(line)
        self.spock = new_lines

    def replace_lists(self):
        pattern = re.compile('\[\D{.*}\]')
        state = ParsingContext.INDETERMINATE
        list_parser = ListParser()
        new_lines = []
        for line in self.spock:
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
        self.spock = new_lines

    def replace_rules(self):
        new_lines = []
        new_lines.append(SUPPRESS_ILLEGAL_IDENTIFIER)
        for (pattern, replace) in self.rules:
            for line in self.spock:
                new_line = re.sub(pattern, replace, line)
                new_lines.append(new_line)
                if new_line != line:
                    print("found match with " + pattern + " on line: " + line + " to " + new_line)
            self.spock = new_lines
            new_lines = []

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
