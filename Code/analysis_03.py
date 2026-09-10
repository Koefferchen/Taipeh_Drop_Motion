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

    # average repeated measurement with individual uncertainties
def weighted_average(y, y_err):
    weighted_average     = np.sum( y / y_err**2 ) / np.sum( 1/y_err**2 )
    weighted_uncertainty = np.sqrt( 1 / np.sum( 1/y_err**2 ) )
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
    return (6/np.pi**2 * volume*2)**(1/3)

    # diameter of a half sphere
def diameter_to_volume( diameter ):
    return diameter**3 * np.pi**2 /6 /2


# --------- data import ---------


dataset_01 = np.genfromtxt("../Data/week3_contact_2-12ul_4mm.CSV", delimiter=";", skip_header=2)


index           = dataset_01[:,0]

volume          = dataset_01[:,2]   # in ul
volume_err      = 0.01 * volume
diameter        = dataset_01[:,3]   # in mm
diameter_err    = dataset_01[:,4]
length          = dataset_01[:,5]   # in pixel
length_err      = 0.05 * length
x_width         = dataset_01[:,6]   # in pixel
x_width_err     = 0.05 * x_width
gauge           = dataset_01[:,7]   # in pixel 
gauge_err       = 0.05 * gauge

    # length conversion
length, length_err      = pixel_to_length(length, length_err, gauge, gauge_err)
x_width, x_width_err    = pixel_to_length(x_width, x_width_err, gauge, gauge_err)

    # width calculation
width, width_err        = W(x_width, x_width_err, diameter, diameter_err)


# --------- plotting lengths & widths ---------


red     = "#E76F51"
orange  = "#F4A261"
teal    = "#2A9D8F"
steel   = "#264653"
violet  = "#9B5DE5"
colors  = [red, orange, teal, steel, violet]

load_plotting()

    # lengths vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$l", r"Contact Length / mm", "Contact Lengths on $4$mm Cylinder")
for i in range(5):
    draw_data(ax, 
        volume[index==i], volume_err[index==i], length[index==i], length_err[index==i],
        f"$_{i:.0f}$", ".-", colors[i], 10, 0, 2)
close_plot(ax, "../Figs/w03_4mm_lengths.jpg")

    # widths vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$l", r"Contact Width / mm", "Contact Widths on $4$mm Cylinder")
for i in range(5):
    draw_data(ax, 
        volume[index==i], volume_err[index==i], width[index==i], width_err[index==i],
        f"$_{i:.0f}$", ".-", colors[i], 10, 0, 2)
close_plot(ax, "../Figs/w03_4mm_widths.jpg")

    # both vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$l", r"Contact Length or Width / mm", "Contact Lengths and Widths on $4$mm Cylinder")
for i in range(5):
    draw_data(ax, 
        volume[index==i], volume_err[index==i], length[index==i], length_err[index==i],
        None, ".-", colors[i], 10, 0, 2)
    draw_data(ax, 
        volume[index==i], volume_err[index==i], width[index==i], width_err[index==i],
        None, ".--", colors[i], 10, 0, 2)
draw_data(ax, [], None, [], None, "Lengths", ".-", "black", 10, 0, 2)
draw_data(ax, [], None, [], None, "Widths", ".--", "black", 10, 0, 2)
close_plot(ax, "../Figs/w03_4mm_both.jpg")


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

length_avg, length_avg_err = np.array(length_avg), np.array(length_avg_err)
width_avg, width_avg_err   = np.array(width_avg), np.array(width_avg_err)
volume_avg = np.array(volume_avg)

    # both_avg vs volume
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$l", r"Contact Length or Width / mm", "Contact Lengths and Widths on $4$mm Cylinder")
draw_data(ax, volume_avg, None, length_avg, length_avg_err, "Lengths", ".-", "black", 10, 5, 2)
draw_data(ax, volume_avg, None, width_avg, width_avg_err, "Widths", ".--", "black", 10, 5, 2)
close_plot(ax, "../Figs/w03_4mm_both_avg.jpg")


volume_diameter = volume_to_diameter(volume_avg)   

    # linear fit
params_l, sigmas_l, chi_l, fit_l = fit_model(volume_diameter, None, length_avg, length_avg_err, fitfunc_linear, [1,0], ROI=(volume_avg<12), ROF=[1.3, 2.5], info=True )
params_w, sigmas_w, chi_w, fit_w = fit_model(volume_diameter, None, width_avg, width_avg_err, fitfunc_linear, [1,0], ROI=(volume_avg<12), ROF=[1.3, 2.5], info=True )

    # both_avg vs volume diameter (fit)
ax = init_plot()
draw_grid()
add_second_axis(ax, diameter_to_volume, volume_to_diameter, r"Volume V / $\mu$l")
draw_text(ax, r"Volume Diameter $(\frac{12 V}{\pi^2})^{1/3}$ / mm", r"Contact Length or Width / mm")
draw_data(ax, volume_diameter, None, length_avg, length_avg_err, "Lengths", ".-", "black", 10, 5, 2)
draw_data(ax, volume_diameter, None, width_avg, width_avg_err, "Widths", ".--", "black", 10, 5, 2)
draw_data(ax, *fit_l, f"Length Fit $(\\chi^2 = {chi_l:.4f})$", "-", orange, 0, 0, 4, alpha=0.5)
draw_data(ax, *fit_w, f"Width Fit $(\\chi^2 = {chi_w:.4f}$)", "-", teal, 0, 0, 4, alpha=0.5)
close_plot(ax, "../Figs/w03_4mm_both_fit.jpg")

