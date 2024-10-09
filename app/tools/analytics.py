# app/tools/analytics.py

from django.http import HttpRequest
from user_agents import parse
from ipware import get_client_ip
import geoip2.database
from .models import AnalyticsVisitorData


def collect_visitor_data(request: HttpRequest):
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_string)
    client_ip, _ = get_client_ip(request)

    visitor_data = AnalyticsVisitorData(
        source=request.META.get('HTTP_REFERER', 'Direct'),
        device=user_agent.device.family,
        browser=user_agent.browser.family,
        os=user_agent.os.family,
        country=get_country_from_ip(client_ip),
        ip_address=client_ip
    )
    visitor_data.save()


def get_country_from_ip(ip_address):
    # You'll need to download a GeoIP database file
    # and update the path accordingly
    reader = geoip2.database.Reader('D:\Knowledgehub\data\GeoLite2-Country.mmdb')
    try:
        response = reader.country(ip_address)
        return response.country.name
    except:
        return 'Unknown'