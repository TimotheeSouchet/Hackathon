def format_duree(secondes):
    minutes = secondes // 60
    sec = secondes % 60
    return f"{minutes}min{sec:02d}"