import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime
from race_stats_creator import get_race_recap, get_legs
import plotly.express as px
from PIL import Image
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

    # Main Image (table)
    main_image = ImageReader(images[0])
    main_image_width, main_image_height = main_image.getSize()
    main_image_width /= 2
    main_image_height /= 2
    c.drawImage(images[0], (width - main_image_width) / 2.0, height - 2 * margin - main_image_height, 
                width=main_image_width, height=main_image_height)

    # New page for Leg1 and Leg2 images
    c.showPage()

    # Images for Leg1
    leg1_y_position = height - margin
    leg1_image1 = ImageReader(images[1])
    leg1_image2 = ImageReader(images[2])
    leg1_image_width, leg1_image_height = leg1_image1.getSize()
    leg1_image_width2, leg1_image_height2 = leg1_image2.getSize()
    leg1_image_width /= 3
    leg1_image_height /= 3
    leg1_image_width2 /= 3
    leg1_image_height2 /= 3
    total_width = leg1_image_width + leg1_image_width2 + separation
    c.drawImage(images[1], (width - total_width) / 2.0, leg1_y_position - leg1_image_height, 
                width=leg1_image_width, height=leg1_image_height)
    c.drawImage(images[2], (width - total_width) / 2.0 + leg1_image_width + separation, 
                leg1_y_position - leg1_image_height, width=leg1_image_width2, height=leg1_image_height2)

    # New page for Leg3 and Leg4 images
    c.showPage()

    # Images for Leg2
    leg2_y_position = height - margin
    leg2_image1 = ImageReader(images[3])
    leg2_image2 = ImageReader(images[4])
    leg2_image_width, leg2_image_height = leg2_image1.getSize()
    leg2_image_width2, leg2_image_height2 = leg2_image2.getSize()
    leg2_image_width /= 3
    leg2_image_height /= 3
    leg2_image_width2 /= 3
    leg2_image_height2 /= 3
    total_width = leg2_image_width + leg2_image_width2 + separation
    c.drawImage(images[3], (width - total_width) / 2.0, leg2_y_position - leg2_image_height, 
                width=leg2_image_width, height=leg2_image_height)
    c.drawImage(images[4], (width - total_width) / 2.0 + leg2_image_width + separation, 
                leg2_y_position - leg2_image_height, width=leg2_image_width2, height=leg2_image_height2)

    # Save the PDF
    c.save()

def create_leg_pngs(leg, name):
    name = f"leg{name}"
    center_lat = leg['Latitude'].mean()
    center_lon = leg['Longitude'].mean()
    custom_color_scale = [
        (0.0, "black"), 
        (0.5, "red"),
        (.6, "orange"),
        (.8, "yellow"),
        (.9, "green"),
        (1, "green")
    ]

    fig = px.scatter_mapbox(leg, lat="Latitude", lon="Longitude", color="VMG%",
                            color_continuous_scale=custom_color_scale,
                            title="Coloured by VMG%")

    fig.update_layout(mapbox_style="open-street-map", mapbox=dict(
            center=dict(lat=center_lat, lon=center_lon),
            zoom=13 
        ))
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.write_image(f"png_race/track_plot_vmg_{name}.png")
    
    custom_color_scale = [
        (0.0, "red"), 
        (0.5, "yellow"), 
        (.7, "green")
    ]

    fig = px.scatter_mapbox(leg, lat="Latitude", lon="Longitude", color="TWD_delta",
                            color_continuous_scale=custom_color_scale,
                            title="Coloured by Tactic")

    fig.update_layout(mapbox_style="open-street-map", 
                      mapbox=dict(
            center=dict(lat=center_lat, lon=center_lon),
            zoom=13 
        ),)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.write_image(f"png_race/track_plot_tactic_{name}.png")

def create_legs_track_png_leg(race, marks):
    leg1, leg2, leg3, leg4 = get_legs(race, marks)
    name = 1
    for leg in [leg1, leg2, leg3, leg4]:
        create_leg_pngs(leg, name)
        name+=1

def pdf_race_recap_creator(race, marks, pdf_buffer):
    now = datetime.now()
    timestamp_string = now.strftime('%Y-%m-%dT%H:%M:%S')
    name = f"race_{timestamp_string}"
    leg1, leg2, leg3, leg4 = get_legs(race, marks)
    r = get_race_recap(race, marks).round(2)
    
    fig, ax = plt.subplots(figsize=(10, 1.4))  

    ax.axis('tight')
    ax.axis('off')
    
    table = ax.table(cellText=r.values, colLabels=r.columns, cellLoc='center', loc='center')
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.1, 1.1)
    
    # Make the column headers taller for multiline text
    for key, cell in table.get_celld().items():
        if key[0] == 0:  # Header row
            cell.set_height(0.8)
            cell.set_text_props(fontsize=11, wrap=True)  # Enable wrapping of text
    
    # Alternating row colors for better readability
    for i in range(len(r)):
        for j in range(len(r.columns)):
            cell = table[(i+1, j)]
            if i % 2 == 0:
                cell.set_facecolor("white")
            else:
                cell.set_facecolor("#f2f2f2")  # Light gray

    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
    fig.savefig('png_race/main.png')
    
    create_legs_track_png_leg(race, marks)
    title = f"{name} recap"
    
    images = [
        "png_race/main.png", "png_race/track_plot_vmg_leg1.png", "png_race/track_plot_tactic_leg1.png", 
        "png_race/track_plot_vmg_leg2.png", "png_race/track_plot_tactic_leg2.png",
        "png_race/track_plot_vmg_leg3.png", "png_race/track_plot_tactic_leg3.png", 
        "png_race/track_plot_vmg_leg4.png", "png_race/track_plot_tactic_leg4.png"
    ]
   
    return create_pdf(title, images, pdf_buffer)
