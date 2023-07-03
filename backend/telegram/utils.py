import emoji


def make_text(raw_text: str, *, language: str = 'alias', **params):
    return emoji.emojize(
        raw_text.format(**params),
        language=language,
    )
