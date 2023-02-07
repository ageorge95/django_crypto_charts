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
