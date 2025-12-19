"""
Script temporal para ver qué valores exactos hay en la columna de precios
"""
import openpyxl
import sys
import io

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

EXCEL_PATH = "BASE DE DATOS PROPIEDADES BOOT.xlsx"

wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)

print("=" * 80)
print("VALORES EN COLUMNA DE PRECIOS (Columna I - índice 8)")
print("=" * 80)

# Ver hoja Casas
sheet = wb["Casas"]
print("\n🏠 HOJA: Casas")
print("-" * 80)

for row_idx, row in enumerate(sheet.iter_rows(min_row=2, max_row=6, values_only=True), start=2):
    direccion = row[4] if len(row) > 4 else None
    valor_str = row[8] if len(row) > 8 else None

    print(f"Fila {row_idx}: {direccion}")
    print(f"  Valor RAW: {repr(valor_str)}")
    print(f"  Tipo: {type(valor_str)}")
    print()

wb.close()
