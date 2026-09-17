from MyPyLib_v6 import *
load_plotting()


# --------------------------------------------
# ------------ global parameters -------------
# --------------------------------------------


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

Lc = 2.71                   # the capillary length
distance_delta = 0.05       # 5% uncertainties on all distances
volume_delta = 0.01         # 1% volume uncertainty

datasets_ratio_PMMA = []
datasets_ratio_PET  = []
datasets_L_PET      = []
datasets_L_PMMA     = []
datasets_W_PET      = []
datasets_W_PMMA     = []


# --------------------------------------------
# ----------- function definitions -----------
# --------------------------------------------


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
    if(np.nansum(y_err)==0):
        return np.nan, np.nan
    weighted_average     = np.nansum( y / y_err**2 ) / np.nansum( 1/y_err**2 )
    weighted_uncertainty = np.sqrt( 1 / np.nansum( 1/y_err**2 ) )
    return weighted_average, weighted_uncertainty

    # volume of a half sphere
def volume_to_diameter( volume ):
    return (12*volume / np.pi)**(1/3)

    # diameter of a half sphere
def diameter_to_volume( diameter ):
    return diameter**3 * np.pi /12

def format_uncert( value, error, unit="" ):
    return f"{ufloat(value,error):.1uS} " + unit


def get_data( csv_name, volume_list, x_column=6 ):

    dataset = np.genfromtxt("../Data/"+csv_name+".CSV", delimiter=";", skip_header=2)

    index           = dataset[:,0]
    volume          = dataset[:,2]              # in ul
    volume_err      = volume_delta * volume     # in ul
    diameter        = dataset[:,3]              # in mm
    diameter_err    = dataset[:,4]              # in mm
    length          = dataset[:,5]              # in pixel
    length_err      = distance_delta * length   # in pixel

        # use the data with focus on the cylinder (lower spread)
    x_width         = dataset[:,x_column]              # in pixel
    x_width_err     = distance_delta * x_width  # in pixel
    gauge           = dataset[:,7]              # in pixel 
    gauge_err       = distance_delta * gauge    # in pixel

        # length conversion
    length, length_err      = pixel_to_length(length, length_err, gauge, gauge_err)
    x_width, x_width_err    = pixel_to_length(x_width, x_width_err, gauge, gauge_err)

        # width calculation
    width, width_err        = W(x_width, x_width_err, diameter, diameter_err)

    data_raw = [volume, volume_err, length, length_err, width, width_err]

        # averaging over measurement graphs 
    length_avg, length_avg_err = [], []
    width_avg, width_avg_err   = [], []

    for v in volume_list:
        lv, lv_err = weighted_average(length[volume==v], length_err[volume==v])
        wv, wv_err = weighted_average(width[volume==v], width_err[volume==v])
        length_avg.append(lv)
        length_avg_err.append(lv_err)
        width_avg.append(wv)
        width_avg_err.append(wv_err)

    length_avg, length_avg_err = np.array(length_avg), np.array(length_avg_err)
    width_avg, width_avg_err   = np.array(width_avg), np.array(width_avg_err)
    volume_avg = np.array(volume_list)

    data_avg = [volume_avg, volume_delta*volume_avg, length_avg, length_avg_err, width_avg, width_avg_err]

    return index, diameter[0], data_raw, data_avg


