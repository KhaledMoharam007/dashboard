import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import warnings
import openpyxl
warnings.filterwarnings('ignore')

# At the top of your script
st.set_page_config(
    page_title="Production DashBoard",
    page_icon=":bar_chart:",
    layout="wide"
)

st.title("📊 Production DashBoard Monitoring")

# Custom CSS + JS to keep scroll position after rerun
st.markdown(
    """
    <style>
    div.block-container {
        padding-top: 2rem;
    }
    </style>
    <script>
    // Save scroll position before page reload
    window.addEventListener('beforeunload', function() {
        localStorage.setItem("scrollPos", window.scrollY);
    });

    // Restore scroll position on load
    window.addEventListener('load', function() {
        var scrollPos = localStorage.getItem("scrollPos");
        if (scrollPos !== null) {
            window.scrollTo(0, parseInt(scrollPos));
        }
    });
    </script>
    """,
    unsafe_allow_html=True
)


# st.set_page_config(page_title="Production DashBoard", page_icon=":bar_chart:", layout="wide")
# st.title(" :bar_chart: Production DashBoard Monitoring")
# st.markdown('<style>div.block-container{padding-top:2rem;}</style', unsafe_allow_html=True)


fl = st.file_uploader(":file_folder: Upload a file", type=["csv", "txt", "xlsx", "xls"])

if fl is not None:
    filename = fl.name
    st.write(filename)
    # Read the file content using pandas
    if filename.endswith('.xlsx') or filename.endswith('.xls'):
        df = pd.read_excel(fl)  # Reading the file directly from the uploader
        st.write(df.head())  # Show a preview of the DataFrame
else:
    os.chdir(r"/Users/khaledmoharam/Desktop/Coding Projects")
    df = pd.read_excel("ProductionDB.xlsx")
    st.write(df.head())  # Show a preview of the DataFrame


# -------------------------------------------------------------------------------

col1, col2 = st.columns((2))
df['Date']=pd.to_datetime(df['Date'])

startDate = df['Date'].min()
endDate = df['Date'].max()

with col1:
    date1 = st.date_input("Start Date", startDate)

with col2:
    date2 = st.date_input("End Date", endDate)

date1 = pd.to_datetime(date1)
date2 = pd.to_datetime(date2)

if date1 > date2:
    date1, date2 = date2, date1

# Filter
df = df[(df['Date'] >= date1) & (df['Date'] <= date2)].copy()

# Optional: show range
st.write(f"Filtering from {date1.date()} to {date2.date()}")



# -------------------------------------------------------------------------------

# Side Bar 
st.sidebar.header("Choose Your Filter")

# Side Bar Sales Branch
salesBranch = st.sidebar.multiselect("Pick Sales Branch", df['Sales Branch'].unique())
if not salesBranch:
    df2 = df.copy()
else:
    df2 = df[df["Sales Branch"].isin(salesBranch)]

# Side Bar Packing Type
packingType = st.sidebar.multiselect("Pick Packing Type", df2['Packing Type'].unique())
if not packingType:
    df3 = df2.copy()
else:
    df3=df2[df2['Packing Type'].isin(packingType)]

productDescription = st.sidebar.multiselect("Pick Product Descrption", df3['Product Description'].unique())

# Filter SideBar Data 
if not salesBranch and not packingType and not productDescription:
    filtered_df = df

elif not packingType and not productDescription:
    filtered_df = df[df['Sales Branch'].isin(salesBranch)]

elif not salesBranch and not productDescription:
    filtered_df = df[df['Packing Type'].isin(packingType)]

elif salesBranch and packingType and not productDescription:
    filtered_df = df3[(df3['Sales Branch'].isin(salesBranch)) &
                      (df3['Packing Type'].isin(packingType))]

elif salesBranch and productDescription and not packingType:
    filtered_df = df3[(df3['Sales Branch'].isin(salesBranch)) &
                      (df3['Product Description'].isin(productDescription))]

