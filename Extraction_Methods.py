import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import math
import matplotlib.pyplot as plt

# function that gets coordinate points
def Getting_coordinate_points(temp_doc):
    details_table = temp_doc.find(["table"], class_="details")
    coordinates_table = details_table.find(["td"], class_="cell2")
    coordinates_item = coordinates_table.find(["pre"])
    item_string = str(coordinates_item)
    coordinates_raw =(item_string.split("/pre")[-2]).split(">")[-1][:-1]

    # extracting points from string
    try:
        zero_index = coordinates_raw.index(".0")
    except:
        zero_index = 1000

    try:
        nine_index = coordinates_raw.index(".9")
    except:
        nine_index = 1000

    if(zero_index<nine_index):
        starting_index = zero_index-1
    else:
        starting_index = nine_index-1

    coordinates = coordinates_raw[starting_index:]

    # creating lists of coordinates
    x_coords = []
    y_coords = []

    list_of_coordinates = coordinates.split()
    for i in range(len(list_of_coordinates)):
        # find all occurrences of -. or . and change them to -0. 0.
        if(list_of_coordinates[i][:2] == "-."):
            list_of_coordinates[i] = "-0." + list_of_coordinates[i][2:]
        elif(list_of_coordinates[i][0] == "."):
            list_of_coordinates[i] = "0" + list_of_coordinates[i]

        # jumping over non-numeric values
        if (list_of_coordinates[i][0] != "0" and list_of_coordinates[i][0] != "1" and list_of_coordinates[i][0] != "-"):
            continue
        # sorting coordinates
        if(i%2 == 0):
            x_coords.append(list_of_coordinates[i])
        else:
            y_coords.append(list_of_coordinates[i])
    if(len(x_coords) !=len(y_coords)): # just a safety in a case there is some inconsistency
        return 0,0
    return x_coords,y_coords

# function that gets cl cd values for angle 0 and Ncrit 9
def Getting_Cl_Cd_links(temp_doc):
    list_of_Cl_Cd_Re_values = []
    polar_table = temp_doc.find(["table"], class_="polar")
    list_of_all_detail_items = polar_table.find_all(["td"], class_="cell7")
    for i in range(0,len(list_of_all_detail_items),2):
        detail_item = list_of_all_detail_items[i].find(["a"])
        temp_url = (str(detail_item).split("href=")[-1]).split(">")[0]
        temp_url = temp_url.replace('"', "")
        temp_page = "http://airfoiltools.com" + temp_url
        temp_doc_2 = BeautifulSoup(requests.get(temp_page).text, "html.parser")  # run the link of each airfoil
        result = []
        result = Getting_Re_Cl_Cd(temp_doc_2)
        if(result ==-1):
            continue
        for item in result:
            list_of_Cl_Cd_Re_values.append(item)
        #list_of_Cl_Cd_Re_values.append([Getting_Re_Cl_Cd(temp_doc_2)])

    return list_of_Cl_Cd_Re_values

def Getting_Re_Cl_Cd(temp_doc):
    details_table = temp_doc.find(["table"], class_="details")
    # Re
    item_with_data_Re = details_table.find(["td"], class_="cell1")
    item_string_Re = str(item_with_data_Re)
    start_position = item_string_Re.index("Reynolds number:")+21
    end_position = item_string_Re[start_position:].index("<")+start_position
    Re_string = item_string_Re[start_position:end_position]
    Re_string = Re_string.replace(",","")
    Re = float(Re_string)

    # Cl, Cd
    item_with_data = details_table.find(["td"], class_="cell2")
    data_item = item_with_data.find(["pre"])
    item_string = str(data_item)
    data_raw = (item_string.split("/pre")[-2]).split(">")[-1][:-1]

    # extracting data
    starting_index = data_raw.rindex("-----") + 5
    data = data_raw[starting_index:]
    list_of_values = data.split()
    Cl_array,Cd_array,angle_array = [], [],[]
    for i in range(0,len(list_of_values),7):
        angle_array.append(list_of_values[i])
        Cl_array.append(list_of_values[i+1])
        Cd_array.append(list_of_values[i+2])

    try:
        angle_array = [float(x) for x in angle_array]
        Cl_array = [float(x) for x in Cl_array]
        Cd_array = [float(x) for x in Cd_array]
    except:
        return [-1]
        #return -1,-1,-1

    # putting everything in one list
    result = []
    for i in range(len(angle_array)):
        result.append([angle_array[i],Cl_array[i],Cd_array[i],Re])

    """# only taking values for angle 0 = 0
    angle_array = [float(x) for x in angle_array]
    try:
        index = angle_array.index(0.0)
    except:
        return -1,-1,-1
    Cl = float(Cl_array[index])
    Cd = float(Cd_array[index])"""

    #return Cl,Cd,Re
    return result

# Sorting points in clockwise manner
def Sorting_points(x_coords,y_coords):
    points = []
    for i in range(len(x_coords)):
        points.append([x_coords[i],y_coords[i]])

    # remove duplicates from list
    result = []
    for point in points:
        if point not in result:
            result.append(point)
    points = result

    # making sure that all points go in circle
    for i in range(len(points)-1):
        if(math.sqrt((points[i+1][0]-points[i][0])**2 + (points[i+1][1]-points[i][1])**2) > 0.5):
            temp_points = points[i+1:]
            temp_points.reverse()
            points = points[0:i+1] + temp_points
            break
    # making sure that circle starts from 00
    if(points[0][0] != 0.0):
        for point in points:
            if point[0] == min(x_coords):
                index = points.index(point)
                points = points[index:] + points[0:index]
                break

    # making sure points are sorted clockwise
    if(points[0][1] < points[-1][1]):
        points.reverse()

    x_coords = []
    y_coords = []

    for point in points:
        x_coords.append(point[0])
        y_coords.append(point[1])

    return x_coords,y_coords

# roatation of points by angle
def Points_Rotation(x_c,y_c,angle):
    angle = angle*math.pi/180

    for i in range(len(x_c)):
        x = x_c[i]
        y = y_c[i]
        x_c[i] = x*math.cos(angle) + y*math.sin(angle)
        y_c[i] = -x*math.sin(angle) + y*math.cos(angle)

    return  x_c,y_c











