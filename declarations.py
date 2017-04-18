import re

from context import ParsingContext

TYPE = '[A-Z][a-zA-Z_0-9<>,]+(, )*[a-zA-Z_0-9<>,]+'  # 2 groups
VAR_NAME = '[a-zA-Z_0-9<>,]+'
MEMBER_VAR_RULE = '^(\s+)(val )?(' + TYPE + ')\s+(' + VAR_NAME + ')\s*$§\\1private lateinit var \\5: \\3§'
MEMBER_VAL_RULE = '^(\s+)(val )?(' + TYPE + ')\s+(' + VAR_NAME + ')\s*=(.*)§\\1private val \\5: \\3 =\\6§'
LOCAL_VAL_RULE = '^(\s+)(' + TYPE + ')\s+(' + VAR_NAME + ')\s*=(.*)§\\1val \\4: \\2 =\\5§'


class VarsParser(object):
    @staticmethod
    def parse(spock):
        compiled_pattern = re.compile('^\s*(fun `.*?`\(\)\s*{|@Before)')
        pattern, replace = MEMBER_VAR_RULE.split('§')[0:2]
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
                    state = ParsingContext.FUNCTION
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
        pattern, replace = '', ''
        state = ParsingContext.INDETERMINATE
        new_lines = []
        for line in spock:
            if 'class' in line:
                state = ParsingContext.MEMBERS
                pattern, replace = MEMBER_VAL_RULE.split('§')[0:2]
                new_lines.append(line)
                continue

            if state == ParsingContext.MEMBERS:
                print("VALS: " + line)
                if len(re.findall(compiled_pattern, line)):
                    new_lines.append(line)
                    state = ParsingContext.FUNCTION
                    pattern, replace = LOCAL_VAL_RULE.split('§')[0:2]
                    continue

                new_line = re.sub(pattern, replace, line)
                new_lines.append(new_line)
                if new_line != line:
                    print("found match with " + pattern + " on line: " + line + " to " + new_line)
                continue

            if state == ParsingContext.FUNCTION:
                new_line = re.sub(pattern, replace, line)
                new_lines.append(new_line)
                if new_line != line:
                    print("found match with " + pattern + " on line: " + line + " to " + new_line)

                continue
            new_lines.append(line)
        return new_lines
