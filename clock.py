#gpt generated 
from datetime import datetime
import pytz

tzone = "Asia/Tehran"

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

def reduce_rime(time , min):
    hour,minute = map(int, time.split(':'))
    minutes = (60 * hour) + minute - min
    if (minutes < 0) : minutes = minutes + (24*60)
    minute = minutes % 60
    hour = (minutes - minute) / 60
    return  hour , minute

def is_time_in_period(period_str):
    time_str = datetime.now(pytz.timezone(tzone)).strftime('%H:%M')
    time_format = '%H:%M'
    time = datetime.strptime(time_str, time_format)
    start_str, end_str = period_str.split('-')
    start_time = datetime.strptime(start_str, time_format)
    end_time = datetime.strptime(end_str, time_format)
    iran_timezone = pytz.timezone('Asia/Tehran')
    time = iran_timezone.localize(time)
    start_time = iran_timezone.localize(start_time)
    end_time = iran_timezone.localize(end_time)
    return start_time <= time <= end_time