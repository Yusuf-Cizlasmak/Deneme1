import math
from math import sqrt,ceil
import pandas as pd 
import numpy as np

# EXTREME POINT ALGORITHM ##
from plots import calculate_remaining_volume,plotBoxes
from main import packing_box
from main import Box,BoxType,Bin

from SA_version import Bin1,Box1,plot_bins,BinPackingProblem
import random as rand
import plotly.io as pio
import time
import streamlit as st

from anneal import Annealer


class BinPackingProblem(Annealer):
    def __init__(self, bins, boxes):
        """
        self.bins: list (Kutuların yerleştirileceği konteynerlerin listesi)
        self.boxes: list (Kutuların listesi)
        self.unplaced_boxes: list (Dizilemeyen kutuların listesi)
        self.state: list (Kutuların yerleştirildiği durum)
        super(BinPackingProblem, self).__init__(self.state) : Annealer'dan attribute kalıtımı
        """
        self.bins = bins
        self.boxes = boxes
        self.box_types = {box.type: box for box in boxes}
        self.unplaced_boxes = []
        self.state = self.initial_state()
        super(BinPackingProblem, self).__init__(self.state)

    
    def update_used_space(self, box, bin, x, y, z):
        for i in range(x, x + box.width):
            for j in range(y, y + box.height):
                for k in range(z, z + box.depth):
                    bin.used_space[i][j][k] = True

    def initial_state(self):
        """
        Başlangıç durumu fonksiyonu

        state: list (Kutuların yerleştirildiği durum)
        bins: list (Kutuların yerleştirileceği konteynerlerin listesi)
        boxes: list (Kutuların listesi)

        return : state (Kutuların yerleştirildiği durum) 
        """
        state = []
        bins = list(self.bins)
        sorted_boxes = sorted(self.boxes, key=lambda box: box.volume, reverse=True)


        for box in sorted_boxes:
            placed = False
            for bin in bins:
                # Konteynerin içerisine kutunun sığabileceği bir pozisyon var mı kontrol edilir.
                x, y, z = self.find_new_position(box, bin)
                if x is not None:
                
                    # Kutu yerleştirilir ve kullanılan alan güncellenir.
                    state.append((box, bin, x, y, z))
                    bin.boxes.append(box)
                    box.set_position(x, y, z)
                    self.update_used_space(box, bin, x, y, z)
                    placed = True
                    break

            # Kutu yerleştirilemezse unplaced_boxes listesine eklenir.
            if not placed:
                self.unplaced_boxes.append(box)

        return state
    
    def can_fit_in_bin(self, box, bin, x, y, z):
        for i in range(x, x + box.width):
            for j in range(y, y + box.height):
                for k in range(z, z + box.depth):
                    if bin.used_space[i][j][k]:
                        return False
        return True


    def find_new_position(self, box, bin):
        """
        Bu fonksiyon, kutunun konteyner içerisindeki yeni pozisyonunu bulur.
        
        """
        for x in range(bin.width - box.width + 1):
            for y in range(bin.height - box.height + 1):
                for z in range(bin.depth - box.depth + 1):
                    if self.can_fit_in_bin(box, bin, x, y, z):
                        return x, y, z
        return None, None, None


    def energy(self):
        """
        Energy: Kutuda kalan boş alanın toplam hacmi - amaç bunu düşük tutmak
        """
        total_wasted_space = sum(
            (bin.width * bin.height * bin.depth) - sum(box.width * box.height * box.depth for box in bin.boxes)
            for bin in self.bins
        )
        return total_wasted_space
    



