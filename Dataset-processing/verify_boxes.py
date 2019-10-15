import os

def parse_data_boxes(input_box):
    result = ''
    for line in input_box:
        result += line[0]
    return result

dirpath = os.getcwd() + '/source'

for node_l1 in os.listdir(dirpath):
    if os.path.isdir(dirpath + '/' + node_l1):
        for node_l2 in os.listdir(dirpath + '/' + node_l1):
            print(node_l2)
    # file = open('name_43b4e083-ef29-11e9-af3d-204747898e80.box','r')
    # print(parse_data_boxes(file))


