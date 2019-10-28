import argparse

GWEI_FACTOR = 1000000000
ETH_FACTOR = 10 ** 18
ETH_USD_EXCHANGE = 200

def to_wei(val, unit = 'ether'):
    if unit == 'ether':
        return val * ETH_FACTOR
    elif unit == 'gwei':
        return val * GWEI_FACTOR
    else:
        raise Exception('unknown unit')

def from_wei(val, unit = 'ether'):
    if unit == 'ether':
        return val / ETH_FACTOR
    elif unit == 'gwei':
        return val / GWEI_FACTOR
    else:
        raise Exception('unknown unit')

def format_value_str(val, unit = 'ether'):
    eth = from_wei(val, 'ether')
    usd = eth * ETH_USD_EXCHANGE

    return '{} {} (${})'.format('%.10f' % from_wei(val, unit), unit, '%.10f' % usd)

def pixels_in_rendition(width, height, fps, num_streams, duration):
    return width * height * fps * num_streams * duration

def ticket_params(ev, gas_price, gas_cost):
    tx_cost = gas_price * gas_cost
    face_value = tx_cost / tx_overhead
    win_prob = ev / face_value
    tickets_to_win = int(1 // win_prob)

    print('Transaction cost to redeem a ticket:', format_value_str(tx_cost, 'ether'))
    print('Ticket face value:', format_value_str(face_value, 'ether'))
    print('Ticket winning probability: {0:.15f}'.format(win_prob))
    print('1 out of {} tickets will win'.format(tickets_to_win))

    return face_value, win_prob, tickets_to_win

gas_cost = 100000
tx_overhead = .01

def print_defaults():
    print('DEFAULTS')
    print('---------')
    print('Ticket redemption gas cost:', gas_cost)
    print('Transaction cost overhead:', tx_overhead)

def prompt_ev():
    ev = to_wei(float(input('Enter the desired ticket expected value (gwei): ')), 'gwei')
    print('Ticket expected value: {} gwei'.format(from_wei(ev, 'gwei')))

    return ev

def prompt_gas_price():
    gas_price = to_wei(float(input('Enter the gas price (gwei) to use for ticket redemption transactions: ')), 'gwei')
    print('Ticket redemption gas price: {} gwei'.format(from_wei(gas_price, 'gwei')))

    return gas_price

def prompt_pixels_per_hour():
    pixels_per_hour = 0

    while True:
        usr_in = input('Would you like to add a rendition to be encoded? (y/n): ')
        if usr_in != 'y' and usr_in != 'n':
            print('Please enter y or n')
            continue
        
        if usr_in == 'n':
            break

        width, height, fps, num_streams = prompt_rendition()
        pixels_per_hour += pixels_in_rendition(width, height, fps, num_streams, 3600)

    return pixels_per_hour

def prompt_rendition():
    width = int(input('Enter the output width: '))
    height = int(input('Enter the output height: '))
    fps = float(input('Enter the output FPS (frames per second): '))
    num_streams = int(input('Ether the number of streams of this renditions: '))

    return width, height, fps, num_streams

def calc_target_hours_to_win():
    print_defaults()

    print('\n')

    ev = prompt_ev()

    print('\n')

    gas_price = prompt_gas_price()

    print('\n')

    face_value, win_prob, tickets_to_win = ticket_params(ev, gas_price, gas_cost)

    print('\n')

    hours_to_win = float(input('Enter the desired number of hours (i.e. 1, .5, etc.) until receiving a winning ticket: '))

    print('\n')

    pixels_per_hour = prompt_pixels_per_hour()

    print('\n')

    tickets_per_hour = tickets_to_win / float(hours_to_win)
    value_per_hour = tickets_per_hour * ev
    price_per_pixel = (tickets_per_hour * ev) / float(pixels_per_hour)

    print('Given the specified renditions you will and a target of 1 winning ticket every {} hours you will: '.format(hours_to_win))
    print('Need to charge {} wei per pixel'.format(price_per_pixel))
    print('Encode {} pixels per hour'.format(pixels_per_hour))
    print('Receive {} tickets per hour'.format(tickets_per_hour))
    print('Receive {} (in terms of ticket expected value) per hour'.format(format_value_str(value_per_hour, 'ether')))

def calc_find_hours_to_win():
    print_defaults()

    print('\n')

    ev = to_wei(float(input('Enter the desired ticket expected value (gwei): ')), 'gwei')

    print('\n')

    gas_price = prompt_gas_price()

    print('\n')

    face_value, win_prob, tickets_to_win = ticket_params(ev, gas_price, gas_cost)

    print('\n')

    num_orchs = int(input('Enter the number of active orchestrators: '))
    suggested_reserve_alloc = face_value
    suggested_reserve = suggested_reserve_alloc * num_orchs
    print('Suggested broadcaster reserve:', format_value_str(suggested_reserve, 'ether'))

    print('\n')

    price_per_pixel = int(input('Enter the price per pixel (wei) to charge: '))
    print('Price per pixel: {} wei'.format(price_per_pixel))

    print('\n')

    pixels_per_hour = prompt_pixels_per_hour() 

    print('\n')

    tickets_per_hour = int((pixels_per_hour * price_per_pixel) // ev)
    value_per_hour = tickets_per_hour * ev
    hours_to_win = tickets_to_win / float(tickets_per_hour)

    print('Given the specified renditions you will:')
    print('Encode {} pixels per hour'.format(pixels_per_hour))
    print('Receive {} tickets per hour'.format(tickets_per_hour))
    print('Receive {} (in terms of ticket expected value) per hour'.format(format_value_str(value_per_hour, 'ether')))
    print('Receive 1 winning ticket every {} hours'.format(hours_to_win))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--find-hours-to-win', help='find hours to win', action='store_true')
    parser.add_argument('-t', '--target-hours-to-win', help='target hours to win', action='store_true')

    args = parser.parse_args()

    if args.find_hours_to_win:
        calc_find_hours_to_win()
    elif args.target_hours_to_win:
        calc_target_hours_to_win()
    else:
        print('must pass in either --find-hours-to-win (-f) or --target-hours-to-win (-t)')