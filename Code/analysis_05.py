from MyPyLib_v6 import *


# --------- calculate the contact width from x, d ---------


    # calculate angle beta of contact width from x in mm
def angle_width(x, x_err, d, d_err):
    angle       = 2*np.arcsin(x/d)
    angle_err   = 2*(x/d) * np.sqrt(1-(x/d)**2)**(-1) * np.sqrt( (x_err/x)**2 + (d_err/d)**2 )
    return angle, angle_err
                                
    # calculate contact width from x in mm
def W(x, x_err, d, d_err):
    angle, angle_err    = angle_width(x, x_err, d, d_err)
    width              = angle * d/2
    width_err          = width * np.sqrt( (d_err/d)**2 + (angle_err/angle)**2 )
    return width, width_err

    # convert length / pixel into length / mm using a gauge measurement
def pixel_to_length(y, y_err, gauge_pix, gauge_pix_err):
    gauge_mm, gauge_mm_err  = 1.53, 0.02     # in mm         
    length_mm               = gauge_mm / gauge_pix * y 
    length_mm_err           = length_mm * np.sqrt( (y_err/y)**2 + (gauge_pix_err/gauge_pix)**2 + (gauge_mm_err/gauge_mm)**2 ) 
    return length_mm, length_mm_err

def rad_to_degree(rad):
    return rad/ (2*np.pi) * 360

def degree_to_rad(degree):
    return degree/360 * (2*np.pi)

def fitfunc_ID(B, x):
    return B[0] * x 
params_guess = [1]

    # average repeated measurement with individual uncertainties
def weighted_average(y, y_err):
    weighted_average     = np.nansum( y / y_err**2 ) / np.nansum( 1/y_err**2 )
    weighted_uncertainty = np.sqrt( 1 / np.nansum( 1/y_err**2 ) )
    return weighted_average, weighted_uncertainty

    # filter contact lengths by drop volume / ul and cylinder diameter / mm and average
def filter_average(array, array_err, ul, mm):
    mask = (volume==ul) & (diameter==mm)
    array_filtered      = array[mask]
    array_err_filtered  = array_err[mask]
    avg, avg_err        = weighted_average(array_filtered, array_err_filtered)
    return avg, avg_err

    # volume of a half sphere
def volume_to_diameter( volume ):
    return (12*volume / np.pi)**(1/3)

    # diameter of a half sphere
def diameter_to_volume( diameter ):
    return diameter**3 * np.pi /12

def format_uncert( value, error, unit="" ):
    return f"{ufloat(value,error):.1uS} " + unit


red     = "#E76F51"
orange  = "#F4A261"
teal    = "#2A9D8F"
steel   = "#264653"
violet  = "#9B5DE5"
green   = "#55BB50"
pink    = "#D7308F"
colors  = [red, orange, teal, steel, violet, green, pink]

fmt_len = ".-"
fmt_wid = "s--"
siz_wid = 5

load_plotting()

    # the capillary length
Lc = 2.71 


# ----------------------------------------------------
# -------------------- 2mm PMMMA ---------------------
# ----------------------------------------------------



# --------- data import ---------


dataset_2mm = np.genfromtxt("../Data/week4_PMMA_2-3ul_2mm.CSV", delimiter=";", skip_header=2)

index           = dataset_2mm[:,0]

volume          = dataset_2mm[:,2]   # in ul
volume_err      = 0.01 * volume
diameter        = dataset_2mm[:,3]   # in mm
diameter_err    = dataset_2mm[:,4]
length          = dataset_2mm[:,5]   # in pixel
length_err      = 0.05 * length
    # use the data with focus on the cylinder (lower spread)
x_width         = dataset_2mm[:,9]   # in pixel
x_width_err     = 0.05 * x_width
gauge           = dataset_2mm[:,7]   # in pixel 
gauge_err       = 0.05 * gauge

    # length conversion
length, length_err      = pixel_to_length(length, length_err, gauge, gauge_err)
x_width, x_width_err    = pixel_to_length(x_width, x_width_err, gauge, gauge_err)

    # width calculation
