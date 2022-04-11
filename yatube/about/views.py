from django.views.generic import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get(self, request, *args, **kwargs):
        context = {
            'title': "Об авторе проекта"
        }
        return self.render_to_response(context)


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get(self, request, *args, **kwargs):
        context = {
            'title': "Технологии"
        }
        return self.render_to_response(context)
