import os
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
    def __init__(self, spock_path, parsers, one_liners):
        with open(spock_path, encoding="utf-8") as open_spock_file:
            self.spock = open_spock_file.read().splitlines()
            self.rules = []
            self.parsers = parsers
            self.one_liners = one_liners

    def parse(self):
        self.spock.insert(0, SUPPRESS_ILLEGAL_IDENTIFIER)

        self.spock = Formatter.format(self.spock)

        for parser in self.parsers:
            self.spock = parser.parse(self.spock[:])

        new_lines = []
        for line in self.spock:
            for one_liner in self.one_liners:
                if one_liner.match(line):
                    line = one_liner.replace(line)
            new_lines.append(line)
        self.spock = new_lines

        return self.spock


if __name__ == '__main__':

    one_liners = [oneliners.MockParser, oneliners.DifferentMockParser, oneliners.MapParser, oneliners.ListParser,
                  oneliners.LengthParser, oneliners.SizeParser, oneliners.FunNameTypeSwapper, oneliners.QuoteReplacer]
    parsers = [RegexParser, Unroller, VarsParser, ValsParser]

    if len(sys.argv) != 2:
        print("Please provide one argument that is:\n a groovy file\n test/groovy that will be scanned recursively")
        sys.exit(0)

    if os.path.isdir(sys.argv[1]):
        for path, subdirs, files in os.walk(sys.argv[1]):
            for name in files:
                spock_file = os.path.join(path, name)
                kotlin_path = ''.join(spock_file.split('\\')[:-1]) + spock_file.split('\\')[-1].split('.')[0] + "Kt.kt"
                kotlin_path = kotlin_path.replace('/test/groovy', '/test/kotlin')

                spock_parser = SpockParser(spock_file, parsers, one_liners)
                kotlin_lines = spock_parser.parse()

                os.makedirs(os.path.dirname(kotlin_path), exist_ok=True)
                with open(kotlin_path, "w+", encoding="utf-8") as kotlin_file:

                    for line in kotlin_lines:
                        kotlin_file.write(line + '\n')
                    print('Kotlin file {} created'.format(kotlin_path))
    else:
        spock_file = sys.argv[1]
        kotlin_path = ''.join(sys.argv[1].split('\\')[:-1]) + sys.argv[1].split('\\')[-1].split('.')[0] + "Kt.kt"
        kotlin_path = kotlin_path.replace('/test/groovy', '/test/java')

        spock_parser = SpockParser(spock_file, parsers, one_liners)
        kotlin_lines = spock_parser.parse()

        os.makedirs(os.path.dirname(kotlin_path), exist_ok=True)
        with open(kotlin_path, "w+", encoding="utf-8") as kotlin_file:

            for line in kotlin_lines:
                kotlin_file.write(line + '\n')
            print('Kotlin file in {} created'.format(kotlin_path))

        pyperclip.copy(kotlin_path)
        print("{} has been copied to your clipboard".format(kotlin_path))