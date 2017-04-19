import codecs
import re

NEWLINE = "§"
CONFIGURATION_PATH = 'rules.conf'


class RegexParser(object):

    @staticmethod
    def get_rules():
        rules = []
        with codecs.open(CONFIGURATION_PATH, 'r', 'utf-8') as conf_file:
            for rule in conf_file.readlines():
                if not rule.startswith('#'):
                    pattern, replace = rule.split(NEWLINE)[0:2]
                    rules.append((pattern, replace.strip('\n')))

        return rules

    @staticmethod
    def parse(spock):
        new_lines = []
        rules = RegexParser().get_rules()
        for (pattern, replace) in rules:
            for codeline in spock:
                new_line = re.sub(pattern, replace, codeline)
                new_lines.append(new_line)
                if not new_line and new_line != codeline:
                    new_lines.pop()
            spock = new_lines
            new_lines = []
        return spock
