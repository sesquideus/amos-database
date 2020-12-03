import io
import matplotlib
import django.http

from matplotlib import pyplot
from matplotlib.backends.backend_agg import FigureCanvasAgg

matplotlib.use('Agg')


class FigurePNGResponse(django.http.HttpResponse):
    def __init__(self, figure):
        canvas = FigureCanvasAgg(figure)
        buf = io.BytesIO()
        canvas.print_png(buf)
        pyplot.close(figure)

        super().__init__(buf.getvalue(), content_type='image/png')
        self['Content-Length'] = str(len(self.content))
