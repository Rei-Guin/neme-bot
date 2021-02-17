# read all lines and send content
def read(file_name):
    try:
        with open(file_name) as f:
            content = f.read().splitlines()

    except FileNotFoundError:
        content = 'file not found'

    return content


# validate to see if number is in range
def validate_range(val):
    ret = True
    nums = sorted(val[1].split('+'))
    opt_range = {
        'r': [1, 2, 3, 4],
        't': [1, 2, 3],
        'c': [0, 1, 2, 3, 4, 5, 6, 7, 8],
        'f': [1, 2]
    }

    if int(nums[0]) < opt_range[val[0]][0] or int(nums[-1]) > opt_range[val[0]][-1]:
        ret = False

    return ret
