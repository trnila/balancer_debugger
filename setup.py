from widgets import Touch


def setup_charts(app):
    app.next_row()
    #plot(['RX', 'RY'], [0, 65535], colspan=2)
    #plot(['USX', 'USY'], [0, 0.1], colspan=2)
    app.plot(['nx', 'ny'], [-1, 1], colspan=2, title='normal')
    app.plot(['vx', 'vy'], [-1000, 1000], colspan=2, title='speed')

    app.next_row()
    app.plot(['nsx', 'nsy'], [-1, 1], colspan=2, title='normalized speed')

    p3 = app.win.addPlot(colspan=1, title="Touch resistance")
    p3.setXRange(0, 65535)
    p3.setYRange(0, 65535)

    app.charts.append(Touch(p3))