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
                    replacement_lines.append(last_line)
                last_line = line

            for char in line:
                if char == '{':
                    braces_stack += 1
                elif char == '}':
                    braces_stack -= 1
        replacement_lines.append(last_line)
        return replacement_lines
