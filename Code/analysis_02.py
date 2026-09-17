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


# --------- data import ---------


dataset_01 = np.genfromtxt("../Data/week2_PMMA_2-3ul_2-4mm.CSV", delimiter=";", skip_header=2)

volume          = dataset_01[:,2]   # in ul
volume_err      = 0.01 * volume
diameter        = dataset_01[:,3]   # in mm
diameter_err    = dataset_01[:,4]
length          = dataset_01[:,5]   # in pixel
length_err      = 0.03 * length
x_width         = dataset_01[:,6]   # in pixel
x_width_err     = 0.03 * x_width
gauge           = dataset_01[:,8]   # in pixel 
gauge_err       = 0.03 * gauge

    # measured beta (not necessary)
beta_width_meas         = degree_to_rad(dataset_01[:,7])     
beta_width_meas_err     = np.full(len(beta_width_meas), degree_to_rad(5))



# --------- calculate contact width ---------


    # length conversion
length, length_err      = pixel_to_length(length, length_err, gauge, gauge_err)
x_width, x_width_err    = pixel_to_length(x_width, x_width_err, gauge, gauge_err)

    # width calculation
width, width_err        = W(x_width, x_width_err, diameter, diameter_err)


# --------- average over measurements ---------


length_2ul_2mm, length_2ul_2mm_err = filter_average(length, length_err, 2, 2.19)
length_2ul_4mm, length_2ul_4mm_err = filter_average(length, length_err, 2, 3.99)
length_3ul_2mm, length_3ul_2mm_err = filter_average(length, length_err, 3, 2.19)
length_3ul_4mm, length_3ul_4mm_err = filter_average(length, length_err, 3, 3.99)

width_2ul_2mm, width_2ul_2mm_err = filter_average(width, width_err, 2, 2.19)
width_2ul_4mm, width_2ul_4mm_err = filter_average(width, width_err, 2, 3.99)
width_3ul_2mm, width_3ul_2mm_err = filter_average(width, width_err, 3, 2.19)
width_3ul_4mm, width_3ul_4mm_err = filter_average(width, width_err, 3, 3.99)


load_plotting()
ax = init_plot()
draw_grid()
draw_text(ax, r"Drop Volume $V$ / $\mu$l", r"Contact Length / mm")
draw_data(ax, 
          [2,3], None,
          [length_2ul_2mm, length_3ul_2mm], [length_2ul_2mm_err, length_3ul_2mm_err],
          r"L $(2 mm)$", "^", "blue", 10, 5)
draw_data(ax, 
          [2,3], None,
          [length_2ul_4mm, length_3ul_4mm], [length_2ul_4mm_err, length_3ul_4mm_err],
          r"L $(4 mm)$", "^", "violet", 10, 5)
draw_data(ax, 
          [2,3], None,
          [width_2ul_2mm, width_3ul_2mm], [width_2ul_2mm_err, width_3ul_2mm_err],
          r"W $(2 mm)$", "D", "blue", 10, 5)
draw_data(ax, 
          [2,3], None,
          [width_2ul_4mm, width_3ul_4mm], [width_2ul_4mm_err, width_3ul_4mm_err],
          r"W $(4 mm)$", "D", "violet", 10, 5)
close_plot(ax, "../Figs/w02_2-4mm.jpg")
