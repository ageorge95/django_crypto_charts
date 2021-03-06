from time import time

pairs_to_show = {
                'BTC': [{'platform_link': 'https://www.xt.com/tradePro/btc_usdt',
                         'platform': 'XT',
                         'method_args': {'pair': 'btc_usdt',
                                         'period_s': '1min'},
                         'title': 'BTC short __ btc_usdt __ 6 HOURS',
                         'reverse': True},
                         {'platform_link': 'https://www.xt.com/tradePro/btc_usdt',
                          'platform': 'XT',
                          'method_args': {'pair': 'btc_usdt',
                                          'period_s': '1day'},
                          'title': 'BTC long __ btc_usdt __ 10 MONTHS',
                         'reverse': True}],
                'HDD': [
                       {'platform_link': 'https://www.xt.com/tradePro/hdd_usdt',
                        'platform': 'XT',
                        'method_args': {'pair': 'hdd_usdt',
                                        'period_s': '1min'},
                        'title': 'HDD short __ hdd_usdt __ 6 HOURS',
                         'reverse': True},
                        {'platform_link': 'https://www.xt.com/tradePro/hdd_usdt',
                         'platform': 'XT',
                         'method_args': {'pair': 'hdd_usdt',
                                         'period_s': '1day'},
                         'title': 'HDD long __ hdd_usdt __ 10 MONTHS',
                         'reverse': True},
                        ],
                'XCH': [
                       {'platform_link': 'https://www.xt.com/tradePro/xch_usdt',
                        'platform': 'XT',
                        'method_args': {'pair': 'xch_usdt',
                                        'period_s': '1min'},
                        'title': 'XCH short __ xch_usdt __ 6 HOURS',
                         'reverse': True},
                        {'platform_link': 'https://www.xt.com/tradePro/xch_usdt',
                         'platform': 'XT',
                         'method_args': {'pair': 'xch_usdt',
                                         'period_s': '1day'},
                         'title': 'XCH long __ xch_usdt __ 10 MONTHS',
                         'reverse': True}
                ],
                'SIT': [
                       {'platform_link': 'https://trade.citex.co.kr/trade/SIT_USDT',
                        'platform': 'CITEX',
                        'method_args': {'pair': 'sit_usdt',
                                        'period_m': 3, # 1 does not work as of 21 Mar 2022
                                        'size': 120},
                        'title': 'SIT short __ sit_usdt __ 6 HOURS',
                         'reverse': True},
                        {'platform_link': 'https://trade.citex.co.kr/trade/SIT_USDT',
                         'platform': 'CITEX',
                         'method_args': {'pair': 'sit_usdt',
                                         'period_m': 1440,
                                         'size': 300},
                         'title': 'SIT long __ sit_usdt __ 10 MONTHS',
                         'reverse': True},
                ],
                'XCC': [
                    {'platform_link': 'https://www.lbank.info/exchange/xcc/usdt',
                     'platform': 'LBANK',
                     'method_args': {'symbol': 'xcc_usdt',
                                     'size': 360,
                                     'type': 'minute1',
                                     'timestamp': (lambda : int(time()) - 360*60)()},
                     'title': 'XCC short __ xcc_usdt __ 6 HOURS',
                     'reverse': False},
                    {'platform_link': 'https://www.lbank.info/exchange/xcc/usdt',
                     'platform': 'LBANK',
                     'method_args': {'symbol': 'xcc_usdt',
                                     'size': 300,
                                     'type': 'day1',
                                     'timestamp': (lambda : int(time()) - 300*24*60*60)()},
                     'title': 'XCC long __ xcc_usdt __ 10 MONTHS',
                     'reverse': False},
                ]}