from datetime import datetime
from logging import getLogger
from time import sleep
from requests import get
from CryptoCharts.src.utils import ContextMenuBase

class APIwrapperLBANK(ContextMenuBase):
    _log: getLogger()

    def get(self,
            symbol,
            size,
            API_type,
            timestamp):
        self._log.warning(f'This APIwrapper ({type(self).__name__}) is not highly optimised - please do not configure many pairs with it.')

        self._log.info(f"Received symbol {symbol}, size {size} and API_type {API_type} since timestamp {timestamp()}.")

        API_request = f"https://api.lbank.info/v2/kline.do?symbol={symbol}&size={size}&type={API_type}&time={timestamp()}"
        self._log.info('Sending API request: {}'.format(API_request))
        lbank_response = get(API_request).json()['data']

        return [{'local_time': datetime.fromtimestamp(entry[0]),
                 'close_price': float(entry[4])} for entry in lbank_response]


class APIwrapperCITEX(ContextMenuBase):
    _log: getLogger()

    def get(self,
            pair,
            period_m,
            size):

        self._log.warning(f'This APIwrapper ({type(self).__name__}) is not highly optimised - please do not configure many pairs with it.')

        self._log.info('Received pair {}, period_s {} and size {}.'.format(pair,
                                                                           period_m,
                                                                           size))

        API_request = 'https://api.citex.co.kr/v1/common/candlestick?symbol={pair}&type={period_m}&size={size}'.format(pair=pair,
                                                                                                                       period_m=period_m,
                                                                                                                       size=size)
        self._log.info('Sending API request: {}'.format(API_request))
        citex_response = get(API_request).json()

        return [{'local_time': datetime.fromtimestamp(entry[0]/1000),
                 'close_price': float(entry[4])} for entry in citex_response]


class APIwrapperXT(ContextMenuBase):
    _log: getLogger()

    def get(self,
            pair,
            period_s):

        self._log.warning(f'This APIwrapper ({type(self).__name__}) is not highly optimised - please do not configure many pairs with it.')

        self._log.info('Received pair {} and period_s {}.'.format(pair,
                                                                  period_s))

        API_request = 'https://sapi.xt.com/v4/public/kline?symbol={pair}&interval={period_s}'.format(pair=pair,
                                                                                                     period_s=period_s)
        self._log.info('Sending API request: {}'.format(API_request))
        XT_response = get(API_request).json()
        XT_response_data = XT_response['result']

        return [{'local_time': datetime.fromtimestamp(int(entry['t'])/1000),
                 'close_price': float(entry['c'])} for entry in XT_response_data]


class APIwrapperINFINEX(ContextMenuBase):

    _log: getLogger()

    def send_API_call(self,
                      from_tmstmp,
                      to_tmstmp,
                      use_cache = True):

        final_infinex_response = get('https://api.infinex.cc//spot/candlestick',
                                     json={"pair": self.pair,
                                           "res": self.res,
                                           "from": from_tmstmp,
                                           "to": to_tmstmp}).json()['candlestick']

        return [{'local_time': datetime.fromtimestamp(int(entry['time'].split('.')[0])),
                 'close_price': float(entry['close'])} for entry in final_infinex_response]

    def get(self,
            pair,
            res,
            from_tmstmp,
            to_tmstmp):

        self.pair = pair
        self.res = res
        from_tmstmp = from_tmstmp()
        to_tmstmp = to_tmstmp()

        self._log = getLogger()

        self._log.info(f"Received pair {pair}, resolution {res} and since timestamp {from_tmstmp} up until {to_tmstmp}.")

        # compute if multiple API calls are needed
        # Infinex can return 500 max records per API call
        if res == '1': # 1 minute
            if (to_tmstmp - from_tmstmp)/60 > 500:
                to_return = []
                while (from_tmstmp + 500*60) < to_tmstmp:
                    self._log.info(f'Sending API request with a data payload for a part of the timestamp: {from_tmstmp} -> {from_tmstmp + 500*60}...')

                    to_return += self.send_API_call(from_tmstmp=from_tmstmp,
                                                    to_tmstmp=from_tmstmp + 500*60)

                    from_tmstmp += 500*60
                    sleep(1) # some waiting between multiple API calls is always needed

                self._log.info(f'Sending API request with a data payload for the last part of the timestamp: {from_tmstmp} -> {to_tmstmp}...')

                to_return += self.send_API_call(from_tmstmp=from_tmstmp,
                                                to_tmstmp=to_tmstmp)

                return to_return

            else:
                self._log.info('Sending API request with a data payload for the whole timestamp period...')

                return self.send_API_call(from_tmstmp=from_tmstmp,
                                          to_tmstmp=to_tmstmp)

        if res == '1D': # 1 day
            if (to_tmstmp - from_tmstmp)/60/60/24 > 500:
                to_return = []
                while (from_tmstmp + 500*60*60*24) < to_tmstmp:
                    self._log.info(f'Sending API request with a data payload for a part of the timestamp: {from_tmstmp} -> {from_tmstmp + 500*60*60*24}...')

                    to_return += self.send_API_call(from_tmstmp=from_tmstmp,
                                                    to_tmstmp=from_tmstmp + 500*60*60*24)

                    from_tmstmp += 500*60*60*24
                    sleep(1) # some waiting between multiple API calls is always needed

                self._log.info(f'Sending API request with a data payload for a the last part of the timestamp: {from_tmstmp} -> {to_tmstmp}...')

                to_return += self.send_API_call(from_tmstmp=from_tmstmp,
                                                to_tmstmp=to_tmstmp + 500*60*60*24)

                return to_return

            else:
                self._log.info('Sending API request with a data payload for the whole timestamp period...')

                return self.send_API_call(from_tmstmp=from_tmstmp,
                                          to_tmstmp=to_tmstmp)
