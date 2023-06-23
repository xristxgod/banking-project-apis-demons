import emoji


# TODO cache function
def make_text(text: str, **params):
    return emoji.emojize(
        text.format(**params),
        language='alias',
    )
