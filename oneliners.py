import re


class MockParser(object):
    @staticmethod
    def match(line):
        return ' >> ' in line

    @staticmethod
    def replace(line):
        pattern = re.compile(' >> (\S+)')
        returned = re.findall(pattern, line)
        line = re.sub('^(\s+)(.*?) >> (.*)', '\\1whenever(\\2).thenReturn(', line)
        if len(returned) > 1:
            line = line + ', '.join(returned) + ')'
        else:
            line = line + returned[0] + ')'
        return line

class DifferentMockParser(object):
    @staticmethod
    def match(line):
        return ' >>> ' in line

    @staticmethod
    def replace(line):
        pattern = re.compile(' >>> (\S+)')
        returned = re.findall(pattern, line)
        line = re.sub('^(\s+)(.*?) >>> (.*)', '\\1whenever(\\2).thenReturn(', line)
        if len(returned) > 1:
            line = line + ', '.join(returned) + ')'
        else:
            line = line + returned[0] + ')'
        return line


class MapParser(object):
    @staticmethod
    def match(line):
        return re.match('.*\[.*:.*\].*', line)

    @staticmethod
    def replace(line):
        generics = 0
        brackets = 0
        initialized = False

        new_line = ''
        for char in line:
            if char is '[':
                initialized = True

            if not initialized:
                if char is ':':
                    char = '~'
                new_line += char
                continue

            if char is '(':
                brackets += 1
            elif char is ')':
                brackets -= 1
            elif char is '<':
                generics += 1
            elif char is '>':
                generics -= 1
            elif char is ',' and generics == 0 and brackets == 0:
                char = '§'

            new_line += char

        line = new_line

        line = line.replace('[', 'mapOf(Pair(')
        line = line.replace(']', '))')
        line = line.replace(':', ',')
        line = line.replace('~', ':', 1)
        line = line.replace('§', '),Pair(')
        return line


class ListParser(object):
    @staticmethod
    def match(line):
        return re.match('.*\[\D+].*', line)

    @staticmethod
    def replace(line):
        line = line.replace('[', 'listOf(')
        line = line.replace(']', ')')

        return line
