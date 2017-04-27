import re


class Formatter:
    @staticmethod
    def format(lines):
        replacement_lines = []
        last_line = '§'
        braces_stack = 0

        for line in lines:
            match = re.search('^(\s+)(\S+.*)', line)
            if match and len(match.group(1)) > braces_stack * 4:
                last_line += match.group(2)
            else:
                if last_line is not '§':
                    replacement_lines.append(last_line.rstrip(';'))
                last_line = line

            for char in line:
                if char == '{':
                    braces_stack += 1
                elif char == '}':
                    braces_stack -= 1
        replacement_lines.append(last_line)

        # remove double blank lines
        previous_line = replacement_lines[0]
        formatted_lines = [previous_line]
        for line in replacement_lines[1:]:
            if re.search('\S', line) or re.search('\S', previous_line):
                formatted_lines.append(line)
                previous_line = line

        # remove last line if empty
        if not re.match('\S', formatted_lines[-1]):
            formatted_lines.pop()

        return formatted_lines

    @staticmethod
    def removeDoubleEmptyLines(spock):

        previous_line = spock[0]
        formatted_lines = [previous_line]
        for line in spock[1:]:
            if re.search('\S', line) or re.search('\S', previous_line):
                formatted_lines.append(line)
                previous_line = line

        return formatted_lines
