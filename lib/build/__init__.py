import os

# Read globals from virtualtouchpad._info without loading it
info = {}
with open(os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        'virtualtouchpad',
        '_info.py')) as f:
    for line in f:
        try:
            name, value = (i.strip() for i in line.split('='))
            if name.startswith('__') and name.endswith('__'):
                info[name[2:-2]] = eval(value)
        except ValueError:
            pass


# Read README
with open(os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        os.pardir,
        'README')) as f:
    README = f.read()
