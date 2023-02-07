from requests import get
from datetime import datetime
from logging import getLogger
from traceback import format_exc
import plotly.express as px
import plotly.graph_objects as go
from CryptoCharts.src.config import pairs_to_show
from CryptoCharts.src.base import ContextMenuBase,\
    Singleton
from time import sleep
from threading import Thread
from json import load,\
    dump
from os import path
from decimal import Decimal

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

        final_from_tmstmp = from_tmstmp
        final_to_tmstmp = to_tmstmp
        infinex_response = []

        if use_cache:
            # bootstrap the current pair and resolution in the cache, if missing
            if self.pair not in self.cache.keys():
                self.cache[self.pair] = {}
            if self.res not in self.cache[self.pair].keys():
                self.cache[self.pair][self.res] = []

            # remove entries from the cache that are too old
            # for now only 50 entries will be kept in the cache, which may not be the best clean-up mechanism,
            # but it will suffice for now
            self.cache[self.pair][self.res] = self.cache[self.pair][self.res][-50:]

            ### check if data from the cache can be used ###
            for cached_response_descriptor in self.cache[self.pair][self.res]:

                # if the to_timestamp is not before from_timestamp, meaning the call is not too old
                if cached_response_descriptor['to_tmstmp'] > final_from_tmstmp:

                    valid_added = False
                    for entry in cached_response_descriptor['data']:
                        # if valid entries are found grab them from the cache
                        if final_from_tmstmp <= int(entry['time'].split('.')[0]) <= final_to_tmstmp:
                            infinex_response.append(entry)
                            valid_added = True
                    if valid_added: # only if a valid entry wad added previously
                        final_from_tmstmp = min(cached_response_descriptor['to_tmstmp'], final_to_tmstmp)

            cache_hit_unit = ((to_tmstmp-from_tmstmp) - (final_to_tmstmp-final_from_tmstmp)) / (to_tmstmp-from_tmstmp)
            self._log.info(f'Disk cache hit: {round(cache_hit_unit*100, 4)}%')

        # only call the PI if the cache does not have all the data
        if final_from_tmstmp != final_to_tmstmp:
            final_infinex_response = get('https://api.infinex.cc//spot/candlestick',
                                   json={"pair": self.pair,
                                         "res": self.res,
                                         "from": final_from_tmstmp,
                                         "to": final_to_tmstmp}).json()['candlestick']
            infinex_response += final_infinex_response
            self.cache[self.pair][self.res].append({'from_tmstmp': final_from_tmstmp,
                                                    'to_tmstmp': final_to_tmstmp,
                                                    'delta_timestamps': final_to_tmstmp-final_from_tmstmp,
                                                    'data': final_infinex_response})
        else:
            if use_cache:
                self._log.info('Fully served from the disk cache !')
            else:
                self._log.warning('from_timestamp is the same as to_timestamp. Was that on purpose !?')

        return [{'local_time': datetime.fromtimestamp(int(entry['time'].split('.')[0])),
                 'close_price': float(entry['close'])} for entry in infinex_response]

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

class BuildPlotlyHTML(ContextMenuBase):

    _log: getLogger()

    def get_plotly_html_graph(self,
                              x,
                              y,
                              title,
                              coin):

        self._log.info('Received graph to html code conversion request for {}'.format(title))

        minimum = {'index': x[y.index(min(y))],
                   'value': min(y)}
        maximum = {'index': x[y.index(max(y))],
                   'value': max(y)}
        current = {'index': x[-1],
                   'value': y[-1]}

        fig = px.line(x=x,
                      y=y,
                      title=title,
                      labels=dict(x="time", y="value"),
                      render_mode='svg', # webgl would be more fluid, but that may break the webgl contexts limit
                      )

        # disable zoom and dragmode
        fig['layout'][f'xaxis1']['fixedrange'] = True
        fig['layout'][f'yaxis1']['fixedrange'] = True
        fig['layout']['dragmode'] = False

        # disable the automatic number formatting
        # may not be the most slick implementation, but it does the job well :)
        fig['layout'][f'yaxis1']['tickformat'] = f".{max([abs(Decimal(str(_)).as_tuple().exponent) for _ in y])}f"

        ### add a horizontal line, if configured ###
        # small overhead loading the file over and over again, but implementing
        # a cache manager for this would be overkill, currently ...
        if path.isfile('horizontal_lines.json'):
            with open('horizontal_lines.json', 'r') as hor_lines_in_handle:
                self.hor_lines = load(hor_lines_in_handle)
            if self.hor_lines[coin]:
                fig.add_hline(y=self.hor_lines[coin])

        if current['value'] != maximum['value']:
            fig.add_trace(go.Scatter(x=[current['index'], current['index']],
                                     y=[current['value'], maximum['value']],
                                     mode="lines+markers+text",
                                     text=["", str(round(current['value']/maximum['value'],2))],
                                     textposition="top center",
                                     name='down',
                                     marker_color='red'
                                     ))

        if current['value'] != minimum['value']:
            fig.add_trace(go.Scatter(x=[current['index'], current['index']],
                                     y=[current['value'], minimum['value']],
                                     mode="lines+markers+text",
                                     text=["", str(round(current['value']/minimum['value'],2))],
                                     textposition="bottom center",
                                     name='up',
                                     marker_color='green'
                                     ))

        return fig.to_html(include_plotlyjs=False)

