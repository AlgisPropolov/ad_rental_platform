import pandas as pd
from io import StringIO, BytesIO

def export_to_excel(queryset, columns):
    df = pd.DataFrame(list(queryset.values(*columns)))
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Data')
    writer.close()
    return output.getvalue()