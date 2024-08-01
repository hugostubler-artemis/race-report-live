import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import dataframe_image as dfi
from dataframe_image.converter import ChromeConverter 
from datetime import datetime
from race_stats_creator import get_race_recap, get_legs, get_start_recap
import plotly.express as px
# from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Table, Image
from PIL import Image
from io import BytesIO
import streamlit as st
import matplotlib.pyplot as plt

import os


def dataframe_to_png(df, filename):
    dfi.export(df, filename)

def create_pdf(title, images, pdf_buffer):
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    margin = inch
    separation = 0.2 * inch  # Separation between images
    
    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2.0, height - margin, title)
    #c.drawCentredString
    # Subtitle: Recap Table
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, height - 2 * margin, "Recap Table")

    # Main Image (table)
    main_image = ImageReader(images[0])
    main_image_width, main_image_height = main_image.getSize()
    main_image_width /= 2
    main_image_height /= 2
    c.drawImage(images[0], (width - main_image_width) / 2.0, height - 3 * margin - main_image_height, 
                width=main_image_width, height=main_image_height)

    # Start Image (table)
    start_image = ImageReader(images[1])
    start_image_width, start_image_height = start_image.getSize()
    start_image_width /= 2
    start_image_height /= 2
    c.drawImage(images[1], (width - start_image_width) / 2.0, height - 4 * margin - main_image_height - start_image_height, 
                width=start_image_width, height=start_image_height)

    # New page for Leg1 and Leg2 images
    c.showPage()

    # Subtitle: Leg 1
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, height - margin, "Leg 1")

    # Images for Leg1
    leg1_y_position = height - 2 * margin
    leg1_image1 = ImageReader(images[2])
    leg1_image2 = ImageReader(images[3])
    leg1_image_width, leg1_image_height = leg1_image1.getSize()
    leg1_image_width2, leg1_image_height2 = leg1_image2.getSize()
    leg1_image_width /= 3
    leg1_image_height /= 3
    leg1_image_width2 /= 3
    leg1_image_height2 /= 3
    total_width = leg1_image_width + leg1_image_width2 + separation
    c.drawImage(images[2], (width - total_width) / 2.0, leg1_y_position - leg1_image_height, 
                width=leg1_image_width, height=leg1_image_height)
    c.drawImage(images[3], (width - total_width) / 2.0 + leg1_image_width + separation, 
                leg1_y_position - leg1_image_height, width=leg1_image_width2, height=leg1_image_height2)

    # Subtitle: Leg 2
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, leg1_y_position - leg1_image_height - margin, "Leg 2")

    # Images for Leg2
    leg2_y_position = leg1_y_position - leg1_image_height - 2 * margin
    leg2_image1 = ImageReader(images[4])
    leg2_image2 = ImageReader(images[5])
    leg2_image_width, leg2_image_height = leg2_image1.getSize()
    leg2_image_width2, leg2_image_height2 = leg2_image2.getSize()
    leg2_image_width /= 3
    leg2_image_height /= 3
    leg2_image_width2 /= 3
    leg2_image_height2 /= 3
    total_width = leg2_image_width + leg2_image_width2 + separation
    c.drawImage(images[4], (width - total_width) / 2.0, leg2_y_position - leg2_image_height, 
                width=leg2_image_width, height=leg2_image_height)
    c.drawImage(images[5], (width - total_width) / 2.0 + leg2_image_width + separation, 
                leg2_y_position - leg2_image_height, width=leg2_image_width2, height=leg2_image_height2)

    # New page for Leg3 and Leg4 images
    c.showPage()

    # Subtitle: Leg 3
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, height - margin, "Leg 3")

    # Images for Leg3
    leg3_y_position = height - 2 * margin
    leg3_image1 = ImageReader(images[6])
    leg3_image2 = ImageReader(images[7])
    leg3_image_width, leg3_image_height = leg3_image1.getSize()
    leg3_image_width2, leg3_image_height2 = leg3_image2.getSize()
    leg3_image_width /= 3
    leg3_image_height /= 3
    leg3_image_width2 /= 3
    leg3_image_height2 /= 3
    total_width = leg3_image_width + leg3_image_width2 + separation
    c.drawImage(images[6], (width - total_width) / 2.0, leg3_y_position - leg3_image_height, 
                width=leg3_image_width, height=leg3_image_height)
    c.drawImage(images[7], (width - total_width) / 2.0 + leg3_image_width + separation, 
                leg3_y_position - leg3_image_height, width=leg3_image_width2, height=leg3_image_height2)

    # Subtitle: Leg 4
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, leg3_y_position - leg3_image_height - margin, "Leg 4")

    # Images for Leg4
    leg4_y_position = leg3_y_position - leg3_image_height - 2 * margin
    leg4_image1 = ImageReader(images[8])
    leg4_image2 = ImageReader(images[9])
    leg4_image_width, leg4_image_height = leg4_image1.getSize()
    leg4_image_width2, leg4_image_height2 = leg4_image2.getSize()
    leg4_image_width /= 3
    leg4_image_height /= 3
    leg4_image_width2 /= 3
    leg4_image_height2 /= 3
    total_width = leg4_image_width + leg4_image_width2 + separation
    c.drawImage(images[8], (width - total_width) / 2.0, leg4_y_position - leg4_image_height, 
                width=leg4_image_width, height=leg4_image_height)
    c.drawImage(images[9], (width - total_width) / 2.0 + leg4_image_width + separation, 
                leg4_y_position - leg4_image_height, width=leg4_image_width2, height=leg4_image_height2)

    # Save the PDF
    c.save()

