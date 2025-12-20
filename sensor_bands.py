"""
Sensor band definitions for spectral resampling
Based on hsdar R package sensor definitions
"""

SENSOR_BANDS = {
    'Sentinel2a': {
        'wavelengths': [443.9, 496.6, 560.0, 664.5, 703.9, 740.2, 782.5, 835.1, 864.8, 945.0, 1373.5, 1613.7, 2202.4],
        'fwhm': [27, 66, 36, 31, 15, 15, 20, 106, 21, 20, 31, 91, 175]
    },
    'Sentinel2b': {
        'wavelengths': [443.9, 496.6, 560.0, 664.5, 703.9, 740.2, 782.5, 835.1, 864.8, 945.0, 1373.5, 1613.7, 2202.4],
        'fwhm': [27, 66, 36, 31, 15, 15, 20, 106, 21, 20, 31, 91, 175]
    },
    'Landsat8': {
        'wavelengths': [443.0, 482.0, 562.0, 655.0, 865.0, 1609.0, 2201.0],
        'fwhm': [20, 60, 57, 44, 28, 85, 187]
    },
    'Landsat7': {
        'wavelengths': [485.0, 560.0, 660.0, 835.0, 1650.0, 2215.0],
        'fwhm': [70, 80, 60, 140, 200, 270]
    },
    'Landsat5': {
        'wavelengths': [485.0, 560.0, 660.0, 835.0, 1650.0, 2215.0],
        'fwhm': [70, 80, 60, 140, 200, 270]
    },
    'Landsat4': {
        'wavelengths': [485.0, 560.0, 660.0, 835.0, 1650.0, 2215.0],
        'fwhm': [70, 80, 60, 140, 200, 270]
    },
    'Quickbird': {
        'wavelengths': [485.0, 560.0, 660.0, 830.0],
        'fwhm': [65, 80, 60, 90]
    },
    'RapidEye': {
        'wavelengths': [475.0, 555.0, 657.5, 710.0, 805.0],
        'fwhm': [32.5, 52.5, 47.5, 52.5, 47.5]
    },
    'WorldView2-4': {
        'wavelengths': [425.0, 480.0, 545.0, 605.0],
        'fwhm': [40, 60, 70, 50]
    },
    'WorldView2-8': {
        'wavelengths': [425.0, 480.0, 545.0, 605.0, 660.0, 725.0, 833.0, 950.0],
        'fwhm': [40, 60, 70, 50, 50, 40, 106, 30]
    }
}

def resample_spectrum(wavelengths, reflectance, target_wavelengths, fwhm=None):
    """
    Resample spectrum to sensor bands using Gaussian response function
    
    Parameters:
    -----------
    wavelengths : array-like
        Original wavelengths (nm)
    reflectance : array-like
        Original reflectance values
    target_wavelengths : array-like
        Target sensor wavelengths (nm)
    fwhm : array-like, optional
        Full width at half maximum for each band (nm)
    
    Returns:
    --------
    resampled : array
        Resampled reflectance values
    """
    import numpy as np
    from scipy.interpolate import interp1d
    
    # Interpolate original spectrum to 1nm resolution
    wl_full = np.arange(400, 2501, 1)
    f = interp1d(wavelengths, reflectance, kind='linear', 
                 bounds_error=False, fill_value=0.0)
    rho_interp = f(wl_full)
    
    resampled = []
    for i, target_wl in enumerate(target_wavelengths):
        if fwhm is not None and i < len(fwhm):
            sigma = fwhm[i] / (2 * np.sqrt(2 * np.log(2)))  # Convert FWHM to sigma
        else:
            sigma = 10.0  # Default sigma if FWHM not provided
        
        # Gaussian response function
        weights = np.exp(-0.5 * ((wl_full - target_wl) / sigma) ** 2)
        weights = weights / np.sum(weights)  # Normalize
        
        # Weighted average
        band_reflectance = np.sum(rho_interp * weights)
        resampled.append(band_reflectance)
    
    return np.array(resampled)

