from widgets import Touch
import pyqtgraph as pg


def setup_charts(app):
    app.next_row()
#    app.plot(['nx', 'ny'], [-1, 1], colspan=2, title='normal')
    app.plot(['posx', 'posy'], [0, 300], colspan=2, title='pos')
    app.plot(['vx', 'vy'], [-20, 20], colspan=2, title='speed')
    app.plot(['rax', 'ray'], [-2, 2], colspan=2, title='acceleration')

    #p3 = app.win.addPlot(colspan=1, title="Normal")
    #p3.setXRange(-0.3, 0.3)
    #p3.setYRange(-0.3, 0.3)
    #app.charts.append(Touch(p3, ['nx', 'ny'], lastPoints=10))

   
    p3 = app.win.addPlot(colspan=1, title="resistence")
    p3.setXRange(0, 4500)
    p3.setYRange(0, 4500)
    app.charts.append(Touch(p3, ['rx', 'ry'], lastPoints=10))

    app.next_row()
    app.plot(['rawx', 'rawy'], [0, 4000], colspan=2, title='raw')
    app.plot(['cx', 'cy'], [-1, 1], colspan=2, title='change')
    app.plot(['usx', 'usy'], [500, 1500], colspan=2, title='USX/USY')

    p3 = app.win.addPlot(colspan=1, title="position")
    p3.setXRange(0, 300)
    p3.setYRange(0, 300)
    app.charts.append(Touch(p3, ['posx', 'posy']))

    roi = pg.RectROI([0, 0], [170, 230], pen=(0, 9))
    p3.addItem(roi)

