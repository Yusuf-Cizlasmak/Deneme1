import math
from math import sqrt,ceil
import pandas as pd

import Helpers.graph as graph
import Helpers.GenMod as rand
import time
import streamlit as st
time.clock = time.time


class Box:

    def __init__(self, index, boxtype, orientation, pos=(0, 0, 0)):
        self.index = index
        self.boxtype = boxtype
        self.orientation = orientation  # New orientation attribute
        self.size = self.calculate_size()  # Calculate size based on orientation
        self.position = pos
        self.color = boxtype.color
        self.volume= self.size[0] * self.size[1] * self.size[2]

    def calculate_size(self):
        if self.orientation == 0:  # Horizontal orientation
            return self.boxtype.size
        elif self.orientation == 1:  # Vertical orientation
            return self.boxtype.size[0], self.boxtype.size[2], self.boxtype.size[1]
        elif self.orientation == 2:  # Vertical orientation
            return self.boxtype.size[1], self.boxtype.size[2], self.boxtype.size[0]
        elif self.orientation == 3:  # Vertical orientation
            return self.boxtype.size[1], self.boxtype.size[0], self.boxtype.size[2]
        elif self.orientation == 4:
            return self.boxtype.size[2], self.boxtype.size[0], self.boxtype.size[1]
        elif self.orientation == 5:
            return self.boxtype.size[2], self.boxtype.size[1], self.boxtype.size[0]
        else:
            return self.boxtype.size

    def __repr__(self):
        string = 'Box no. ' + str(self.index)
        string += '\ntype: ' + self.boxtype.type
        string += '\norientation: ' + str(self.orientation)
        string += '\nsize: ' + str(self.size)
        string += '\nPosition: ' + str(self.position)
        string += '\nColor: ' + str(self.color) + '\n'

        return string


class BoxType:

    def __init__(self, type, benefit, weight, senario:int ,size=(1, 1, 1)):
        self.type = str(type)
        self.size = size
        self.color = [rand.random(), rand.random(), rand.random()]
        self.senario = senario
        self.benefit = benefit
        self.weight = weight
        self.volume = size[0] * size[1] * size[2]
        self.bw = benefit / weight
        self.bv = benefit / self.volume
        self.gm = sqrt(self.bw * self.bv)

    def __repr__(self):
        string = 'Box Type ' + self.type
        string += '\nsize: ' + str(self.size)
        string += '\nbenefit: ' + str(self.benefit)
        string += '\nweight: ' + str(self.weight)
        string += '\nvolume: ' + str(self.volume)
        string += '\nb/w: ' + str(self.bw)
        string += '\nb/v: ' + str(self.bv)
        string += '\nGeometric mean: ' + str(self.gm) + '\n'
        return string


class Bin:

    def __init__(self, size=(200, 700, 300), name='Main Container', maxWeight=rand.randint(10, 20) * 100000000):
        self.name = name
        self.size = size
        self.maxWeight = maxWeight
        self.volume = size[0] * size[1] * size[2]

    def __repr__(self):
        string = 'Container ' + self.name
        string += '\nsize: ' + str(self.size)
        string += '\nMax Weight: ' + str(self.maxWeight)
        string += '\nvolume: ' + str(self.volume) + '\n'
        return string
    

def packing_box(df, binX, binY, binZ):
    if df is None:
        st.error("Please upload a CSV file.")
        return
    
    


    # Dosya yüklendiyse devam et
    df = pd.read_csv(df)

    if not df.empty:
        st.success("File uploaded successfully.")

    # Rest of the code...
    bin = Bin((binX, binY, binZ), name="OverPacking Container", maxWeight=120000)

    weight = 0
    volume = 0

    boxtypes = []

    # BoxType'ları manuel olarak ekleyin
    # parametreleri type: int, benefit: int,weight: int,size: Any = (1, 1, 1))


    boxtypes = []
    nboxes = []

    #Kutular rastgele senaryo oluşturulmuştur.
    for i in range(len(df)):
        boxtypes.append(BoxType(df['Sunger_Kodu'][i], 1, 60,df["Senaryo"][i],(df['X'][i], df['Y'][i], df['Z'][i])))
        nboxes.append(df['Miktar'][i])
        




    # Her bir kutu tipi için kutu sayısını belirleyin

    maxboxes = []



    for i, box_type in enumerate(boxtypes):
        nmaxw = math.floor(bin.maxWeight / box_type.weight) 
        nmaxv = math.floor(bin.volume / box_type.volume) 

        if nmaxw > nmaxv:
            maxboxes.append(nmaxv)
        else:
            maxboxes.append(nmaxw)
            

    numberbox = {}




    boxes = []

