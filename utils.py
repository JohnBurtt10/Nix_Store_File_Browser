def print_progress_update(idx, total_jobsets, bar_length):
    percent_complete = (idx + 1) / total_jobsets * 100
    progress = int(bar_length * (idx + 1) / total_jobsets)
    
    # # Extract timestamp using string slicing
    # timestamp_str = jobset.split('-')[1]
    
    # # Convert timestamp string to datetime object
    # timestamp = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
    
    if idx > 0:
        # time_difference = timestamp - datetime.strptime(sorted_jobsets[idx - 1].split('-')[1], '%Y%m%d%H%M%S')
        # print(f"Processing jobset {jobset} - Time Difference: {time_difference} - {percent_complete:.2f}% complete [{'#' * progress + ' ' * (bar_length - progress)}]")
        print(f"{percent_complete:.2f}% complete [{'#' * progress + ' ' * (bar_length - progress)}]")
    else:
        # print(f"Processing jobset {jobset} - {percent_complete:.2f}% complete [{'#' * progress + ' ' * (bar_length - progress)}]")
        print(f"{percent_complete:.2f}% complete [{'#' * progress + ' ' * (bar_length - progress)}]")