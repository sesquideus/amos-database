from django.shortcuts import render
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from django.http import JsonResponse

# Create your views here.

class JSONDetailView(BaseDetailView):
    def get_context_data(self, **kwargs):
        try:
            return self.get_object().json()
        except AttributeError as e:
            raise NotImplementedError(f"Model {self.model.__name__} does not provide a json() method")

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)


class JSONListView(BaseListView):
    def get_context_data(self, **kwargs):
        try:
            return {obj.id: obj.json() for obj in self.get_queryset()}
        except AttributeError as e:
            raise NotImplementedError(f"Model {self.model.__name__} does not provide a json() method")

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)


def about(request):
    return render(request, 'core/about.html', {})

