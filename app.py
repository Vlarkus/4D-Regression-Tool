import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import os

st.set_page_config(page_title="4D Regression Visualizer", layout="wide")

st.markdown("""
<style>
    .reportview-container .main .block-container {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to find CSVs
def get_csv_files(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return [f for f in os.listdir(directory) if f.endswith('.csv')]

# Sidebar
st.sidebar.title("Controls")

data_dir = "data"
csv_files = get_csv_files(data_dir)

if not csv_files:
    st.sidebar.warning(f"No CSV files found in {data_dir}/ directory.")
    selected_file = None
else:
    selected_file = st.sidebar.selectbox("Select Data File", csv_files)

if selected_file:
    df = pd.read_csv(os.path.join(data_dir, selected_file))
    cols = df.columns.tolist()
    
    st.sidebar.subheader("Dimension Mapping")
    col_x = st.sidebar.selectbox("X Axis", cols, index=0)
    col_y = st.sidebar.selectbox("Y Axis", cols, index=min(1, len(cols)-1))
    col_z = st.sidebar.selectbox("Z Axis", cols, index=min(2, len(cols)-1))
    col_w = st.sidebar.selectbox("4th Dimension (Color/Filter)", cols, index=min(3, len(cols)-1))
    
    show_points = st.sidebar.checkbox("Show Points", value=True)
    
    # 4th Dimension Filter
    st.sidebar.subheader("4th Dimension Filter")
    w_min, w_max = float(df[col_w].min()), float(df[col_w].max())
    w_range = st.sidebar.slider(f"Range of {col_w}", w_min, w_max, (w_min, w_max))
    
    # Color options
    color_options = ["Viridis", "Plasma", "Inferno", "Magma", "Cividis", "Redor", "Greens"]
    color_scale = st.sidebar.selectbox("Color Gradient", color_options)
    
    # Regression Section
    st.sidebar.subheader("Regression Model")
    show_regression = st.sidebar.checkbox("Show Regression Plane", value=False)
    
    # Filter data based on 4w range
    filtered_df = df[(df[col_w] >= w_range[0]) & (df[col_w] <= w_range[1])]
    
    # Fit regression model
    if show_regression:
        try:
            X_reg = df[[col_x, col_y]]
            y_reg = df[col_z]
            model = LinearRegression().fit(X_reg, y_reg)
            r2 = model.score(X_reg, y_reg)
            
            st.sidebar.write(f"**R² Score:** {r2:.4f}")
            st.sidebar.write(f"**Coefficients:**")
            st.sidebar.write(f"{col_x}: {model.coef_[0]:.4f}")
            st.sidebar.write(f"{col_y}: {model.coef_[1]:.4f}")
            st.sidebar.write(f"Intercept: {model.intercept_:.4f}")
        except Exception as e:
            st.sidebar.error(f"Regression error: {e}")

    # Main Visual
    st.title("4D Point Visualization")
    
    fig = go.Figure()
    
    if show_points:
        fig.add_trace(go.Scatter3d(
            x=filtered_df[col_x],
            y=filtered_df[col_y],
            z=filtered_df[col_z],
            mode='markers',
            marker=dict(
                size=5,
                color=filtered_df[col_w],
                colorscale=color_scale,
                colorbar=dict(title=col_w),
                opacity=0.8
            ),
            name="Data Points"
        ))
    
    if show_regression:
        # Create a grid for the plane
        x_range = np.linspace(df[col_x].min(), df[col_x].max(), 20)
        y_range = np.linspace(df[col_y].min(), df[col_y].max(), 20)
        x_grid, y_grid = np.meshgrid(x_range, y_range)
        z_grid = model.predict(np.c_[x_grid.ravel(), y_grid.ravel()]).reshape(x_grid.shape)
        
        fig.add_trace(go.Surface(
            x=x_range,
            y=y_range,
            z=z_grid,
            opacity=0.5,
            colorscale='Greys',
            showscale=False,
            name="Regression Plane"
        ))
        
    fig.update_layout(
        scene=dict(
            xaxis_title=col_x,
            yaxis_title=col_y,
            zaxis_title=col_z,
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=700
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Please upload or select a CSV file to begin.")
