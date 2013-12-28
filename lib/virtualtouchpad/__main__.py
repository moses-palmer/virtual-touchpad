from argparse import ArgumentParser

from . import main

if __name__ == '__main__':
    parser = ArgumentParser(
        description = ''
            'Turns your mobile or tablet into a touchpad and keyboard for your '
            'computer.')

    parser.add_argument('--port',
        type = int,
        help = ''
            'The port on which to listen',
        default = 16080)

    main(**vars(parser.parse_args()))

