import pandas as pd
import json

def analyze_common_traits():
    csv_path = '/home/edgar/.gemini/antigravity-cli/brain/6137966f-76f6-4d54-a854-71ca87156e97/scratch/detalle_20_activas.csv'
    
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    total_rows = len(df)
    print(f"Analizando {total_rows} registros...\n")

    # Drop columns that are completely unique like 'id' or 'Nº Pos Actual'
    cols_to_ignore = ['id', 'Nº Pos Actual', 'rn']
    df_analysis = df.drop(columns=[col for col in cols_to_ignore if col in df.columns], errors='ignore')

    common_traits = {}
    mostly_common_traits = {}

    for col in df_analysis.columns:
        counts = df_analysis[col].value_counts(dropna=False)
        if len(counts) == 0:
            continue
        
        top_val = counts.index[0]
        top_count = counts.iloc[0]
        
        if top_count == total_rows:
            common_traits[col] = top_val
        elif top_count >= total_rows * 0.8:  # 80% or more common
            mostly_common_traits[col] = {
                'value': top_val,
                'percentage': f"{(top_count / total_rows) * 100:.1f}%",
                'count': top_count
            }

    print("=== CARACTERÍSTICAS 100% IDÉNTICAS EN LAS 20 POSICIONES ===")
    for col, val in common_traits.items():
        # Handle nan nicely
        if pd.isna(val):
            val_str = "<VACÍO/NULL>"
        else:
            val_str = str(val)
        print(f"- {col}: {val_str}")
        
    print("\n=== PATRONES FUERTES (Compartido por 80%+ de las posiciones) ===")
    for col, data in mostly_common_traits.items():
        val = data['value']
        if pd.isna(val):
            val_str = "<VACÍO/NULL>"
        else:
            val_str = str(val)
        print(f"- {col}: {val_str} (en {data['count']} de {total_rows} posiciones - {data['percentage']})")

if __name__ == '__main__':
    analyze_common_traits()
