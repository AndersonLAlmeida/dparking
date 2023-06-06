from xml.etree import ElementTree as elements
import pickle
import os
from os import listdir, getcwd, path, makedirs
from os.path import join
from PIL import Image
import numpy as np

import fileinput

sets=[('PUCPR', '3499'), ('UFPR04', '3032'), ('UFPR05', '3321')]



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
    
def convert(size, x, y, w, h):
    dw = 1./(size[0])
    dh = 1./(size[1])

    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)


#Precisa receber cada arquivo xml e o local aonde vai salvar essas informacoes dos labels
def convert_annotation(source_xml):
    source_label = source_xml.replace(".xml", ".txt")
    source_img = source_xml.replace(".xml", ".jpg")
    
    count_vagas_desocupadas_total = 0
    count_vagas_ocupadas_total = 0
    count_vagas_descartadas = 0
    count_total = 0
    
    img = Image.open(source_img) 
    img_width = img.width 
    img_height = img.height 

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
                    if components.tag == "center":
                        center_x = float(components.attrib.get("x"))
                        center_y = float(components.attrib.get("y"))
                    if components.tag == "size":
                        w = float(components.attrib.get("w"))
                        h = float(components.attrib.get("h"))
        # for countor in spaces:
            # if countor.tag == "contour":
                # for point in countor:
                    # if ymin == -1:
                        # ymin = point.attrib.get("y")
                    # elif point.attrib.get("y") < ymin:
                        # ymin = point.attrib.get("y")

                    # if ymax == -1:
                        # ymax = point.attrib.get("y")
                    # elif point.attrib.get("y") > ymax:
                        # ymax = point.attrib.get("y")

                    # if xmin == -1:
                        # xmin = point.attrib.get("x")
                    # elif point.attrib.get("x") < xmin:
                        # xmin = point.attrib.get("x")

                    # if xmax == -1:
                        # xmax = point.attrib.get("x")
                    # elif point.attrib.get("x") > xmax:
                        # xmax = point.attrib.get("x")
               
        count_total = count_total + 1    

        cls_id = spaces.attrib.get("occupied")
        if cls_id is None:
            #print("Descartando uma vaga por nao conter a classificacao")
            count_vagas_descartadas = count_vagas_descartadas + 1
            continue
        
        if (cls_id == "1"):
            count_vagas_ocupadas_total = count_vagas_ocupadas_total + 1
        elif (cls_id == "0"):
            count_vagas_desocupadas_total = count_vagas_desocupadas_total + 1
        
        # b = (float(xmin), float(xmax), float(ymin), float(ymax))
        bb = convert((img_width, img_height), center_x, center_y, w, h)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')
        
        
        
        # ymin = -1
        # ymax = -1
        # xmin = -1
        # xmax = -1
        
    return count_total, count_vagas_desocupadas_total, count_vagas_ocupadas_total, count_vagas_descartadas

def labels_from_xml(directory, path_name="", train_value=0, train_test_path=os.path.join(get_parent_dir(0)), count=0):
    # First get all images and xml files from path and its subfolders
    image_paths = GetFileList(directory, ".jpg")
    xml_paths = GetFileList(directory, ".xml")
    
    count_vagas_total = 0
    count_vagas_desocupadas_total = 0
    count_vagas_ocupadas_total = 0
    count_vagas_descartadas_total = 0
    count_vagas_ocupadas_treino = 0
    count_vagas_desocupadas_treino = 0
    count_vagas_ocupadas_teste = 0
    count_vagas_desocupadas_teste = 0
    count_total_treino = 0 
    count_total_teste = 0
    count_total_treino_imagens = 0
    count_total_teste_imagens = 0
    
    if not len(image_paths) == len(xml_paths):
        print("number of annotations doesnt match number of images")
        return 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1
    for image in image_paths:
        #print("Iniciando criacao de labels da imagem " + image)
        target_filename = os.path.join(path_name, image) if path_name else image
        source_filename = os.path.join(directory, image)
        y_size, x_size, _ = np.array(Image.open(source_filename)).shape
        source_xml = image.replace(".jpg", ".xml")
        
        count_total, count_vagas_desocupadas, count_vagas_ocupadas, count_vagas_descartadas = convert_annotation(source_xml)
        
        count_vagas_desocupadas_total = count_vagas_desocupadas_total + count_vagas_desocupadas
        count_vagas_ocupadas_total = count_vagas_ocupadas_total + count_vagas_ocupadas
        count_vagas_descartadas_total = count_vagas_descartadas_total + count_vagas_descartadas
        count_vagas_total = count_vagas_total + count_total
        
        if count <= train_value:
            train_file = open(train_test_path + "/train.txt", "a+")
            train_file.write(image)
            train_file.write("\n")
            train_file.close()
            count_vagas_ocupadas_treino = count_vagas_ocupadas_treino + count_vagas_ocupadas
            count_vagas_desocupadas_treino = count_vagas_desocupadas_treino + count_vagas_desocupadas
            count_total_treino = count_total_treino + count_vagas_total
            count_total_treino_imagens = count_total_treino_imagens + 1
        elif count > train_value:
            test_file = open(train_test_path + "/test.txt", "a+")
            test_file.write(image)
            test_file.write("\n")
            test_file.close()
            count_vagas_ocupadas_teste = count_vagas_ocupadas_teste + count_vagas_ocupadas
            count_vagas_desocupadas_teste = count_vagas_desocupadas_teste + count_vagas_desocupadas
            count_total_teste = count_total_teste + count_vagas_total
            count_total_teste_imagens = count_total_teste_imagens + 1
        count = count + 1
        
    return count, count_vagas_total, count_total_treino, count_total_teste, count_total_treino_imagens, count_total_teste_imagens, count_vagas_desocupadas_total, count_vagas_ocupadas_total, count_vagas_ocupadas_treino, count_vagas_desocupadas_treino, count_vagas_ocupadas_teste, count_vagas_desocupadas_teste, count_vagas_descartadas, 0


