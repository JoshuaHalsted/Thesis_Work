"""
This module deals with all animals. So far, only dogs are implemented.

# TODO

 - Add the rest of the animals.

"""

class Dog:
    name = str
    """The name of this dog. May contain non-ASCII characters."""
    friends = ["Dog"]
    """Friends this dog has made."""

    def __init__(self, name: str):
        """Make a Dog without any friends (yet)."""
        self.name = name
        self.friends = []

    def bark(self, loud: bool = True):
        """*woof*"""