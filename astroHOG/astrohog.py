# This file is part of AstroHOG
#
# Copyright (C) 2013-2017 Juan Diego Soler

import numpy as np
from astropy.convolution import convolve_fft
from astropy.convolution import Gaussian2DKernel
from .congrid import *

# ------------------------------------------------------------------------------------------------------------------------
def HOG_PRS(phi):
   # Calculates the projected Rayleigh statistic of the distributions of angles phi.
   #
   # INPUTS
   # phi      - angles between -pi/2 and pi/2
   #
   # OUTPUTS
   # Zx       - value of the projected Rayleigh statistic   
   # s_Zx     - 
   # meanPhi  -
 
   angles=2.*phi

   Zx=np.sum(np.cos(angles))/np.sqrt(np.size(angles)/2.)	
   temp=np.sum(np.cos(angles)*np.cos(angles))
   s_Zx=np.sqrt((2.*temp-Zx*Zx)/np.size(angles))
   
   Zy=np.sum(np.sin(angles))/np.sqrt(np.size(angles)/2.)
   temp=np.sum(np.sin(angles)*np.sin(angles))
   s_Zx=np.sqrt((2.*temp-Zy*Zy)/np.size(angles))

   meanPhi=0.5*np.arctan2(Zy, Zx)

   return Zx, s_Zx, meanPhi  

# -------------------------------------------------------------------------------------------------------------------------------
def HOGvotes_simple(phi):
    # Calculates the correlation   
    #
    # INPUTS
    #
    # OUTPUTS
    #
    #

    sz=np.shape(phi)
    corrframe=np.zeros(sz)	
    #paraThres=20.*np.pi/180.
    #condPara=np.logical_and(np.isfinite(phi), np.logical_or(phi < paraThres, phi > np.pi-paraThres)).nonzero() 
    #corrframe[condPara]=1.
    corrframe=np.cos(phi)	 	
    corrframe[np.isnan(phi).nonzero()]=0. #np.nan
    #import pdb; pdb.set_trace() 
    Zx, s_Zx, meanPhi = HOG_PRS(phi[np.isfinite(phi).nonzero()])	

    return Zx, corrframe

# -------------------------------------------------------------------------------------------------------------------------------
def HOGvotes_blocks(phi, wd=3):
    # Calculates the correlation   
    #
    # INPUTS
    #
    # OUTPUTS
    #
    #

   sz=np.shape(phi)
   corrframe=np.zeros(sz)

   for i in range(0, sz[0]):
      for k in range(0, sz[1]):
         if (i<wd):
            if (k<wd):
               temp=phi[0:i+wd,0:k+wd]; corrframe[i,k]=np.mean(temp[np.isfinite(temp).nonzero()])
            elif (k>sz[1]-1-wd):
               temp=phi[0:i+wd,k-wd:sz[1]-1]; corrframe[i,k]=np.mean(temp[np.isfinite(temp).nonzero()])
            else:
               temp=phi[0:i+wd,k-wd:k+wd]; corrframe[i,k]=np.mean(temp[np.isfinite(temp).nonzero()])
         elif (i>sz[0]-1-wd):
            if (k<wd):
               temp=phi[i-wd:sz[1]-1,0:k+wd]; corrframe[i,k]=np.mean(temp[np.isfinite(temp).nonzero()])
            elif (k>sz[1]-1-wd):
               temp=phi[i-wd:sz[0]-1,k-wd:sz[1]-1]; corrframe[i,k]=np.mean(temp[np.isfinite(temp).nonzero()])
            else:
               temp=phi[i-wd:sz[0]-1,k-wd:k+wd]; corrframe[i,k]=np.mean(temp[np.isfinite(temp).nonzero()])
         elif (k<wd):
            if (i<wd):
               temp=phi[0:i+wd,0:k+wd]; corrframe[i,k]=np.mean(temp[np.isfinite(temp).nonzero()])
            elif (i>sz[0]-1-wd):
               temp=phi[i-wd:sz[0]-1,0:k+wd]; corrframe[i,k]=np.mean(temp[np.isfinite(temp).nonzero()])
            else:
               temp=phi[i-wd:i+wd,0:k+wd]; corrframe[i,k]=np.mean(temp[np.isfinite(temp).nonzero()])	
         elif (k>sz[1]-1-wd):
            if (i<wd):
               temp=phi[0:i+wd,k-wd:sz[1]-1]; corrframe[i,k]=np.mean(temp[np.isfinite(temp).nonzero()])
            elif (i>sz[0]-1-wd):
               temp=phi[i-wd:sz[0]-1,k-wd:sz[1]-1]; corrframe[i,k]=np.mean(temp[np.isfinite(temp).nonzero()])
            else:
               temp=phi[i-wd:i+wd,k-wd:sz[1]-1]; corrframe[i,k]=np.mean(temp[np.isfinite(temp).nonzero()])
         else:
            temp=phi[i-wd:i+wd,k-wd:k+wd]; corrframe[i,k]=np.mean(temp[np.isfinite(temp).nonzero()])
	
   corrframe[np.isnan(phi).nonzero()]=0.

   nPara=np.size(corrframe[(corrframe>0.).nonzero()])
   nGood=np.size(phi[np.isfinite(phi).nonzero()])

   hogcorr=nPara/float(nGood)

   return hogcorr, corrframe


