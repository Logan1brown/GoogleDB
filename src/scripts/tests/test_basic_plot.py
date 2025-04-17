import plotly.express as px

# Create a simple scatter plot
df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length", title="Basic Scatter Plot")

# Save the figure
fig.write_html('output/test_basic_plot.html')
