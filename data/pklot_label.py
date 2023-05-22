from xml.etree import ElementTree as elements
import pickle
import os
from os import listdir, getcwd, path, makedirs
from os.path import join
from PIL import Image
import numpy as np

sets=[('PUCPR', '2699'), ('UFPR04', '2232'), ('UFPR05', '2521')]


def get_parent_dir(n=1):
    """returns the n-th parent dicrectory of the current
    working directory"""
    current_path = os.path.dirname(os.path.abspath(__file__))
    for k in range(n):
        current_path = os.path.dirname(current_path)
    return current_path

def GetFileList(dirName, endings):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Make sure all file endings start with a '.'

    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + GetFileList(fullPath, endings)
        else:
            for ending in endings:
                if entry.endswith(ending):
                    allFiles.append(fullPath)
    return allFiles

def convert(size, box):
    dw = 1./(size[0])
    dh = 1./(size[1])
    x = (box[0] + box[1])/2.0 - 1
    y = (box[2] + box[3])/2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)


#Precisa receber cada arquivo xml e o local aonde vai salvar essas informacoes dos labels
def convert_annotation(source_xml, label_dir):
    label_name = source_xml.replace(".xml", ".txt")
    label_name = label_name[-23:]
    
    dir_label = label_dir + '/labels/'
    source_label = dir_label + label_name
    
    if not os.path.exists(dir_label):
        os.makedirs(dir_label)
    
    in_file = open(source_xml)
    out_file = open(source_label, "w+")
    
    ymin = -1
    ymax = -1
    xmin = -1
    xmax = -1

    root = elements.parse(source_xml).getroot()
    for spaces in root:
        for rotatedRect in spaces:
            if rotatedRect.tag == "rotatedRect":
                for components in rotatedRect:
                    if components.tag == "size":
                        w = float(components.attrib.get("w"))
                        h = float(components.attrib.get("h"))
        for countor in spaces:
            if countor.tag == "contour":
                for point in countor:
                    if ymin == -1:
                        ymin = point.attrib.get("y")
                    elif point.attrib.get("y") < ymin:
                        ymin = point.attrib.get("y")

                    if ymax == -1:
                        ymax = point.attrib.get("y")
                    elif point.attrib.get("y") > ymax:
                        ymax = point.attrib.get("y")

                    if xmin == -1:
                        xmin = point.attrib.get("x")
                    elif point.attrib.get("x") < xmin:
                        xmin = point.attrib.get("x")

                    if xmax == -1:
                        xmax = point.attrib.get("x")
                    elif point.attrib.get("x") > xmax:
                        xmax = point.attrib.get("x")
               
        cls_id = spaces.attrib.get("occupied")
        if cls_id is None:
            print("Descartando uma vaga por nao conter a classificacao")
            continue
        b = (float(xmin), float(xmax), float(ymin), float(ymax))
        bb = convert((w,h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')
        
        ymin = -1
        ymax = -1
        xmin = -1
        xmax = -1

def labels_from_xml(directory, path_name="", label_dir="", train_value=0, train_test_path=os.path.join(get_parent_dir(0))):
    # First get all images and xml files from path and its subfolders
    image_paths = GetFileList(directory, ".jpg")
    xml_paths = GetFileList(directory, ".xml")
    count = 0
    
    if not len(image_paths) == len(xml_paths):
        print("number of annotations doesnt match number of images")
        return False
    for image in image_paths:
        print("Iniciando criacao de labels da imagem " + image)
        target_filename = os.path.join(path_name, image) if path_name else image
        source_filename = os.path.join(directory, image)
        y_size, x_size, _ = np.array(Image.open(source_filename)).shape
        source_xml = image.replace(".jpg", ".xml")
        
        convert_annotation(source_xml, label_dir)
        
        if count <= train_value:
            train_file = open(train_test_path + "/train.txt", "a+")
            train_file.write(image)
            train_file.write("\n")
            train_file.close()
        elif count > train_value:
            test_file = open(train_test_path + "/test.txt", "a+")
            test_file.write(image)
            test_file.write("\n")
            test_file.close()
        count = count + 1


if __name__ == "__main__":
    PUCPR_path = os.path.join(get_parent_dir(0), "PKLot", "PUCPR")
    UFPR04_path = os.path.join(get_parent_dir(0), "PKLot", "UFPR04")
    UFPR05_path = os.path.join(get_parent_dir(0), "PKLot", "UFPR05")
    
    PKLot_path = os.path.join(get_parent_dir(0), "PKLot")

    dirs_paths = [PUCPR_path, UFPR04_path, UFPR05_path]
    i = 0
    for dir_path in dirs_paths:
        dataset, train_value = sets[i]
        for diretorio, subpastas, arquivos in os.walk(dir_path):
            for subpasta in subpastas:
                for dir, subs, arq in os.walk(diretorio +"/"+subpasta):
                    for sub in subs:
                        for d, s, a in os.walk(dir+"/"+sub):
                            labels_from_xml(d, path_name=d, label_dir=dir_path, train_value=int(train_value), train_test_path=PKLot_path)
                            
        i = i + 1
        
    
        
    
    
    