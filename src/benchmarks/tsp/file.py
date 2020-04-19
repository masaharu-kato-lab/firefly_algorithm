
def load(filepath : str):

    options = dict()
    datalist = dict()

    with open(filepath,'r') as f:
        for line in f:
            
            v = line.rstrip('\r\n').split(':')
            keyword = v[0].strip()

            if(keyword == 'EOF') : break 
            if(keyword == 'COMMENT') : continue

            if(len(v) == 1):
                datalist[keyword] = data_part(f, options, keyword)
            else:
                value = v[1].strip()
                options[keyword] = value
    
    return (datalist, options)


def data_part(file, options, name):
    if(name == 'NODE_COORD_SECTION'):
        return node_coord_section(file, options)
    else:
        raise ValueError('Invalid name of data part : {:}'.format(name))


def node_coord_section(file, options):

    length = int(options['DIMENSION'])
    coords = {}

    for _ in range(length):
        v = file.readline().rstrip('\r\n').split()
        coords[int(v[0].strip())] = list(map(float, v[1:]))

    return coords
