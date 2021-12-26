from demon import demon, web, app, loop


if __name__ == '__main__':
    loop.create_task(demon.start_demon_parser_of_network())
    web.run_app(app, loop=loop)