width, width_err        = W(x_width, x_width_err, diameter, diameter_err)


# --------- plotting lengths & widths ---------


    # lengths vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Length $L/L_c$")
add_textbox(ax, "$2$mm Cylinder (PMMA)", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
for i in range(4):
    draw_data(ax, 
        volume[index==i], volume_err[index==i], length[index==i]/Lc, length_err[index==i]/Lc,
        f"$_{i:.0f}$", fmt_len, colors[i], 10, 0, 2)
close_plot(ax, "../Figs/w05_02mm_lengths.jpg")

    # widths vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Width $W/L_c$")
add_textbox(ax, "$2$mm Cylinder (PMMA)", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
for i in range(4):
    draw_data(ax, 
        volume[index==i], volume_err[index==i], width[index==i]/Lc, width_err[index==i]/Lc,
        f"$_{i:.0f}$", fmt_wid, colors[i], siz_wid, 0, 2)
close_plot(ax, "../Figs/w05_02mm_widths.jpg")

    # both vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Length $L/L_c$ or Width $W/L_c$")
add_textbox(ax, "$2$mm Cylinder (PMMA)", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
for i in range(4):
    draw_data(ax, 
        volume[index==i], volume_err[index==i], length[index==i]/Lc, length_err[index==i]/Lc,
        None, fmt_len, colors[i], 10, 0, 2)
    draw_data(ax, 
        volume[index==i], volume_err[index==i], width[index==i]/Lc, width_err[index==i]/Lc,
        None, fmt_wid, colors[i], siz_wid, 0, 2)
draw_data(ax, [], None, [], None, "Lengths", fmt_len, "black", 10, 0, 2)
draw_data(ax, [], None, [], None, "Widths", fmt_wid, "black", siz_wid, 0, 2)
close_plot(ax, "../Figs/w05_02mm_both.jpg")


    # averaging over measurement graphs 
volume_avg = [2,2.2,2.4,2.6,2.9,3.2]
length_avg, length_avg_err = [], []
width_avg, width_avg_err   = [], []

for v in volume_avg:
    lv, lv_err = weighted_average(length[volume==v], length_err[volume==v])
    wv, wv_err = weighted_average(width[volume==v], width_err[volume==v])
    length_avg.append(lv)
    length_avg_err.append(lv_err)
    width_avg.append(wv)
    width_avg_err.append(wv_err)

length_avg_2mm, length_avg_err_2mm = np.array(length_avg), np.array(length_avg_err)
width_avg_2mm, width_avg_err_2mm   = np.array(width_avg), np.array(width_avg_err)
volume_avg_2mm = np.array(volume_avg)

    # both_avg vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Length $L/L_c$ or Width $W/L_c$")
add_textbox(ax, "$2$mm Cylinder (PMMA)", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
draw_data(ax, volume_avg_2mm, None, length_avg_2mm/Lc, length_avg_err_2mm/Lc, "Lengths", fmt_len, "black", 10, 5, 2)
draw_data(ax, volume_avg_2mm, None, width_avg_2mm/Lc, width_avg_err_2mm/Lc, "Widths", fmt_wid, "black", siz_wid, 5, 2)
close_plot(ax, "../Figs/w05_02mm_both_avg.jpg")



ratio_2mm     = length_avg_2mm/width_avg_2mm
ratio_err_2mm = ratio_2mm * np.sqrt( (length_avg_err_2mm/length_avg_2mm)**2 + (width_avg_err_2mm/width_avg_2mm)**2 )


    # ratio vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Aspect Ratio $L/W$")
add_textbox(ax, "$2$mm Cylinder (PMMA)", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
draw_data(ax, volume_avg_2mm, None, ratio_2mm, ratio_err_2mm, "Data", ".-", "black", 10, 5, 2)
close_plot(ax, "../Figs/w05_02mm_ratio.jpg")


volume_diameter_2mm = volume_to_diameter(volume_avg_2mm)   


    # linear fit
params_l, sigmas_l, chi_l, fit_l = fit_model(volume_diameter_2mm, None, length_avg_2mm, length_avg_err_2mm, fitfunc_ID, params_guess, ROI=None, ROF=None, info=True )
params_w, sigmas_w, chi_w, fit_w = fit_model(volume_diameter_2mm, None, width_avg_2mm, width_avg_err_2mm, fitfunc_ID, params_guess, ROI=None, ROF=None, info=True )

    # both_avg vs volume diameter (fit)
ax = init_plot()
draw_grid()
add_second_axis(ax, diameter_to_volume, volume_to_diameter, r"Volume V / $\mu$L")
draw_text(ax, r"Reference Length $L_0(V)$ / mm", r"Contact Length $L$ or Width $W$ / mm")
add_textbox(ax, "$2$mm Cylinder (PMMA)", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
draw_data(ax, volume_diameter_2mm, None, length_avg_2mm, length_avg_err_2mm, "Lengths", fmt_len, "black", 10, 5, 2)
draw_data(ax, volume_diameter_2mm, None, width_avg_2mm, width_avg_err_2mm, "Widths", fmt_wid, "black", siz_wid, 5, 2)
draw_data(ax, *fit_l, r"Fit: $k_L \,\,=$ "+format_uncert(params_l[0],sigmas_l[0]), "-", orange, 0, 0, 4, alpha=0.5)
draw_data(ax, *fit_w, r"Fit: $k_W =$ "+format_uncert(params_w[0],sigmas_w[0]), "-", teal, 0, 0, 4, alpha=0.5)
close_plot(ax, "../Figs/w05_02mm_both_fit.jpg")




# ----------------------------------------------------
# -------------------- 4mm PMMMA ---------------------
# ----------------------------------------------------



# --------- data import ---------


dataset_4mm = np.genfromtxt("../Data/week3_PMMA_2-12ul_4mm.CSV", delimiter=";", skip_header=2)


index           = dataset_4mm[:,0]

volume          = dataset_4mm[:,2]   # in ul
volume_err      = 0.01 * volume
diameter        = dataset_4mm[:,3]   # in mm
diameter_err    = dataset_4mm[:,4]
length          = dataset_4mm[:,5]   # in pixel
length_err      = 0.05 * length
x_width         = dataset_4mm[:,6]   # in pixel
x_width_err     = 0.05 * x_width
gauge           = dataset_4mm[:,7]   # in pixel 
gauge_err       = 0.05 * gauge

    # length conversion
length, length_err      = pixel_to_length(length, length_err, gauge, gauge_err)
x_width, x_width_err    = pixel_to_length(x_width, x_width_err, gauge, gauge_err)

    # width calculation
width, width_err        = W(x_width, x_width_err, diameter, diameter_err)


# --------- plotting lengths & widths ---------


    # lengths vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Length $L/L_c$")
add_textbox(ax, "$4$mm Cylinder (PMMA)", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
for i in range(5):
    draw_data(ax, 
        volume[index==i], volume_err[index==i], length[index==i]/Lc, length_err[index==i]/Lc,
        f"$_{i:.0f}$", fmt_len, colors[i], 10, 0, 2)
close_plot(ax, "../Figs/w05_04mm_lengths.jpg")

    # widths vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Width $W/L_c$")
add_textbox(ax, "$4$mm Cylinder (PMMA)", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
for i in range(5):
    draw_data(ax, 
        volume[index==i], volume_err[index==i], width[index==i]/Lc, width_err[index==i]/Lc,
        f"$_{i:.0f}$", fmt_wid, colors[i], siz_wid, 0, 2)
close_plot(ax, "../Figs/w05_04mm_widths.jpg")

    # both vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Length $L/L_c$ or Width $W/L_c$")
add_textbox(ax, "$4$mm Cylinder (PMMA)", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
for i in range(5):
    draw_data(ax, 
        volume[index==i], volume_err[index==i], length[index==i]/Lc, length_err[index==i]/Lc,
        None, fmt_len, colors[i], 10, 0, 2)
    draw_data(ax, 
        volume[index==i], volume_err[index==i], width[index==i]/Lc, width_err[index==i]/Lc,
        None, fmt_wid, colors[i], siz_wid, 0, 2)
draw_data(ax, [], None, [], None, "Lengths", fmt_len, "black", 10, 0, 2)
draw_data(ax, [], None, [], None, "Widths", fmt_wid, "black", siz_wid, 0, 2)
close_plot(ax, "../Figs/w05_04mm_both.jpg")


    # averaging over measurement graphs 
volume_avg = [2,4,6,8,10,12]
length_avg, length_avg_err = [], []
width_avg, width_avg_err   = [], []

for v in volume_avg:
    lv, lv_err = weighted_average(length[volume==v], length_err[volume==v])
    wv, wv_err = weighted_average(width[volume==v], width_err[volume==v])
    length_avg.append(lv)
    length_avg_err.append(lv_err)
    width_avg.append(wv)
    width_avg_err.append(wv_err)

length_avg_4mm, length_avg_err_4mm = np.array(length_avg), np.array(length_avg_err)
width_avg_4mm, width_avg_err_4mm   = np.array(width_avg), np.array(width_avg_err)
volume_avg_4mm = np.array(volume_avg)

    # both_avg vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Length $L/L_c$ or Width $W/L_c$")
add_textbox(ax, "$4$mm Cylinder (PMMA)", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
draw_data(ax, volume_avg_4mm, None, length_avg_4mm/Lc, length_avg_err_4mm/Lc, "Lengths", fmt_len, "black", 10, 5, 2)
draw_data(ax, volume_avg_4mm, None, width_avg_4mm/Lc, width_avg_err_4mm/Lc, "Widths", fmt_wid, "black", siz_wid, 5, 2)
close_plot(ax, "../Figs/w05_04mm_both_avg.jpg")



ratio_4mm     = length_avg_4mm/width_avg_4mm
ratio_err_4mm = ratio_4mm * np.sqrt( (length_avg_err_4mm/length_avg_4mm)**2 + (width_avg_err_4mm/width_avg_4mm)**2 )


    # ratio vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Aspect Ratio $L/W$")
add_textbox(ax, "$4$mm Cylinder (PMMA)", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
draw_data(ax, volume_avg_4mm, None, ratio_4mm, ratio_err_4mm, "Data", fmt_len, "black", 10, 5, 2)
close_plot(ax, "../Figs/w05_04mm_ratio.jpg")


volume_diameter_4mm = volume_to_diameter(volume_avg_4mm)   


    # linear fit
params_l, sigmas_l, chi_l, fit_l = fit_model(volume_diameter_4mm, None, length_avg_4mm, length_avg_err_4mm, fitfunc_ID, params_guess, ROI=(volume_avg_4mm<12), ROF=[1.9, 3.5], info=True )
params_w, sigmas_w, chi_w, fit_w = fit_model(volume_diameter_4mm, None, width_avg_4mm, width_avg_err_4mm, fitfunc_ID, params_guess, ROI=(volume_avg_4mm<12), ROF=[1.9, 3.5], info=True )

    # both_avg vs volume diameter (fit)
ax = init_plot()
draw_grid()
add_second_axis(ax, diameter_to_volume, volume_to_diameter, r"Volume V / $\mu$L")
draw_text(ax, r"Reference Length $L_0(V)$ / mm", r"Contact Length $L$ or Width $W$ / mm")
add_textbox(ax, "$4$mm Cylinder (PMMA)", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
draw_data(ax, volume_diameter_4mm, None, length_avg_4mm, length_avg_err_4mm, "Lengths", fmt_len, "black", 10, 5, 2)
draw_data(ax, volume_diameter_4mm, None, width_avg_4mm, width_avg_err_4mm, "Widths", fmt_wid, "black", siz_wid, 5, 2)
draw_data(ax, *fit_l, r"Fit: $k_L \,\,=$ "+format_uncert(params_l[0],sigmas_l[0]), "-", orange, 0, 0, 4, alpha=0.5)
draw_data(ax, *fit_w, r"Fit: $k_W =$ "+format_uncert(params_w[0],sigmas_w[0]), "-", teal, 0, 0, 4, alpha=0.5)
close_plot(ax, "../Figs/w05_04mm_both_fit.jpg")





# ----------------------------------------------------
# ------------------- 10mm PMMMA ---------------------
# ----------------------------------------------------







dataset_10mm = np.genfromtxt("../Data/week4_PMMA_2-30ul_10mm.CSV", delimiter=";", skip_header=2)


index           = dataset_10mm[:,0]

volume          = dataset_10mm[:,2]   # in ul
volume_err      = 0.01 * volume
diameter        = dataset_10mm[:,3]   # in mm
diameter_err    = dataset_10mm[:,4]
length          = dataset_10mm[:,5]   # in pixel
length_err      = 0.05 * length
x_width         = dataset_10mm[:,6]   # in pixel
x_width_err     = 0.05 * x_width
gauge           = dataset_10mm[:,7]   # in pixel 
gauge_err       = 0.05 * gauge

    # length conversion
length, length_err      = pixel_to_length(length, length_err, gauge, gauge_err)
x_width, x_width_err    = pixel_to_length(x_width, x_width_err, gauge, gauge_err)

    # width calculation
width, width_err        = W(x_width, x_width_err, diameter, diameter_err)


# --------- plotting lengths & widths ---------


    # lengths vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Length $L/L_c$")
add_textbox(ax, "$10$mm Cylinder (PMMA)", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
for i in range(6):
    draw_data(ax, 
        volume[index==i], volume_err[index==i], length[index==i]/Lc, length_err[index==i]/Lc,
        f"$_{i:.0f}$", fmt_len, colors[i], 10, 0, 2)
close_plot(ax, "../Figs/w05_10mm_lengths.jpg")

    # widths vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Width $W/L_c$")
add_textbox(ax, "$10$mm Cylinder (PMMA)", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
for i in range(6):
    draw_data(ax, 
        volume[index==i], volume_err[index==i], width[index==i]/Lc, width_err[index==i]/Lc,
        f"$_{i:.0f}$", fmt_wid, colors[i], siz_wid, 0, 2)
close_plot(ax, "../Figs/w05_10mm_widths.jpg")

    # both vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Length $L/L_c$ or Width $W/L_c$")
add_textbox(ax, "$10$mm Cylinder (PMMA)", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
for i in range(6):
    draw_data(ax, 
        volume[index==i], volume_err[index==i], length[index==i]/Lc, length_err[index==i]/Lc,
        None, fmt_len, colors[i], 10, 0, 2)
    draw_data(ax, 
        volume[index==i], volume_err[index==i], width[index==i]/Lc, width_err[index==i]/Lc,
        None, fmt_wid, colors[i], siz_wid, 0, 2)
draw_data(ax, [], None, [], None, "Lengths", fmt_len, "black", 10, 0, 2)
draw_data(ax, [], None, [], None, "Widths", fmt_wid, "black", siz_wid, 0, 2)
close_plot(ax, "../Figs/w05_10mm_both.jpg")


    # averaging over measurement graphs 
volume_avg = [2,4,8,12,16,20]
length_avg, length_avg_err = [], []
width_avg, width_avg_err   = [], []

for v in volume_avg:
    lv, lv_err = weighted_average(length[volume==v], length_err[volume==v])
    wv, wv_err = weighted_average(width[volume==v], width_err[volume==v])
    length_avg.append(lv)
    length_avg_err.append(lv_err)
    width_avg.append(wv)
    width_avg_err.append(wv_err)

length_avg_10mm, length_avg_err_10mm = np.array(length_avg), np.array(length_avg_err)
width_avg_10mm, width_avg_err_10mm   = np.array(width_avg), np.array(width_avg_err)
volume_avg_10mm = np.array(volume_avg)

    # both_avg vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Length $L/L_c$ or Width $W/L_c$")
add_textbox(ax, "$10$mm Cylinder (PMMA)", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
draw_data(ax, volume_avg_10mm, None, length_avg_10mm/Lc, length_avg_err_10mm/Lc, "Lengths", fmt_len, "black", 10, 5, 2)
draw_data(ax, volume_avg_10mm, None, width_avg_10mm/Lc, width_avg_err_10mm/Lc, "Widths", fmt_wid, "black", siz_wid, 5, 2)
close_plot(ax, "../Figs/w05_10mm_both_avg.jpg")


ratio_10mm     = length_avg_10mm/width_avg_10mm
ratio_err_10mm = ratio_10mm * np.sqrt( (length_avg_err_10mm/length_avg_10mm)**2 + (width_avg_err_10mm/width_avg_10mm)**2 )


    # ratio vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Aspect Ratio $L/W$")
add_textbox(ax, "$10$mm Cylinder (PMMA)", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
draw_data(ax, volume_avg_10mm, None, ratio_10mm, ratio_err_10mm, "Data", ".-", "black", 10, 5, 2)
close_plot(ax, "../Figs/w05_10mm_ratio.jpg")


volume_diameter_10mm = volume_to_diameter(volume_avg_10mm)   


    # linear fit
params_l, sigmas_l, chi_l, fit_l = fit_model(volume_diameter_10mm, None, length_avg_10mm, length_avg_err_10mm, fitfunc_ID, params_guess, ROI=(volume_avg_10mm<20), ROF=[1.9, 4.1], info=True )
params_w, sigmas_w, chi_w, fit_w = fit_model(volume_diameter_10mm, None, width_avg_10mm, width_avg_err_10mm, fitfunc_ID, params_guess, ROI=(volume_avg_10mm<20), ROF=[1.9, 4.1], info=True )

    # both_avg vs volume diameter (fit)
ax = init_plot()
draw_grid()
add_second_axis(ax, diameter_to_volume, volume_to_diameter, r"Volume V / $\mu$L")
draw_text(ax, r"Reference Length $L_0(V)$ / mm", r"Contact Length $L$ or Width $W$ / mm")
add_textbox(ax, "$10$mm Cylinder (PMMA)", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
draw_data(ax, volume_diameter_10mm, None, length_avg_10mm, length_avg_err_10mm, "Lengths", fmt_len, "black", 10, 5, 2)
draw_data(ax, volume_diameter_10mm, None, width_avg_10mm, width_avg_err_10mm, "Widths", fmt_wid, "black", siz_wid, 5, 2)
draw_data(ax, *fit_l, r"Fit: $k_L \,\,=$ "+format_uncert(params_l[0],sigmas_l[0]), "-", orange, 0, 0, 4, alpha=0.5)
draw_data(ax, *fit_w, r"Fit: $k_W =$ "+format_uncert(params_w[0],sigmas_w[0]), "-", teal, 0, 0, 4, alpha=0.5)
close_plot(ax, "../Figs/w05_10mm_both_fit.jpg")






# ----------------------------------------------------
# -------------------- Comparison ---------------------
# ----------------------------------------------------





    # ratio vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Aspect Ratio $L/W$")
draw_data(ax, volume_avg_2mm, None, ratio_2mm, ratio_err_2mm, "On $2$mm", ".-", green, 10, 5, 2)
draw_data(ax, volume_avg_4mm, None, ratio_4mm, ratio_err_4mm, "On $4$mm", ".-", teal, 10, 5, 2)
draw_data(ax, volume_avg_10mm, None, ratio_10mm, ratio_err_10mm, "On $10$mm", ".-", red, 10, 5, 2)
close_plot(ax, "../Figs/w05_ratios.jpg")


    # both_avg vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Length $L/L_c$ or Width $W/L_c$")
add_textbox(ax, "$10$mm Cylinder (PMMA)", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
draw_data(ax, volume_avg_2mm, None, length_avg_2mm/Lc, length_avg_err_2mm/Lc, "Lengths on $2$mm", fmt_len, green, 10, 5, 2)
draw_data(ax, volume_avg_2mm, None, width_avg_2mm/Lc, width_avg_err_2mm/Lc, "Widths on $2$mm", fmt_wid, green, siz_wid, 5, 2)
draw_data(ax, volume_avg_4mm, None, length_avg_4mm/Lc, length_avg_err_4mm/Lc, "Lengths on $4$mm", fmt_len, teal, 10, 5, 2)
draw_data(ax, volume_avg_4mm, None, width_avg_4mm/Lc, width_avg_err_4mm/Lc, "Widths on $4$mm", fmt_wid, teal, siz_wid, 5, 2)
draw_data(ax, volume_avg_10mm, None, length_avg_10mm/Lc, length_avg_err_10mm/Lc, "Lengths on $10$mm", fmt_len, red, 10, 5, 2)
draw_data(ax, volume_avg_10mm, None, width_avg_10mm/Lc, width_avg_err_10mm/Lc, "Widths on $10$mm", fmt_wid, red, siz_wid, 5, 2)
close_plot(ax, "../Figs/w05_both_avg.jpg")



# contact lenghts / widths should be Norm. by the cylinder diameter 
# drop volumes should be Norm. by the cylinder cross-sectional area

norm_volume_2mm = np.pi * (2.19/2)**2
norm_volume_4mm = np.pi * (3.99/2)**2
norm_volume_10mm = np.pi * (10.2/2)**2

norm_lengths_2mm = 2.19
norm_lengths_4mm = 3.99
norm_lengths_10mm = 10.2


    # ratio vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Norm. Drop Volume $V$ / $\frac{\pi}{4} D^2$   / mm", r"Aspect Ratio $L/W$")
draw_data(ax, volume_avg_2mm/norm_volume_2mm, None, ratio_2mm, ratio_err_2mm, "On $2$mm", ".-", green, 10, 5, 2)
draw_data(ax, volume_avg_4mm/norm_volume_4mm, None, ratio_4mm, ratio_err_4mm, "On $4$mm", ".-", teal, 10, 5, 2)
draw_data(ax, volume_avg_10mm/norm_volume_10mm, None, ratio_10mm, ratio_err_10mm, "On $10$mm", ".-", red, 10, 5, 2)
close_plot(ax, "../Figs/w05_ratios_norm.jpg")


    # both_avg vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Norm. Drop Volume $V$ / $\frac{\pi}{4} D^2$   / mm", r"Norm. Contact Length $L/D$ or Width $W/D$"  )
draw_data(ax, volume_avg_2mm/norm_volume_2mm, None, length_avg_2mm/norm_lengths_2mm, length_avg_err_2mm/norm_lengths_2mm, "Lengths on $2$mm", fmt_len, green, 10, 5, 2)
draw_data(ax, volume_avg_2mm/norm_volume_2mm, None, width_avg_2mm/norm_lengths_2mm, width_avg_err_2mm/norm_lengths_2mm, "Widths on $2$mm", fmt_wid, green, siz_wid, 5, 2)
draw_data(ax, volume_avg_4mm/norm_volume_4mm, None, length_avg_4mm/norm_lengths_4mm, length_avg_err_4mm/norm_lengths_4mm, "Lengths on $4$mm", fmt_len, teal, 10, 5, 2)
draw_data(ax, volume_avg_4mm/norm_volume_4mm, None, width_avg_4mm/norm_lengths_4mm, width_avg_err_4mm/norm_lengths_4mm, "Widths on $4$mm", fmt_wid, teal, siz_wid, 5, 2)
draw_data(ax, volume_avg_10mm/norm_volume_10mm, None, length_avg_10mm/norm_lengths_10mm, length_avg_err_10mm/norm_lengths_10mm, "Lengths on $10$mm", fmt_len, red, 10, 5, 2)
draw_data(ax, volume_avg_10mm/norm_volume_10mm, None, width_avg_10mm/norm_lengths_10mm, width_avg_err_10mm/norm_lengths_10mm, "Widths on $10$mm", fmt_wid, red, siz_wid, 5, 2)
close_plot(ax, "../Figs/w05_both_avg_norm.jpg")