def create_start_png(data):
    start_ = fetch_latest_marks()
    #st.write(start_)
    rc, pin = start_['RC'], start_['PIN']
    # Custom color scale
    custom_color_scale = [
        (0.0, "black"),    # 0 -> blue,    # 16k is approximately 20% of the way to the max
        (0.5, "red"),   # 22k is approximately 40% of the way to the max
        (.6, "orange"),  # 26k is approximately 60% of the way to the max
        (.8, "yellow"),
        (.9, "green"),
        (1, "green")# 30k is approximately 80% of the way to the m     # 38k and above -> red
    ]
    
    # Create the scatter mapbox plot
    fig = px.scatter_mapbox(data, lat="Latitude", lon="Longitude", color="BSP%",
                            color_continuous_scale=custom_color_scale,
                            title="Coloured by BSP")
    
    # Add two marks and a line between them
    # Replace index1 and index2 with the actual indices of the points
    index1, index2 = 0, 1  # Example indices
    lat1, lon1 = data.loc[index1, 'Latitude'], data.loc[index1, 'Longitude']
    lat2, lon2 = data.loc[index2, 'Latitude'], data.loc[index2, 'Longitude']
    
    fig.add_trace(go.Scattermapbox(
        lat=[rc[0], pin[0]],
        lon=[rc[1], pin[1]],
        mode='markers+lines',
        marker=dict(size=10, color='red'),
        line=dict(width=2, color='blue'),
        name="Start Line"
    ))
    
    # Add text annotations every 10 seconds
    for i, row in data.iterrows():
        if i % 10 == 0:  # Assuming the rows are ordered by time and the interval is consistent
            fig.add_trace(go.Scattermapbox(
                lat=[row['Latitude']],
                lon=[row['Longitude']],
                mode='text',
                text=[f"BSP: {row['BSP']}"],
                textposition="top right",
                showlegend=False
            ))
    
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.write_image("png_race/pre_start.png")

    
def create_leg_pngs(leg, name):
    name = f"leg{name}"
    center_lat = leg['Latitude'].mean()
    center_lon = leg['Longitude'].mean()
    custom_color_scale = [
        (0.0, "black"),    # 0 -> blue,    # 16k is approximately 20% of the way to the max
        (0.5, "red"),   # 22k is approximately 40% of the way to the max
        (.6, "orange"),  # 26k is approximately 60% of the way to the max
        (.8, "yellow"),
        (.9, "green"),
        (1, "green")# 30k is approximately 80% of the way to the m     # 38k and above -> red
    ]

    # Create the scatter mapbox plot
    fig = px.scatter_mapbox(leg, lat="Latitude", lon="Longitude", color="VMG%",
                            color_continuous_scale=custom_color_scale,
                            title="Coloured by VMG%")

    fig.update_layout(mapbox_style="open-street-map",mapbox=dict(
            center=dict(lat=center_lat, lon=center_lon),
            bearing=leg.TWD.mean(),
            zoom=13 # Adjust zoom level here
        ))
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.write_image(f"png_race/track_plot_vmg_{name}.png")
    
    custom_color_scale = [
    (0.0, "red"),    # 0 -> blue,    # 16k is approximately 20% of the way to the max
    (0.5, "yellow"),   # 22k is approximately 40% of the way to the max
    (.7, "green"),  # 26k is approximately 60% of the way to the max
         # 38k and above -> red
    ]

   
    fig = px.scatter_mapbox(leg, lat="Latitude", lon="Longitude", color="TWD_delta",
                            color_continuous_scale=custom_color_scale,
                            title="Coloured by Tactic")

    fig.update_layout(mapbox_style="open-street-map", 
                      mapbox=dict(
            center=dict(lat=center_lat, lon=center_lon),
            bearing=leg.TWD.mean(),
            zoom=13 # Adjust zoom level here
        ),)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.write_image(f"png_race/track_plot_tactic_{name}.png")

