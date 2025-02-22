from pathlib import Path

import pandas as pd

from shiny import App, Inputs, Outputs, Session, reactive, render, ui, req
from shiny.types import FileInfo
from shiny.ui import markdown
import shinyswatch

from src import (
    list_sheet_names,
    extract_report,
)


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.accordion(
            ui.accordion_panel(
                "1. Upload",
                ui.input_file(
                    "file_input",
                    "Choose Excel or CSV File",
                    accept=[".csv", ".xlsx"],
                    multiple=False,
                ),
                ui.input_select(
                    "excel_sheet_select",
                    "If Excel, select sheet:",
                    [],
                ),
            ),
            ui.accordion_panel(
                "2. Configuration",
                ui.input_selectize(
                    "report_col_select",
                    "Input report column:",
                    [],
                ),
                ui.input_selectize(
                    "report_format_select",
                    "Input report format:",
                    {"plain": "Plain Text", "html": "HTML Text"},
                    selected="plain",
                ),
            ),
            ui.accordion_panel(
                "3. Download",
                ui.download_button("downloadData", "Download CSV"),
            ),
            open=None,
        ),
        width=300,
        title=markdown("**Steps**")
    ),
    # For Debug
    # ui.output_text_verbatim("tester_verbatim"),
    # shinyswatch.theme_picker_ui(),
    ui.output_data_frame("output_df"),
    title="Radiology Report Data Extractor",
    fillable=True,
    theme=shinyswatch.theme.united,
)


def server(input: Inputs, output: Outputs, session: Session):
    
    ## Theme Chooser
    # shinyswatch.theme_picker_server()
    ## Read & Parse Input file
    @reactive.calc
    def read_input_file():
        """Read input file into a data frame"""
        
        file: list[FileInfo] | None = input.file_input()
        if file is None:
            return pd.DataFrame()
        
        file_path =  Path(file[0]["datapath"])
        
        if file_path.suffix.lower() == ".csv":
            return pd.read_csv(file_path)
        
        elif file_path.suffix.lower() == ".xlsx":
            sheet_name = input.excel_sheet_select()
            if len(sheet_name) == 0:
                return pd.DataFrame()
            else:
                return pd.read_excel(file_path, sheet_name = input.excel_sheet_select())
        else:
            raise ValueError(f"Invalid file extension: {file_path.suffix}")
    
    ## Excel Sheet Names
    @reactive.calc
    def get_excel_sheet_name():
        file: list[FileInfo] | None = input.file_input()
        req(input.file_input())
        file_path =  Path(file[0]["datapath"])
        if file_path.suffix.lower() == ".xlsx":
            sheet_names = list_sheet_names(file_path)
            return sheet_names
    
    @reactive.Effect
    def update_excel_sheet_select():
        sheet_names = get_excel_sheet_name()
        ui.update_select("excel_sheet_select",
                         choices = sheet_names,
                         )
    ## Select Column
    @reactive.calc
    def get_column_name():
        req(input.file_input())
        df_input = read_input_file()
        col_names = df_input.columns.to_list()
        return col_names
    
    @reactive.Effect
    def update_report_col_select():
        col_names = get_column_name()
        ui.update_selectize("report_col_select", 
                            choices = col_names)
    
    ## Extract Report !!!
    @reactive.calc
    def get_extracted_report():
        req(input.file_input(), 
            input.report_col_select(), 
            input.report_format_select(), cancel_output=True)

        df = read_input_file()
        df_extracted = extract_report(
            df = df,
            report_col = input.report_col_select(),
            report_format = input.report_format_select(),
            verbose = False, 
        )
        
        return df_extracted
    
    
    ## Render DF for display
    @render.data_frame
    def output_df():
        
        df_extracted = get_extracted_report()
        return render.DataGrid(df_extracted, filters=True)
    
    ## Download
    @session.download(filename=lambda: f"{Path(input.file_input()[0]["name"]).stem}_extracted.csv")
    def downloadData():
        """
        Download
        """
        df_extracted = get_extracted_report()
        yield df_extracted.to_csv()
    
    ## For Debug
    # @render.text  
    # def tester_verbatim():
    
    #     return f"""
    # Column names: {get_column_name()}
    # Selected col: {input.report_col_select()}
    # """



app = App(app_ui, server)
