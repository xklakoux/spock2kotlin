import sys

import pyperclip

import oneliners
from declarations import ValsParser
from declarations import VarsParser
from formatter import Formatter
from regexparser import RegexParser
from unroller import Unroller

SUPPRESS_ILLEGAL_IDENTIFIER = '@file:Suppress("IllegalIdentifier")\n'


class SpockParser:
    def __init__(self, spock_path, parsers):
        with open(spock_path) as open_spock_file:
            self.spock = open_spock_file.read().splitlines()
            self.rules = []
            self.parsers = parsers

    def parse(self):
        self.spock.insert(0, SUPPRESS_ILLEGAL_IDENTIFIER)

        self.spock = Formatter.format(self.spock)

        for parser in self.parsers:
            self.spock = parser.parse(self.spock[:])

        new_lines = []
        for line in self.spock:
            for one_liner in one_liners:
                if one_liner.match(line):
                    line = one_liner.replace(line)
            new_lines.append(line)
        self.spock = new_lines

        return self.spock


if __name__ == '__main__':
    spock_file = sys.argv[1]
    kotlin_path = ''.join(sys.argv[1].split('\\')[:-1]) + sys.argv[1].split('\\')[-1].split('.')[0] + "Kt.kt"
    kotlin_path = kotlin_path.replace('/test/groovy', '/test/java')

    one_liners = [oneliners.MockParser, oneliners.MapParser, oneliners.ListParser]
    parsers = [RegexParser, Unroller, VarsParser, ValsParser]

    spock_parser = SpockParser(spock_file, parsers)
    kotlin_lines = spock_parser.parse()

    with open(kotlin_path, "w+") as kotlin_file:

        for line in kotlin_lines:
            kotlin_file.write(line + '\n')

    pyperclip.copy(kotlin_path)
    print("{} has been copied to your clipboard".format(kotlin_path))
