import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET
from config import CURRENT_YEAR, MDB_XML_PATH

def get_mdb_data(mdb_xml_path: Path = MDB_XML_PATH) -> pd.DataFrame:
    """Parse MDB XML data and return a DataFrame."""
    tree = ET.parse(mdb_xml_path)
    root = tree.getroot()

    mdb_list = []

    for mdb in root.findall('MDB'):
        mdb_dict = {
            'ID': mdb.find('ID').text,
            'NACHNAME': mdb.find('NAMEN/NAME/NACHNAME').text,
            'VORNAME': mdb.find('NAMEN/NAME/VORNAME').text,
            **{element.tag: element.text for element in mdb.find('BIOGRAFISCHE_ANGABEN')},
            'ANZ_WAHLPERIODEN': len(mdb.find('WAHLPERIODEN')),
        }

        # Setze für jede Wahlperiode den Wert auf 1
        for wp in mdb.find('WAHLPERIODEN'):
            mdb_dict[int(wp.find('WP').text)] = 1

        mdb_list.append(mdb_dict)

    return pd.DataFrame(mdb_list)


def get_mdb_wp_data(df_mdb: pd.DataFrame) -> pd.DataFrame:
    """
    Reformat data from wide to long format, creating one row per person per Wahlperiode.
    """
    wps: List[int] = [col for col in df_mdb.columns if isinstance(col, int)]
    columns_to_keep: List[str] = [col for col in df_mdb.columns if not isinstance(col, int)]
    
    # Melt the dataframe to long format
    df_long = df_mdb.melt(id_vars=columns_to_keep, 
                          value_vars=wps, 
                          var_name='WP', 
                          value_name='is_active')
    
    # Filter only active Wahlperioden and drop the 'is_active' column
    return df_long[df_long['is_active'] == 1].drop('is_active', axis=1)
