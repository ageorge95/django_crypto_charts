from time import sleep

class CryptoCharts():
    def return_html_code(self):
        # Using plotly.express
        import plotly.express as px
        import plotly.graph_objects as go

        df = px.data.stocks()
        list_to_print = list(df['GOOG'])

        minimum = {'index': list_to_print.index(min(list_to_print)),
                   'value': min(list_to_print)}
        maximum = {'index': list_to_print.index(max(list_to_print)),
                   'value': max(list_to_print)}
        current = {'index': len(list_to_print)-1,
                   'value': list_to_print[-1]}

        fig = px.line(list_to_print)

        if current['value'] != maximum['value']:
            fig.add_trace(go.Scatter(x=[current['index'], current['index']],
                                     y=[current['value'], maximum['value']],
                                     mode="lines+markers+text",
                                     text=["", "maximum text"],
                                     textposition="top center"
                                     ))
            # fig.add_annotation(x=current['index'], y=maximum['value'],
            #                    text="maximum text",
            #                    showarrow=True,
            #                    arrowhead=1)

        if current['value'] != minimum['value']:
            fig.add_trace(go.Scatter(x=[current['index'], current['index']],
                                     y=[current['value'], minimum['value']],
                                     mode="lines+markers+text",
                                     text=["", "minimum text"],
                                     textposition="bottom center"
                                     ))
            # fig.add_annotation(x=current['index'], y=minimum['value'],
            #                    text="minimum text",
            #                    showarrow=True,
            #                    arrowhead=1)

        return ''''
        <table>
          <tr>
            <th>{graph_code1}</th>
            <th>{graph_code2}</th>
          </tr>
        </table>
        '''.format(graph_code1=fig.to_html(include_plotlyjs=False),
                   graph_code2=fig.to_html(include_plotlyjs=False))
