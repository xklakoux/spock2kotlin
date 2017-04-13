import re

from context import ParsingContext

TYPE = '[A-Z][a-zA-Z_0-9<>,]+(, )*[a-zA-Z_0-9<>,]+'  # 2 groups
VAR_NAME = '[a-zA-Z_0-9<>,]+'
VAR_RULE = '^(\s+)(' + TYPE + ')\s+(' + VAR_NAME + ')\s*$§\\1private lateinit var \\4: \\2§'
VAL_RULE = '^(\s+)(' + TYPE + ')\s+(' + VAR_NAME + ')\s*=(.*)§\\1private val \\4: \\2 =\\5§'


class VarsParser(object):
    @staticmethod
    def parse(spock):
        compiled_pattern = re.compile('^\s*(fun `.*?`\(\)\s*{|@Before)')
        pattern, replace = VAR_RULE.split('§')[0:2]

        state = ParsingContext.INDETERMINATE
        new_lines = []
        for line in spock:
            if 'class' in line:
                state = ParsingContext.MEMBERS
                new_lines.append(line)
                continue

            if state == ParsingContext.MEMBERS:
                print("VARS: " + line)
                if len(re.findall(compiled_pattern, line)):
                    new_lines.append(line)
                    state = ParsingContext.INDETERMINATE
                    continue

                new_line = re.sub(pattern, replace, line)
                new_lines.append(new_line)
                if new_line != line:
                    print("found match with " + pattern + " on line: " + line + " to " + new_line)
                continue
            new_lines.append(line)
        return new_lines


class ValsParser(object):
    @staticmethod
    def parse(spock):
        compiled_pattern = re.compile('^\s*(fun `.*?`\(\)\s*{|@Before)')
        pattern, replace = VAL_RULE.split('§')[0:2]

        state = ParsingContext.INDETERMINATE
        new_lines = []
        for line in spock:
            if 'class' in line:
                state = ParsingContext.MEMBERS
                new_lines.append(line)
                continue

            if state == ParsingContext.MEMBERS:
                print("VALS: " + line)
                if len(re.findall(compiled_pattern, line)):
                    new_lines.append(line)
                    state = ParsingContext.INDETERMINATE
                    continue

                new_line = re.sub(pattern, replace, line)
                new_lines.append(new_line)
                if new_line != line:
                    print("found match with " + pattern + " on line: " + line + " to " + new_line)
                continue
            new_lines.append(line)
        return new_lines