class CryptoCharts(metaclass=Singleton):

    def __init__(self):
        self._log = getLogger()

    def return_final_html(self):

        try:
            final_html_code = '''
                                <table>
                              '''

            for pair in pairs_to_show.items():
                final_html_code += '<tr>'
                for input in pair[1]:
                    final_html_code += '<th>'
                    final_html_code += 'Graph age: ' + str(datetime.now() - self.shared_cache[input['title']]['date_created'])
                    final_html_code += '<br>'
                    final_html_code += self.shared_cache[input['title']]['plotly_graph']
                    final_html_code += '</th>'
                final_html_code += '</tr>'
            final_html_code += '''
                                </table>
                               '''

            return final_html_code
        except:
            self._log.error('Error found:\n{}'.format(format_exc(chain=False)))
            return '<p> ERROR </p>'

    def return_final_html_external(self,
                                   pairs_to_show):

        try:
            final_html_code = '''
                                <table>
                              '''

            for pair in pairs_to_show.items():
                final_html_code += '<tr>'
                for input in pair[1]:
                    with globals()['APIwrapper{}'.format(input['platform'])]() as do:
                        API_out = do.get(**input['method_args'])

                    x_to_send = [entry['local_time'] for entry in API_out]
                    y_to_send = [entry['close_price'] for entry in API_out]
                    x_to_send.reverse()
                    y_to_send.reverse()

                    with BuildPlotlyHTML() as do:

                        plotly_code = do.get_plotly_html_graph(x=x_to_send,
                                                               y=y_to_send,
                                                               title=input['title'],
                                                               coin=pair[0])

                    final_html_code += '<th>{graph_code}</th>'.format(graph_code=plotly_code)
                final_html_code += '</tr>'
            final_html_code += '''
                                </table>
                               '''

            return final_html_code
        except:
            self._log.error('Error found:\n{}'.format(format_exc(chain=False)))
            return '<p> ERROR </p>'

class slave_cache_manager(ContextMenuBase,
                          metaclass=Singleton):
    def __init__(self):
        super(slave_cache_manager, self).__init__()
        sleep(2) # allow the django server to fully start

    def do(self):
        for pair in pairs_to_show.items():
            for input in pair[1]:
                try:
                    with globals()['APIwrapper{}'.format(input['platform'])]() as do:
                        API_out = do.get(**input['method_args'])

                    x_to_send = [entry['local_time'] for entry in API_out]
                    y_to_send = [entry['close_price'] for entry in API_out]
                    if input['reverse']:
                        x_to_send.reverse()
                        y_to_send.reverse()

                    with BuildPlotlyHTML() as do:

                        plotly_code = do.get_plotly_html_graph(x=x_to_send,
                                                               y=y_to_send,
                                                               title=input['title'],
                                                               coin=pair[0])
                    self.shared_cache[input['title']] = {'plotly_graph': plotly_code,
                                                         'date_created': datetime.now()}
                except:
                    # only add the exception text if the last stored result was also an exception
                    # reason: if the last response was valid and the current response threw an exception, keep the previous valid response
                    exception_html_code = f"{ input['title'] }<br>ERROR"

                    add_flag = False
                    if input['title'] in self.shared_cache.keys():
                        if self.shared_cache[input['title']] == exception_html_code:
                            add_flag = True
                    else:
                        add_flag = True
                    if add_flag: self.shared_cache[input['title']] = {'plotly_graph': exception_html_code,
                                                                      'date_created': datetime.now()}

                    self._log.error(format_exc(chain=False))

class initial_actions():
    def __init__(self):
        if path.isfile('horizontal_lines.json'):
            with open('horizontal_lines.json', 'r') as hor_lines_in_handle:
                try:
                    self.hor_lines = load(hor_lines_in_handle)
                except:
                    self.hor_lines = {}
        else:
            self.hor_lines = {}

        for configured_pair in pairs_to_show.keys():
            if configured_pair not in self.hor_lines.keys():
                self.hor_lines[configured_pair] = 0

        with open('horizontal_lines.json', 'w') as hor_lines_out_handle:
            dump(self.hor_lines, hor_lines_out_handle, indent=2)

class worker_daemon_thread(metaclass=Singleton):

    def starter_wrapper(self,
                        obj,
                        cycle_sleep_s:int):
        while True:
            with obj() as init_obj:
                init_obj.do()
            sleep(cycle_sleep_s)

    def start_all_threads(self):
        for ContextClass in [{'obj': slave_cache_manager,
                              'cycle_sleep_s': 45*60}
                             ]:
            Thread(target=self.starter_wrapper, kwargs={**ContextClass}).start()

        initial_actions()