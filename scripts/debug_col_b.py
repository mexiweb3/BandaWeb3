import openpyxl

def debug_col_b():
    input_file = "shared/inputs/Spoken - Spaces Dashboard.xlsx"
    print(f"Loading {input_file}...")
    wb = openpyxl.load_workbook(input_file)
    ws = wb.active

    print("\nChecking Column B (Title) for hyperlinks in first few data rows...")
    for r in range(4, 10):
        cell_b = ws.cell(row=r, column=2) # B
        
        val = cell_b.value
        link = cell_b.hyperlink
        link_target = link.target if link else "No Link"
        
        print(f"Row {r}: Val (trunc)='{str(val)[:50]}...'")
        print(f"       Link='{link_target}'")

if __name__ == "__main__":
    debug_col_b()
