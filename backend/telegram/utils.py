import emoji


def make_text(text: str, *, language: str = 'alias', **params):
    return emoji.emojize(
        text.format(**params),
        language=language,
    )
