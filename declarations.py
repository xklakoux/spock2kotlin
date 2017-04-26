import re

from context import ParsingContext

TYPE = '[A-Z][a-zA-Z_0-9<>,.]+(, )*[a-zA-Z_0-9<>,.]+'  # 2 groups
VAR_NAME = '[a-zA-Z_0-9<>,]+'
MEMBER_VAR_RULE = '^(\s+)(val )?(' + TYPE + ')\s+(' + VAR_NAME + ')\s*$§\\1private lateinit var \\5: \\3§'
MEMBER_VAL_RULE = '^(\s+)(val )?(' + TYPE + ')\s+(' + VAR_NAME + ')\s*=(.*)§\\1private val \\5: \\3 =\\6§'
LOCAL_VAL_RULE = '^(\s+)(val )?(' + TYPE + ')\s+(' + VAR_NAME + ')\s*=(.*)§\\1val \\5: \\3 =\\6§'
END_MEMBERS_PATTERN = re.compile('^.*\s+(fun .*{)')


class VarsParser(object):
    @staticmethod
    def parse(spock):
        pattern, replace = MEMBER_VAR_RULE.split('§')[0:2]
        state = ParsingContext.INDETERMINATE
        new_lines = []
        for line in spock:
            if 'class' in line:
                state = ParsingContext.MEMBERS
                new_lines.append(line)
                continue

            if state == ParsingContext.MEMBERS:

                if len(re.findall(END_MEMBERS_PATTERN, line)):
                    new_lines.append(line)
                    state = ParsingContext.FUNCTION
                    continue
                new_line = re.sub(pattern, replace, line)
                new_lines.append(new_line)
                continue
            new_lines.append(line)

        return new_lines


class ValsParser(object):
    @staticmethod
    def parse(spock):
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
                if len(re.findall(END_MEMBERS_PATTERN, line)):
                    new_lines.append(line)
                    state = ParsingContext.FUNCTION
                    pattern, replace = LOCAL_VAL_RULE.split('§')[0:2]
                    continue

                new_line = re.sub(pattern, replace, line)
                new_lines.append(new_line)
                continue

            if state == ParsingContext.FUNCTION:
                new_line = re.sub(pattern, replace, line)
                new_lines.append(new_line)
                continue
            new_lines.append(line)
        return new_lines


class SwapPrivateToProtectedParser(object):
    @staticmethod
    def parse(spock):

        for line in spock:
            if 'Parameterized' in line:
                break
        else:
            return spock

        pattern, replace = '', ''
        state = ParsingContext.INDETERMINATE
        new_lines = []
        for line in spock:
            if 'class' in line:
                state = ParsingContext.MEMBERS
                new_lines.append(line)
                continue

            if state == ParsingContext.MEMBERS:
                if len(re.findall(END_MEMBERS_PATTERN, line)):
                    state = ParsingContext.FUNCTION
                    new_lines.append(re.sub('private', 'protected', line))
                    continue

                new_lines.append(re.sub('private', 'protected', line))
                continue

            if state == ParsingContext.FUNCTION:
                if len(re.findall(END_MEMBERS_PATTERN, line)):
                    new_lines.append(re.sub('private', 'protected', line))
                    continue

            new_lines.append(line)
        return new_lines