def plot_single(csv_name, material_str, volume_list, iterations, ROI_max, ROF, x_column=6):

    index, diameter_float, data_raw, data_avg = get_data( csv_name, volume_list, x_column )
    volume, volume_err, length, length_err, width, width_err = data_raw
    diameter_ID = f"{round(diameter_float):02d}mm"
    diameter_string = f"{round(diameter_float):d}"+r"$\,$mm"

        # L vs volume
    ax = init_plot()
    draw_grid()
    draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Length $L/L_c$")
    add_textbox(ax, diameter_string+" Cylinder / "+material_str, [0.97, 0.03], 12, "right", "bottom", draw_box=True)
    for i in range(iterations):
        draw_data(ax, 
            volume[index==i], volume_err[index==i], length[index==i]/Lc, length_err[index==i]/Lc,
            f"$_{i:.0f}$", fmt_len, colors[i], 10, 0, 2)
    close_plot(ax, "../Plots/w06_"+diameter_ID+"_"+material_str+"_L.jpg", "upper left")

        # W vs volume
    ax = init_plot()
    draw_grid()
    draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Width $W/L_c$")
    add_textbox(ax, diameter_string+" Cylinder / "+material_str, [0.97, 0.03], 12, "right", "bottom", draw_box=True)
    for i in range(iterations):
        draw_data(ax, 
            volume[index==i], volume_err[index==i], width[index==i]/Lc, width_err[index==i]/Lc,
            f"$_{i:.0f}$", fmt_wid, colors[i], siz_wid, 0, 2)
    close_plot(ax, "../Plots/w06_"+diameter_ID+"_"+material_str+"_W.jpg", "upper left")

        # L + W vs volume
    ax = init_plot()
    draw_grid()
    draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Length $L/L_c$ or Width $W/L_c$")
    add_textbox(ax, diameter_string+" Cylinder / "+material_str, [0.97, 0.03], 12, "right", "bottom", draw_box=True)
    for i in range(iterations):
        draw_data(ax, 
            volume[index==i], volume_err[index==i], length[index==i]/Lc, length_err[index==i]/Lc,
            None, fmt_len, colors[i], 10, 0, 2)
        draw_data(ax, 
            volume[index==i], volume_err[index==i], width[index==i]/Lc, width_err[index==i]/Lc,
            None, fmt_wid, colors[i], siz_wid, 0, 2)
    draw_data(ax, [], None, [], None, "Lengths", fmt_len, "black", 10, 0, 2)
    draw_data(ax, [], None, [], None, "Widths", fmt_wid, "black", siz_wid, 0, 2)
    close_plot(ax,  "../Plots/w06_"+diameter_ID+"_"+material_str+"_L+W.jpg", "upper left")


    volume_avg, volume_avg_err, length_avg, length_avg_err, width_avg, width_avg_err = data_avg

        # both_avg vs volume
    ax = init_plot()
    draw_grid()
    draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Length $L/L_c$ or Width $W/L_c$")
    add_textbox(ax, diameter_string+" Cylinder / "+material_str, [0.97, 0.03], 12, "right", "bottom", draw_box=True)
    draw_data(ax, volume_avg, None, length_avg/Lc, length_avg_err/Lc, "Lengths", fmt_len, "black", 10, 5, 2)
    draw_data(ax, volume_avg, None, width_avg/Lc, width_avg_err/Lc, "Widths", fmt_wid, "black", siz_wid, 5, 2)
    close_plot(ax, "../Plots/w06_"+diameter_ID+"_"+material_str+"_L+W_avg.jpg", "upper left")

    ratio     = length_avg/width_avg
    ratio_err = ratio * np.sqrt( (length_avg_err/length_avg)**2 + (width_avg_err/width_avg)**2 )

        # ratio vs volume
    ax = init_plot()
    draw_grid()
    draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Aspect Ratio $L/W$")
    add_textbox(ax, diameter_string+" Cylinder / "+material_str, [0.97, 0.03], 12, "right", "bottom", draw_box=True)
    draw_data(ax, volume_avg, None, ratio, ratio_err, "Data", ".-", "black", 10, 5, 2)
    close_plot(ax, "../Plots/w06_"+diameter_ID+"_"+material_str+"_ratio.jpg")

    volume_diameter = volume_to_diameter(volume_avg)   

        # linear fit
    params_l, sigmas_l, chi_l, fit_l = fit_model(volume_diameter, None, length_avg, length_avg_err, fitfunc_ID, params_guess, ROI=(volume_avg<ROI_max), ROF=ROF, info=False )
    params_w, sigmas_w, chi_w, fit_w = fit_model(volume_diameter, None, width_avg, width_avg_err, fitfunc_ID, params_guess, ROI=(volume_avg<ROI_max), ROF=ROF, info=False )

        # both_avg vs volume diameter (fit)
    ax = init_plot()
    draw_grid()
    add_second_axis(ax, diameter_to_volume, volume_to_diameter, r"Volume V / $\mu$L")
    draw_text(ax, r"Reference Length $L_0(V)$ / mm", r"Contact Length $L$ or Width $W$ / mm")
    add_textbox(ax, diameter_string+" Cylinder / "+material_str, [0.97, 0.03], 12, "right", "bottom", draw_box=True)
    draw_data(ax, volume_diameter, None, length_avg, length_avg_err, "Lengths", fmt_len, "black", 10, 5, 2)
    draw_data(ax, volume_diameter, None, width_avg, width_avg_err, "Widths", fmt_wid, "black", siz_wid, 5, 2)
    draw_data(ax, *fit_l, r"Fit: $k_L \,\,=$ "+format_uncert(params_l[0],sigmas_l[0]), "-", orange, 0, 0, 4, alpha=0.5)
    draw_data(ax, *fit_w, r"Fit: $k_W =$ "+format_uncert(params_w[0],sigmas_w[0]), "-", teal, 0, 0, 4, alpha=0.5)
    close_plot(ax, "../Plots/w06_"+diameter_ID+"_"+material_str+"_L+W_fit.jpg", "upper left")

    if (material_str == "PMMA"):
        datasets_ratio_PMMA.append([volume_avg.copy(), None, ratio.copy(), ratio_err.copy()])
        datasets_L_PMMA.append([volume_avg.copy(), None, (length_avg/Lc).copy(), (length_avg_err/Lc).copy()])
        datasets_W_PMMA.append([volume_avg.copy(), None, (width_avg/Lc).copy(), (width_avg_err/Lc).copy()])
    if (material_str == "PET"):
        datasets_ratio_PET.append([volume_avg.copy(), None, ratio.copy(), ratio_err.copy()])
        datasets_L_PET.append([volume_avg.copy(), None, (length_avg/Lc).copy(), (length_avg_err/Lc).copy()])
        datasets_W_PET.append([volume_avg.copy(), None, (width_avg/Lc).copy(), (width_avg_err/Lc).copy()])


