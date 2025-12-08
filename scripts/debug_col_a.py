import openpyxl

def debug_col_a():
    input_file = "shared/inputs/Spoken - Spaces Dashboard.xlsx"
    print(f"Loading {input_file}...")
    wb = openpyxl.load_workbook(input_file)
    ws = wb.active

    print("\nChecking Column A (Host/Image?) for hyperlinks in first few data rows...")
    for r in range(4, 10):
        cell_a = ws.cell(row=r, column=1) # A
        
        val = cell_a.value
        link = cell_a.hyperlink
        link_target = link.target if link else "No Link"
        
        print(f"Row {r}: Val='{val}'")
        print(f"       Link='{link_target}'")

if __name__ == "__main__":
    debug_col_a()
