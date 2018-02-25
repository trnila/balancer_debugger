from widgets import Touch


def setup_charts(app):
    app.next_row()
    app.plot(['nx', 'ny'], [-1, 1], colspan=2, title='normal')
    app.plot(['vx', 'vy'], [-20, 20], colspan=2, title='speed')

    #p3 = app.win.addPlot(colspan=1, title="Normal")
    #p3.setXRange(-0.3, 0.3)
    #p3.setYRange(-0.3, 0.3)
    #app.charts.append(Touch(p3, ['nx', 'ny'], lastPoints=10))
    p3 = app.win.addPlot(colspan=1, title="resistence")
    p3.setXRange(0, 65000)
    p3.setYRange(0, 65000)
    app.charts.append(Touch(p3, ['RX', 'RY'], lastPoints=10))

    app.next_row()
    app.plot(['cx', 'cy'], [-1, 1], colspan=2, title='change')
    app.plot(['USX', 'USY'], [0.060, 0.090], colspan=2, title='USX/USY')

    p3 = app.win.addPlot(colspan=1, title="position")
    p3.setXRange(0, 300)
    p3.setYRange(0, 300)
    app.charts.append(Touch(p3, ['posx', 'posy']))

