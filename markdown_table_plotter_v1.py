#pip install streamlit pandas plotly
#streamlit run markdown_table_plotter_plotly.py

import streamlit as st
import pandas as pd
import plotly.express as px

def extract_table_from_markdown(markdown_content):
    table_start = markdown_content.find("| Dataset Type")
    if table_start == -1:
        return None
    
    table_end = markdown_content.find("\n\n", table_start)
    if table_end == -1:
        table_end = len(markdown_content)
    
    table_content = markdown_content[table_start:table_end]
    lines = table_content.strip().split('\n')
    headers = [header.strip() for header in lines[0].split('|') if header.strip()]
    
    data = []
    for line in lines[2:]:
        row = [cell.strip() for cell in line.split('|') if cell.strip()]
        if len(row) == len(headers):
            data.append(row)
    
    df = pd.DataFrame(data, columns=headers)
    return df

def extract_images_from_markdown(markdown_content):
    image_links = {}
    lines = markdown_content.split('\n')
    for line in lines:
        if line.startswith('![') and '](' in line and ')' in line:
            alt_text = line[line.find('[')+1:line.find(']')]
            image_url = line[line.find('(')+1:line.find(')')]
            image_links[alt_text] = image_url
    return image_links

def main():
    st.title("Synthetic Face Datasets Visualization")

    uploaded_file = st.file_uploader("Choose the README.md file", type="md")
    
    if uploaded_file is not None:
        content = uploaded_file.getvalue().decode("utf-8")
        df = extract_table_from_markdown(content)
        image_links = extract_images_from_markdown(content)
        
        if df is not None:
            st.subheader("Extracted Table")
            st.dataframe(df)
            
            # Convert numeric columns to float
            numeric_columns = df.select_dtypes(include='number').columns.tolist()
            if numeric_columns:
                st.subheader("Data Visualization")
                
                # Plotly visualizations
                st.subheader("Plotly Visualizations")
                
                # Bar plot
                st.subheader("Plotly Bar Plot")
                metric = st.selectbox("Select metric for bar plot", numeric_columns)
                if 'Dataset Name' in df.columns:
                    fig_bar = px.bar(df, x='Dataset Name', y=metric, color='Dataset Type', 
                                     title=f'Comparison of {metric} across Datasets',
                                     hover_data=['Generator', 'Nid', 'Nsamples'])
                    fig_bar.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_bar)
                else:
                    st.warning("Column 'Dataset Name' not found for bar plot.")
                
                # Heatmap
                st.subheader("Plotly Heatmap")
                if numeric_columns:
                    fig_heatmap = px.imshow(df[numeric_columns].astype(float), 
                                            labels=dict(x="Metrics", y="Dataset", color="Score"),
                                            title="Heatmap of All Metrics")
                    st.plotly_chart(fig_heatmap)
                else:
                    st.warning("No numeric columns available for heatmap.")
                
                # Scatter plot
                st.subheader("Plotly Scatter Plot")
                if len(numeric_columns) > 1:
                    x_metric = st.selectbox("Select X-axis metric", numeric_columns)
                    y_metric = st.selectbox("Select Y-axis metric", [col for col in numeric_columns if col != x_metric])
                    if 'Dataset Type' in df.columns:
                        fig_scatter = px.scatter(df, x=x_metric, y=y_metric, color='Dataset Type', 
                                                 hover_data=['Dataset Name', 'Generator'],
                                                 title=f'{x_metric} vs {y_metric}')
                        st.plotly_chart(fig_scatter)
                    else:
                        st.warning("Column 'Dataset Type' not found for scatter plot.")
                else:
                    st.warning("Not enough numeric columns available for scatter plot.")

            # Display images
            st.subheader("Examples and Evaluations")
            for alt_text, image_url in image_links.items():
                st.image(image_url, caption=alt_text, use_column_width=True)

        else:
            st.error("No table found in the markdown file.")
    else:
        st.info("Please upload the README.md file to proceed.")

if __name__ == "__main__":
    main()
