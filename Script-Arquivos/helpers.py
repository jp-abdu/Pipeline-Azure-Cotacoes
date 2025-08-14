from datetime import datetime
def yymmdd(dt:datetime):
    # B3 likely expects format without hyphens, using yymmdd format
    return dt.strftime("%y%m%d")
