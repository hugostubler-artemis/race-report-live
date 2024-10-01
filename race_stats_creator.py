import pandas as pd
import numpy as np
from arrow import get
from astropy.time import Time
import os
from datetime import datetime, timedelta
from geopy import distance
import math
import mysql.connector
import streamlit as st
import os


MYSQL_HOST = "sailing-performance.artemisracing.com"
MYSQL_PORT = 3306
MYSQL_USR = "admin"
MYSQL_PWD = "Vh&bxj07oiFNFP;Jg+BZ"
MYSQL_SCHEMA = "ac40"

def compute_targets(df, target):
    target["VMG"] = target['BSP'] * np.cos(target['TWA'] * np.pi / 180)
    target.iloc[0] = 0
    for var in ['VMG','BSP','TWA']:
        polynom_up = interpolation_p(target.iloc[1:]['TWS'], target.iloc[1:][var], 4)
        polynom_down = interpolation_p(
            target.iloc[1:].TWS, target.iloc[1:][var], 4
        )
        df[f"Tgt_{var}"] = np.where(df.TWA>90, polynom_down(df.TWS), polynom_up(df.TWS))
        df[f"{var}%"] = (df[var]/df[f"Tgt_{var}"]).abs()
    return df
    
def get_legs(race, marks):
    race_marks = marks[(marks.time>race.Datetime.min()) & (marks.time<race.Datetime.max())]
    #st.write(marks)
    #st.write('time 1',race.Datetime.min())
    #st.write('time 2',race.Datetime.max())
    #st.write(len(race_marks))
    #st.write("time 2",race_marks.iloc[0].time)
    output_dir = "targets"
    os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

    up_path = os.path.join(output_dir, f"upwind-Tableau 3.csv")
    down_path = os.path.join(output_dir, f"downwind-Tableau 3.csv")
    target_up = pd.read_csv(up_path,sep=";")
    target_down = pd.read_csv(down_path,sep=";")
    #st.write(target_up)
    
    leg1 = race[race.Datetime<race_marks.iloc[0].time]
    leg2 = race[(race.Datetime<race_marks.iloc[1].time) & (race.Datetime>race_marks.iloc[0].time)]
    leg3 = race[(race.Datetime<race_marks.iloc[2].time) & (race.Datetime>race_marks.iloc[1].time)]
    leg4 = race[race.Datetime>race_marks.iloc[2].time]
    
    
    leg1['TWD_delta'] = np.where(leg1.TWA>0,leg1.TWD-leg1.TWD.mean(),leg1.TWD.mean()-leg1.TWD)
    leg2['TWD_delta'] = np.where(leg2.TWA>0,leg2.TWD-leg2.TWD.mean(),leg2.TWD.mean()-leg2.TWD)
    leg3['TWD_delta'] = np.where(leg3.TWA>0,leg3.TWD-leg3.TWD.mean(),leg3.TWD.mean()-leg3.TWD)
    leg4['TWD_delta'] = np.where(leg4.TWA>0,leg4.TWD-leg4.TWD.mean(),leg4.TWD.mean()-leg4.TWD)

    leg1 = compute_targets(leg1, target_up)
    #st.write(leg1['Tgt_VMG'])
    #st.write(leg1['VMG%'])
    leg2 = compute_targets(leg2, target_down)
    leg3 = compute_targets(leg3, target_up)
    leg4 = compute_targets(leg4, target_down)
    return leg1, leg2, leg3, leg4

def cross_product_sign(lat1, lon1, lat2, lon2, boat_lat, boat_lon):
    """
    Calculate the cross product of the vector from (lat1, lon1) to (lat2, lon2) 
    and the vector from (lat1, lon1) to (boat_lat, boat_lon).
    """
    return (lat2 - lat1) * (boat_lon - lon1) - (lon2 - lon1) * (boat_lat - lat1)

def find_crossing_time(df, lat1, lon1, lat2, lon2):
    """
    Find the timestamp when the boat crosses the line defined by (lat1, lon1) and (lat2, lon2).
    df: DataFrame containing 'datetime', 'Latitude', 'Longitude' columns.
    """
    prev_side = None
    crossing_time = None

    for i, row in df.iterrows():
        boat_lat = row['gpsLat']
        boat_lon = row['gpsLon']
        timestamp = row['Datetime']
        
        # Determine the current side of the boat relative to the line
        current_side = np.sign(cross_product_sign(lat1, lon1, lat2, lon2, boat_lat, boat_lon))

        # If previous side is not None and there is a change in side, crossing has occurred
        if prev_side is not None and prev_side != current_side and current_side != 0:
            crossing_time = timestamp
            break

        prev_side = current_side

    return crossing_time
    