if "__main__" == __name__:
    import plotly.graph_objects as go
    import plotly.express as px
    
    st.set_page_config(page_title="Packing Box :package:", page_icon=":package:", layout="wide")
    st.title("Packing Box")
    st.markdown(
        """
        <style>
        body {
            background-color: #201d23;
            color: #ffffff;
            font-family: monospace;
        }
        .st-df {
            background-color: #5b6c96;
        }
        </style>
        """,
        unsafe_allow_html=True)


    with st.sidebar:
        st.image("https://uxwing.com/wp-content/themes/uxwing/download/logistics-shipping-delivery/truck-loading-icon.png", width=100) # Container ship icon
        st.title("Sünger Optimizasyonu Uygulaması")
        option = st.radio("Select an option:", ["1.Algoritma","2.Algoritma","Example CSV File Download"])


    ## EXTREME POINT ALGORITHM ## 
    if option == "1.Algoritma":

        df = st.file_uploader("Upload a CSV file", type=["csv"])
        
        st.write("Lütfen bir CSV dosyası yükleyin ve ardından 'Algoritmayı Çalıştır' butonuna tıklayın")
        
            # Run the packing_box function
        BinX = 4000
        BinY = 300
        BinZ = 300

        if df is None:
            st.error("Lütfen bir CSV dosyası yükleyin. Eğer bir CSV dosyanız yoksa, örnek bir CSV dosyasını indirebilirsiniz.")
        else:
            boxes, non_plotted_boxes, bin_size = packing_box(df, BinX, BinY, BinZ)

        #ÇALIŞTIRMA BUTONU##
        if st.button("Algoritmayı Çalıştır"):
            col1, col2 = st.columns([1, 1])

            bin = Bin(size=(bin_size.size[0], bin_size.size[1], bin_size.size[2]))
            # Calculate remaining volume
            remaining_volume = calculate_remaining_volume(bin, boxes)

            labels = ['Dizilmeyen', 'Dizilen Kutular']
            sizes = [100 - remaining_volume, remaining_volume]
            colors = ['#ff9999', '#66b3ff']



            #KUTU BOŞLUĞU PIE CHART ve KUTU TÜRÜ BAR CHART###
            with col1:
                col1_chart = go.Figure(data=[go.Pie(labels=labels, values=sizes, textinfo='label+percent',
                             marker=dict(colors=colors))])
                col1_chart.update_layout(title='Remaining Volume')
                st.plotly_chart(col1_chart, use_container_width=True)

            box_types2 = [f"{box.boxtype.senario} Sünger {box.boxtype.type}" for box in boxes]

            box_quantities = [box_types2.count(box_type) for box_type in set(box_types2)]

            with col2:


                box_types = [f"{box.boxtype.senario} Sünger {box.boxtype.type}" for box in boxes]
                col2_chart = go.Figure(data=[go.Bar(x=list(set(box_types)), y=box_quantities, marker_color=px.colors.sequential.Blues_r)],
                     layout=go.Layout(
                         xaxis=dict(title='Box Types'),
                         yaxis=dict(title='Quantity'),
                     ))
                col2_chart.update_layout(title='Diziye Alınan Kutu Türleri ve Miktarları')
                col2_chart.update_layout(xaxis={'categoryorder': 'total descending'})
                st.plotly_chart(col2_chart, use_container_width=True)
            
            
            #KUTU DİZİMİ GÖRSELLEŞTİRME ##
            st.title("Box Plot of Data")
            fig = plotBoxes(boxes, bin)
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("Görseli İndir"):
                fig.write_html(file="plot.html", auto_open=False)
                with open("plot.html", "rb") as file:
                    st.download_button(
                        label="3 boyutlu görseli indir",
                        data=file.read(),
                        file_name="Plot.html",
                        mime="text/html"
                    )

            #DATAFRAME OLUŞTURMA##
            st.markdown("Container Bilgileri")

            box_sizes = [box.size for box in boxes]  # Get the sizes of all the boxes
            total_box_volume = sum(box[0] * box[1] * box[2] for box in box_sizes)  # Calculate the total volume of all boxes
            different_box_types = len(set(box_sizes))  # Get the number of different box types

            # Create a Pandas DataFrame to display statistics
            stats_df = pd.DataFrame({
                "Parameter": ["Bin Size", "Number of Bins", "Different Box Types","Non_Packed Boxes"],
                "Value": [", ".join(map(str, bin_size.size)), len(boxes), different_box_types, len(non_plotted_boxes)]
            })


            # Display statistics in a table
            st.table(stats_df)

            # Add a success message
            st.success("Algoritma başarıyla çalıştırıldı.")




            # Dizilmeyen kutuların listesi ##
            st.write("Kutu içerisine dizilemeyen kutularımız dağılımı;")
            non_plotted_boxes = non_plotted_boxes
            if len(non_plotted_boxes) == 0:
                st.success("Tüm kutular dizilmiştir.")
            else:
                non_plotted_box_types = [box.boxtype.senario + " Sünger " + box.boxtype.type for box in non_plotted_boxes]
                non_plotted_box_quantities = [non_plotted_box_types.count(box_type) for box_type in set(non_plotted_box_types)]
                non_plotted_fig = go.Figure(
                    data=[go.Bar(x=list(set(non_plotted_box_types)), y=non_plotted_box_quantities, marker=dict(color=px.colors.sequential.Burg))],
                    layout=go.Layout(
                        xaxis=dict(title='Box Types'),
                        yaxis=dict(title='Quantity'),
                        colorway=px.colors.sequential.Viridis
                    ))
                non_plotted_fig.update_layout(title='Dizilmeyen Kutu Türleri ve Miktarları', barmode='stack')
                non_plotted_fig.update_layout(xaxis={'categoryorder': 'total descending'})
                non_plotted_chart = st.plotly_chart(non_plotted_fig, use_container_width=True)


    elif option == "2.Algoritma":
        st.title("Simulated Annealing for Bin Packing")

        col3, col4 = st.columns([1, 1])

        # File uploader for input CSV
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded_file is not None:
            data = pd.read_csv(uploaded_file)

        else:
            st.write("Please upload a CSV file.")
    

        #st.progress(0)

      
        if st.button("Algoritmayı Çalıştır"):
            
                progress_text="İlgili Algoritma çalışıyor... Kutuların yerleştirilmesi bekleniyor."
                my_bar = st.progress(0,text=progress_text)

                container_width = 330
                container_height = 30
                container_depth = 30

                bins1 = [Bin1(container_width, container_height, container_depth)]
                boxes1 = []
                for i in range(len(data)):
                    for j in range(data['Miktar'][i]):
                        boxes1.append(Box1(i+1, int(data['X'][i] *0.1)  , int(data['Y'][i]*0.1) , int(data['Z'][i]*0.1) ,data['Senaryo'][i]))


                # Assign random colors to box types for visualization
                box_colors = {k: f'rgb({rand.randint(0, 255)}, {rand.randint(0, 255)}, {rand.randint(0, 255)})' for k in range(1, len(boxes1) + 1)}
                for box in boxes1:
                    box.set_color(box_colors[box.type])

                
                # Initialize and run the simulated annealing
                problem = BinPackingProblem(bins1, boxes1)
                problem.steps = 50
                state, energy = problem.anneal()



                # Progress bar ## 
                for percent_complete in range(100):
                    time.sleep(0.3)
                    my_bar.progress(percent_complete + 1,text=progress_text)
                
                col3, col4 = st.columns([1, 1])
                with col3:
                    #PIE CHART FOR 2 ALGORITMA ##
                    total_box_volume = problem.energy()
                    container_dimensions = np.array([container_width, container_height, container_depth])
                    remaining_volume = np.prod(container_dimensions) - total_box_volume
                    used_volume = total_box_volume
                    labels = ['Remaining Volume', 'Used Volume']
                    sizes = [remaining_volume*100, used_volume*100]
                    colors = ['#ff9999', '#66b3ff']
                    fig = go.Figure(data=[go.Pie(
                        labels=labels,
                        values=sizes,
                        textinfo='label+percent',
                        texttemplate='%{label}: %{percent:.2%}',
                        marker=dict(colors=colors)
                    )])
                    fig.update_layout(title='Remaining Volume')
                    st.plotly_chart(fig, use_container_width=True)

                with col4:
                    #BAR CHART FOR 2 ALGORITMA ##
                    box_type_counts = {}
                    for box in boxes1:
                        if box.type in box_type_counts:
                            box_type_counts[box.type] += 1
                        else:
                            box_type_counts[box.type] = 1

                    fig = go.Figure(data=[go.Bar(
                        x=list(box_type_counts.keys()),
                        y=list(box_type_counts.values()),
                        marker=dict(color=px.colors.sequential.Burg)
                    )])

                    fig.update_layout(title='Dizilen Kutu Türleri ve Miktarları')
                    fig.update_layout(xaxis={'categoryorder': 'total descending'})
                    st.plotly_chart(fig, use_container_width=True)


                
                # Visualizing the result
                
                fig = plot_bins(bins1, container_width, container_height, container_depth, box_colors)
                

                # Show plot in Streamlit
                st.plotly_chart(fig, use_container_width=True)



                st.success("Check the 'plots' directory for output files.")
                with open("plots/plot.html", "r") as f:
                    download_html = f.read()
                    st.download_button(label="Download Plot as HTML", data=download_html, file_name="packed_plot.html", mime="text/html")



                ## DİZİLMEYEN KUTULAR İÇİN 

                st.write("Kutu içerisine dizilemeyen kutularımız dağılımı;")

                if len(problem.unplaced_boxes) == 0:
                    st.success("Tüm kutular dizilmiştir.")

                else:
                    unplaced_box_types = [box.type for box in problem.unplaced_boxes]
                    unplaced_box_quantities = [unplaced_box_types.count(box_type) for box_type in set(unplaced_box_types)]
                    unplaced_fig = go.Figure(
                        data=[go.Bar(x=list(set(unplaced_box_types)), y=unplaced_box_quantities, marker=dict(color=px.colors.sequential.Burg))],
                        layout=go.Layout(
                            xaxis=dict(title='Box Types', type='category'),
                            yaxis=dict(title='Quantity'),
                            colorway=px.colors.sequential.Viridis
                        ))
                    unplaced_fig.update_layout(title='Dizilmeyen Kutu Türleri ve Miktarları', barmode='stack')
                    unplaced_fig.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': sorted(set(unplaced_box_types))})
                    unplaced_chart = st.plotly_chart(unplaced_fig, use_container_width=True)


                st.success("Algoritma başarıyla çalıştırıldı.")
                my_bar.empty()

    
    
    ## OTOMATIK CSV DOSYASI OLUŞTURMA##

    # elif option == "Manuel Loader":

    #     st.markdown(
    #     """
    #     <span style='color:White; font-size:60px'>
    #     <b>Enter the size of the bin</b>
    #         </span>
    #     """,
    #     unsafe_allow_html=True)


    #     # Add Bin size inputs
    #     st.markdown(
    #     """
    #     <span style='color:Green '>
    #     <b>Enter the size of the bin:</b>
    #         </span>
    #     """,
    #     unsafe_allow_html=True)



    #     binX1, binY1, binZ1 = st.columns(3)
    #     with binX1:
    #         binX1 = st.number_input("X", 1, 100)
    #     with binY1:
    #         binY1 = st.number_input("Y", 1, 100)
    #     with binZ1:
    #         binZ1 = st.number_input("Z", 1, 100)
    #     bin1 = Bin(size=(binX1, binY1, binZ1))



    #     # Add a slider to select the number of boxes
    #     nums= st.number_input("Select the number of boxes", 1, 10)


    #     box_types1 = []
    #     nboxes1 = []

    #     for i in range(nums):
    #         senario = st.text_input(f"Senaryo {i+1}", f"Senaryo {i+1}")
            
    #         X, Y, Z = st.columns(3)
    #         with X:
    #             X = st.number_input("X", 1, 100, key=f"X_input_{i}")
    #         with Y:
    #             Y = st.number_input("Y", 1, 100, key=f"Y_input{i}")
    #         with Z:
    #             Z = st.number_input("Z", 1, 100, key=f"Z_input{i}")
            
    #         if X > binX1 or Y > binY1 or Z > binZ1:
    #             st.error(".")
    #             continue

            
    #         nboxes1.append(st.slider(f"Number of Boxes {i+1}", 1, 10))
    #         box_types1.append(BoxType(i+1, 1, 60, senario, (X, Y, Z)))

    #     if st.button("Add"):
    #         st.write("Box Types:")

    #         box_types_df = pd.DataFrame({
    #         "Senaryo": [box_type.senario for box_type in box_types1],
    #         "Sunger_Kodu": ["-" for i in range(len(box_types1))],
    #         "X": [box_type.size[0] for box_type in box_types1],
    #         "Y": [box_type.size[1] for box_type in box_types1],
    #         "Z": [box_type.size[2] for box_type in box_types1],
    #         "Miktar": [nbox for nbox in nboxes1]
    #         })


    #         # Create a DataFrame to display the box types
    #         # Convert DataFrame to CSV
            
    #         csv_data = box_types_df.to_csv(index=False)


    #         # Save CSV file
    #         csv_file_path = "box_types.csv"
    #         with open(csv_file_path, "w") as file:
    #             file.write(csv_data)
            
    #         box_types_df=box_types_df.drop(columns=["Sunger_Kodu"])
            
    #         st.table(box_types_df)


    #         # Run the packing_box function
    #         boxes1, non_plotted_boxes1, bin_size1 = packing_box(csv_file_path, bin1.size[0], bin1.size[1], bin1.size[2])

    #         # Display the DataFrame
    #         with st.expander("Show Boxes"):
                    
    #                 st.title("Box Plot of Data")
                    
    #                 fig = plotBoxes(boxes1, bin_size1)
                    
    #                 st.pyplot(fig)

            
    #         st.markdown("Container Information")



    #         st.write("Kutu içerisine dizilemeyen kutularımız dağılımı;")
            
    #         if len(non_plotted_boxes1) == 0:
    #             st.success("Tüm kutular dizilmiştir.")
    #         else:
    #             box_types = [f"{box.boxtype.senario} Sünger {box.boxtype.type}" for box in non_plotted_boxes1]

    #             # Count the occurrences of each unique box type
    #             box_type_counts = {box_type: box_types.count(box_type) for box_type in set(box_types)}

    #             # Create a bar chart with Plotly
    #             fig = go.Figure(
    #                 data=[go.Bar(
    #                     x=list(box_type_counts.keys()),
    #                     y=list(box_type_counts.values()),
    #                     marker=dict(color=px.colors.sequential.Burg)
    #                 )],
    #                 layout=go.Layout(
    #                     xaxis=dict(title='Box Types'),
    #                     yaxis=dict(title='Quantity'),
    #                     colorway=px.colors.sequential.Viridis
    #                 )
    #             )

    #             # Update layout for a more professional appearance
    #             fig.update_layout(
    #                 title='Dizilmeyen Kutu Türleri ve Miktarları',
    #                 barmode='stack',
    #                 xaxis={'categoryorder': 'total descending'}
    #             )

    #             # Add a hover template for better data visualization
    #             fig.update_traces(
    #                 hovertemplate='Box Type: %{x}<br>Quantity: %{y}'
    #             )





            



    ## ÖRNEK CSV DOSYASI İNDİRME ##
    elif option == "Example CSV File Download":
        # Add your code for the "Example CSV File Download" option here
        
        st.write("Örnek bir CSV dosyasını indirebilirsiniz.")
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Microsoft_Office_Excel_%282013%E2%80%932019%29.svg/120px-Microsoft_Office_Excel_%282013%E2%80%932019%29.svg.png", width=100) # Excel icon

        with open("deneme.csv", "rb") as file:
            st.download_button("Örnek Dosyayı İndir", file, "example.csv", "text/csv")

