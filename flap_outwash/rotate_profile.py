import numpy as np 
import matplotlib.pyplot as plt 
import numpy.polynomial.polynomial as Polynomial 
from tkinter import Tk
from tkinter.filedialog import askopenfilename
# plt.style.use('fivethirtyeight')  # Commentato per avere sfondo bianco

def find_rot_location(rot_location,x_camber): 
    x = x_camber
    cord = x.max() - x.min() #find the length of the profile
    x_loc = x.min()+rot_location*cord
    index_loc = np.argmin(np.abs(x-x_loc))
    return index_loc,x_loc

def camber_line(data):

    #find the lenght of the .dat 
    Np = data.shape[0]

    # find the middle point
    mp = int(Np/2)

    #find the coordinates
    x_upper = data[0:mp+1,0]
    x_lower = data[mp:,0]
    # y_upper = data[0:mp+1,1]
    # y_lower = data[mp:,1]
    y_upper = data[0:mp+1,1]
    y_lower = data[mp:,1]

    # Allinea le lunghezze
    min_len = min(len(y_upper), len(y_lower))
    y_upper = y_upper[:min_len]
    y_lower = y_lower[:min_len]

    x_upper = data[0:mp+1,0][:min_len] 

    #min_len = min(len(x_upper), len(x_lower))
    x_camber = x_upper  # si assume che upper e lower abbiano stessi x
    y_camber = (y_upper + np.flip(y_lower)) / 2
    t = np.abs(y_upper - np.flip(y_lower))
    
    # Plot rimossi
    return x_camber, y_camber,t

def rotation(polygrade,rot_location,x_camber,y_camber):

    idx,x_rot = find_rot_location(rot_location,x_camber)

    # now I need to build the curve that interpolates the point from the first to x_rot

    # idx_lex = np.argmin(np.abs(x_camber-0))
    # idx_ley = np.argmin(np.abs(y_camber-0))

    x_sub = x_camber[-(idx+1):]
    y_sub = y_camber[-(idx+1):]

    if len(x_sub) < polygrade + 1:
        raise ValueError("Troppi pochi punto per il polinomio")

    a = np.polyfit(x_sub,y_sub,polygrade)
    p = np.poly1d(a) # this function generate a polynom that is zero in every point of a

    dp = p.deriv()
    dy_dx = dp(x_rot)
    theta = np.arctan(dy_dx)
    norm_x = -dy_dx / np.sqrt(1 + dy_dx**2)
    norm_y = 1 / np.sqrt(1 + dy_dx**2)

    cos_theta = np.cos(-theta)
    sin_theta = np.sin(-theta)

    R = np.array([[cos_theta,-sin_theta],[sin_theta,cos_theta]])

    pivot = np.array([x_camber[idx],y_camber[idx]])

    dat = np.column_stack((x_camber,y_camber))

    rotated = (dat-pivot)@R.T +pivot

    x_upper = rotated[:,0] + norm_x * t / 2
    y_upper = rotated[:,1] + norm_y * t / 2

    x_lower = rotated[:,0]- norm_x * t / 2
    y_lower = rotated[:,1] - norm_y * t / 2   

    return rotated, theta, pivot, p, x_rot,x_upper,x_lower,y_upper,y_lower

## -----------------------------------------------------------------------------------------

#file_path = "/Users/danielegalluzzo/progettoAerodinamico/OUTWASH/profili/s1210.dat" 

Tk().withdraw()  # Nasconde la finestra principale
file_path = askopenfilename(title="Seleziona il file .dat", filetypes=[("DAT files", "*.dat")])

if not file_path:
    raise FileNotFoundError("Nessun file selezionato")

data = np.loadtxt(file_path)

x_c,y_c,t = camber_line(data)

rot_location = 0.25

rotated_data, theta, pivot, p, x_rot,x_up,x_lo,y_up,y_lo = rotation(3,rot_location,x_c,y_c)

print(f"Rotation Angle: {-np.degrees(theta):.2f}°")
print(f"Pivot Point): {pivot}")



# === Nuovo Plot di Confronto ===
plt.figure(figsize=(12, 5))

# Subplot 1: Profilo originale
plt.subplot(1, 2, 1)
plt.plot(data[:, 0], data[:, 1], 'b-', linewidth=2, label='Profilo Originale')
plt.plot(x_c, y_c, 'k--', linewidth=1.5, alpha=0.8, label='Linea media')
plt.scatter(*pivot, color='red', s=50, marker='o', label=f'Pivot ({rot_location}% corda)')
plt.axis('equal')
plt.grid(True, alpha=0.3)
plt.legend()
plt.xlabel('x')
plt.ylabel('y')
plt.title('Profilo Originale')

# Subplot 2: Profilo ruotato
plt.subplot(1, 2, 2)
# Plottiamo il profilo ruotato completo usando le superfici superiore e inferiore come un unico profilo
plt.plot(x_up, y_up, 'r-', linewidth=2)
plt.plot(x_lo, y_lo, 'r-', linewidth=2, label='Profilo Ruotato')
plt.plot(rotated_data[:, 0], rotated_data[:, 1], 'k--', linewidth=1.5, alpha=0.8, label='Linea media ruotata')
plt.scatter(*pivot, color='red', s=50, marker='o', label=f'Pivot ({rot_location}% corda)')
# Linea tangente al profilo ruotato nel punto pivot
# Dopo la rotazione, la tangente è orizzontale (pendenza = 0)
x_tang_range_rot = np.linspace(min(x_lo.min(), x_up.min()), max(x_lo.max(), x_up.max()), 100)
y_tang_rot = np.full_like(x_tang_range_rot, pivot[1])  # Linea orizzontale
plt.plot(x_tang_range_rot, y_tang_rot, 'r--', linewidth=1.5, alpha=0.7, label='Linea tangente (orizzontale)')
plt.axis('equal')
plt.grid(True, alpha=0.3)
plt.legend()
plt.xlabel('x')
plt.ylabel('y')
plt.title('Profilo Ruotato')

plt.tight_layout()
plt.show()