elif productDescription and packingType and not salesBranch:
    filtered_df = df3[(df3['Product Description'].isin(productDescription)) &
                      (df3['Packing Type'].isin(packingType))]

elif productDescription and not salesBranch and not packingType:
    filtered_df = df3[df3['Product Description'].isin(productDescription)]

else:  # all three present
    filtered_df = df3[(df3['Sales Branch'].isin(salesBranch)) &
                      (df3['Packing Type'].isin(packingType)) &
                      (df3['Product Description'].isin(productDescription))]


cateogory_df = (
    filtered_df.groupby(by=['Product Type'], as_index=False)['Packing Type'].sum()
    .sort_values(by="Packing Type", ascending=False)  # Sort products by quantity
)

# -------------------------------------------------------------------------------

# --- Aggregate Packing Quantity ---
summary = filtered_df.groupby(["Sales Branch", "Packing Type"], as_index=False)["Packing Quantity"].sum()

# -------------------------------------------------------------------------------

# --- Metrics Calculation ---
# Get unique Packing Types (limit to 4)
packing_types = filtered_df['Packing Type'].unique()[:4]

# Total Packing Quantity per type
totals = filtered_df.groupby('Packing Type')['Packing Quantity'].sum()

# --- Display metrics in 4 columns ---
col1, col2, col3, col4 = st.columns(4)
cols = [col1, col2, col3, col4]

for i, col in enumerate(cols):
    if i < len(packing_types):
        value = totals.get(packing_types[i], 0)
        col.metric(label=f"{packing_types[i]}", value=f"{value:,}")
    else:
        col.metric(label="N/A", value="0")


