from datetime import datetime

class Log:
    @staticmethod
    def __init__(log_file, with_date, *values):
        value_list = list(values)
        if with_date == True:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            value_list.insert(0, now)
        value_list = [str(v) for v in value_list]
        with open(log_file, 'a') as f:
            f.write(','.join(value_list))
            f.write('\n')

if __name__ == "__main__":
    Log('aaa.log', True, 'aaa', 'bbb', '12', 23, None)