import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st

def parse_column_view(xml_content):
    try:
        # Parse the XML content
        root = ET.fromstring(xml_content)
        data = []

        # Extract the source table/view from the input entity
        entity = root.find('.//input/entity')
        source_table_view = entity.text.replace('#//', '') if entity is not None else "N/A"

        # Extract parameter details
        for parameter in root.findall('.//parameter'):
            param_name = parameter.get('name', '')
            param_label = parameter.find('.//endUserTexts').get('label', '') if parameter.find('.//endUserTexts') is not None else ''
            data.append({
                "Technical Name": param_name,
                "Field Label": param_label,
                "Source Table/View": "N/A",  # Parameters do not have a source table
                "Source Field Name": "N/A",
                "Attribute/ Measure": "Parameter",
                "Direct/ Calculation": "N/A",
                "Data Type": "N/A",  # Data type is not applicable for parameters
                "Logic": "N/A"
            })

        # Extract information from viewNode
        for element in root.findall('.//viewNode/element'):
            data_type = element.find('.//inlineType')
            primitive_type = data_type.get('primitiveType', '') if data_type is not None else 'N/A'
            length = data_type.get('length', '') if data_type is not None else '0'  # Default to '0' if not found
            
            # Format data type based on length
            if length != '0':
                full_data_type = f"{primitive_type}({length})"
            else:
                full_data_type = primitive_type
            
            row = {
                "Technical Name": element.get('name', ''),
                "Field Label": element.find('.//endUserTexts').get('label', '') if element.find('.//endUserTexts') is not None else '',
                "Source Table/View": source_table_view,
                "Source Field Name": element.get('name', '').replace('#', ''),  # Clean up the source field name
                "Attribute/ Measure": "Attribute",  # Assuming these are attributes
                "Direct/ Calculation": "Direct",  # Assuming these are directly mapped
                "Data Type": full_data_type,
                "Logic": "N/A"  # Adjust this based on your logic
            }
            data.append(row)

        return pd.DataFrame(data)

    except ET.ParseError as e:
        st.error(f"Error parsing XML: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error

# Function to create download link for DataFrame
def create_download_link(df, file_type):
    if file_type == 'xlsx':
        return df.to_excel('data_dictionary.xlsx', index=False)
    elif file_type == 'csv':
        return df.to_csv('data_dictionary.csv', index=False)

# Streamlit application
def main():
    st.title("HANA View Data Dictionary Generator")
    uploaded_file = st.file_uploader("Upload an XML file", type="xml")
    
    if uploaded_file is not None:
        xml_content = uploaded_file.read().decode("utf-8")
        df = parse_column_view(xml_content)
        
        if not df.empty:
            st.write("### Parsed Data Dictionary")
            st.dataframe(df)  # Display the DataFrame in Streamlit
            
            # Download buttons for XLSX and CSV
            st.write("### Download Options")
            if st.button('Download as XLSX'):
                create_download_link(df, 'xlsx')
                st.success("XLSX file downloaded!")
            
            if st.button('Download as CSV'):
                create_download_link(df, 'csv')
                st.success("CSV file downloaded!")
        else:
            st.warning("No data found in the uploaded XML.")

if __name__ == "__main__":
    main()