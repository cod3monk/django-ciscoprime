from django.views.generic import TemplateView
from django.conf import settings

from braces.views import LoginRequiredMixin
import requests
import pprint

from .utils import api_request


class OverviewView(TemplateView):
    template_name = 'main/overview.html'

    def get_context_data(self, **kwargs):
        context = super(OverviewView, self).get_context_data(**kwargs)
        #controller summary
        context['ctrl'] = dict()
        context['ctrl']['response'] = api_request(
            'https://140.221.243.254/webacs/api/v1/data/WlanControllers/2285283/.json')
        if context['ctrl']['response'].get('json_response'):
            context['ctrl']['entity'] = context['ctrl']['response']['json_response']['queryResponse']['entity'][0]

        #client count
        context['clients'] = dict()
        context['clients']['response'] = api_request(
            'https://140.221.243.254/webacs/api/v1/data/Clients.json?status="ASSOCIATED"')
        if context['clients']['response'].get('json_response'):
            context['clients']['count'] = context['clients']['response']['json_response']['queryResponse']['@count']

        #ap stats
        context['ap'] = dict()
        r = api_request(
            'https://140.221.243.254/webacs/api/v1/data/AccessPoints.json?.sort=-clientCount')
        if r.get('json_response'):
            most_clients_ap_id = r['json_response']['queryResponse']['entityId'][0]['$']
            r2 = api_request(
            'https://140.221.243.254/webacs/api/v1/data/AccessPoints/%d.json' % int(most_clients_ap_id))
            if r2.get('json_response'):
                context['ap']['highest_client_count'] = r2['json_response']['queryResponse']['entity'][0]['accessPointsDTO']
        return context


class ApiCallView(LoginRequiredMixin, TemplateView):
    template_name = 'main/api_call.html'

    def get_context_data(self, **kwargs):
        context = super(ApiCallView, self).get_context_data(**kwargs)
        if self.request.GET.get('url'):
            context['request_url'] = self.request.GET.get('url')
        elif self.request.GET.get('query'):
            context['request_url'] = 'https://140.221.243.254/webacs/api/v1/%s.json' % self.request.GET['query']
            if self.request.GET.get('params'):
                context['request_url'] += self.request.GET.get('params')
        if context.get('request_url'):
            r = requests.get(
                context['request_url'],
                verify=False,
                auth=(settings.API_USER, settings.API_PASSWORD))
            try:
                context['response'] = r.json()
            except ValueError:
                context['response'] = r.content
            pp = pprint.PrettyPrinter(indent=4)
            context['pprint_json'] = pp.pformat(context['response'])
        return context
