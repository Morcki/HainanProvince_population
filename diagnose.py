#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  hainan.py
#  
#  Copyright 2018 Mocki <mocki@mocki-HP-EliteBook-840-G3>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import numpy as np
def location_array(arr_shape):
    '''
    Build a "Location" matrix :
        for example:
            
        shape(4,3)-->
        [[0,0],
         [0,1],
         [0,2],
         [1,0],
         [1,1],
         [1,2],
         ...
         [3,0],
         [3,1],
         [3,2]]
    '''
    m,n = arr_shape
    loc = [[i,j] for i in range(m) for j in range(n)]
    loc_arr = np.array(loc,dtype = np.int32)
    return(loc_arr)
    
def main(args):
    import pandas as pd
    "Read Hainan province population data(excel)"
    hainan_df = pd.read_excel('./popdata/Hainan0016.xlsx')#excel path:./popdata/Hainan0016.xlsx
    hainan_df.index = hainan_df['年份'];del hainan_df['年份']
    "capture information:"
    Year_index = hainan_df.index#Get Year index
    City_index = hainan_df.columns#Get City index
    hainan_popdata = hainan_df.values/10000#million people
    def xinge_func():
        '''
        xinge function:
            lg Pi = lg K - alph * lg Ri ;
            Pi * Ri^alph = K = P1
            
            Pi --- Population of City at Rank i.
            Ri --- City Rank in Province.
            K  --- P1(Population of City at Rank 1).
            alph --- index of Ri
        '''
        nonlocal Year_index;nonlocal City_index;nonlocal hainan_popdata
        "sequential analysis:"
        hainan_sort_mtr = -np.sort(-hainan_popdata)#sorted matrix based on poplution
        basepop_mtr = np.max(hainan_popdata,axis = 1).reshape(hainan_popdata.shape[0],1)# K or P1 or every year
        Relativ_mtr = np.argsort(np.argsort(-hainan_popdata,axis = 1),axis = 1)+1#City Rank matrix
        
        judge_mtr = (Relativ_mtr==1)#obtain base city location
        alph_mtr = (np.log10(basepop_mtr) - np.log10(hainan_popdata))/np.log10(Relativ_mtr)
        alph_mtr[judge_mtr] = float('inf')
        np.savetxt('./index/pop_rank.txt',hainan_sort_mtr,fmt = "%.3f",delimiter = ",")
        np.savetxt('./index/relative_index.txt',Relativ_mtr,fmt = "%d",delimiter = ",")
        np.savetxt('./index/alph_index.txt',alph_mtr,fmt = "%.3f",delimiter = ",")
        return None
    def firstclass_index():
        '''
        city firstclass index:
            S2 = P1/P2
            S4 = P1/(P2+P3+P4)
            S11 = 2*P1/(P2+ ... +P11)
        '''
        nonlocal Year_index;nonlocal City_index;nonlocal hainan_popdata
        "sequential analysis:"
        Relativ_mtr = np.argsort(np.argsort(-hainan_popdata,axis = 1),axis = 1)+1
        base_p1 = np.max(hainan_popdata,axis = 1)
        "S2 index:"
        judge_s2 = (Relativ_mtr==2)
        S2_index = base_p1/hainan_popdata[judge_s2]
        #np.savetxt('./index/S2_index.txt',S2_index,fmt = "%.3f",delimiter = ",")
        "S4 index:"
        judge_s4 = (Relativ_mtr>=2) & (Relativ_mtr<=4)
        S4_index = base_p1/np.sum(hainan_popdata*judge_s4,axis = 1)
        #np.savetxt('./index/S4_index.txt',S4_index,fmt = "%.3f",delimiter = ",")
        "S11 index:"
        judge_s11 = (Relativ_mtr>=2) & (Relativ_mtr<=11)
        S11_index = base_p1*2/np.sum(hainan_popdata*judge_s11,axis = 1)
        #np.savetxt('./index/S11_index.txt',S11_index,fmt = "%.3f",delimiter = ",")
        #Output to File
        Headline = '|Index\Year|'+'|'.join([str(year) for year in Year_index])+'\n'
        Midline = '| :------:'*(len(Year_index)+1)+'|\n'
        with open('./index/S_index.txt','w') as f:
            f.writelines(Headline+Midline)
            f.writelines('|S2|'+'|'.join([str(round(S2,3)) for S2 in list(S2_index.flat)])+'\n')
            f.writelines('|S4|'+'|'.join([str(round(S4,3)) for S4 in list(S4_index.flat)])+'\n')
            f.writelines('|S11|'+'|'.join([str(round(S11,3)) for S11 in list(S11_index.flat)])+'\n')
        return None
    def Plot_CityRank_3D():
        from pyecharts import Bar3D
        nonlocal Year_index;nonlocal City_index
        hainan_pprank_bar3d = Bar3D("海南省地级市序位分布3D图", width=1200, height=600)
        xyz_names = ['年份','位序','人口数目：（万人）']
        x_axis = Year_index
        y_axis = [x+1 for x in range(len(City_index))]
        
        hainan_pprank = np.loadtxt('./index/pop_rank.txt',delimiter=",")
        hainan_pprank_shape = hainan_pprank.shape
        loc_arr = location_array(hainan_pprank_shape)
        popdata_flat = np.array([pop for pop in hainan_pprank.flat]).reshape(hainan_pprank.size,1)
        poprank_data = np.hstack((loc_arr,popdata_flat)).tolist()
        
        range_color = ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8','#ffffbf','#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
        hainan_pprank_bar3d.add("",
                                x_axis,
                                y_axis,
                                poprank_data,
                                is_visualmap=True,
                                visual_range=[0, 90],
                                visual_range_color=range_color,
                                grid3d_width=200,
                                grid3d_depth=80,
                                xaxis3d_name = xyz_names[0],
                                yaxis3d_name = xyz_names[1],
                                zaxis3d_name = xyz_names[2]
                                )
        hainan_pprank_bar3d.render('./echartspic/hainan_pprank_bar3d.html')
        return(None)
    def Plot_CityPop_3D():
        from pyecharts import Bar3D
        nonlocal Year_index;nonlocal City_index;nonlocal hainan_popdata
        hainan_pprank_bar3d = Bar3D("海南省地级市人口分布3D图", width=1200, height=600)
        xyz_names = ['年份','城市','人口数目：（万人）']
        x_axis = Year_index
        y_axis = City_index
        
        loc_arr = location_array(hainan_popdata.shape)
        popdata_flat = np.array([pop for pop in hainan_popdata.flat]).reshape(hainan_popdata.size,1)
        popdata = np.hstack((loc_arr,popdata_flat))
        range_color = ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8','#ffffbf','#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
        hainan_pprank_bar3d.add("",
                                x_axis,
                                y_axis,
                                popdata,
                                is_visualmap=True,
                                visual_range=[0, 90],
                                visual_range_color=range_color,
                                grid3d_width=200, 
                                grid3d_depth=80,
                                xaxis3d_name = xyz_names[0],
                                yaxis3d_name = xyz_names[1],
                                zaxis3d_name = xyz_names[2]
                                )
        hainan_pprank_bar3d.render('./echartspic/hainan_ppcity_bar3d.html')
        return(None)
    def Plot_CityRank_line():
        from pyecharts import Line
        nonlocal Year_index;nonlocal City_index;nonlocal hainan_popdata
        x_axis = [x+1 for x in range(len(City_index))]
        hainan_poprank = Line("海南省地级市序位分布图",width=1200, height=600)
        hainan_popsort = -np.sort(-hainan_popdata)
        year_index = iter(Year_index)
        for year_data in hainan_popsort:
            hainan_poprank.add(
                       str(next(year_index)),
                       x_axis,
                       year_data,
                       is_smooth =True,
                       #mark_line = ["average"],
                       legend_orient = "vertical",
                       legend_pos = "left",
                       legend_top = 'center',
                       xaxis_type = 'value',
                       xaxis_name = "位序",
                       yaxis_name = "人口：（万人）"
                       )
        hainan_poprank.render("./echartspic/hainan_poprank_line.html")
        return(None)
    xinge_func()
    firstclass_index()
    Plot_CityRank_3D()
    Plot_CityPop_3D()
    Plot_CityRank_line()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
