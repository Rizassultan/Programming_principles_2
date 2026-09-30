from datetime import datetime

date1 = datetime(2026, 9, 30, 10, 0, 0)
date2 = datetime(2026, 9, 30, 12, 30, 0)

difference = date2 - date1

print(difference.total_seconds())