# -------------------------------------------------------------------------------------------------------------------------------
def HOGcorr_frame(frame1, frame2, gradthres=0., pxsz=1., ksz=1., res=1., mask1=0, mask2=0, wd=1, allow_huge=False, regrid=False):

   # Calculates the spatial correlation between frame1 and frame2 using the HOG methods
   #
   # INPUTS
   # frame1 -
   # frame2 -
   #
   # OUTPUTS
   # hogcorr -   
   # corrframe -

   sf=3. #Number of pixels per kernel FWHM	
     
   pxksz =ksz/pxsz 
   pxres =res/pxsz

   sz1=np.shape(frame1)  	

   if (ksz > 1): 
      if (regrid):
         intframe1=congrid(frame1, [np.int(np.round(sf*sz1[0]/pxres)), np.int(np.round(sf*sz1[1]/pxres))])
         intframe2=congrid(frame2, [np.int(np.round(sf*sz1[0]/pxres)), np.int(np.round(sf*sz1[1]/pxres))])
         if np.array_equal(np.shape(frame1), np.shape(mask1)): 
            intmask1=congrid(mask1, [np.int(np.round(sf*sz1[0]/pxres)), np.int(np.round(sf*sz1[1]/pxres))])
            if np.array_equal(np.shape(frame2), np.shape(mask2)):
               intmask2=congrid(mask2, [np.int(np.round(sf*sz1[0]/pxres)), np.int(np.round(sf*sz1[1]/pxres))])
      else:		
         intframe1=frame1
         intframe2=frame2     
         intmask1=mask1
         intmask2=mask2
      grad1=np.gradient(convolve_fft(intframe1, Gaussian2DKernel(pxksz), allow_huge=allow_huge))
      grad2=np.gradient(convolve_fft(intframe2, Gaussian2DKernel(pxksz), allow_huge=allow_huge))	
   else:
      grad1=np.gradient(intframe1)
      grad2=np.gradient(intframe2)
   
   # Calculation of the relative orientation angles
   tempphi=np.arctan2(grad1[0]*grad2[1]-grad1[1]*grad2[0], grad1[0]*grad2[0]+grad1[1]*grad2[1]) 
   phi=np.arctan(np.tan(tempphi))

   # Excluding small gradients
   normGrad1=np.sqrt(grad1[1]**2+grad1[0]**2)
   normGrad2=np.sqrt(grad2[1]**2+grad2[0]**2)
   bad=np.logical_or(normGrad1 <= gradthres, normGrad2 <= gradthres).nonzero()
   phi[bad]=np.nan
 
   # Excluding masked regions	
   if (np.shape(np.shape(intmask1))[0]==2):
      phi[(intmask1==0).nonzero()]=np.nan
      if (np.shape(np.shape(intmask2))[0]==2):		
         phi[(intmask2==0).nonzero()]=np.nan

   # Evaluating the HOG correlation
   if (wd > 1):
      hogcorr, corrframe =HOGvotes_blocks(phi, mask=mask1, wd=wd)
   else:
      hogcorr, corrframe =HOGvotes_simple(phi)

   return hogcorr, corrframe


# -------------------------------------------------------------------------------------------------------------------------------
def HOGcorr_frameandvec(frame1, vecx, vecy, gradthres=0., vecthres=0., ksz=1, mask1=0, mask2=0, wd=1):
   # Calculates the correlation   
   #
   # INPUTS
   #
   # OUTPUTS
   #
   #

   sz1=np.shape(frame1)

   if (ksz > 1):
      grad1=np.gradient(convolve_fft(frame1, Gaussian2DKernel(ksz)))
   else:
      grad1=np.gradient(frame1)

   normGrad1=np.sqrt(grad1[1]**2+grad1[0]**2)
   normVec=np.sqrt(vecx*vecx+vecy*vecy)
   bad=np.logical_or(normGrad1 <= gradthres, normVec <= vecthres).nonzero()

   normGrad1[bad]=1.; normVec[bad]=1.;
   #cosphi=(grad1[1]*vecx+grad1[0]*vecy)/(normGrad1*normVec)
   phi=np.arctan2(grad1[1]*vecy-grad1[0]*vecx, grad1[1]*vecx+grad1[0]*vecy)
   phi[bad]=np.nan
	
   if np.array_equal(np.shape(frame1), np.shape(mask1)):
      if np.array_equal(np.shape(normVec), np.shape(mask2)):
         phi[np.logical_or(mask1==0, mask2==0).nonzero()]=np.nan
	 good=np.logical_and(mask1 > 0., mask2 > 0.).nonzero()
      else:
         phi[(mask1==0).nonzero()]=np.nan
         good=(mask1 > 0.).nonzero()
   else:
      good=np.isfinite(phi).nonzero()

   if (wd > 1):
      hogcorr, corrframe =HOGvotes_blocks(phi, wd=wd)
   else:
      hogcorr, corrframe =HOGvotes_simple(phi)
	
   #plt.imshow(phi, origin='lower')
   #plt.show()
   #import pdb; pdb.set_trace() 
   return hogcorr, corrframe


