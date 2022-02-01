import numpy as np
import pandas as pd
import os
import sys

os.system('cls' if os.name == 'nt' else 'clear')

df = pd.read_csv (r'C:\Users\17577\Thesis_Work\Pressure_Polynomial.csv', delimiter=',')

def Reverse(lst):
    new_lst = lst[::-1]
    return new_lst

def nonlinear_function(coeff_list):
    poly = np.poly1d(coeff_list)
    return poly


def Dnonlinear_function(coeff_arr):
    poly_arr = Reverse(coeff_arr)
    deriv_coeff = [poly_arr[i] * i for i in range(1, len(poly_arr))]
    correct_coeff = Reverse(deriv_coeff)
    deriv_poly = nonlinear_function(correct_coeff)
    return deriv_poly

def newton(f, fprime, x0, epsilon = 1.0e-9, LOUD=False):
    """Find the root of the function f via Newton-Raphson method
    Args:
        f: function to find root of
        fprime: derivative of f
        x0: initial guess
        epsilon: tolerance
    Returns:
        estimate of root
    """
    x = x0
    #if (LOUD):
        #print("x0 =", x0)
    iterations = 0
    fx = f(x)
    while (np.fabs(fx) > epsilon):
        fprimex = fprime(x)
        #if (LOUD):
            #print("x_", iterations+1, "=", x, "-", fx,
            #"/",fprimex,"=",x - fx/fprimex)
        x = x - fx/fprimex
        iterations += 1
        fx = f(x)

    #print("It took", iterations, "iterations")
    return x #return estimate of root
time_array = np.linspace(0, df.shape[0]*0.5, num=df.shape[0])
number_rows = df.shape[0]
number_columns = df.shape[1]
mass_flow_rate = []
print(df)
for row in range(0, number_rows):
    coeff_arr = []
    for column in range(0, number_columns-2):
        coeff_arr.append(df.iloc[row][column])
    polynomial = nonlinear_function(coeff_arr)
    #print(polynomial)
    derivative = Dnonlinear_function(coeff_arr)
    root = newton(polynomial, derivative, df.iloc[row][-2], LOUD= True)
    mass_flow_rate.append(root * df.iloc[row][-1])

MFR_dict = {'Time': time_array, 'mfr': mass_flow_rate}
MFR_df = pd.DataFrame(MFR_dict)
MFR_df.to_csv(r'C:\Users\17577\Thesis_Work\MFR_Time_Step.csv', index = False)