def color_cells_perc(val):
    color = 'white'
    if isinstance(val, (int, float)):
        if val < 90:
            color = 'lightcoral'
        elif val < 95:
            color = 'lightyellow'
        else:
            color = 'lightgreen'
    return f'background-color: {color}'

def color_cells_twa(val):
    color = 'white'
    if isinstance(val, (int, float)):
        if val > 51 or val < 125 :
            color = 'lightcoral'
        elif val > 47 or val < 135:
            color = 'lightyellow'
        else:
            color = 'lightgreen'
    return f'background-color: {color}'

def color_cells_shift(val):
    color = 'white'
    if isinstance(val, (int, float)):
        if val < 0 :
            color = 'lightcoral'
        elif val ==0 :
            color = 'lightyellow'
        else:
            color = 'lightgreen'
    return f'background-color: {color}'

def color_cells(val):
    color = 'white'
    if isinstance(val, (int, float)):
        if val < 10 :
            color = 'lightcoral'
        elif val < 25 :
            color = 'lightyellow'
        else:
            color = 'lightgreen'
    return f'background-color: {color}'


def create_legs_track_png_leg(race, marks):
    leg1, leg2, leg3, leg4 = get_legs(race, marks)
    name = 1
    for leg in [leg1, leg2, leg3, leg4]:
        create_leg_pngs(leg, name)
        name+=1

def pdf_race_recap_creator(race, marks, pdf_buffer):
    now = datetime.now()

    # format it as a string in the desired format
    timestamp_string = now.strftime('%Y-%m-%dT%H:%M:%S')
    name = f"race_{timestamp_string}" #[name for name, var in globals().items() if var is race][0]
    leg1, leg2, leg3, leg4 = get_legs(race, marks)
    #st.write(type(leg1)
    r = get_race_recap(race, marks).round(2) # .style.background_gradient(cmap="YlGnBu", axis=0).set_precision(2)
    st.write(r)
    fig, ax = plt.subplots(figsize=(10, 2.8))  # Adjust the size as needed

    # Hide the axes
    ax.axis('tight')
    ax.axis('off')
    
    # Create a table with taller column headers
    table = ax.table(cellText=r.values, colLabels=r.columns, cellLoc='center', loc='center')
    
    # Adjust the font size and scale of the table
    table.auto_set_font_size(True)
    table.set_fontsize(11)
    table.scale(1.1, 1.1)
    
    # Make the column headers taller for multiline text
    for key, cell in table.get_celld().items():
        if key[0] == 0:  # This is the header row
            cell.set_height(0.8)  # Adjust the height of the header row
            cell.set_text_props(fontsize=11, wrap=True)  # Enable wrapping of text
    
    # Adjust layout
    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
    
    # Color the cells based on their values
    
    # Make the column headers taller for multiline text
    #for key, cell in table.get_celld().items():
    #    if key[0] == 0:  # Header row
    #        cell.set_height(0.8)
    #       cell.set_text_props(fontsize=11, wrap=True)  # Enable wrapping of text
    
    # Alternating row colors for better readability
    for i in range(len(r)):
        for j in range(len(r.columns)):
            cell = table[(i+1, j)]
            if i % 2 == 0:
                cell.set_facecolor("white")
            else:
                cell.set_facecolor("#f2f2f2")  # Light gray
    fig.savefig('png_race/main.png')
    fig, ax = plt.subplots(figsize=(10, 1.4))  

    ax.axis('tight')
    ax.axis('off')
    s = get_start_recap(race, marks).round(2)
    st.write(s)
    table_start = ax.table(cellText=s.values, colLabels=s.columns, cellLoc='center', loc='center')
    table_start.auto_set_font_size(True)
    table_start.set_fontsize(11)
    table_start.scale(1.1, 1.1)
    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
    fig.savefig('png_race/start.png')
    # Convert the DataFrame to an image and save it to the output file
    #dfi.export(r, output_file, format='png', scale=2)
    #dfi.export(r, 'png_race/main.png')
    # img = Image.open("png_race/track_plot_vmg_leg1.png")
    # img.save("png_race/track_plot_vmg_leg1_bis.png")
    create_legs_track_png_leg(race, marks)
    title = f"{name} recap"
    
    images = ["png_race/main.png","png_race/start.png", "png_race/track_plot_vmg_leg1.png", "png_race/track_plot_tactic_leg1.png", 
               "png_race/track_plot_vmg_leg2.png", "png_race/track_plot_tactic_leg2.png",
               "png_race/track_plot_vmg_leg3.png", "png_race/track_plot_tactic_leg3.png", 
               "png_race/track_plot_vmg_leg4.png", "png_race/track_plot_tactic_leg4.png", ]
   
    return create_pdf(title, images, pdf_buffer)
