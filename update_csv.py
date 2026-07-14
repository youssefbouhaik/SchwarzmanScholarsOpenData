import csv

file = 'scholars_cleaned.csv'
try:
    with open(file, 'r', encoding='utf-8') as f:
        reader = list(csv.reader(f))
    
    if reader:
        header = reader[0]
        yt_idx = header.index('youtube_video_id') if 'youtube_video_id' in header else -1
        adm_idx = header.index('admission_inferred') if 'admission_inferred' in header else -1
        
        fixed_count = 0
        if yt_idx != -1 and adm_idx != -1:
            for row in reader[1:]:
                if len(row) > yt_idx and row[yt_idx].strip():
                    if len(row) > adm_idx and row[adm_idx] != '1':
                        row[adm_idx] = '1'
                        fixed_count += 1
                        
            with open(file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(reader)
            
            print(f"Fixed {fixed_count} rows in {file}")
except Exception as e:
    print(f"Error: {e}")
