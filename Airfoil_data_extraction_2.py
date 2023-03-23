import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import Extraction_Methods
import matplotlib.pyplot as plt
from scipy import interpolate

# initializing inputs dataset
data = []

# loading page with all airfoils
start_url = "http://airfoiltools.com/search/airfoils"
page = requests.get(start_url).text
doc = BeautifulSoup(page,"html.parser")

# finding all airfoils
all_airfoils_table_raw = doc.find(["table"], class_="listtable")
all_airfoils_table_clean = all_airfoils_table_raw.find_all(["td"], class_="link")

################ extracting data

for i in range(1600,len(all_airfoils_table_clean)):#all_airfoils_table_clean:

    item = all_airfoils_table_clean[i]
    print(i)
    coordinates_map = []
    points_list = []

    link_raw = item.find(["a"])

    #for link in links_list_raw:
    temp_url = (str(link_raw).split("href=")[-1]).split(">")[0]
    temp_url = temp_url.replace('"', "")
    temp_page = "http://airfoiltools.com" + temp_url
    temp_doc = BeautifulSoup(requests.get(temp_page).text, "html.parser") # run the link of each airfoil
    angle_Cl_Cd_Re_values_list = []
    try:
        angle_Cl_Cd_Re_values_list = Extraction_Methods.Getting_Cl_Cd_links(temp_doc)  # read Cl, Cd and Re

    except:
        print("cl_cd_re_extraction_error:" + temp_url)
        continue
    x_c, y_c = Extraction_Methods.Getting_coordinate_points(temp_doc) # read coordinate points

    if(x_c != 0):
        # convert values to float
        try:
            x_c = [float(x) for x in x_c]
            y_c = [float(x) for x in y_c]
        except:
            print("float_conversion_error:" + temp_url)
            continue

        try:

            x_c, y_c = Extraction_Methods.Sorting_points(x_c, y_c)
            tck, u = interpolate.splprep([x_c, y_c], k=1, s=0)
            xnew, ynew = interpolate.splev(np.linspace(0, 1, 1000), tck)
            # visual inspection
            """plt.plot(x_c, y_c, 'o',  xnew, ynew)
            plt.legend(["data",'spline'])
            plt.axis([0,1, -0.5, 0.5])
            plt.show()"""
        except:
            print("interpolation_error:" + temp_url)
            print(x_c)
            print(y_c)
            continue


        # adding data to maindataset
        for item in angle_Cl_Cd_Re_values_list:
            if(item[0] != -1):
                data.append(np.append(ynew,item))

df = pd.DataFrame(data)
df.to_pickle("airfoil_database_safety.pk1")