def get_start_recap(race, marks):
    race_recap = pd.DataFrame()
    leg1, leg2, leg3, leg4 = get_legs(race, marks)
    start_ = fetch_latest_marks()
    #st.write(start_)
    rc, pin = start_['RC'], start_['PIN']
    dist_to_line = closest_distance_to_line(rc[0], rc[1], pin[0], pin[1], leg1.iloc[0].gpsLat, leg1.iloc[0].gpsLon)
    speed_start = leg1.iloc[0]['BSP%']
    #st.write(speed_start)
    race_recap.loc[0,'DTL'] = dist_to_line
    race_recap.loc[0,'BSP_start'] = speed_start
    ttc = find_crossing_time(race, rc[0], rc[1], pin[0], pin[1])
    if ttc == None:
        race_recap.loc[0,'TTC'] = np.nan
    else :
        race_recap.loc[0,'TTC'] = (get(ttc) - get(race.iloc[0].Datetime)).total_seconds()
    return race_recap


def get_race_recap(race, marks):
    leg1, leg2, leg3, leg4 = get_legs(race, marks)
    
    race_recap = pd.DataFrame()
    for leg in [leg1, leg2, leg3, leg4]:
        
        #print(get_small_man_stats(leg))
        if len(leg)==0:
            st.write("ca va pas marcher")
        else :
            race_recap = pd.concat([race_recap, get_recap_table_leg(leg)],ignore_index=True)
            #race_recap.index = ['leg1','leg2','leg3','leg4']
            race_recap.rename(index={0: 'leg1', 1: 'leg2', 2: 'leg3', 3: 'leg4'})
    
    return race_recap.rename(index={0: 'leg1', 1: 'leg2', 2: 'leg3', 3: 'leg4'})

def get_small_man_stats(df):
    
    man = get_man_summaryV2_(df,4)
    if len(man)>0:
        if df.TWA.abs().mean()<90:
            tack = man[man.man_type=='tack']
            target_tack = pd.read_csv('targets/targets_tacks.csv')
            for col in target_tack.columns:
                p_tack = interpolation_p(target_tack.dropna()['Unnamed: 0'], target_tack.dropna()[col], 3)
                tack[f'{col}'] = p_tack(tack.tws)
            tack['DistanceMG%'] = tack.dmg_cog/tack.Tgt_dmg_cog
            return len(tack), tack['DistanceMG%'].mean(), tack.vmg_loss_avg.mean()
        else :
            gybe = man[man.man_type=='gybe']
            target_gybe = pd.read_csv('targets/targets_gybes.csv')
            for col in target_gybe.columns:
                p_tack = interpolation_p(target_gybe.dropna()['Unnamed: 0'], target_gybe.dropna()[col], 3)
                gybe[f'{col}'] = p_tack(gybe.tws)
            gybe['DistanceMG%'] = gybe.dmg_cog/gybe.Tgt_dmg_cog
        return len(gybe), gybe['DistanceMG%'].mean(), gybe.vmg_loss_avg.mean()
    else :
        return np.nan, np.nan, np.nan

def interpolation_p(x, y, degree):
    coefficients = np.polyfit(x, y, degree)
    poly_function = np.poly1d(coefficients)
    return poly_function



def get_recap_table_leg(leg):
    recap_table = pd.DataFrame()
    leg_num = 'leg1'
    i=1
     
    num_man, dmg, loss = get_small_man_stats(leg)
    for man in get_man_summaryV2(leg)[1:].Datetime :
        leg =  leg[(leg.Datetime<man-pd.Timedelta(seconds=5)) | (leg.Datetime>man+timedelta(seconds=20))]
    if len(leg)==0:
        st.write("ca va pas marcher")
    else : 
        leg['Heel'] = np.where(leg.TWA>0,leg['Heel'], -leg['Heel'])
        recap_table = pd.DataFrame()
        recap_table.loc[f'{leg_num}','VMG%'] = leg['VMG%'].mean() #[leg['VMG%']>0]
        recap_table.loc[f'{leg_num}','delta_BSP'] = np.mean((leg['BSP'].rolling('10s').max() - leg['BSP'].rolling('10s').min()))
        recap_table.loc[f'{leg_num}','TWA'] = leg['TWA'].abs().mean()
        # st.write(leg.Heel)
        recap_table.loc[f'{leg_num}','Heel'] = leg['Heel'].mean() 
        recap_table.loc[f'{leg_num}','BSP'] = leg['BSP'].mean()
        recap_table.loc[f'{leg_num}','VMG'] = leg['VMG'].mean()
        recap_table.loc[f'{leg_num}','dist_sailed'] = leg['BSP'].sum()/(1854) #.set_index(leg.Datetime)
        leg['TWD_delta'] = np.where(leg.TWA>0,leg.TWD-leg.TWD.mean(),leg.TWD.mean()-leg.TWD)
        recap_table.loc[f'{leg_num}','Shift'] = leg['TWD_delta'].mean()
        recap_table.loc[f'{leg_num}','%InPhase'] = np.where(leg.TWA.abs().mean()<90, len(leg[leg['TWD_delta']>0])/len(leg)*100,100-len(leg[leg['TWD_delta']>0])/len(leg)*100)
        recap_table.loc[f'{leg_num}','#man'] = num_man
        recap_table.loc[f'{leg_num}','DMG%'] = dmg
        recap_table.loc[f'{leg_num}','DistLoss'] = loss
    return recap_table