# ================================================================================================================
def HOGcorr_cube(cube1, cube2, z1min, z1max, z2min, z2max, pxsz=1., ksz=1., res=1., mask1=0, mask2=0, wd=1, regrid=False):
   # Calculates the correlation   
   #
   # INPUTS
   #
   # OUTPUTS
   #
   #

   sf=3. #Number of pixels per kernel FWHM      
   pxksz =ksz/pxsz
   pxres =res/pxsz
   sz1=np.shape(cube1)
   sz2=np.shape(cube2)

   corrplane=np.zeros([z1max+1-z1min, z2max+1-z2min])
   corrcube=np.zeros([sz1[0], np.int(np.round(sf*sz1[1]/pxres)), np.int(np.round(sf*sz1[2]/pxres))])       #np.zeros(sz1)
   corrframe_temp=np.zeros([np.int(np.round(sf*sz1[1]/pxres)), np.int(np.round(sf*sz1[2]/pxres))]) #np.zeros([sz1[1],sz1[2]])

   for i in range(z1min, z1max+1):
      corrframe_temp*=0.
      for k in range(z2min, z2max+1):
         frame1=cube1[i,:,:]
         frame2=cube2[k,:,:]
         if np.array_equal(np.shape(cube1), np.shape(mask1)):
            if np.array_equal(np.shape(cube2), np.shape(mask2)):				
               corr, corrframe=HOGcorr_frame(frame1, frame2, pxsz=pxsz, ksz=ksz, res=res, mask1=mask1[i,:,:], mask2=mask2[k,:,:], wd=wd, regrid=regrid)
            else:
               corr, corrframe=HOGcorr_frame(frame1, frame2, pxsz=pxsz, ksz=ksz, res=res, mask1=mask1[i,:,:], wd=wd, regrid=regrid)
         else:
            corr, corrframe=HOGcorr_frame(frame1, frame2, ksz=ksz, wd=wd)
         corrplane[i-z1min,k-z2min]=corr
         corrframe_temp+=corrframe
      corrcube[i-z1min,:,:]=corrframe/float(z2max+1-z2min)
      #import pdb; pdb.set_trace() 	
   return corrplane, corrcube


# ================================================================================================================
def HOGcorr_cubeandpol(cube1, ex, ey, z1min, z1max, ksz=1, mask1=0, mask2=0, wd=1, rotatepol=False):
   # Calculates the correlation   
   #
   # INPUTS
   #
   # OUTPUTS
   #
   #

   sz1=np.shape(cube1)
   sz2=np.shape(ex)

   if(rotatepol):
      xvec= ey
      yvec=-ex
   else:	
      xvec= ex
      yvec= ey
   normVec=np.sqrt(xvec*xvec+yvec*yvec)

   corrvec=0.*np.arange(z1min,z1max+1)
   corrframe=np.zeros([sz1[1],sz1[2]])	
   corrcube=np.zeros(sz1)

   for i in range(z1min, z1max+1):
      if np.array_equal(np.shape(cube1), np.shape(mask1)):
         if np.array_equal(np.shape(normVec), np.shape(mask2)):                
            corr, corrframe=HOGcorr_frameandvec(cube1[i,:,:], xvec, yvec, ksz=ksz, mask1=mask1[i,:,:], mask2=mask2, wd=wd)
         else:
            corr, corrframe=HOGcorr_frameandvec(cube1[i,:,:], xvec, yvec, ksz=ksz, mask1=mask1[i,:,:], wd=wd)
      else:
         corr, corrframe=HOGcorr_frameandvec(cube1[i,:,:], xvec, yvec, ksz=ksz, wd=wd)
      corrvec[i-z1min]=corr
      #corrcube[i-z1min]=corrframe

   return corrvec , corrcube


