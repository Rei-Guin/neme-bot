from utilities import io_helper as uio


# Split and extract arguments for further usage
def get_arg(args):
    # split option name and values
    ret = {'opt': args.split('=')[0], 'val': split_val(args.split('=')[1])}

    # if option is pack, read set_ids to convert pack shorthand name to id
    if ret['opt'] == 'p':
        ids = uio.read('pack_info/set_ids.txt')
        ret['val'] = [val.split(':')[1].replace(' ', '')
                      for val in ids if args.split('=')[1] == val.split(':')[0]]

    # if option is either name or keyword, split it but not by +
    # since shadowverse-portal uses + to connect text values
    if ret['opt'] == 'n' or ret['opt'] == 'k':
        ret['val'] = [args.split('=')[1]]

    # if option os mana cost, any values above 10 becomes 10
    if ret['opt'] == 'm':
        temp = args.split('=')[1].split('+')
        for i in range(len(temp)):
            ret['val'][i] = '10' if int(temp[i]) > 10 else ret['val'][i]

    return ret


# split value by +
def split_val(vals):
    return vals.split('+')
