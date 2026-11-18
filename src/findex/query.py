import re
from dataclasses import dataclass
from abc import ABC, abstractmethod


class QueryNode(ABC):
    @abstractmethod
    def evaluate(self, index):
        pass

    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __invert__(self):
        return Not(self)


@dataclass
class Term(QueryNode):
    value: str

    def evaluate(self, index):
        return {
            posting.doc_id
            for posting in index.get(self.value.casefold(), [])
        }


@dataclass
class Phrase(QueryNode):
    value: str

    def evaluate(self, index):
        words = self.value.casefold().split()

        if not words:
            return set()

        candidates = Term(words[0]).evaluate(index)

        for word in words[1:]:
            candidates &= Term(word).evaluate(index)

        results = set()

        for doc_id in candidates:
            position_lists = []

            for word in words:
                posting = next(
                    (
                        item for item in index.get(word, [])
                        if item.doc_id == doc_id
                    ),
                    None
                )

                if posting is None:
                    break

                position_lists.append(set(posting.positions))

            if len(position_lists) != len(words):
                continue

            for position in position_lists[0]:
                if all(
                    position + offset in position_lists[offset]
                    for offset in range(1, len(words))
                ):
                    results.add(doc_id)
                    break

        return results


@dataclass
class And(QueryNode):
    left: QueryNode
    right: QueryNode

    def evaluate(self, index):
        return self.left.evaluate(index) & self.right.evaluate(index)


@dataclass
class Or(QueryNode):
    left: QueryNode
    right: QueryNode

    def evaluate(self, index):
        return self.left.evaluate(index) | self.right.evaluate(index)


@dataclass
class Not(QueryNode):
    node: QueryNode

    def evaluate(self, index):
        return set(index.documents) - self.node.evaluate(index)


class QueryParser:
    def __init__(self, query):
        self.tokens = re.findall(r'"[^"]*"|\(|\)|[^\s()]+', query)
        self.position = 0

    def current(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def consume(self):
        token = self.current()
        self.position += 1
        return token

    def parse(self):
        if not self.tokens:
            raise ValueError("Empty query")

        result = self.parse_or()

        if self.current() is not None:
            raise ValueError(f"Unexpected token: {self.current()}")

        return result

    def parse_or(self):
        node = self.parse_and()

        while self.current() and self.current().upper() == "OR":
            self.consume()
            node = Or(node, self.parse_and())

        return node

    def parse_and(self):
        node = self.parse_not()

        while self.current() is not None:
            token = self.current()
            upper = token.upper()

            if upper == "OR" or token == ")":
                break

            if upper == "AND":
                self.consume()
                node = And(node, self.parse_not())
            elif upper == "NOT":
                self.consume()
                node = And(node, Not(self.parse_not()))
            else:
                node = And(node, self.parse_not())

        return node

    def parse_not(self):
        if self.current() and self.current().upper() == "NOT":
            self.consume()
            return Not(self.parse_not())

        return self.parse_primary()

    def parse_primary(self):
        token = self.current()

        if token is None:
            raise ValueError("Unexpected end of query")

        if token == "(":
            self.consume()
            node = self.parse_or()

            if self.current() != ")":
                raise ValueError("Missing closing parenthesis")

            self.consume()
            return node

        if token == ")":
            raise ValueError("Unexpected closing parenthesis")

        self.consume()

        if token.startswith('"') and token.endswith('"'):
            return Phrase(token[1:-1])

        if token.upper() in ("AND", "OR", "NOT"):
            raise ValueError(f"Unexpected operator: {token}")

        return Term(token)


def parse_query(query):
    return QueryParser(query).parse()