def plot_single_flat(csv_name, material_str, volume_list, iterations, ROI_max, ROF):

    index, diameter_float, data_raw, data_avg = get_data( csv_name, volume_list, 6)
    volume, volume_err, length, length_err, width, width_err = data_raw
    volume_avg, volume_avg_err, length_avg, length_avg_err, width_avg, width_avg_err = data_avg

        # L vs volume
    ax = init_plot()
    draw_grid()
    draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Length $L/L_c$")
    add_textbox(ax,"Flat / "+material_str, [0.97, 0.03], 12, "right", "bottom", draw_box=True)
    for i in range(iterations):
        draw_data(ax, 
            volume[index==i], volume_err[index==i], length[index==i]/Lc, length_err[index==i]/Lc,
            f"$_{i:.0f}$", fmt_len, colors[i], 10, 0, 2, alpha=0.5)
    draw_data(ax, volume_avg, None, length_avg/Lc, length_avg_err/Lc, "Average", fmt_len, "black", 10, 5, 2)
    close_plot(ax, "../Plots/w06_flat_"+material_str+"_L.jpg", "upper left")

    volume_diameter = volume_to_diameter(volume_avg)   

        # linear fit
    params_l, sigmas_l, chi_l, fit_l = fit_model(volume_diameter, None, length_avg, length_avg_err, fitfunc_ID, params_guess, ROI=(volume_avg<ROI_max), ROF=ROF, info=False )

        # L vs volume diameter (fit)
    ax = init_plot()
    draw_grid()
    add_second_axis(ax, diameter_to_volume, volume_to_diameter, r"Volume V / $\mu$L")
    draw_text(ax, r"Reference Length $L_0(V)$ / mm", r"Contact Length $L$ or Width $W$ / mm")
    add_textbox(ax, "Flat / "+material_str, [0.97, 0.03], 12, "right", "bottom", draw_box=True)
    draw_data(ax, volume_diameter, None, length_avg, length_avg_err, "Lengths", fmt_len, "black", 10, 5, 2)
    draw_data(ax, *fit_l, r"Fit: $k_L \,\,=$ "+format_uncert(params_l[0],sigmas_l[0]), "-", orange, 0, 0, 4, alpha=0.5)
    close_plot(ax, "../Plots/w06_flat_"+material_str+"_L_fit.jpg", "upper left")

    if (material_str == "PMMA"):
        datasets_L_PMMA.append([volume_avg.copy(), None, (length_avg/Lc).copy(), (length_avg_err/Lc).copy()])
        datasets_W_PMMA.append([volume_avg.copy(), None, (length_avg/Lc).copy(), (length_avg_err/Lc).copy()])
    if (material_str == "PET"):
        datasets_L_PET.append([volume_avg.copy(), None, (length_avg/Lc).copy(), (length_avg_err/Lc).copy()])
        datasets_W_PET.append([volume_avg.copy(), None, (length_avg/Lc).copy(), (length_avg_err/Lc).copy()])


