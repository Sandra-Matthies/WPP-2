import itertools
from enum import Enum
from typing import Iterator


class TokenType(Enum):
    LPAREN = 1
    RPAREN = 2
    PHRASE = 3
    PROX_K = 4
    AND = 6
    OR = 7
    NOT = 8
    TERM = 9


class Token:
    """
    Represents a logical token in the input string.
    The contents of `value` depend on the `type` of the token.
    """

    def __init__(self, pos: int, value: str, type: TokenType):
        self.pos = pos
        self.end = pos + len(value)
        self.value = value
        self.type = type

    def __repr__(self) -> str:
        return f"{self.pos}-{self.end} {self.type} {self.value}"


def lex(input: str) -> Iterator[Token]:
    """
    Tokenizes the input string.
    """
    i = 0
    c = None

    while i < len(input):
        c = input[i]

        if c == '"':
            phrase = "".join(itertools.takewhile(lambda x: x != '"', input[i + 1 :]))
            j = i
            i += len(phrase) + 2
            yield Token(j, phrase, TokenType.PHRASE)
        elif c == "(":
            yield Token(i, c, TokenType.LPAREN)
        elif c == ")":
            yield Token(i, c, TokenType.RPAREN)
        elif c.isspace():
            pass
        elif c == "/" and i + 1 < len(input):
            k = "".join(itertools.takewhile(lambda x: x.isdigit(), input[i + 1 :]))
            chars = Token(i, k, TokenType.PROX_K)
            i += len(k)
            yield chars
        else:
            chars = "".join(itertools.takewhile(lambda x: x.isalnum(), input[i:]))

            j = i
            i += len(chars) - 1

            match chars:
                case "AND":
                    yield Token(j, chars, TokenType.AND)
                case "OR":
                    yield Token(j, chars, TokenType.OR)
                case "NOT":
                    yield Token(j, chars, TokenType.NOT)
                case _:
                    yield Token(j, chars, TokenType.TERM)

        i += 1


class QueryType(Enum):
    TERM = 1
    PROX = 2
    PHRASE = 3
    OR = 4
    GROUP = 5


class Query:
    """
    Represents one independent query.
    It can be a subquery of a larger query, but it can be evaluated
    independently.
    """

    def __init__(self, type: QueryType, is_not: bool = False):
        self.type = type
        self.is_not = is_not

    def __repr__(self) -> str:
        return "NOT " if self.is_not else ""


class TermQuery(Query):
    """
    Represents the easiest query, a single term query.

    Example:
        term1
    """

    def __init__(self, term: str):
        super().__init__(QueryType.TERM)
        self.term = term

    def __repr__(self) -> str:
        return super().__repr__() + str(self.term)


class ProxQuery(Query):
    """
    Represents a proximity query.

    Example:
        term1 /4 term2
    """

    def __init__(self, term_a: str, term_b: str, k: int):
        super().__init__(QueryType.PROX)
        self.term_a = term_a
        self.term_b = term_b
        self.k = k

    def __repr__(self) -> str:
        return super().__repr__() + f"{self.term_a} /{str(self.k)} {self.term_b}"


class PhraseQuery(Query):
    """
    Represents a phrase query.

    Example:
        "term1 term2"
    """

    def __init__(self, phrase: str):
        super().__init__(QueryType.PHRASE)
        self.phrase = phrase
        self.parts = phrase.split()

    def __repr__(self) -> str:
        return super().__repr__() + f'"{self.phrase}"'


class OrQuery(Query):
    """
    Represents an OR query that can consist of multiple, even nested (grouped)
    subqueries.

    Examples:
        term1 OR term2 OR term3
        term1 OR NOT (term2 OR NOT term3)
        (term1 OR NOT (term2 OR term3))
    """

    def __init__(self, *parts: Query):
        super().__init__(QueryType.OR)
        self.parts = parts

    def __repr__(self) -> str:
        parts = map(lambda x: x.__repr__(), self.parts)
        return super().__repr__() + f"{' OR '.join(parts)}"


class GroupQuery(Query):
    """
    Represents a grouped query, which consists of multiple `AND` queries.
    """

    def __init__(self, *and_queries: Query):
        super().__init__(QueryType.GROUP)
        self.and_queries = and_queries

    def __repr__(self) -> str:
        parts = map(lambda x: x.__repr__(), self.and_queries)
        return super().__repr__() + f"({' AND '.join(parts)})"


def parse(input: str) -> list[Query]:
    """
    Parses the input string into a list of queries.
    """
    tokens = list(lex(input))
    return _parse_internal(tokens)


def _parse_internal(tokens):
    """
    Internal implementation to parse the input string into a list of queries.

    The parser is implemented recursively and the gist is as follows:
        TODO
    """
    and_queries = []
    query_part = None
    negate = False
    i = 0

    def add_query(query):
        nonlocal negate
        nonlocal query_part

        if negate:
            query.is_not = True

        negate = False
        and_queries.append(query)
        query_part = None

    while i < len(tokens):
        t = tokens[i]

        match t.type:
            case TokenType.NOT:
                negate = not negate
            case TokenType.AND:
                add_query(query_part)
            case TokenType.OR:
                # TODO: documentation
                idx_next_and = None
                for j in range(i + 1, len(tokens)):
                    if tokens[j].type == TokenType.AND:
                        idx_next_and = j
                        break

                or_queries = []
                processed_tokens = None

                if idx_next_and is not None:
                    or_queries = _parse_internal(tokens[i + 1 : idx_next_and])
                    processed_tokens = len(tokens[i + 1 : idx_next_and])
                else:
                    or_queries = _parse_internal(tokens[i + 1 :])
                    processed_tokens = len(tokens[i + 1 :])

                flattened = []

                def flatten(or_query_parts):
                    for part in or_query_parts:
                        if part.type == QueryType.OR:
                            flatten(part.parts)
                        else:
                            flattened.append(part)

                flatten(or_queries)
                i += processed_tokens

                query_part.is_not = negate
                negate = False

                flattened.insert(0, query_part)
                query_part = OrQuery(*flattened)

            case TokenType.PROX_K:
                query_part = ProxQuery(
                    query_part, TermQuery(tokens[i + 1].value), int(t.value)
                )
                i += 1
            case TokenType.PHRASE:
                query_part = PhraseQuery(t.value)
            case TokenType.TERM:
                query_part = TermQuery(t.value)
            case TokenType.LPAREN:
                # TODO: documentation
                idx_rparen = None
                for j in range(i + 1, len(tokens)):
                    if tokens[j].type == TokenType.RPAREN:
                        idx_rparen = j
                        break

                paren_queries = _parse_internal(tokens[i + 1 : idx_rparen])
                processed_tokens = len(tokens[i + 1 : idx_rparen])
                query_part = GroupQuery(*paren_queries)
                query_part.is_not = negate
                negate = False
                i += processed_tokens
            case TokenType.RPAREN:
                # Not needed.
                pass

        i += 1

    # We only add to the list when encountering an `AND` token.
    # So we have to manually add the last query part.
    if query_part is not None:
        add_query(query_part)

    return and_queries
