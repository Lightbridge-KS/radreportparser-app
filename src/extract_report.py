from typing import Literal
import logging
import pandas as pd
from markdownify import markdownify as md

from radreportparser import RadReportExtractor


def extract_report(df: pd.DataFrame, 
                   report_col: str | None = None, 
                   report_format: Literal["html", "plain"] = "plain",
                   **kwargs):
    """Extract report text from a given column of DF with option to choose report formatting"""
    extractor = RadReportExtractor()
    # Convert column to string
    df[report_col] = df[report_col].astype(str)
    
    def convert_formatting(text: str, report_format: str):
        return md(text) if report_format == "html" else text
    
    # Extract to `__dict__` column
    try:
        df["__dict__"] = df.apply(lambda row: extractor.extract_all(convert_formatting(row[report_col], report_format), **kwargs).to_dict(), axis=1)
        ## Unnest
        df_out = pd.concat(
            [df.drop(columns='__dict__'), df['__dict__'].apply(pd.Series)], axis=1
        )
    except ValueError as e:
        logging.warning(f"ValueEror: {e}")
        
    return df_out
    