def plot_compare_ratio( diameters_PMMA, diameters_PET ):

        # PMMA ratio
    ax = init_plot()
    draw_grid()
    draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Aspect Ratio $L/W$")
    add_textbox(ax, "PMMA", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
    for i, dataset_i in enumerate(datasets_ratio_PMMA):
        draw_data(ax, *dataset_i, f"D = {diameters_PMMA[i]:.2f} mm", ".-", colors[i], 10, 5, 2)
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    draw_data(ax, [0, 30], None, [1,1], None, r"$D = 0.00$ mm", "--", violet,0,0,1)
    close_plot(ax, "../Plots/w06_PMMA_ratios.jpg", xlim=xlim, ylim=ylim)

        # PET ratio
    ax = init_plot()
    draw_grid()
    draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Aspect Ratio $L/W$")
    add_textbox(ax, "PET", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
    for i, dataset_i in enumerate(datasets_ratio_PET):
        draw_data(ax, *dataset_i, f"D = {diameters_PET[i]:.2f} mm", ".-", colors[i], 10, 5, 2)
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    draw_data(ax, [0, 30], None, [1,1], None, r"$D = 0.00$ mm", "--", violet,0,0,1)
    close_plot(ax, "../Plots/w06_PET_ratios.jpg", xlim=xlim, ylim=ylim)

        # PMMA ratio normed
    ax = init_plot()
    draw_grid()
    draw_text(ax, r"Norm. Drop Volume $V$ / $\frac{\pi}{4} D^2$   / mm", r"Aspect Ratio $L/W$")
    add_textbox(ax, "PMMA", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
    for i, dataset_i in enumerate(datasets_ratio_PMMA):
        dataset_i = [dataset_i[0]/(np.pi*diameters_PMMA[i]**2), dataset_i[1], dataset_i[2], dataset_i[3]]
        draw_data(ax, *dataset_i, f"D = {diameters_PMMA[i]:.2f} mm", ".-", colors[i], 10, 5, 2)
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    draw_data(ax, [0, 30], None, [1,1], None, r"$D = 0.00$ mm", "--", violet,0,0,1)
    close_plot(ax, "../Plots/w06_PMMA_ratios_normed.jpg", xlim=xlim, ylim=ylim)

        # PET ratio normed
    ax = init_plot()
    draw_grid()
    draw_text(ax, r"Norm. Drop Volume $V$ / $\frac{\pi}{4} D^2$   / mm", r"Aspect Ratio $L/W$")
    add_textbox(ax, "PET", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
    for i, dataset_i in enumerate(datasets_ratio_PET):
        dataset_i = [dataset_i[0]/(np.pi*diameters_PET[i]**2), dataset_i[1], dataset_i[2], dataset_i[3]]
        draw_data(ax, *dataset_i, f"D = {diameters_PET[i]:.2f} mm", ".-", colors[i], 10, 5, 2)
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    draw_data(ax, [0, 30], None, [1,1], None, r"$D = 0.00$ mm", "--", violet,0,0,1)
    close_plot(ax, "../Plots/w06_PET_ratios_normed.jpg", xlim=xlim, ylim=ylim)    


def plot_compare_L_W( diameters_PMMA, diameters_PET ):

        # L vs volume (PMMA)
    ax = init_plot()
    draw_grid()
    draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Length $L/L_c$")
    add_textbox(ax, "PMMA", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
    for i, dataset_i in enumerate(datasets_L_PMMA):
        draw_data(ax, *dataset_i, f"D = {diameters_PMMA[i]:.2f} mm", fmt_len, colors[i], 10, 5, 2)
    close_plot(ax, "../Plots/w06_PMMA_L.jpg", "upper left")

        # W vs volume (PMMA)
    ax = init_plot()
    draw_grid()
    draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Width $W/L_c$")
    add_textbox(ax, "PMMA", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
    for i, dataset_i in enumerate(datasets_W_PMMA):
        draw_data(ax, *dataset_i, f"D = {diameters_PMMA[i]:.2f} mm", fmt_len, colors[i], 10, 5, 2)
    close_plot(ax, "../Plots/w06_PMMA_W.jpg", "upper left")

        # L vs volume (PET)
    ax = init_plot()
    draw_grid()
    draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Length $L/L_c$")
    add_textbox(ax, "PET", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
    for i, dataset_i in enumerate(datasets_L_PET):
        draw_data(ax, *dataset_i, f"D = {diameters_PET[i]:.2f} mm", fmt_len, colors[i], 10, 5, 2)
    close_plot(ax, "../Plots/w06_PET_L.jpg", "upper left")

        # W vs volume (PET)
    ax = init_plot()
    draw_grid()
    draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Width $W/L_c$")
    add_textbox(ax, "PET", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
    for i, dataset_i in enumerate(datasets_W_PET):
        draw_data(ax, *dataset_i, f"D = {diameters_PET[i]:.2f} mm", fmt_len, colors[i], 10, 5, 2)
    close_plot(ax, "../Plots/w06_PET_W.jpg", "upper left")

# --------------------------------------------
# ---------------- Plotting ------------------
# --------------------------------------------



plot_single("week4_PMMA_2-3ul_2mm", "PMMA", [2,2.2,2.4,2.6,2.9,3.2], 4, 100, None, 9)

plot_single("week3_PMMA_2-12ul_4mm", "PMMA", [2,4,6,8,10,12], 5, 12, [1.9, 3.5])

plot_single("week4_PMMA_2-30ul_10mm", "PMMA", [2,4,8,12,16,20], 6, 20, [1.9, 4.1])

plot_single_flat("week6_PMMA_2-24ul_0mm", "PMMA", [2,4,6,8,12,16,20,24], 5, 100, None)

plot_single("week6_PET_2-12ul_4mm", "PET", [2,4,6,8,10,12], 5, 12, [1.9, 3.5])

plot_single("week5_PET_2-24ul_10mm", "PET", [2,4,8,12,16,20,24], 7, 20, [1.9, 4.1])

plot_single_flat("week6_PET_2-24ul_0mm", "PET", [2,4,6,8,12,16,20,24], 5, 100, None)

plot_compare_ratio([2.19,3.99,10.2],[4.08, 10.2])

plot_compare_L_W([2.19,3.99,10.2,0.0],[4.08, 10.2,0.0])

# ----------------------------------------------------
# -------------------- Comparison --------------------
# ----------------------------------------------------

#   
#   
#   
#   
#       # ratio vs volume
#   ax = init_plot()
#   draw_grid()
#   draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Aspect Ratio $L/W$")
#   draw_data(ax, volume_avg_2mm, None, ratio_2mm, ratio_err_2mm, "On $2$mm", ".-", green, 10, 5, 2)
#   draw_data(ax, volume_avg_4mm, None, ratio_4mm, ratio_err_4mm, "On $4$mm", ".-", teal, 10, 5, 2)
#   draw_data(ax, volume_avg_10mm, None, ratio_10mm, ratio_err_10mm, "On $10$mm", ".-", red, 10, 5, 2)
#   close_plot(ax, "../Plots/w06_ratios_PMMA.jpg")
#   
#   
#       # both_avg vs volume
#   ax = init_plot()
#   draw_grid()
#   draw_text(ax, r"Drop Volume $V$ / $\mu$L", r"Contact Length $L/L_c$ or Width $W/L_c$")
#   add_textbox(ax, "$10$mm Cylinder (PMMA)", [0.97, 0.03], 12, "right", "bottom", draw_box=True)
#   draw_data(ax, volume_avg_2mm, None, length_avg_2mm/Lc, length_avg_err_2mm/Lc, "Lengths on $2$mm", fmt_len, green, 10, 5, 2)
#   draw_data(ax, volume_avg_2mm, None, width_avg_2mm/Lc, width_avg_err_2mm/Lc, "Widths on $2$mm", fmt_wid, green, siz_wid, 5, 2)
#   draw_data(ax, volume_avg_4mm, None, length_avg_4mm/Lc, length_avg_err_4mm/Lc, "Lengths on $4$mm", fmt_len, teal, 10, 5, 2)
#   draw_data(ax, volume_avg_4mm, None, width_avg_4mm/Lc, width_avg_err_4mm/Lc, "Widths on $4$mm", fmt_wid, teal, siz_wid, 5, 2)
#   draw_data(ax, volume_avg_10mm, None, length_avg_10mm/Lc, length_avg_err_10mm/Lc, "Lengths on $10$mm", fmt_len, red, 10, 5, 2)
#   draw_data(ax, volume_avg_10mm, None, width_avg_10mm/Lc, width_avg_err_10mm/Lc, "Widths on $10$mm", fmt_wid, red, siz_wid, 5, 2)
#   close_plot(ax, "../Plots/w06_both_avg_PMMA.jpg")
#   
#   
#   
#   # contact lenghts / widths should be Norm. by the cylinder diameter 
#   # drop volumes should be Norm. by the cylinder cross-sectional area
#   
#   norm_volume_2mm = np.pi * (2.19/2)**2
#   norm_volume_4mm = np.pi * (3.99/2)**2
#   norm_volume_10mm = np.pi * (10.2/2)**2
#   
#   norm_lengths_2mm = 2.19
#   norm_lengths_4mm = 3.99
#   norm_lengths_10mm = 10.2
#   
#   
#       # ratio vs volume
#   ax = init_plot()
#   draw_grid()
#   draw_text(ax, r"Norm. Drop Volume $V$ / $\frac{\pi}{4} D^2$   / mm", r"Aspect Ratio $L/W$")
#   draw_data(ax, volume_avg_2mm/norm_volume_2mm, None, ratio_2mm, ratio_err_2mm, "On $2$mm", ".-", green, 10, 5, 2)
#   draw_data(ax, volume_avg_4mm/norm_volume_4mm, None, ratio_4mm, ratio_err_4mm, "On $4$mm", ".-", teal, 10, 5, 2)
#   draw_data(ax, volume_avg_10mm/norm_volume_10mm, None, ratio_10mm, ratio_err_10mm, "On $10$mm", ".-", red, 10, 5, 2)
#   close_plot(ax, "../Plots/w06_ratios_norm_PMMA.jpg")
#   
#   
#       # both_avg vs volume
#   ax = init_plot()
#   draw_grid()
#   draw_text(ax, r"Norm. Drop Volume $V$ / $\frac{\pi}{4} D^2$   / mm", r"Norm. Contact Length $L/D$ or Width $W/D$"  )
#   draw_data(ax, volume_avg_2mm/norm_volume_2mm, None, length_avg_2mm/norm_lengths_2mm, length_avg_err_2mm/norm_lengths_2mm, "Lengths on $2$mm", fmt_len, green, 10, 5, 2)
#   draw_data(ax, volume_avg_2mm/norm_volume_2mm, None, width_avg_2mm/norm_lengths_2mm, width_avg_err_2mm/norm_lengths_2mm, "Widths on $2$mm", fmt_wid, green, siz_wid, 5, 2)
#   draw_data(ax, volume_avg_4mm/norm_volume_4mm, None, length_avg_4mm/norm_lengths_4mm, length_avg_err_4mm/norm_lengths_4mm, "Lengths on $4$mm", fmt_len, teal, 10, 5, 2)
#   draw_data(ax, volume_avg_4mm/norm_volume_4mm, None, width_avg_4mm/norm_lengths_4mm, width_avg_err_4mm/norm_lengths_4mm, "Widths on $4$mm", fmt_wid, teal, siz_wid, 5, 2)
#   draw_data(ax, volume_avg_10mm/norm_volume_10mm, None, length_avg_10mm/norm_lengths_10mm, length_avg_err_10mm/norm_lengths_10mm, "Lengths on $10$mm", fmt_len, red, 10, 5, 2)
#   draw_data(ax, volume_avg_10mm/norm_volume_10mm, None, width_avg_10mm/norm_lengths_10mm, width_avg_err_10mm/norm_lengths_10mm, "Widths on $10$mm", fmt_wid, red, siz_wid, 5, 2)
#   close_plot(ax, "../Plots/w06_both_avg_norm_PMMA.jpg")
#   
#   

