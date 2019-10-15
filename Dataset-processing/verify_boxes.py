import os

def parse_data_boxes(input_box):
    result = ''
    for line in input_box:
        result += line[0]
    return result

dirpath = os.path.join(os.getcwd(), "source")

for node_l1 in os.listdir(dirpath):
    if os.path.isdir(os.path.join(dirpath, node_l1)):
        for node_l2 in os.listdir(os.path.join(dirpath, node_l1)):
            if node_l2.endswith('.box'):
                file = open(os.path.join(dirpath, node_l1, node_l2),'r')
                print(parse_data_boxes(file))
            