# orientation seçimi


    for i, box_type in enumerate(boxtypes):

        for j in range(nboxes[i]):
            orientation_choice = 0
        
            if j <= maxboxes[i] - 1 and volume + box_type.volume <= bin.volume and weight + \
                    box_type.weight <= bin.maxWeight:
                
                boxes.append(Box(box_type.type + '-' + str(j + 1),
                                box_type, orientation_choice))
                volume += box_type.volume
                weight += box_type.weight
            else:
                break


    print(boxes)

    volume = 0
    weight = 0

    plotted = False

    to_graph_boxes = []

    eps = [(0, 0, 0)]


    boxes =  sorted(boxes, key=lambda box: (box.volume),reverse=True)


    empty_x=0
    empty_y=0
    empty_z=0


    for k, box in enumerate(boxes, start=1):
        eps = sorted(eps)

        if  box.size[0] <= bin.size[0] and box.size[1] <= bin.size[1] and box.size[2] <= bin.size[2] :

            plotted = False

            for ep in eps:

                size_condition = False

                for ep2 in eps:
                    if ep2 != ep:
                        if ep[1] == ep2[1] and ep[2] == ep2[2]:
                            if ep[0] + box.size[0] > ep2[0]:
                                size_condition = True
                                break
                        elif ep[0] == ep2[0] and ep[2] == ep2[2]:
                            if ep[1] + box.size[1] > ep2[1]:
                                size_condition = True
                                break

                if ep[0] + box.size[0] <= bin.size[0] and \
                        ep[2] + box.size[2] <= bin.size[2] and \
                        ep[1] + box.size[1] <= bin.size[1] and not size_condition:
                    box.position = ep

                    n = eps.count((ep[0] + box.size[0], ep[1] +
                                box.size[1], ep[2] + box.size[2]))

                    if eps.count((ep[0] + box.size[0], ep[1] + box.size[1], ep[2] + box.size[2])) < 1:
                        
                        eps.append((ep[0] + box.size[0], ep[1] +
                                    box.size[1], ep[2] + box.size[2]))
                    else:
                        eps.remove((ep[0] + box.size[0], ep[1] +
                                    box.size[1], ep[2] + box.size[2]))

                    if eps.count((ep[0] + box.size[0], ep[1], ep[2])) < 1:
                        
                        eps.append((ep[0] + box.size[0], ep[1], ep[2]))
                    else:
                        eps.remove((ep[0] + box.size[0], ep[1], ep[2]))

                    if eps.count((ep[0] + box.size[0], ep[1] + box.size[1], ep[2])) < 1:
                        eps.append(
                            (ep[0] + box.size[0], ep[1] + box.size[1], ep[2]))
                    else:
                        eps.remove(

                            (ep[0] + box.size[0], ep[1] + box.size[1], ep[2]))

                    if eps.count((ep[0] + box.size[0], ep[1], ep[2] + box.size[2])) < 1:
                        eps.append(
                            (ep[0] + box.size[0], ep[1], ep[2] + box.size[2]))
                    else:
                        eps.remove(
                            (ep[0] + box.size[0], ep[1], ep[2] + box.size[2]))

                    if eps.count((ep[0], ep[1] + box.size[1], ep[2] + box.size[2])) < 1:
                        eps.append(
                            (ep[0], ep[1] + box.size[1], ep[2] + box.size[2]))
                    else:
                        eps.remove(
                            (ep[0], ep[1] + box.size[1], ep[2] + box.size[2]))

                    if eps.count((ep[0], ep[1], ep[2] + box.size[2])) < 1:
                        eps.append((ep[0], ep[1], ep[2] + box.size[2]))
                    else:
                        eps.remove((ep[0], ep[1], ep[2] + box.size[2]))

                    if eps.count((ep[0], ep[1] + box.size[1], ep[2])) < 1:
                        eps.append((ep[0], ep[1] + box.size[1], ep[2]))
                    else:
                        eps.remove((ep[0], ep[1] + box.size[1], ep[2]))

                    eps.remove(ep)

                    weight += box.boxtype.weight
                    volume += box.boxtype.volume
                    to_graph_boxes.append(box)
                    # graph.plotBoxes(to_graph_boxes, bin)

                    # kutuların boyutlarını tekrardan belirleme

                    plotted = True
                if plotted:
                    

                    
                    empty_x = bin.size[0] - \
                        max(box.position[0] + box.size[0] for box in to_graph_boxes)
                    empty_y = bin.size[1] - \
                        max(box.position[1] + box.size[1] for box in to_graph_boxes)
                    empty_z = bin.size[2] - \
                        max(box.position[2] + box.size[2] for box in to_graph_boxes)
                    # print(len(boxes))
                    last_boxes = len(boxes)
                

                    if k == last_boxes:
                        print(
                            f"X ekseninde {empty_x}, Y ekseninde {empty_y}, Z ekseninde {empty_z} boşluk bulunmaktadır")
                        
                        X_upper=bin.size[0]  
                        Y_upper=bin.size[1] 
                        Z_upper=bin.size[2] 


                        # All case
                        if 0 < empty_x < X_upper and 0 < empty_y <= Y_upper and 0 < empty_z <= Z_upper:
                            print("b0")
                            bin.size = (
                                ceil(bin.size[0] - empty_x), bin.size[1] - empty_y, bin.size[2]-empty_z)

                        # x-y
                        elif 0 < empty_x < X_upper and 0 < empty_y <= Y_upper:
                            print("b1")
                            bin.size = (ceil(bin.size[0] - empty_x),
                                        ceil(bin.size[1] - empty_y), bin.size[2])

                        # y-z
                        elif 0 < empty_y <= Y_upper and 0 < empty_z <= Z_upper:
                            print("b2")
                            bin.size = (bin.size[0], 
                                        ceil(bin.size[1]-empty_y), ceil(bin.size[2]-empty_z))
                        # x-z
                        elif 0 < empty_x <= X_upper and 0 < empty_z <= Z_upper:
                            print("b3")
                            bin.size = (ceil(bin.size[0]-empty_x),
                                        bin.size[1], ceil(bin.size[2]-empty_z))

                        #x
                        elif 0 < empty_x <= X_upper:
                            print("b4")
                            bin.size = (ceil(bin.size[0]-empty_x),
                                        bin.size[1], bin.size[2])

                        # y
                        elif 0 < empty_y <= Y_upper:
                            print("b5")
                            bin.size = (
                                bin.size[0],ceil(bin.size[1]-empty_y), bin.size[2])
                        # z
                        elif 0 < empty_z <= Z_upper:
                            print("b6")
                            bin.size = (bin.size[0], bin.size[1],
                                        ceil(bin.size[2]-empty_z))
                        # no cutting
                        else:
                            bin.size = (bin.size[0], bin.size[1], bin.size[2])



                    break


    # graph.plotBoxes(to_graph_boxes, bin)
    # # graph.plotBox3d(to_graph_boxes, bin)

    print(
        f"Artık X ekseninde {empty_x}, Y ekseninde {empty_y}, Z ekseninde {empty_z} boşluk bulunmaktadır")
    print(
        f"kutumuz değişimler sonucu {bin.size[0]},{bin.size[1]}, {bin.size[2]}  olmuştur")
    non_plotted_boxes = [x for x in boxes if x not in to_graph_boxes]
    print("Kutu içerisine dizilemeyen kutularımız;")
    for box in non_plotted_boxes:

        print(f"{box.boxtype.senario}:{box.index}  Boyutu:{box.size}  Ağırlığı:{box.boxtype.weight}")


    return to_graph_boxes, non_plotted_boxes, bin