if __name__ == "__main__":
    PUCPR_path = os.path.join(get_parent_dir(0), "PKLot", "PUCPR")
    UFPR04_path = os.path.join(get_parent_dir(0), "PKLot", "UFPR04")
    UFPR05_path = os.path.join(get_parent_dir(0), "PKLot", "UFPR05")
    
    count_vagas_total = 0
    count_vagas_desocupadas_total = 0
    count_vagas_ocupadas_total = 0
    count_vagas_descartadas_total = 0
    count_dias_descartados_total = 0
    
    count_vagas_ocupadas_treino_total = 0
    count_vagas_desocupadas_treino_total = 0
    count_vagas_ocupadas_teste_total = 0
    count_vagas_desocupadas_teste_total = 0
    count_total_treino_total = 0 
    count_total_teste_total = 0
    
    count_imagens = 0
    count_total_treino_imagens_total = 0
    count_total_teste_imagens_total = 0
    
    PKLot_path = os.path.join(get_parent_dir(0), "PKLot")

    dirs_paths = [PUCPR_path, UFPR04_path, UFPR05_path]
    i = 0
    count = 0
    for dir_path in dirs_paths:
        dataset, train_value = sets[i]
        for diretorio, subpastas, arquivos in os.walk(dir_path):
            for subpasta in subpastas:
                for dir, subs, arq in os.walk(diretorio +"/"+subpasta):
                    for sub in subs:
                        for d, s, a in os.walk(dir+"/"+sub):
                            count, count_total, count_total_treino, count_total_teste, count_total_treino_imagens, count_total_teste_imagens, count_vagas_desocupadas, count_vagas_ocupadas, count_vagas_ocupadas_treino, count_vagas_desocupadas_treino, count_vagas_ocupadas_teste, count_vagas_desocupadas_teste, count_vagas_descartadas, count_dias_descartados = labels_from_xml(d, path_name=d, train_value=int(train_value), count=count)
                            
                            count_dias_descartados_total = count_dias_descartados_total + count_dias_descartados
                            count_vagas_total = count_vagas_total + count_total
                            count_vagas_desocupadas_total = count_vagas_desocupadas_total + count_vagas_desocupadas
                            count_vagas_ocupadas_total = count_vagas_ocupadas_total + count_vagas_ocupadas
                            count_vagas_descartadas_total = count_vagas_descartadas_total + count_vagas_descartadas
                            count_vagas_ocupadas_treino_total = count_vagas_ocupadas_treino_total + count_vagas_ocupadas_treino
                            count_vagas_desocupadas_treino_total = count_vagas_desocupadas_treino_total + count_vagas_desocupadas_treino
                            count_vagas_ocupadas_teste_total = count_vagas_ocupadas_teste_total + count_vagas_ocupadas_teste
                            count_vagas_desocupadas_teste_total = count_vagas_desocupadas_teste_total + count_vagas_desocupadas_teste
                            count_total_treino_total = count_total_treino_total + count_total_treino
                            count_total_teste_total = count_total_teste_total + count_total_teste
                            
                            count_imagens = count_imagens + count
                            
                            count_total_treino_imagens_total = count_total_treino_imagens_total + count_total_treino_imagens
                            count_total_teste_imagens_total = count_total_teste_imagens_total + count_total_teste_imagens
        i = i + 1           
        count = 0
        

    print("Total de vagas: " + str(count_vagas_total))
    print("Total de dias descartados: " + str(count_dias_descartados_total))
    print("Vagas desocupadas: " + str(count_vagas_desocupadas_total))
    print("Vagas ocupadas: " + str(count_vagas_ocupadas_total))
    print("Vagas descartadas: " + str(count_vagas_descartadas_total))
    
    print("Vagas Ocupadas Treino: " + str(count_vagas_ocupadas_treino_total))
    print("Vagas Desocupadas Treino: " + str(count_vagas_desocupadas_treino_total))
    print("Vagas Ocupadas Teste: " + str(count_vagas_ocupadas_teste_total))
    print("Vagas Desocupadas Teste: " + str(count_vagas_desocupadas_teste_total))
    print("Vagas Total Treino: " + str(count_total_treino_total))
    print("Vagas Total teste: " + str(count_total_teste_total))
    
    print("Total de imagens: " + str(count_imagens))
    print("Total de imagens Treino: " + str(count_total_treino_imagens_total))
    print("Total de imagens Teste: " + str(count_total_teste_imagens_total))
    
    
    