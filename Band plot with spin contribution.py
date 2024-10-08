# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 20:37:13 2023

@author: rijan
"""


import matplotlib as mpl
# mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import re

def parse_filband(feig, npl=10):
    # feig : filband in bands.x input file
    # npl : number per line, 10 for bands.x, 6 for phonon

    f=open(feig,'r')
    lines = f.readlines()

    header = lines[0].strip()
    line = header.strip('\n')
    shape = re.split('[,=/]', line)
    nbnd = int(shape[1])
    nks = int(shape[3])
    eig = np.zeros((nks, nbnd+1), dtype=np.float32)

    dividend = nbnd
    divisor = npl
    div = nbnd // npl + 1 if nbnd % npl == 0 else nbnd // npl + 2 
    kinfo=[]
    for index, value in enumerate(lines[1:]):
        value = value.strip(' \n')
        quotient = index // div
        remainder = index % div

        if remainder == 0:
            kinfo.append(value)
        else:
            value = re.split('[ ]+', value)
            a = (remainder - 1) * npl
            b = a + len(value)
            eig[quotient][a:b] = value

    f.close()

    return eig, nbnd, nks, kinfo



do_find_gap=True
e_ref=0.0 # set to fermi-level in scf output for metal, only applicable for do_find_gap=False
if do_find_gap:
    nvband=78 # valence band number, only applicable for do_find_gap=True
else:
    nvband=0

ymin=-1 # y range in plot
ymax=1.5
lw=1 # line width

p1=plt.subplot(1, 1, 1)

F=plt.gcf()
#F.set_size_inches([5,5])

eig, nbnd, nks, kinfo = parse_filband('Bandx.dat')
eig_s, nbnd_s, nks_s, kinfo_s = parse_filband('Bandx.dat.3')

if nbnd <= nvband:
    print("warning: nvband should be less than the calculated band.")

plt.xlim([0,nks-1]) # k-points
plt.ylim([ymin,ymax])
#plt.xlabel(r'$k (\AA^{-1})$',fontsize=16)
plt.ylabel(r' $\mathit{E}$ - $\mathit{E}$$_{VBM}$ ',fontsize=25)

if do_find_gap and nbnd > nvband: # for insulators only, nvband can be found by gappw.sh(https://github.com/yyyu200/gappw)
    eig_vbm=max(eig[:,nvband-1])
    eig_cbm=min(eig[:,nvband])
    Gap=eig_cbm-eig_vbm
    # plt.title("Band gap= %.4f eV" % (Gap))  
    # plt.title("z-component")
    e_ref=eig_vbm 

x_val=np.arange(0,nks)
for i in range(nbnd):
    plt.plot( eig[:,i]-e_ref,color='r',linewidth=0.2 ) 
    plt.scatter(x_val,eig[:,i]-e_ref,c=eig_s[:,i]*(-1),marker='.',s=200,  cmap='seismic',alpha=0.9,linewidth=0.1, vmin=-0.5, vmax=0.5)
    

vlines= [0,80,110,191] # positions of vertical lines, or specified by [0, 20, 40, ...]
for vline in vlines:
    plt.axvline(x=vline, ymin=ymin, ymax=ymax,linewidth=lw,color='black')

xlabeltext=[r'K', '$\Gamma$', 'M', 'K\u2032']
if len(xlabeltext)<len(vlines):
    for i in range(len(vlines)-len(xlabeltext)):
        xlabeltext.append('X')
elif len(xlabeltext)>len(vlines):
    xlabeltext=xlabeltext[0:len(vlines)]

assert len(xlabeltext)==len(vlines)

plt.xticks( vlines, xlabeltext, fontsize=25)
plt.yticks(fontsize=20)

# plt.text(4, 8, '9R WTe$_{2}$', fontsize=12, color='black', bbox=dict(facecolor='white',alpha=0.99,edgecolor='black') )
plt.tight_layout()
cbar=plt.colorbar()
cbar.ax.tick_params(colors='black', labelsize=20)
plt.savefig('3r_Z_comp.png',dpi=600, bbox_inches='tight')
plt.show()


