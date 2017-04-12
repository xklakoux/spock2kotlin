import re
from enum import Enum

class MapState(Enum):
    NOT_STARTED = 0
    BEFORE_MAP = 1
    AFTER_MAP = 2
    VALUES = 3
    END = 4


class MapParser(object):
    def __init__(self):
        self.brackets_stack = []
        self.recorded_lines = []
        self.state = MapState.NOT_STARTED

    def record(self, line):
        if '[' in line:
            line = line.replace('[', 'mapOf(')
            self.state = MapState.AFTER_MAP
        if len(re.findall(re.compile('=\s*$'), line)):
            self.state = MapState.BEFORE_MAP
        if ':' in line:
            if self.state == MapState.AFTER_MAP:
                line = re.sub("(.*)mapOf\((.*):(.*)(,)", "\\1mapOf(Pair(\\2,\\3)\\4", line)
                self.state = MapState.VALUES
            elif self.state == MapState.VALUES:
                line = re.sub("(\s*)(.*):(.*)(,)+", "\\1Pair(\\2,\\3)\\4", line)
        if ']' in line:
            line = line.replace(']', ')')
            self.state = MapState.END
        self.recorded_lines.append(line)
        if self.state == MapState.END or self.state == MapState.NOT_STARTED:
            return True
        return False

    def get_lines(self):
        return self.recorded_lines