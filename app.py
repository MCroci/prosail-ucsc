"""
PROSAIL Model - Remote sensing for precision agriculture
Python version using Streamlit and prosail library
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from itertools import product
from scipy.interpolate import interp1d

# Import prosail library
try:
    import prosail
    HAS_PROSAIL = True
except ImportError:
    HAS_PROSAIL = False
    st.warning("⚠️ prosail library not installed. Please install it: `pip install prosail` or `conda install -c jgomezdans prosail`")

# Import sensor band definitions
try:
    from sensor_bands import SENSOR_BANDS, resample_spectrum
    HAS_SENSOR_BANDS = True
except ImportError:
    HAS_SENSOR_BANDS = False

# Page configuration
st.set_page_config(
    page_title="PROSAIL Model - Remote Sensing",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stSlider > div > div > div > div {
        background-color: #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">🌱 PROSAIL Model</div>', unsafe_allow_html=True)
st.markdown("### Remote sensing for precision agriculture")

# Sidebar for inputs
with st.sidebar:
    st.header("⚙️ Parameters")
    
    # Leaf parameters
    st.subheader("🍃 Leaf Parameters")
    N = st.slider(
        "Leaf Mesophyll index (N)",
        min_value=1.0,
        max_value=2.5,
        value=(1.2, 1.5),
        step=0.1,
        help="Leaf structure parameter"
    )
    
    Cm = st.slider(
        "Dry matter content (Cm, g cm⁻²)",
        min_value=0.0,
        max_value=0.02,
        value=(0.01, 0.012),
        step=0.001,
        help="Leaf dry matter content"
    )
    
    Cw = st.slider(
        "Equivalent water thickness (Cw, g cm⁻²)",
        min_value=0.0,
        max_value=0.05,
        value=(0.02, 0.03),
        step=0.01,
        help="Leaf equivalent water thickness"
    )
    
    Cab = st.slider(
        "Leaf Chlorophyll Content (Cab, µg cm⁻²)",
        min_value=0,
        max_value=90,
        value=(45, 60),
        step=5,
        help="Leaf chlorophyll a+b content"
    )
    
    # Canopy parameters
    st.subheader("🌳 Canopy Parameters")
    LAI = st.slider(
        "Leaf Area Index (LAI, m²/m²)",
        min_value=1.0,
        max_value=10.0,
        value=(1.0, 2.0),
        step=0.5,
        help="Leaf Area Index"
    )
    
    lidfa = st.slider(
        "Average Leaf Angle (ALA, degrees °)",
        min_value=0.0,
        max_value=90.0,
        value=(45.0, 67.0),
        step=0.5,
        help="Average leaf angle"
    )
    
    # Satellite sensor
    st.subheader("🛰️ Satellite")
    sensor = st.selectbox(
        "Choose a sensor:",
        ["Sentinel2a", "Sentinel2b", "Landsat4", "Landsat5", "Landsat7", 
         "Landsat8", "Quickbird", "RapidEye", "WorldView2-4", "WorldView2-8"],
        index=0,
        help="Satellite sensor for spectral resampling"
    )
    
    # Vegetation indices
    st.subheader("📊 Vegetation Indices")
    vis = st.selectbox(
        "Choose a VI:",
        ["NDVI", "NDRE", "GNDVI"],
        index=0,
        help="Vegetation index to plot"
    )

def create_param_range(min_val, max_val, step):
    """Create parameter range from slider values"""
    if min_val >= max_val:
        return [min_val]
    # Generate values between min and max with given step
    values = np.arange(min_val, max_val + step/2, step)
    return values.tolist()

@st.cache_data
def calculate_prospect(N_values, Cm_values, Cw_values, Cab_values):
    """Calculate PROSPECT leaf reflectance"""
    if not HAS_PROSAIL:
        return pd.DataFrame({'Wav': range(400, 2501), 'mean': [0]*2101, 'sd': [0]*2101})
    
    try:
        # Create parameter ranges from slider values
        if isinstance(N_values, (list, tuple)) and len(N_values) == 2:
            N_vals = create_param_range(N_values[0], N_values[1], 0.1)
        else:
            N_vals = [N_values] if not isinstance(N_values, list) else N_values
            
        if isinstance(Cm_values, (list, tuple)) and len(Cm_values) == 2:
            Cm_vals = create_param_range(Cm_values[0], Cm_values[1], 0.001)
        else:
            Cm_vals = [Cm_values] if not isinstance(Cm_values, list) else Cm_values
            
        if isinstance(Cw_values, (list, tuple)) and len(Cw_values) == 2:
            Cw_vals = create_param_range(Cw_values[0], Cw_values[1], 0.01)
        else:
            Cw_vals = [Cw_values] if not isinstance(Cw_values, list) else Cw_values
            
        if isinstance(Cab_values, (list, tuple)) and len(Cab_values) == 2:
            Cab_vals = create_param_range(Cab_values[0], Cab_values[1], 5.0)
        else:
            Cab_vals = [Cab_values] if not isinstance(Cab_values, list) else Cab_values
        
        # Create parameter grid
        params = list(product(N_vals, Cm_vals, Cw_vals, Cab_vals))
        
        # Calculate PROSPECT for each parameter combination
        spectra_list = []
        wavelengths = None
        for n, cm, cw, cab in params:
            # Note: prosail uses cw in cm (equivalent water thickness)
            # Original R code uses Cw in g/cm², conversion: cw_cm = Cw_g_cm2 / 1.0 (assuming density of 1 g/cm³)
            lam, rho, tau = prosail.run_prospect(
                n=n, 
                cab=cab, 
                car=0.0, 
                cbrown=0.0, 
                cw=cw,  # Already in cm equivalent (g/cm² ≈ cm for water)
                cm=cm*100,  # Convert g/cm² to g/m² (prosail expects g/m² for cm)
                ant=0.0, 
                prospect_version='D'
            )
            if wavelengths is None:
                wavelengths = lam
            spectra_list.append(rho)
        
        # Calculate mean and sd across parameter combinations
        spectra_matrix = np.array(spectra_list)
        reflectance_mean = np.mean(spectra_matrix, axis=0)
        reflectance_sd = np.std(spectra_matrix, axis=0)
        
        return pd.DataFrame({
            'Wav': wavelengths,
            'mean': np.round(reflectance_mean, 3),
            'sd': np.round(reflectance_sd, 3)
        })
    except Exception as e:
        st.error(f"Error calculating PROSPECT: {str(e)}")
        return pd.DataFrame({'Wav': range(400, 2501), 'mean': [0]*2101, 'sd': [0]*2101})

@st.cache_data
def calculate_prosail(N_values, Cm_values, Cw_values, Cab_values, LAI_values, lidfa_values, sensor_name):
    """Calculate PROSAIL canopy reflectance"""
    if not HAS_PROSAIL:
        return (
            pd.DataFrame({'Wav': range(400, 2501), 'mean': [0]*2101, 'sd': [0]*2101}),
            pd.DataFrame({'Wav': [], 'mean': [], 'sd': []}),
            pd.DataFrame()
        )
    
    try:
        # Create parameter ranges from slider values
        if isinstance(N_values, (list, tuple)) and len(N_values) == 2:
            N_vals = create_param_range(N_values[0], N_values[1], 0.1)
        else:
            N_vals = [N_values] if not isinstance(N_values, list) else N_values
            
        if isinstance(Cm_values, (list, tuple)) and len(Cm_values) == 2:
            Cm_vals = create_param_range(Cm_values[0], Cm_values[1], 0.001)
        else:
            Cm_vals = [Cm_values] if not isinstance(Cm_values, list) else Cm_values
            
        if isinstance(Cw_values, (list, tuple)) and len(Cw_values) == 2:
            Cw_vals = create_param_range(Cw_values[0], Cw_values[1], 0.01)
        else:
            Cw_vals = [Cw_values] if not isinstance(Cw_values, list) else Cw_values
            
        if isinstance(Cab_values, (list, tuple)) and len(Cab_values) == 2:
            Cab_vals = create_param_range(Cab_values[0], Cab_values[1], 5.0)
        else:
            Cab_vals = [Cab_values] if not isinstance(Cab_values, list) else Cab_values
            
        if isinstance(LAI_values, (list, tuple)) and len(LAI_values) == 2:
            LAI_vals = create_param_range(LAI_values[0], LAI_values[1], 0.5)
        else:
            LAI_vals = [LAI_values] if not isinstance(LAI_values, list) else LAI_values
            
        if isinstance(lidfa_values, (list, tuple)) and len(lidfa_values) == 2:
            lidfa_vals = create_param_range(lidfa_values[0], lidfa_values[1], 0.5)
        else:
            lidfa_vals = [lidfa_values] if not isinstance(lidfa_values, list) else lidfa_values
        
        # Create parameter grid
        params = list(product(N_vals, Cm_vals, Cw_vals, Cab_vals, LAI_vals, lidfa_vals))
        param_df = pd.DataFrame(params, columns=['N', 'Cm', 'Cw', 'Cab', 'LAI', 'lidfa'])
        
        # Calculate PROSAIL for each parameter combination
        spectra_list = []
        wavelengths = np.arange(400, 2501, 1)
        
        for n, cm, cw, cab, lai, lidfa in params:
            # prosail.run_prosail parameters
            rho_canopy = prosail.run_prosail(
                n=n,
                cab=cab,
                car=0.0,
                cbrown=0.0,
                cw=cw,  # Already in cm equivalent
                cm=cm*100,  # Convert g/cm² to g/m²
                lai=lai,
                lidfa=lidfa,
                hspot=0.01,  # Hotspot parameter
                tts=45.0,  # Solar zenith angle
                tto=0.0,  # Observer zenith angle (nadir)
                psi=0.0,  # Relative azimuth
                ant=0.0,
                alpha=40.0,
                prospect_version='D',
                typelidf=2,  # Ellipsoidal distribution
                lidfb=0.0,
                factor='SDR'  # Surface directional reflectance
            )
            spectra_list.append(rho_canopy)
        
        # Calculate mean and sd across parameter combinations
        spectra_matrix = np.array(spectra_list)
        reflectance_mean_full = np.mean(spectra_matrix, axis=0)
        reflectance_sd_full = np.std(spectra_matrix, axis=0)
        
        full_spectra_df = pd.DataFrame({
            'Wav': wavelengths,
            'mean': np.round(reflectance_mean_full, 3),
            'sd': np.round(reflectance_sd_full, 3)
        })
        
        # Spectral resampling for sensor
        sensor_spectra_list = []
        if HAS_SENSOR_BANDS and sensor_name in SENSOR_BANDS:
            sensor_info = SENSOR_BANDS[sensor_name]
            target_wls = sensor_info['wavelengths']
            fwhm = sensor_info.get('fwhm')
            
            for rho_full in spectra_list:
                rho_sensor = resample_spectrum(wavelengths, rho_full, target_wls, fwhm)
                sensor_spectra_list.append(rho_sensor)
            
            sensor_spectra_matrix = np.array(sensor_spectra_list)
            reflectance_mean_s2 = np.mean(sensor_spectra_matrix, axis=0)
            reflectance_sd_s2 = np.std(sensor_spectra_matrix, axis=0)
            
            sensor_spectra_df = pd.DataFrame({
                'Wav': target_wls,
                'mean': np.round(reflectance_mean_s2, 3),
                'sd': np.round(reflectance_sd_s2, 3)
            })
            
            # Create full dataset with bands
            full_dataset = param_df.copy()
            band_cols = [f'R{int(w)}' for w in target_wls]
            full_dataset[band_cols] = np.round(sensor_spectra_matrix, 4)
            full_dataset = full_dataset.rename(columns={'lidfa': 'ALA'})
            
            # Calculate vegetation indices (for Sentinel-2: B8 (833nm), B4 (665nm), B5 (704nm), B3 (560nm))
            if sensor_name.startswith('Sentinel') and len(target_wls) >= 9:
                # Sentinel-2 bands: B1(443), B2(496), B3(560), B4(665), B5(704), B6(740), B7(783), B8(835), B8a(865), B9(945), B11(1614), B12(2202)
                # Index: 0=B1, 1=B2, 2=B3, 3=B4, 4=B5, 7=B8
                full_dataset['NDVI'] = (full_dataset[band_cols[7]] - full_dataset[band_cols[3]]) / (full_dataset[band_cols[7]] + full_dataset[band_cols[3]] + 1e-10)
                full_dataset['NDRE'] = (full_dataset[band_cols[7]] - full_dataset[band_cols[4]]) / (full_dataset[band_cols[7]] + full_dataset[band_cols[4]] + 1e-10)
                full_dataset['GNDVI'] = (full_dataset[band_cols[7]] - full_dataset[band_cols[2]]) / (full_dataset[band_cols[7]] + full_dataset[band_cols[2]] + 1e-10)
            else:
                # Generic calculation if band structure unknown
                if len(band_cols) >= 4:
                    full_dataset['NDVI'] = 0.0
                    full_dataset['NDRE'] = 0.0
                    full_dataset['GNDVI'] = 0.0
        else:
            sensor_spectra_df = pd.DataFrame({'Wav': [], 'mean': [], 'sd': []})
            full_dataset = param_df.copy()
            full_dataset['NDVI'] = 0.0
            full_dataset['NDRE'] = 0.0
            full_dataset['GNDVI'] = 0.0
        
        return full_spectra_df, sensor_spectra_df, full_dataset
    except Exception as e:
        st.error(f"Error calculating PROSAIL: {str(e)}")
        return (
            pd.DataFrame({'Wav': range(400, 2501), 'mean': [0]*2101, 'sd': [0]*2101}),
            pd.DataFrame({'Wav': [], 'mean': [], 'sd': []}),
            pd.DataFrame()
        )

# Main content
if not HAS_PROSAIL:
    st.error("""
    ## ⚠️ Setup Required
    
    This app requires the `prosail` Python library.
    
    **Installation:**
    
    Option 1 - Using conda (recommended):
    ```bash
    conda install -c jgomezdans prosail
    ```
    
    Option 2 - Using pip:
    ```bash
    pip install prosail
    ```
    
    Then install other dependencies:
    ```bash
    pip install streamlit pandas numpy plotly
    ```
    
    For more information, visit: https://github.com/jgomezdans/prosail
    """)
    st.stop()

# Calculate spectra
with st.spinner("Calculating PROSPECT leaf reflectance..."):
    prospect_df = calculate_prospect(N, Cm, Cw, Cab)

with st.spinner("Calculating PROSAIL canopy reflectance..."):
    prosail_full, prosail_sensor, prosail_dataset = calculate_prosail(N, Cm, Cw, Cab, LAI, lidfa, sensor)

# Plot 1: Leaf reflectance - PROSPECT
st.markdown("### 🍃 Leaf Reflectance - PROSPECT")
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=prospect_df['Wav'],
    y=prospect_df['mean'],
    mode='lines',
    name='Mean Reflectance',
    line=dict(color='darkgreen', width=2, dash='dash')
))
fig1.add_trace(go.Scatter(
    x=prospect_df['Wav'],
    y=prospect_df['mean'] - prospect_df['sd'],
    mode='lines',
    name='Lower bound',
    line=dict(width=0),
    showlegend=False
))
fig1.add_trace(go.Scatter(
    x=prospect_df['Wav'],
    y=prospect_df['mean'] + prospect_df['sd'],
    mode='lines',
    name='Upper bound',
    line=dict(width=0),
    fillcolor='rgba(0, 128, 0, 0.3)',
    fill='tonexty',
    showlegend=False
))
fig1.update_layout(
    xaxis_title="Wavelength (nm)",
    yaxis_title="Reflectance (-)",
    xaxis_range=[400, 2500],
    yaxis_range=[0, 1],
    template="plotly_white",
    height=400
)
st.plotly_chart(fig1, use_container_width=True)

# Plot 2: Canopy reflectance - SAIL
st.markdown("### 🌳 Canopy Reflectance - SAIL")
fig2 = go.Figure()
# Full spectrum line
fig2.add_trace(go.Scatter(
    x=prosail_full['Wav'],
    y=prosail_full['mean'],
    mode='lines',
    name='Canopy Reflectance',
    line=dict(color='darkred', width=2, dash='dash')
))
# Confidence band
fig2.add_trace(go.Scatter(
    x=prosail_full['Wav'],
    y=prosail_full['mean'] - prosail_full['sd'],
    mode='lines',
    line=dict(width=0),
    showlegend=False
))
fig2.add_trace(go.Scatter(
    x=prosail_full['Wav'],
    y=prosail_full['mean'] + prosail_full['sd'],
    mode='lines',
    line=dict(width=0),
    fillcolor='rgba(139, 0, 0, 0.3)',
    fill='tonexty',
    name='Confidence band',
    showlegend=False
))
# Sensor bands
if not prosail_sensor.empty:
    fig2.add_trace(go.Scatter(
        x=prosail_sensor['Wav'],
        y=prosail_sensor['mean'],
        mode='markers',
        name=f'{sensor} bands',
        marker=dict(color='green', size=8, line=dict(color='black', width=1)),
        opacity=0.7
    ))
fig2.update_layout(
    xaxis_title="Wavelength (nm)",
    yaxis_title="Reflectance (-)",
    xaxis_range=[400, 2500],
    yaxis_range=[0, 1],
    template="plotly_white",
    height=400
)
st.plotly_chart(fig2, use_container_width=True)

# Plot 3 and 4: LAI and Chlorophyll relationships
if not prosail_dataset.empty and vis in prosail_dataset.columns:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 LAI")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=prosail_dataset[vis],
            y=prosail_dataset['LAI'],
            mode='markers',
            name='Data points',
            marker=dict(color='green', size=8, line=dict(color='black', width=1)),
            opacity=0.7
        ))
        # Add trend line
        z = np.polyfit(prosail_dataset[vis], prosail_dataset['LAI'], 1)
        p = np.poly1d(z)
        x_trend = np.linspace(prosail_dataset[vis].min(), prosail_dataset[vis].max(), 100)
        fig3.add_trace(go.Scatter(
            x=x_trend,
            y=p(x_trend),
            mode='lines',
            name='Trend line',
            line=dict(color='blue', width=2)
        ))
        fig3.update_layout(
            xaxis_title=vis,
            yaxis_title="LAI (m²/m²)",
            template="plotly_white",
            height=350
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        st.markdown("### 🍃 Chlorophyll")
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(
            x=prosail_dataset[vis],
            y=prosail_dataset['Cab'],
            mode='markers',
            name='Data points',
            marker=dict(color='green', size=8, line=dict(color='black', width=1)),
            opacity=0.7
        ))
        # Add trend line
        z = np.polyfit(prosail_dataset[vis], prosail_dataset['Cab'], 1)
        p = np.poly1d(z)
        x_trend = np.linspace(prosail_dataset[vis].min(), prosail_dataset[vis].max(), 100)
        fig4.add_trace(go.Scatter(
            x=x_trend,
            y=p(x_trend),
            mode='lines',
            name='Trend line',
            line=dict(color='blue', width=2)
        ))
        fig4.update_layout(
            xaxis_title=vis,
            yaxis_title="Cab (µg cm⁻²)",
            template="plotly_white",
            height=350
        )
        st.plotly_chart(fig4, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
**Created by:** UCSC Field Crops Group - Remote sensing team

**Michele Croci**, **Giorgio Impollonia** and **Stefano Amaducci**
""")

