import sys

from list_parser import ListParser
from map_parser import MapParser
from regexparser import RegexParser
import pyperclip

from unroller import Unroller
from members import ValsParser
from members import VarsParser

SUPPRESS_ILLEGAL_IDENTIFIER = '@file:Suppress("IllegalIdentifier")\n'

class SpockParser(object):
    def __init__(self, spock_path, parsers):
        with open(spock_path) as open_spock_file:
            self.spock = open_spock_file.read().splitlines()
            self.rules = []
            self.parsers = parsers

    def parse(self):
        self.spock.insert(0, SUPPRESS_ILLEGAL_IDENTIFIER)

        for parser in self.parsers:
            self.spock = parser.parse(self.spock[:])

        return self.spock


if __name__ == '__main__':
    spock_file = sys.argv[1]
    kotlin_path = ''.join(sys.argv[1].split('\\')[:-1]) + sys.argv[1].split('\\')[-1].split('.')[0] + "Kt.kt"
    kotlin_path = kotlin_path.replace('/test/groovy', '/test/java')

    parsers = [RegexParser, Unroller, VarsParser, ValsParser, MapParser, ListParser]

    spock_parser = SpockParser(spock_file, parsers)
    kotlin_lines = spock_parser.parse()

    with open(kotlin_path, "w+") as kotlin_file:

        for line in kotlin_lines:
            kotlin_file.write(line + '\n')

    pyperclip.copy(kotlin_path)
    print("{} has been copied to your clipboard".format(kotlin_path))
