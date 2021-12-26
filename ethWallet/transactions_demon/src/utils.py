from datetime import datetime

def convert_time(t: int) -> str:
    return datetime.fromtimestamp(int(t)).strftime('%d-%m-%Y %H:%M:%S')