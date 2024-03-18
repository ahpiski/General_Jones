#gpt generated 

def merge_time_periods(time_periods):
    time_dict = {}
    
    for period in time_periods:
        start, end = period.split('-')
        start_minutes = time_to_minutes(start)
        end_minutes = time_to_minutes(end)
        
        if start_minutes not in time_dict:
            time_dict[start_minutes] = 1
        else:
            time_dict[start_minutes] += 1
        
        if end_minutes not in time_dict:
            time_dict[end_minutes] = -1
        else:
            time_dict[end_minutes] -= 1
    
    merged_periods = []
    start_time = None
    open_periods = 0
    
    for time in sorted(time_dict.keys()):
        if open_periods == 0:
            start_time = time
        open_periods += time_dict[time]
        if open_periods == 0:
            merged_periods.append(minutes_to_time(start_time) + '-' + minutes_to_time(time))
    
    return merged_periods

def time_to_minutes(time_str):
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

def minutes_to_time(minutes):
    hours, mins = divmod(minutes, 60)
    return '{:02d}:{:02d}'.format(hours, mins)

# Example usage
#time_periods = ['11:20-12:30', '11:20-12:32']
#merged_periods = merge_time_periods(time_periods)
#print("Merged Time Periods:", merged_periods)

def No_clock_interference(period_list):
    return merge_time_periods(period_list)


def split_clocks(clocks):
    first_clocks = [clock.split('-')[0] for clock in clocks]
    second_clocks = [clock.split('-')[1] for clock in clocks]
    
    return first_clocks, second_clocks

