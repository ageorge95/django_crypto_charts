from requests import get
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from main._02_config import pairs_to_show

class CryptoCharts():

    def get_from_XT(self,
                    pair,
                    period_s):

        XT_response = get('https://www.xt.pub/exchange/api/markets/returnChartData?currencyPair={pair}&period={period_s}'.format(pair=pair,
                                                                                                                                 period_s=period_s)).json()
        return [{'local_time': datetime.fromtimestamp(entry['date']/1000),
                 'close_price': entry['close']} for entry in XT_response]

    def transform_to_plotly_html(self,
                                 x,
                                 y,
                                 title):

        minimum = {'index': x[y.index(min(y))],
                   'value': min(y)}
        maximum = {'index': x[y.index(max(y))],
                   'value': max(y)}
        current = {'index': x[-1],
                   'value': y[-1]}

        fig = px.line(x=x,
                      y=y,
                      title=title,
                      labels=dict(x="time", y="value"))

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
                                     marker_color='green'))

        return fig.to_html(include_plotlyjs=False)

    def return_html_code(self):

        final_html_code = '''
                            <table>
                          '''

        for pair in pairs_to_show.items():
            final_html_code += '<tr>'
            for input in pair[1]:
                API_out = getattr(self, 'get_from_{}'.format(input['platform']))(**input['method_args'])

                x_to_send = [entry['local_time'] for entry in API_out]
                y_to_send = [entry['close_price'] for entry in API_out]
                x_to_send.reverse()
                y_to_send.reverse()

                plotly_code = self.transform_to_plotly_html(x=x_to_send,
                                                            y=y_to_send,
                                                            title=input['title'])

                final_html_code += '<th>{graph_code}</th>'.format(graph_code=plotly_code)
            final_html_code += '</tr>'
        final_html_code += '''
                            </table>
                           '''

        return final_html_code