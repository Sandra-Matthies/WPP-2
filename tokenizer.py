import re


def tokenize(path):
    """
    Returns an iterator of token strings where each token matches
    the following regex: [a-z0-9']+
    """
    token_pos = 0
    with open(path, "r") as f:
        while True:
            line = f.readline()
            if not line:
                break

            # Remove surrounding whitespaces and new lines.
            line = line.strip()

            if line == "":
                continue

            # Split on one or more whitespace.
            parts = line.split()

            for part in parts:
                capture = re.search(
                    r"[^a-zA-Z0-9']*([a-zA-Z0-9']+)[^a-zA-Z0-9']*", part
                )

                # Tokens like "=" do not match the above regex so we ignore them.
                if capture is not None:
                    yield (capture.groups()[0].lower(), token_pos)
                    token_pos += 1