# Black theme + metrics CSS
st.markdown(
    """
    <style>
    /* Main background */
    .css-18e3th9 {background-color: #000000;}
    
    /* Sidebar background */
    .css-1d391kg {background-color: #1a1a1a;}
    
    /* Text color */
    .css-15zrgzn, .css-1d391kg * {color: #ffffff;}
    
    /* Buttons */
    .stButton>button {background-color: #1abc9c; color: #000000;}
    
    /* Metrics container background & padding */
    .stMetric {
        background-color: #0a0a0a !important; /* pure black for metric cards */
        border-radius: 10px;
        padding: 20px;
        box-shadow: 2px 2px 5px #111111;
    }
    
    /* Metric label (header) font size and color */
    .stMetric label {
        font-size: 18px;
        font-weight: bold;
        color: #1abc9c !important;
    }
    
    /* Metric value font size and color */
    .stMetric div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)



# -------------------------------------------------------------------------------
# Add vertical space
st.write("\n")  # small space

col_left, col_right = st.columns([4, 4])
# --- Bar Chart --- 
with col_left:
    st.subheader("Sales Branch Vs Packing Type")
    fig = px.bar(
        summary,
        x="Sales Branch",
        y="Packing Quantity",
        color="Packing Type",  # separate color for each packing type
        barmode="group",       # side-by-side bars; use "stack" for stacked
        text="Packing Quantity",
        height=400
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

branch_summary = filtered_df.groupby("Sales Branch", as_index=False)["Total QuantityMT"].sum()

# --- Pie Chart in col2 ---
with col_right:
    st.subheader("Quantity Distribution by Sales Branch")
    fig_pie = px.pie(
        branch_summary,
        names="Sales Branch",
        values="Total QuantityMT",
        title="Total QuantityMT by Sales Branch",
        hole=0.0
    )
    fig_pie.update_traces(textinfo="percent+label")
    st.plotly_chart(fig_pie, use_container_width=True)


# -------------------------------------------------------------------------------
# Add vertical space
st.write("\n")  # small space

col_left, col_right = st.columns([4, 4])

with col_left:
    # Keep only Group G4
    df_g4 = filtered_df[filtered_df['Group'] == 'G4']

    # Aggregate total Packing Quantity by Product Description
    agg_df = df_g4.groupby("Product Description")["Packing Quantity"].sum().reset_index()

    # Get top 10 products sorted descending
    top10_df = agg_df.sort_values(by="Packing Quantity", ascending=False).head(10)

    # Horizontal bar chart
    fig_bar = px.bar(
        top10_df,
        x="Packing Quantity",
        y="Product Description",
        orientation="h",
        color="Packing Quantity",
        text="Packing Quantity",
        color_continuous_scale="blues",
    )

    # Styling
    fig_bar.update_layout(
        yaxis=dict(autorange="reversed"),
        title=dict(x=0.5),
    )

    fig_bar.update_traces(textposition="outside")

    st.subheader("Top 10 Products by Total Packing Quantity (Group G4)")
    st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------------------------------------------------------------
with col_right:
    # Keep only Group G1
    df_g1 = filtered_df[filtered_df['Group'] == 'G1']

    # Aggregate total Packing Quantity by Product Description
    agg_df = df_g1.groupby("Product Description")["Packing Quantity"].sum().reset_index()

    # Get top 10 products sorted descending
    top10_df = agg_df.sort_values(by="Packing Quantity", ascending=False).head(10)

    # Horizontal bar chart
    fig_bar = px.bar(
        top10_df,
        x="Packing Quantity",
        y="Product Description",
        orientation="h",
        color="Packing Quantity",
        text="Packing Quantity",
        color_continuous_scale="blues"
    )

    # Styling
    fig_bar.update_layout(
        yaxis=dict(autorange="reversed"),
        title=dict(x=0.5)
    )

    fig_bar.update_traces(textposition="outside")

    st.subheader("Top 10 Products by Total Packing Quantity (Group G1)")
    st.plotly_chart(fig_bar, use_container_width=True)


# -------------------------------------------------------------------------------
# Add vertical space
st.write("\n")  # small space

col_left, col_right = st.columns([4, 4])

# --- Horizontal Bar Chart ---

with col_left:
    # Aggregate total QuantityMT by Group
    agg_df = filtered_df.groupby('Group')['Total QuantityMT'].sum().reset_index()

    # Sort ascending (smallest to largest)
    agg_df = agg_df.sort_values(by='Total QuantityMT', ascending=True)

    # Round Total QuantityMT to 1 decimal place for labels
    agg_df['Total_QuantityMT_label'] = agg_df['Total QuantityMT'].round(1)

    # Create horizontal bar chart
    fig = px.bar(
        agg_df,
        x='Total QuantityMT',
        y='Group',
        text='Total_QuantityMT_label',
        color='Total QuantityMT',
        color_continuous_scale='blues',
        orientation='h'
    )

    # Dark theme styling
    fig.update_layout(
        title="Total QuantityMT by Group",
        xaxis_title="Total QuantityMT",
        yaxis_title="Group",
        font=dict(color='white')
    )

    # Show values outside the bars
    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)

# --- Donut Chart ---

with col_right:
    agg_df_donut = filtered_df.groupby('Group')['Total QuantityMT'].sum().reset_index()

    fig_donut = px.pie(
        agg_df_donut,
        names='Group',
        values='Total QuantityMT',
        hole=0.4,
        color='Group',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    fig_donut.update_layout(
        title="Total QuantityMT Distribution by Group",
    )

    fig_donut.update_traces(textinfo='label+percent', textfont_size=14)

    st.plotly_chart(fig_donut, use_container_width=True)

# -------------------------------------------------------------------------------
# Add vertical space
st.write("\n")  # small space

col_left, col_middle, col_right = st.columns([3, 3, 3])
with col_left:
    # Ensure Date column is datetime
    filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])

    # Filter for Cartons only
    cartons_df = filtered_df[filtered_df['Packing Type'] == 'Cartons']

    # Aggregate by Month
    cartons_df['Month'] = cartons_df['Date'].dt.to_period('M')
    monthly_df = cartons_df.groupby('Month')['Packing Quantity'].sum().reset_index()
    monthly_df['Month'] = monthly_df['Month'].dt.to_timestamp()  # convert Period to Timestamp

    # Create line chart
    fig = px.line(
        monthly_df,
        x='Month',
        y='Packing Quantity',
        title='Cartons Packing Quantity per Month',
        markers=True,
        labels={'Month': 'Month', 'Packing Quantity': 'Quantity (Cartons)'}
    )

    # Show Y-axis value on each point (raw numbers)
    fig.update_traces(
        text=monthly_df['Packing Quantity'].apply(lambda x: f'{x}'),  # actual Y-axis value
        textposition='top center'
    )

    # Display chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)


with col_middle:
    # Ensure Date column is datetime
    filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])

    # Filter for Drums only
    drums_df = filtered_df[filtered_df['Packing Type'] == 'Drums']

    # Aggregate by Month
    drums_df['Month'] = drums_df['Date'].dt.to_period('M')
    monthly_df = drums_df.groupby('Month')['Packing Quantity'].sum().reset_index()
    monthly_df['Month'] = monthly_df['Month'].dt.to_timestamp()  # convert Period to Timestamp

    # Create line chart
    fig = px.line(
        monthly_df,
        x='Month',
        y='Packing Quantity',
        title='Drums Packing Quantity per Month',
        markers=True,
        labels={'Month': 'Month', 'Packing Quantity': 'Quantity (Drums)'}
    )

    # Show Y-axis value on each point (raw numbers)
    fig.update_traces(
        text=monthly_df['Packing Quantity'].apply(lambda x: f'{x}'),
        textposition='top center'
    )

    # Display chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)


with col_right:
    # Ensure Date column is datetime
    filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])

    # Filter for Gallons only
    gallons_df = filtered_df[filtered_df['Packing Type'] == 'Gallons']

    # Aggregate by Month
    gallons_df['Month'] = gallons_df['Date'].dt.to_period('M')
    monthly_df = gallons_df.groupby('Month')['Packing Quantity'].sum().reset_index()
    monthly_df['Month'] = monthly_df['Month'].dt.to_timestamp()  # convert Period to Timestamp

    # Create line chart
    fig = px.line(
        monthly_df,
        x='Month',
        y='Packing Quantity',
        title='Gallons Packing Quantity per Month',
        markers=True,
        labels={'Month': 'Month', 'Packing Quantity': 'Quantity (Gallons)'}
    )

    # Show Y-axis value on each point (raw numbers)
    fig.update_traces(
        text=monthly_df['Packing Quantity'].apply(lambda x: f'{x}'),
        textposition='top center'
    )

    # Display chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------------------------------------
# Add vertical space
st.write("\n")  # small space

# Define three columns for the row
col_left, col_middle, col_right = st.columns([3, 3, 3])

# Left metric
with col_left:
    filtered_line_left = filtered_df[filtered_df['Production Line'] == "1L Cans, Turkey - Production Line 1"]
    total_packing_qty_left = filtered_line_left["Packing Quantity"].sum()
    
    st.markdown(
        f"""
        <div style='text-align: center; background-color: #000000; padding: 20px; border-radius: 10px;'>
            <div style='font-size:20px; font-weight:500; color:#ffffff;'>
                Packing Quantity "in Cartons" <br> (1L Cans, Production Line 1)
            </div>
            <div style='font-size:48px; font-weight:bold; color:#0a84ff;'>{int(total_packing_qty_left)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Middle metric
with col_middle:
    filtered_line_middle = filtered_df[filtered_df['Production Line'] == "1L Plastic, China - Production Line 2"]
    total_packing_qty_middle = filtered_line_middle["Packing Quantity"].sum()
    
    st.markdown(
        f"""
        <div style='text-align: center; background-color: #000000; padding: 20px; border-radius: 10px;'>
            <div style='font-size:20px; font-weight:500; color:#ffffff;'>
                Packing Quantity "in Cartons" <br> (1L Plastic, Production Line 2)
            </div>
            <div style='font-size:48px; font-weight:bold; color:#0a84ff;'>{int(total_packing_qty_middle)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Right metric
with col_right:
    filtered_line_right = filtered_df[filtered_df['Production Line'] == "1L Plastic, China - Production Line 3"]
    total_packing_qty_right = filtered_line_right["Packing Quantity"].sum()
    
    st.markdown(
        f"""
        <div style='text-align: center; background-color: #000000; padding: 20px; border-radius: 10px;'>
            <div style='font-size:20px; font-weight:500; color:#ffffff;'>
                Packing Quantity "in Cartons" <br> (1L Plastic, Production Line 3)
            </div>
            <div style='font-size:48px; font-weight:bold; color:#0a84ff;'>{int(total_packing_qty_right)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -------------------------------------------------------------------------------
# Add vertical space
st.write("\n")  # small space

# Define three columns for the row
col_left, col_middle, col_right = st.columns([3, 3, 3])

# Left metric
with col_left:
    filtered_line_right = filtered_df[filtered_df['Production Line'] == "4L, 5L Plastic, China - Production Line 4"]
    total_packing_qty_right = filtered_line_right["Packing Quantity"].sum()
    
    st.markdown(
        f"""
        <div style='text-align: center; background-color: #000000; padding: 20px; border-radius: 10px;'>
            <div style='font-size:20px; font-weight:500; color:#ffffff;'>
                Packing Quantity "in Cartons" <br> (4L, 5L Plastic, Production Line 4)
            </div>
            <div style='font-size:48px; font-weight:bold; color:#0a84ff;'>{int(total_packing_qty_right)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Middle metric
with col_middle:
    filtered_line_right = filtered_df[filtered_df['Production Line'] == "Brake Fluid, USA - Production Line 5"]
    total_packing_qty_right = filtered_line_right["Packing Quantity"].sum()
    
    st.markdown(
        f"""
        <div style='text-align: center; background-color: #000000; padding: 20px; border-radius: 10px;'>
            <div style='font-size:20px; font-weight:500; color:#ffffff;'>
                Packing Quantity "in Cartons" <br> (Brake Fluid, Production Line 5)
            </div>
            <div style='font-size:48px; font-weight:bold; color:#0a84ff;'>{int(total_packing_qty_right)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Right metric
with col_right:
    # Filter by Production Line AND Packing Type = "Gallons" from sidebar
    filtered_line_right = filtered_df[
        (filtered_df['Production Line'] == "16L, 20L, 25L Gallon, China - Production Line 6") &
        (filtered_df['Packing Type'] == "Gallons")
    ]

    # Calculate total Packing Quantity
    total_packing_qty_right = filtered_line_right["Packing Quantity"].sum()

    # Show metric
    st.markdown(
        f"""
        <div style='text-align: center; background-color: #000000; padding: 20px; border-radius: 10px;'>
            <div style='font-size:20px; font-weight:500; color:#ffffff;'>
                Packing Quantity "in Gallons" <br> (16L, 20L, 25L, Production Line 6)
            </div>
            <div style='font-size:48px; font-weight:bold; color:#0a84ff;'>{int(total_packing_qty_right)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

  # -------------------------------------------------------------------------------
# Add vertical space
st.write("\n")  # small space

col_left, col_right = st.columns([4, 4])

with col_left:
    # Horizontal Bar Chart
    
    fig = px.bar(
        filtered_df,
        y="Production Line",
        x="Packing Quantity",
        orientation="h",
        title="Production Line vs Packing Quantity",
    )

    # Customize layout
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor="rgba(240,240,240,0.5)",
        paper_bgcolor="rgba(240,240,240,0.5)",
        title={
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    st.plotly_chart(fig, use_container_width=True)

# Right column → Area chart
    with col_right:
        
        # Sort dataframe by Packing Quantity ascending
        filtered_df_sorted = filtered_df.sort_values(by="Packing Quantity", ascending=True)

        # Area chart
        fig_area = px.area(
            filtered_df_sorted,
            x="Production Line",       # X-axis
            y="Packing Quantity",      # Y-axis
            title="Area Chart (Ascending): Production Line vs Packing Quantity"
        )

        # Customize layout
        fig_area.update_layout(
            plot_bgcolor="rgba(200,200,200,0.8)",
            paper_bgcolor="rgba(200,200,200,0.8)",
            title={'x':0.5, 'xanchor':'center', 'yanchor':'top'}
        )

        st.plotly_chart(fig_area, use_container_width=True)

# Sort by Packing Quantity ascending
filtered_df_sorted = filtered_df.sort_values(by="Packing Quantity", ascending=True)

# Funnel chart
fig_funnel = px.funnel(
    filtered_df_sorted,
    x="Packing Quantity",
    y="Production Line",
    title="Funnel Chart (Ascending): Production Line vs Packing Quantity"
)

# Customize layout
fig_funnel.update_layout(
    plot_bgcolor="rgba(200,200,200,0.8)",
    paper_bgcolor="rgba(200,200,200,0.8)",
    title={'x':0.5, 'xanchor':'center', 'yanchor':'top'}
)

st.plotly_chart(fig_funnel, use_container_width=True)

  # -------------------------------------------------------------------------------
  # Add vertical space
st.write("\n")  # small space

     # Define three columns for the row
col_left, col_middle, col_right = st.columns([3, 3, 3])
with col_left:
    
    # Example Production Line
    pl_filter = "1L Cans, Turkey - Production Line 1"

    # Total QuantityMT for this Production Line
    pl_total = filtered_df[filtered_df['Production Line'] == pl_filter]['Total QuantityMT'].sum()

    # Total QuantityMT for all Production Lines
    total_all = filtered_df['Total QuantityMT'].sum()

    # Calculate percentage
    percentage = (pl_total / total_all) * 100

    # Create percentage gauge with dark grey background
    fig_percentage_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentage,
        number={'suffix': "%", 'font': {'color': 'black'}},
        title={'text': "1L Cans - Production Line 1", 'font': {'size': 24, 'color': 'black'}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': 'black'},
            'bar': {'color': "cyan"},
            'bgcolor': "darkgrey",
            'steps': [
                {'range': [0, 50], 'color': "gray"},
                {'range': [50, 100], 'color': "dimgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))

    fig_percentage_gauge.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    st.plotly_chart(fig_percentage_gauge, use_container_width=True)

with col_middle:
    # Example Production Line
    pl_filter = "1L Plastic, China - Production Line 2"

    # Total QuantityMT for this Production Line
    pl_total = filtered_df[filtered_df['Production Line'] == pl_filter]['Total QuantityMT'].sum()

    # Total QuantityMT for all Production Lines
    total_all = filtered_df['Total QuantityMT'].sum()

    # Calculate percentage
    percentage = (pl_total / total_all) * 100

    # Create percentage gauge with dark grey background
    fig_percentage_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentage,
        number={'suffix': "%", 'font': {'color': 'black'}},  # white for visibility
        title={'text': "1L Plastic - Production Line 2", 'font': {'size': 24, 'color': 'black'}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': 'black'},
            'bar': {'color': "cyan"},
            'bgcolor': "dimgray",
            'steps': [
                {'range': [0, 50], 'color': "gray"},
                {'range': [50, 100], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))

    fig_percentage_gauge.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    st.plotly_chart(fig_percentage_gauge, use_container_width=True)

with col_right:
    # Example Production Line
    pl_filter = "1L Plastic, China - Production Line 3"

    # Total QuantityMT for this Production Line
    pl_total = filtered_df[filtered_df['Production Line'] == pl_filter]['Total QuantityMT'].sum()

    # Total QuantityMT for all Production Lines
    total_all = filtered_df['Total QuantityMT'].sum()

    # Calculate percentage
    percentage = (pl_total / total_all) * 100

    # Create percentage gauge with dark grey background
    fig_percentage_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentage,
        number={'suffix': "%", 'font': {'color': 'black'}},  # white for visibility
        title={'text': "1L Plastic - Production Line 3", 'font': {'size': 24, 'color': 'black'}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': 'black'},
            'bar': {'color': "cyan"},
            'bgcolor': "dimgray",
            'steps': [
                {'range': [0, 50], 'color': "gray"},
                {'range': [50, 100], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))

    fig_percentage_gauge.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    st.plotly_chart(fig_percentage_gauge, use_container_width=True)
     # -------------------------------------------------------------------------------
 # Add vertical space
st.write("\n")  # small space

# Define three columns for the row
col_left, col_middle, col_right = st.columns([3, 3, 3])

# Function to create a gauge
def create_percentage_gauge(pl_filter, title_text):
    pl_total = filtered_df[filtered_df['Production Line'] == pl_filter]['Total QuantityMT'].sum()
    total_all = filtered_df['Total QuantityMT'].sum()
    percentage = (pl_total / total_all) * 100

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentage,
        number={'suffix': "%", 'font': {'color': 'black'}},
        title={'text': title_text, 'font': {'size': 24, 'color': 'black'}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': 'black'},
            'bar': {'color': "cyan"},
            'bgcolor': "dimgray",
            'steps': [
                {'range': [0, 50], 'color': "gray"},
                {'range': [50, 100], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white"
    )
    return fig

# Left column
with col_left:
    fig_left = create_percentage_gauge("4L, 5L Plastic, China - Production Line 4", "4L, 5L - Production Line 4")
    st.plotly_chart(fig_left, use_container_width=True)

# Middle column
with col_middle:
    fig_middle = create_percentage_gauge("Brake Fluid, USA - Production Line 5", "Brake Fluid - Production Line 5")
    st.plotly_chart(fig_middle, use_container_width=True)

# Right column
with col_right:
    fig_right = create_percentage_gauge("16L, 20L, 25L Gallon, China - Production Line 6", "Gallons - Production Line 6")
    st.plotly_chart(fig_right, use_container_width=True)    

     # -------------------------------------------------------------------------------

# Add vertical space
st.write("\n")  # small space

# Centered subheader using HTML
st.markdown("<h3 style='text-align: center;'>Production Line vs Total QuantityMT</h3>", unsafe_allow_html=True)
    
# Aggregate and round Total QuantityMT by Production Line
agg_df = filtered_df.groupby("Production Line")["Total QuantityMT"].sum().reset_index()
agg_df["Total QuantityMT"] = agg_df["Total QuantityMT"].round(0).astype(int)
    
# Create treemap with rounded values
fig = px.treemap(
        agg_df,
        path=['Production Line'],
        values='Total QuantityMT',
        color='Total QuantityMT',
        color_continuous_scale='Blues',
        hover_data={'Total QuantityMT': True}
    )
    
# Show value labels on blocks
fig.update_traces(texttemplate='%{label}<br>%{value}', textinfo='text+value')

# Set faint black background
fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0.05)',  # very faint black
        plot_bgcolor='rgba(0,0,0,0.05)',
        font_color='white'                 # optional: make text white for contrast
    )
    
st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------------------------

 # Add vertical space
st.write("\n")  # small space

# Centered subheader
st.markdown("<h3 style='text-align: center;'>Production Line vs Total QuantityMT</h3>", unsafe_allow_html=True)

# Aggregate and round Total QuantityMT by Production Line
agg_df = filtered_df.groupby("Production Line")["Total QuantityMT"].sum().reset_index()
agg_df["Total QuantityMT"] = agg_df["Total QuantityMT"].round(0).astype(int)

# Create pie chart
fig = px.pie(
    agg_df,
    names='Production Line',
    values='Total QuantityMT',
    color_discrete_sequence=px.colors.sequential.Blues
)

# Show label with both value and percentage
fig.update_traces(
    textinfo='label+percent+value',
    texttemplate="%{label}<br>(%{percent})",
    textposition='outside',  # labels outside
    textfont_size=14,
    showlegend=False,      # remove legend
    hoverinfo='skip'       # remove hover info
)

# Set faint black background
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0.05)',
    plot_bgcolor='rgba(0,0,0,0.05)',
    font_color='black'
)

# Display chart full width
st.plotly_chart(fig, use_container_width=True)

 # -------------------------------------------------------------------------------