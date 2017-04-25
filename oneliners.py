import re


class MockThrowParser(object):
    @staticmethod
    def match(line):
        return ' >> { throw' in line

    @staticmethod
    def replace(line):
        line = re.sub(r'^(\s+)(.*?) >> { throw (.*?) }', '\\1whenever(\\2).thenThrow(\\3)', line)
        return line

class MockParser(object):
    @staticmethod
    def match(line):
        return ' >> ' in line

    @staticmethod
    def replace(line):
        pattern = re.compile(' >> (.+((?= >> )|$))')
        returned = re.findall(pattern, line)
        line = re.sub('^(\s+)(.*?) >> (.*)', '\\1whenever(\\2).thenReturn(', line)
        returned = [a for (a, b) in returned]
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
        return re.search('\[.*:.*\]', line)

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
        return re.search('\s\[\D+.*]', line)

    @staticmethod
    def replace(line):
        line = line.replace('[', 'listOf(')
        line = line.replace(']', ')')
        if ListParser.match(line):
            return ListParser.replace(line)
        return line


class LengthParser(object):
    @staticmethod
    def match(line):
        return re.search('\.length\(\)', line)

    @staticmethod
    def replace(line):
        line = line.replace('.length()', '.length')

        return line


class SizeParser(object):
    @staticmethod
    def match(line):
        return re.search('\.size\(\)', line)

    @staticmethod
    def replace(line):
        line = line.replace('.size()', '.size')

        return line


class ArgumentsNameTypeSwapper(object):
    @staticmethod
    def match(line):
        return re.search('^(\s+)private fun .* {$', line)

    @staticmethod
    def replace(line):
        type = '[A-Z][a-zA-Z_0-9<>,]+(, )*[a-zA-Z_0-9<>,]+'  # 2 groups
        var_name = '[a-zA-Z_0-9<>,]+'
        pattern = re.compile('^(\s+private fun .*\()(.*)(\) {$)')
        match = re.search(pattern, line)

        arguments_list = match.group(2)

        new_list = ''
        generics = 0
        for char in arguments_list:
            if generics == 0 and char is ',':
                char = '§'
            elif char is '<':
                generics += 1
            elif char is '>':
                generics -= 1
            new_list += char

        arguments = []
        for argument in new_list.split('§'):
            arguments.append(re.sub('(' + type + ') (' + var_name + ')', '\\3: \\1', argument))

        return match.group(1) + ','.join(arguments) + match.group(3)


class QuoteReplacer(object):
    @staticmethod
    def match(line):
        return re.search('\'', line)

    @staticmethod
    def replace(line):
        return line.replace('\'', '"')


class VerifyReplacer(object):
    @staticmethod
    def match(line):
        return re.search('^(\s+)(\d{1,3}) \* (.*?)\.(.*)', line)

    @staticmethod
    def replace(line):
        if re.search('^(\s+)(\d{1,3}) \* (.*?)\.(.*)', line).group(2) is '1':
            return re.sub('^(\s+)(\d{1,3}) \* (.*?)\.(.*)', '\\1verify(\\3).\\4', line)
        else:
            return re.sub('^(\s+)(\d{1,3}) \* (.*?)\.(.*)', '\\1verify(\\3, times(\\2)).\\4', line)
