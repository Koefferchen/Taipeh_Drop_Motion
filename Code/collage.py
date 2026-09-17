from MyPyLib_v6 import *


def exp_collage( folder, volumes, diameter, iterations, perspective):

    N_row, N_col    = len(volumes), iterations 
    image_matrix = np.full( (N_col,N_row), "",dtype=object )
    x_labels = range(iterations)
    y_labels = []

    for row, vol in enumerate(volumes):
        y_labels.append(f"{vol:d} ul")
        for col in range(N_col):
            image_matrix[col,row] = f"../Experiments/{folder}/{vol:02d}ul_{diameter:02d}mm_{perspective}-{col}.jpg"

    collage(f"../Collages/collage_{folder}_{perspective}", image_matrix, x_labels, y_labels, 3, 3)



exp_collage("PET_2-12ul_04mm", [2,4,6,8,10,12], 4, 5, "front")
exp_collage("PET_2-12ul_04mm", [2,4,6,8,10,12], 4, 5, "side")

exp_collage("PET_2-24ul_00mm", [2,4,6,8,12,16,20,24], 0, 5, "PET")
exp_collage("PMMA_2-24ul_00mm", [2,4,6,8,12,16,20,24], 0, 5, "PMMA")

exp_collage("PET_2-24ul_10mm", [2,4,8,12,16,20,24], 10, 5, "front")
exp_collage("PET_2-24ul_10mm", [2,4,8,12,16,20,24], 10, 5, "side")

exp_collage("PMMA_2-12ul_4mm", [2,4,6,8,10,12], 4, 5, "front")
exp_collage("PMMA_2-12ul_4mm", [2,4,6,8,10,12], 4, 5, "side")

exp_collage("PMMA_2-30ul_10mm", [2,4,8,12,16,20], 10, 5, "front")
exp_collage("PMMA_2-30ul_10mm", [2,4,8,12,16,20], 10, 5, "side")

