import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import dataframe_image as dfi
from datetime import datetime
from race_stats_creator import get_race_recap, get_legs
import plotly.express as px
# from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Table, Image
from PIL import Image
from io import BytesIO
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

    # Main Image (scaled to half size and centered, placed closer to the title)
    main_image = ImageReader(images[0])
    main_image_width, main_image_height = main_image.getSize()
    main_image_width /= 2
    main_image_height /= 2
    c.drawImage(images[0], (width - main_image_width) / 2.0, height - 1.5 * margin - main_image_height, width=main_image_width, height=main_image_height)

    # Subtitle Leg1
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, height - 3 * margin - main_image_height, "Leg1")

    # Two images side by side for Leg1 with separation and lower position
    leg1_y_position = height - 3.5 * margin - main_image_height
    leg1_image1 = ImageReader(images[1])
    leg1_image2 = ImageReader(images[2])
    leg1_image_width, leg1_image_height = leg1_image1.getSize()
    leg1_image_width2, leg1_image_height2 = leg1_image2.getSize()
    leg1_image_width /= 3
    leg1_image_height /= 3
    leg1_image_width2 /= 3
    leg1_image_height2 /= 3
    total_width = leg1_image_width + leg1_image_width2 + separation
    c.drawImage(images[1], (width - total_width) / 2.0, leg1_y_position - leg1_image_height, width=leg1_image_width, height=leg1_image_height)
    c.drawImage(images[2], (width - total_width) / 2.0 + leg1_image_width + separation, leg1_y_position - leg1_image_height, width=leg1_image_width2, height=leg1_image_height2)

    # Subtitle Leg2
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, leg1_y_position - leg1_image_height - 1.5 * margin, "Leg2")

    # Two images side by side for Leg2 with separation and lower position
    leg2_y_position = leg1_y_position - leg1_image_height - 2 * margin
    leg2_image1 = ImageReader(images[3])
    leg2_image2 = ImageReader(images[4])
    leg2_image_width, leg2_image_height = leg2_image1.getSize()
    leg2_image_width2, leg2_image_height2 = leg2_image2.getSize()
    leg2_image_width /= 3
    leg2_image_height /= 3
    leg2_image_width2 /= 3
    leg2_image_height2 /= 3
    total_width = leg2_image_width + leg2_image_width2 + separation
    c.drawImage(images[3], (width - total_width) / 2.0, leg2_y_position - leg2_image_height, width=leg2_image_width, height=leg2_image_height)
    c.drawImage(images[4], (width - total_width) / 2.0 + leg2_image_width + separation, leg2_y_position - leg2_image_height, width=leg2_image_width2, height=leg2_image_height2)

    # New page
    c.showPage()

    # Subtitle Leg3
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, height - margin, "Leg3")

    # Two images side by side for Leg3 with separation
    leg3_y_position = height - 2 * margin
    leg3_image1 = ImageReader(images[5])
    leg3_image2 = ImageReader(images[6])
    leg3_image_width, leg3_image_height = leg3_image1.getSize()
    leg3_image_width2, leg3_image_height2 = leg3_image2.getSize()
    leg3_image_width /= 3
    leg3_image_height /= 3
    leg3_image_width2 /= 3
    leg3_image_height2 /= 3
    total_width = leg3_image_width + leg3_image_width2 + separation
    c.drawImage(images[5], (width - total_width) / 2.0, leg3_y_position - leg3_image_height, width=leg3_image_width, height=leg3_image_height)
    c.drawImage(images[6], (width - total_width) / 2.0 + leg3_image_width + separation, leg3_y_position - leg3_image_height, width=leg3_image_width2, height=leg3_image_height2)

    # Subtitle Leg4
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, leg3_y_position - leg3_image_height - 1.5 * margin, "Leg4")

    # Two images side by side for Leg4 with separation
    leg4_y_position = leg3_y_position - leg3_image_height - 2 * margin
    leg4_image1 = ImageReader(images[7])
    leg4_image2 = ImageReader(images[8])
    leg4_image_width, leg4_image_height = leg4_image1.getSize()
    leg4_image_width2, leg4_image_height2 = leg4_image2.getSize()
    leg4_image_width /= 3
    leg4_image_height /= 3
    leg4_image_width2 /= 3
    
    leg4_image_height2 /= 3
    total_width = leg4_image_width + leg4_image_width2 + separation
    c.drawImage(images[7], (width - total_width) / 2.0, leg4_y_position - leg4_image_height, width=leg4_image_width, height=leg4_image_height)
    c.drawImage(images[8], (width - total_width) / 2.0 + leg4_image_width + separation, leg4_y_position - leg4_image_height, width=leg4_image_width2, height=leg4_image_height2)

    # Save the PDF
    c.save()


def create_leg_pngs(leg, name):
    name = f"leg{name}"
    center_lat = leg['Latitude'].mean()
    center_lon = leg['Longitude'].mean()
    custom_color_scale = [
        (0.0, "blue"),    # 0 -> blue,    # 16k is approximately 20% of the way to the max
        (0.6, "green"),   # 22k is approximately 40% of the way to the max
        (.7, "yellow"),  # 26k is approximately 60% of the way to the max
        (.8, "orange"),
        (1, "red") # 30k is approximately 80% of the way to the m     # 38k and above -> red
    ]

    # Create the scatter mapbox plot
    fig = px.scatter_mapbox(leg, lat="Latitude", lon="Longitude", color="VMG%",
                            color_continuous_scale=custom_color_scale,
                            title="Coloured by VMG%")

    fig.update_layout(mapbox_style="open-street-map",mapbox=dict(
            center=dict(lat=center_lat, lon=center_lon),
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
            zoom=13 # Adjust zoom level here
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

    # format it as a string in the desired format
    timestamp_string = now.strftime('%Y-%m-%dT%H:%M:%S')
    name = f"race_{timestamp_string}" #[name for name, var in globals().items() if var is race][0]
    leg1, leg2, leg3, leg4 = get_legs(race, marks)
    #st.write(type(leg1)
    r = get_race_recap(race, marks).style.background_gradient(cmap="YlGnBu", axis=0).set_precision(2)
    
    #r = race_recap.style.background_gradient(cmap="YlGnBu", axis=0).set_precision(2)
    dfi.export(r, 'png_race/main.png')
    # img = Image.open("png_race/track_plot_vmg_leg1.png")
    # img.save("png_race/track_plot_vmg_leg1_bis.png")
    create_legs_track_png_leg(race, marks)
    title = f"{name} recap"
    
    images = ["png_race/main.png", "png_race/track_plot_vmg_leg1.png", "png_race/track_plot_tactic_leg1.png", 
               "png_race/track_plot_vmg_2.png", "png_race/track_plot_tactic_leg2.png",
               "png_race/track_plot_vmg_leg3.png", "png_race/track_plot_tactic_leg3.png", 
               "png_race/track_plot_vmg_leg4.png", "png_race/track_plot_tactic_leg4.png", ]
    """images = ["png_race/main.png", "track_plot_vmg_leg1.png", "track_plot_tactic_leg1.png", 
               "track_plot_vmg_2.png", "track_plot_tactic_leg2.png",
               "track_plot_vmg_leg3.png", "track_plot_tactic_leg3.png", 
               "track_plot_vmg_leg4.png", "track_plot_tactic_leg4.png", ]
               """
    return create_pdf(title, images, pdf_buffer)
