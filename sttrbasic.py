import re
from dataclasses import dataclass
from pathlib import Path
from typing import Pattern, Match, Optional, Iterator

import click


@click.command()
@click.argument('source', default=Path(__file__).with_name('STTR1.bas').read_text())
def main(source: str):
    for stmt in Parser().parse(text=source):
        print(stmt)


KEYWORD = dict(
    REM=re.compile('REM'),
    DIM_NUMERIC=re.compile('DIM(?= +[A-Z][^$])'),
    DIM_STRING=re.compile('DIM(?= +[A-Z]\\$)'),
    DIM_ARRAY=re.compile('DIM(?= +[A-Z]\\[)'),
    ASSIGNMENT_NUMERIC=re.compile('(?=[A-Z][0-9]?=)'),
    ASSIGNMENT_STRING=re.compile('(?=[A-Z]\\$)'),
    ASSIGNMENT_ARRAY=re.compile('(?=[A-Z]\\[)'),
    DEF=re.compile('DEF'),
    MAT=re.compile('MAT'),
    PRINT=re.compile('PRINT'),
    IMAGE=re.compile('IMAGE'),
    INPUT=re.compile('INPUT'),
    GOTO=re.compile('GOTO'),
    GOSUB=re.compile('GOSUB'),
    RETURN=re.compile('RETURN'),
    IF=re.compile('IF'),
    FOR=re.compile('FOR'),
    NEXT=re.compile('NEXT'),
    END=re.compile('END'),
)


@dataclass
class REM:
    line_nr: int
    comment: str

    def __str__(self):
        return f'{self.line_nr} REM {self.comment}'


class Parser:
    def __init__(self):
        self.text = ''
        self.line_nr = 1
        self.pos = 0
        self.line_start = 0

    def parse(self, text: str) -> Iterator:
        self.text = text
        self.line_nr = 0
        self.pos = 0
        self.line_start = 0

        while self.pos < len(self.text):
            self.line_nr += 1
            line_nr: Optional[int] = self.consume_optional_line_nr()
            if line_nr is None:
                self.skip_line()
                continue

            keyword: str = self.consume_keyword()

            if keyword == 'REM':
                yield REM(line_nr=line_nr,
                          comment=self.consume_rest_of_line())
            else:
                print(f'{line_nr} {keyword} NOT YET IMPLEMENTED')
                self.skip_line()

    def consume_optional_line_nr(self) -> Optional[int]:
        self.skip(WHITESPACE)
        m = LINE_NR.match(self.text[self.pos:])
        if m:
            return int(self.consume_match(match=m))
        else:
            return None

    def consume_keyword(self) -> str:
        self.skip(WHITESPACE)

        for keyword, pattern in KEYWORD.items():

            m: Match = pattern.match(self.text[self.pos:])
            if m is not None:
                return self.consume_match(match=m)
        raise self.parse_error(msg=f'invalid statement')

    def consume(self, p: Pattern) -> str:
        m = p.match(self.text[self.pos:])
        if not m:
            raise self.parse_error(msg=f'expected pattern: /{p}/')
        return self.consume_match(match=m)

    def consume_match(self, match: Match) -> str:
        t = self.text[self.pos:self.pos + match.span()[1]]
        self.pos += match.span()[1]
        return t

    def skip(self, p: Pattern):
        m = p.match(self.text[self.pos:])
        advance = m.span()[1] if m else 0
        self.pos += advance

    def skip_line(self):
        i = self.text.find('\n', self.pos)
        if i >= 0:
            self.pos = min(i + 1, len(self.text))
        else:
            self.pos = len(self.text)
        self.line_start = self.pos

    def consume_rest_of_line(self) -> str:
        i = self.text.find('\n', self.pos)
        old_pos = self.pos
        if i >= 0:
            self.pos = min(i + 1, len(self.text))
        else:
            self.pos = len(self.text)
        self.line_start = self.pos
        return self.text[old_pos:i]

    def parse_error(self, msg: str):
        return ParseError(line_nr=self.line_nr, pos=self.pos - self.line_start, msg=msg)







class ParseError(BaseException):
    def __init__(self, line_nr: int, pos: int, msg: str):
        super().__init__(f'at {line_nr}:{pos} {msg}')
        self.line_nr = line_nr
        self.pos = pos


WHITESPACE = re.compile('[ \t]*')
LINE_NR = re.compile('[0-9]+')


if __name__ == '__main__':
    main()
