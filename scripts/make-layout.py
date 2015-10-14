#!/usr/bin/env python

from __future__ import print_function

import collections
import re

from itertools import product, tee


#: The regular expression used to find the last line of an event block
END_RE = re.compile(
    r'^\s*XFilterEvent returns: (True|False)$')

#: The regular expression used to check whether an event is an event
EVENT_RE = re.compile(
    r'(?m)^Key(Press|Release) event')

#: The regular expression used to extract the key code and symbol name
SYMBOL_RE = re.compile(
    r'keycode ([0-9]+) \(keysym (0x[0-9A-fa-f]+), (.*?)\)')

#: The regular expression used to extract the display name
NAME_RE = re.compile(
    r'XLookupString gives [0-9]+ bytes: \(.+\) "(.*?)"\s')

#: The regular expression that matches dead keys
DEAD_RE = re.compile(r'dead_.*')


#: The characters written on the actual keyboard; `?` indicates unknown values
LAYOUT_DESCRIPTION = (
    ('?1234567890??', 'key left of 1 to key right of backspace'),
    ('qwertyuiop??', 'key right of tab (Q) to key left of enter'),
    ('asdfghjkl???', 'key right of caps lock (A) to key left of enter'),
    ('?zxcvbnm???', 'keys between shift keys'))


def is_shift(symbol):
    """Determines whether a key is *shift*.

    :param str symbol: The ``X`` key symbol to check.

    :returns: ``True`` if the symbol represents any of the *shift* keys
    """
    return symbol in ('Shift_L', 'Shift_R')


def is_altgr(symbol):
    """Determines whether a key is *altgr*.

    :param str symbol: The ``X`` key symbol to check.

    :returns: ``True`` if the symbol represents *altgr*
    """
    return symbol == 'ISO_Level3_Shift'


def event_strings():
    """Yields strings describing ``X`` events read from ``xev``.

    This generator will first launch ``xev`` and then read from its ``stdout``.
    Every time a line matching :attr:`END_RE` is encountered, the lines read
    thus far are yielded and the line buffer is cleared.
    """
    import atexit
    import io
    import subprocess

    try:
        p = subprocess.Popen(['xev'], stdout=subprocess.PIPE)
        atexit.register(lambda: p.kill())
    except Exception as e:
        raise RuntimeError('failed to launch xev: %s', str(e))

    # This is the current block to which we add lines until we find the end
    # line
    block = ''

    # Wrap the output to disable buffering; we want events when they occur
    for line in io.open(p.stdout.fileno(), closefd=False):
        block += line
        if not END_RE.match(line):
            continue

        yield block
        block = ''

    # Yield the last event as well
    if block:
        yield block


def keyboard_events():
    """Yields keyboard events by invoking ``xev`` and reading its output.

    A keyboard event is the tuple ``(pressed, code, keysym, symbol, name)``,
    where ``pressed`` is a ``bool`` indicating whether this was a key press
    event, ``code`` a key code corresponding to the physical location of the
    key, ``keysym`` the integer value of the key symbol, ``symbol`` the *X*
    symbol name of the key and ``name`` the display name of the key.
    """
    for event_string in event_strings():
        # Try to extract information from the block
        event_match = EVENT_RE.search(event_string)
        if not event_match:
            continue
        pressed = event_match.group(1) == 'Press'

        # Get the code and symbol
        symbol_match = SYMBOL_RE.search(event_string)
        if not symbol_match:
            continue
        code = int(symbol_match.group(1))
        keysym = int(symbol_match.group(2), 16)
        symbol = symbol_match.group(3)

        # Get the name of the key; this is not required
        name_match = NAME_RE.search(event_string)
        if name_match:
            name = name_match.group(1)
        else:
            name = None

        yield (pressed, code, keysym, symbol, name or '')


def describe_modifiers(shift, altgr):
    """Creates a string describing a modifier state.

    :param bool shift: Whether *shift* is pressed.

    :param bool altgr: Whether *altgr* is pressed.

    :return: a descriptive string, which may be empty
    """
    modifier_descriptions = []
    if shift:
        modifier_descriptions.append('shift')
    if altgr:
        modifier_descriptions.append('altgr')
    return ' and '.join(modifier_descriptions)


def wait_for_modifiers(events, shift_value, altgr_value, release=False):
    """Waits for a specific modifier state.

    :param events: A generator compatible with what :func:`keyboard_events`
        yields.

    :param bool shift_value: Whether the *shift* state should reflect the value
        of ``release``.

    :param bool altgr_value: Whether the *altgr* state should reflect the value
        of ``release``.

    :param bool release: Whether to wait for the modifiers to be released. If
        this is ``True``, the modifiers are expected to be pressed, otherwise
        they are expected to be released.
    """
    shift = False
    altgr = False
    while True:
        if shift == shift_value and altgr == altgr_value:
            return

        pressed, code, keysym, symbol, name = next(events)
        if is_shift(symbol):
            shift = pressed != release
        elif is_altgr(symbol):
            altgr = pressed != release


def make_layout(layout_file, layout_name):
    import json

    # Launch xev and start reading events
    events = keyboard_events()

    print('Press return to begin...')
    for pressed, code, keysym, symbol, name in events:
        if not pressed and symbol == 'Return':
            break

    layout = collections.OrderedDict()

    modifier_combinations = product(*tee((False, True)))

    # Iterate over all values for the modifier keys
    for shift, altgr in modifier_combinations:
        # The key codes for the keys pressed during this round
        codes = set()

        # The index for this shift state
        index = shift << 0 | altgr << 1

        # First wait for the modifiers to be pressed
        modifier_description = describe_modifiers(shift, altgr)
        if modifier_description:
            print('Press and hold %s' % modifier_description)
        wait_for_modifiers(events, shift, altgr)

        # Iterate over every row
        for row, (keys, row_description) in enumerate(LAYOUT_DESCRIPTION):
            print('Press entire row of %s' % row_description)

            for col, key_description in enumerate(keys):
                # The key ID
                keyid = 'A%c%02d' % ('EDCB'[row], col + int(row > 0))

                print('<%2d, %2d, [%s]> [%s] ' % (
                    row, col, keyid, key_description), end='')

                while True:
                    pressed, code, keysym, symbol, name = next(events)

                    # Make sure no modifier is changed
                    if is_shift(symbol) or is_altgr(symbol):
                        raise RuntimeError(
                            'shift or altgr must not be modified')

                    # Ignore keypress events and already used keys
                    if pressed or code in codes:
                        continue

                    # Now we have an actual layout key press
                    codes.add(code)
                    data = layout.get(keyid, None)
                    if data is None:
                        data = [''] * 4
                        layout[keyid] = data
                    data[index] = [
                        name, keysym, symbol]

                    print('= %s (%s)' % (name or '<unnamed>', symbol))

                    break

            print()

        # Finally wait for the modifiers to be released
        if modifier_description:
            print('Release %s' % modifier_description)
        wait_for_modifiers(events, shift, altgr, release=True)
        print()

    json.dump(
        collections.OrderedDict((
            ('meta', collections.OrderedDict((
                ('name', layout_name),))),
            ('layout', layout))),
        layout_file,
        indent=4)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Generates layout files for Virtual Touchpad')

    parser.add_argument(
        'layout_file',
        type=argparse.FileType('w'),
        help='The layout file to generate')

    parser.add_argument(
        'layout_name',
        type=str,
        help='The display name of the layout')

    try:
        make_layout(**vars(parser.parse_args()))
    except Exception as e:
        print()
        try:
            print(e.args[0] % e.args[1:])
        except:
            print(str(e))