def get_man_summaryV2(data):
    # avg_window =5
    data.index = data["Datetime"]
    man_summary = pd.DataFrame()
    #data["abs_Yaw_rate"] = np.abs(data.HDG.diff())
    # Find all tack and gybes
    sign = data.TWA > 0
    sign_change = sign != sign.shift(1)
    mans = data[sign_change]
    # filtering the ones where the boat is stopped:
    mans = mans[mans.BSP > 10]
    # if mans.empty:
    #    return mans
    return mans

def mean_bearing(bearing1, bearing2):
    # Convert bearings from degrees to radians
    
    bearing1_rad = math.radians(bearing1)
    bearing2_rad = math.radians(bearing2)
    
    # Compute the sine and cosine of each bearing
    sin1, cos1 = math.sin(bearing1_rad), math.cos(bearing1_rad)
    sin2, cos2 = math.sin(bearing2_rad), math.cos(bearing2_rad)
    
    # Average the sine and cosine values
    sin_mean = (sin1 + sin2) / 2
    cos_mean = (cos1 + cos2) / 2
    
    # Compute the arctangent of the average sine and cosine values
    mean_bearing_rad = math.atan2(sin_mean, cos_mean)
    
    # Convert the result back to degrees
    mean_bearing_deg = math.degrees(mean_bearing_rad)
    
    # Normalize the result to be within 0 to 360 degrees
    if mean_bearing_deg < 0:
        mean_bearing_deg += 360
        
    #if bearing1<bearing2:
    return mean_bearing_deg
    
    #else :
     #   return 180 - mean_bearing_de
        
        


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance in meters between two points on the earth specified in decimal degrees."""
    # Convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a)) 
    r = 6371000  # Radius of earth in meters
    return c * r

def closest_distance_to_line(lat1, lon1, lat2, lon2, boat_lat, boat_lon):
    """Calculate the minimum distance from the boat to the line segment defined by two GPS points."""
    # Calculate distances between the points
    A = np.array([lat1, lon1])
    B = np.array([lat2, lon2])
    P = np.array([boat_lat, boat_lon])

    AB = B - A
    AP = P - A
    BP = P - B

    AB_AB = np.dot(AB, AB)
    if AB_AB == 0:
        # The line segment is actually a point
        return haversine_distance(lat1, lon1, boat_lat, boat_lon)
    
    AB_AP = np.dot(AP, AB)
    t = AB_AP / AB_AB

    if t < 0:
        closest_point = A
    elif t > 1:
        closest_point = B
    else:
        closest_point = A + t * AB

    return haversine_distance(closest_point[0], closest_point[1], boat_lat, boat_lon)

def fetch_latest_marks():
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USR,
            password=MYSQL_PWD,
            database=MYSQL_SCHEMA
        )
        cursor = conn.cursor()
        query = """
        SELECT `type`, `latitude`, `longitude`, `dropTimeUtc`
        FROM `coursemarks`
        ORDER BY `dropTimeUtc` DESC
        LIMIT 8
        """
        cursor.execute(query)
        result = cursor.fetchall()
        marks = {row[0]: [row[1], row[2]] for row in result}
        return marks
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
        
def get_man_summaryV2_(data, avg_window):
    # avg_window =5
    data.index = data["Datetime"]
    man_summary = pd.DataFrame()
    #data["abs_Yaw_rate"] = np.abs(data.HDG.diff())
    # Find all tack and gybes
    sign = data.TWA > 0
    sign_change = sign != sign.shift(1)
    mans = data[sign_change]
    # filtering the ones where the boat is stopped:
    mans = mans[mans.BSP > 10]
    # if mans.empty:
    #    return mans

    ide=0
    for tman in mans.index.dropna().unique():
        dict = {}
        tack_summary = pd.DataFrame()
        # tman = get(tman)
        tman = get(tman)
        start = tman.shift(seconds=-10).format("YYYY-MM-DD HH:mm:ss")
        entry = tman.shift(seconds=-5).format("YYYY-MM-DD HH:mm:ss")
            
        stop = tman.shift(seconds=+20).format("YYYY-MM-DD HH:mm:ss")
        tdata = data[(data.index <= stop) & (data.index >= start)]
        entry = tman.shift(seconds=-5).format("YYYY-MM-DD HH:mm:ss")
        exit = tman.shift(seconds=+5).format("YYYY-MM-DD HH:mm:ss")
        build = tman.shift(seconds=+15).format("YYYY-MM-DD HH:mm:ss")
        bigger_build = tman.shift(seconds=+25).format("YYYY-MM-DD HH:mm:ss")
         

        tdata = data[(data.index <= stop) & (data.index >= start)]
        tdata['TackSign'] = np.sign(tdata.TWA)
        if np.sign(tdata.iloc[:5].TWA.mean()) != np.sign(tdata.iloc[-5:].TWA.mean()):
            if np.sign(tdata.TWA).diff().abs().sum()<=3:
                if tdata.iloc[:5].mean().FoilStbd_Cant+tdata.iloc[:5].mean().FoilPort_Cant>160:
                    if max(tdata.FoilPort_Cant.iloc[-10:].mean(),tdata.FoilStbd_Cant.iloc[-10:].mean())> 120:
                        if max(len(tdata[tdata.FoilStbd_Cant.diff().abs()>1]), len(tdata[tdata.FoilPort_Cant.diff().abs()>1]))>0:
                            if tdata.TackSign.iloc[:10].mean()>0:

                                drop_time = tdata[tdata.FoilStbd_Cant.diff().abs()>1].iloc[0].name
                                exit_time = tdata[tdata.FoilPort_Cant>120].iloc[0].name
                            else : 
                                drop_time = tdata[tdata.FoilPort_Cant.diff().abs()>1].iloc[0].name
                                exit_time = tdata[tdata.FoilStbd_Cant>120].iloc[0].name

                            entry_data = tdata[
                                (tdata.index <= drop_time + pd.Timedelta(seconds=1))
                                & (
                                    tdata.index
                                    >= drop_time - pd.Timedelta(seconds=1)
                                )
                            ]
                            exit_data = tdata[
                                (tdata.index >= exit_time)
                                & (
                                    tdata.index
                                    <= exit_time + pd.Timedelta(seconds=2)
                                )
                            ]
                            tmanoeuvre = data[(data.index <= exit) & (data.index >= entry)]
                            first_half = data[(data.index <= tman.format("YYYY-MM-DD HH:mm:ss")) & (data.index >= entry)]
                            second_half = data[(data.index <= exit) & (data.index >= tman.format("YYYY-MM-DD HH:mm:ss"))]
                            bigbuild_data = data[(data.index >= exit) & (data.index <= bigger_build)]
                            build_data = data[(data.index >= exit) & (data.index <= build)]
                            vmg_data = data[(data.index >= entry) & (data.index <= build)]

                            if len(entry_data) > 0:
                                if len(exit_data) > 0:
                                    if exit_data.BSP.mean() > 10:

                                        twa_man = tmanoeuvre.TWA.abs().mean()
                                        entry_bsp = round(entry_data.BSP.mean(), 2)
                                        # entry_bsp_bd = bd_data.BSP.values
                                        # ExitBSP
                                        exit_bsp = round(exit_data.BSP.mean(), 2)
                                        # Min BSP
                                        min_bsp = round(tdata.BSP.min(), 2)
                                        # Entry TWA
                                        entry_vmg = round(entry_data.VMG.mean(), 1)
                                        entry_twa = round(entry_data["TWA"].abs().mean(), 1)
                                        
                                        entry_cog = entry_data.COG.mean()
                                        # exit TWA
                                        exit_vmg = round(exit_data.VMG.abs().mean(), 1)
                                        
                                        exit_cog = exit_data.COG.mean()

                                            # dividing tacks and gybes:
                                        if twa_man > 120:
                                            man_type = "gybe"
                                        elif twa_man < 60:
                                            man_type = "tack"
                                        else:
                                            man_type = np.nan
                                        
                                        tdata_vmg = vmg_data
                                        datetime_series = pd.to_datetime(tdata_vmg.Datetime)
                                        time_diffs = datetime_series.diff()

                                        # Drop the first entry since it won't have a preceding timestamp to calculate the difference
                                        time_diffs = time_diffs.dropna()

                                        # Calculate the total number of seconds by summing the timedeltas
                                        total_seconds = time_diffs.sum().total_seconds()
                                        #.   tdata_vmg["time"] = np.arange(len(tdata_vmg.VMG))
                                        # distance_vmg = np.abs(tdata_vmg.VMG.sum()) / 2
                                        distance_vmg = (
                                            np.abs((tdata_vmg.VMG * time_diffs).sum().total_seconds()) / 2
                                        )

                                        distance_before = np.abs(entry_vmg) * total_seconds / 2
                                        distance_avg = (np.abs(entry_vmg) +np.abs(np.abs(vmg_data.iloc[-10:].VMG.mean())))* total_seconds / 4

                                        if distance_before - distance_vmg > 0:
                                            vmg_loss = distance_before - distance_vmg
                                            vmg_loss_avg = distance_avg - distance_vmg
                                        else:
                                            vmg_loss = np.nan
                                            vmg_loss_avg = np.nan

                                            # VMG LOSS TARGET

                                        distance_target = (
                                            np.abs(entry_data.Tgt_VMG.mean()) * total_seconds / 2
                                        )

                                        if distance_target - distance_vmg > 0:
                                            vmg_loss_target = distance_target - distance_vmg
                                        else:
                                            vmg_loss_target = np.nan

                                        # Distance via COG indicator : 
                                        if entry_data.TWA.abs().mean()<90:
                                            twd_cog = mean_bearing(entry_cog, exit_cog)
                                        else :
                                            twd_cog = mean_bearing(entry_cog, exit_cog)+180
                                        
                                        twa_cog = twd_cog- tdata_vmg.COG
                                        twa_cog = (twa_cog + 180) % 360 - 180
                                        
                                        vmg_cog = tdata_vmg.BSP*np.cos(twa_cog*np.pi/180)
                                        cog_distance = (
                                            np.abs((vmg_cog * time_diffs).sum().total_seconds()) / 2
                                        )
                                        
                                        
                                            # distance indicator

                                        first = (tdata.iloc[0].Latitude, tdata.iloc[0].Longitude)
                                        last = (tdata.iloc[-1].Latitude, tdata.iloc[-1].Longitude)
                                        #dist = np.sqrt(
                                        #    (first[0] - last[0]) ** 2 + (first[1] - last[1]) ** 2
                                        #)
                                        dist = round(distance.distance(first, last).m, 1)

                                        build_bsp = build_data.BSP.mean()
                                        build_bsp_stab = build_data.BSP.std()
                                        build_twa = build_data.TWA.abs().mean()
                                        entry_tws = entry_data.TWS.mean()
                                        exit_tws = exit_data.TWS.mean()
                                        tws = round((entry_tws + exit_tws) / 2, 1)

                                        """
                                        # T90 : 
                                        t_90 = ((bigbuild_data['VMG']/bigbuild_data.Tgt_VMG).abs().rolling('1s').mean()>.9).astype(int).idxmax()
                                        if t_90>bigbuild_data.rolling('1s').mean().index[0]:
                                            t_90 = (get(t_90)-tman).total_seconds()
                                        if type(t_90)!=float :
                                            t_90 = np.nan
                                        """
                                        if entry_data.TWA.mean() > 0:
                                            tack_side = "stbd"
                                            tackside = 1
                                        else:
                                            tack_side = "port"
                                            tackside = -1

                                        datetime = tdata.index[0]

                                      
                                        man_id=ide
                                        ide+=1

                                        dict = {
                                            "man_type": man_type,
                                           
                                            "twa_man": twa_man,
                                            "datetime": datetime,
                                            "Datetime": datetime,
                                          
                                            "vmg_loss": vmg_loss,
                                            
                                            "tws":tws,
                                            "vmg_loss_target": vmg_loss_target,
                                            "vmg_loss_avg":vmg_loss_avg,
                                           
                                            #"t_90":t_90,
                                            "man_id": man_id,
                                            
        
                                            "dmg_cog" : cog_distance,
                                            "distance_target":distance_target,
                                            
                                        }
                                        if len(dict) > 0:
                                            tack_summary = pd.DataFrame(dict, index=[tman])
                                            # print(tack_summary)
                                            # print(tack_summary)
                                            
                                            man_summary = pd.concat([man_summary, tack_summary])
                                        else:
                                            pass
    man_summary.man_id = np.arange(0,len(man_summary))
    return man_summary


def get_AWA(bsp, twa, tws):
    num = tws * np.sin(twa * np.pi / 180)
    denum = bsp + tws * np.cos(twa * np.pi / 180)
    return np.arctan(num / denum) * 180 / np.pi
