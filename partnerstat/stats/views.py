from django.shortcuts import render
from .models import Viewing
import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from .integration.etv_user_api.resources import UsersResourceClient
from hashlib import md5
from django.conf import settings
import urllib.request
from urllib.request import urlopen
from django.http import JsonResponse
import urllib.parse
from datetime import datetime

# Create your views here.

from .forms import ViewsSearchForm

def date_from_iso(d):
    return datetime.strptime(d, "%Y-%m-%dT%H:%M:%S").strftime("%d %b %Y %H:%M")

@login_required(login_url="/login/")
def index(request):
    latest_question_list = Viewing.objects.all()
    context = {'latest_question_list': latest_question_list}
    return render(request, 'stats/index.html', context)


@login_required(login_url="/login/")
def user_list_json(request):

    resource = UsersResourceClient()

    draw = request.GET.get('draw', 1)
    per_page = request.GET.get('length', 10)
    # domain = 1
    domain = 8
    start = request.GET.get('start', 0)

    page = int((int(start)/int(per_page)) + 1)
    params = {'domain': domain, 'per_page': per_page, 'page': page}

    search_value = request.GET.get('search[value]', None)
    if search_value:
        filter_by = request.GET.get('filterBy', 'username')
        params['search_option'] = filter_by
        params['search'] = search_value

    user_list = resource.get_objects(**params)

    resp = {}
    resp['draw'] = draw
    resp['recordsTotal'] = user_list['count']
    resp['recordsFiltered'] = user_list['count']
    resp['data'] = []

    for u in user_list['results']:

        print(u)

        x = {}
        x['id'] = u['id']
        x['username'] = u['username']
        x['last_name'] = u['last_name']
        x['first_name'] = u['first_name']
        x['plan_name'] = u['plan_name']
        x['plan_status'] = u['plan_status_name']
        x['email'] = u['email']
        x['date_joined'] = u['date_joined']
        x['date_joined_verbose'] = date_from_iso(u['date_joined'])

        resp['data'].append(x)

    response = JsonResponse(resp)
    return response

@login_required(login_url="/login/")
def user_views_json(request):

    def _gen_hash(*args):

        private_key = getattr(settings, 'CDN_STATS_PARTNER_KEY')
        ars = list((private_key,))
        ars.extend(args)
        st = ''.join([str(x).lower() for x in ars])
        ars.extend(st)
        st = md5(st.encode('utf-8')).hexdigest()
        return st

    start = request.GET.get('start', 0)
    draw = request.GET.get('draw', 1)
    page_size = request.GET.get('length', 10)
    page_number = int((int(start)/int(page_size)) + 1)

    id = request.GET.get('id', -1)
    # id = 123456

    partnerid = getattr(settings, 'CDN_STATS_PARTNER_ID')

    hashparam = _gen_hash(id, str(page_number), str(page_size))
    params = urllib.parse.urlencode({'partnerid': partnerid,
                                     'clientid': id,
                                     'pagenumber': page_number,
                                     'pagesize': page_size,
                                     'hashparam': hashparam})

    # views
    url = getattr(settings, 'CDN_STATS_URL') + '/user/DetailsJson?%s' % params

    # print(url)

    # views
    req = urllib.request.Request(url)

    try:
        connection = urlopen(req)
        resp = connection.read()
        connection.close()
        status = 200
    except urllib.error.HTTPError as err:

        if err.code == 400:
            resp = err.read()
            status = err.code
        else:
            raise

    # print(resp['items'])

    import json
    jresp = json.loads(resp.decode("utf-8"))

    metadata = jresp['metaData']

    draw = request.GET.get('draw', 1)

    resp = {}
    resp['draw'] = draw

    resp['recordsTotal'] = metadata['TotalItemCount']
    resp['recordsFiltered'] = metadata['TotalItemCount']
    resp['data'] = []

    items = jresp['items']

    for i in items:
        x = {}
        x['created_utc'] = date_from_iso(i['CreatedUtc'][:19])
        x['media_object_name'] = i['MediaObject']['Name'] if i['MediaObject'] else None
        x['media_packet_name'] = i['MediaPacket']['Name'] if i['MediaPacket'] else None
        x['bitrate_id'] = i['BitrateId']
        x['played_seconds'] = i['PlayedSecondsStr']
        x['client_ip'] = i['ClientIp']

        resp['data'].append(x)

    response = JsonResponse(resp)
    return response

def is_support(user):
    return user.groups.filter(name='support').exists()

@user_passes_test(is_support)
@login_required(login_url="/login/")
def user_list(request):

    return render(request, 'stats/user_list.html')

@user_passes_test(is_support)
@login_required(login_url="/login/")
def user_details(request, id):

    resource = UsersResourceClient()
    user_details =  resource.get_one_object(id)

    context = {}
    context['result'] = user_details
    context['date_joined'] = date_from_iso(user_details['date_joined'])
    context['last_login'] = date_from_iso(user_details['last_login'])

    return render(request, 'stats/user_details.html', context)


@login_required(login_url="/login/")
def search(request):

    rows = []

    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        views = Viewing.objects.all()

        # create a form instance and populate it with data from the request:
        form = ViewsSearchForm(request.POST)

        # check whether it's valid:
        if form.is_valid():

            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:

            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            threshold = form.cleaned_data['threshold']
            stream_type = form.cleaned_data['stream_type']

            if date_from:
                views = views.filter(date__gte=date_from)
            if date_to:
                views = views.filter(date__lte=date_to)
            if threshold:
                views = views.filter(threshold=threshold)

            def daterange(d1, d2):
                return (d1 + datetime.timedelta(days=i) for i in range((d2 - d1).days + 1))

            def seconds_to_hms(seconds):
                m, s = divmod(seconds, 60)
                h, m = divmod(m, 60)
                return "%d:%02d:%02d" % (h, m, s)
                # return "%d hour(s) %02d minute(s) %02d second(s)" % (h, m, s)

            for d in daterange(date_from, date_to):

                date = {'date': d}

                qd = views.filter(date=d,domain='actava')
                qs = qd.filter(stream_type=stream_type)

                if qs:
                    qs = qs[0]
                    date['total_user_qty'] = qs.user_qty
                    date['total_ips_qty'] = qs.ips_qty

                    date['total_streams_' + stream_type] = qs.total_streams

                    if qs != 'all':
                        date['total_streams_all'] = qs.total_streams

                        date['avg_played_seconds_' + stream_type] = seconds_to_hms(qs.avg_played_seconds)
                        date['max_played_seconds_' + stream_type] = seconds_to_hms(qs.max_played_seconds)
                        date['total_played_seconds_' + stream_type] = seconds_to_hms(qs.total_played_seconds)

                    date['avg_played_seconds_all'] = seconds_to_hms(qs.avg_played_seconds)
                    date['max_played_seconds_all'] = seconds_to_hms(qs.max_played_seconds)
                    date['total_played_seconds_all'] = seconds_to_hms(qs.total_played_seconds)

                    date['total_streams_percentage_' + stream_type] = '(100%)'

                else:
                    continue

                if stream_type == 'all':

                    for st in ['vod', 'live']:
                        qs = qd.filter(stream_type=st)

                        if qs:
                            qs = qs[0]
                            date['total_streams_' + st] = qs.total_streams

                            if date['total_streams_all'] > 0:
                                date['total_streams_percentage_' + st] = '(' + str(round((date['total_streams_' + st] / date['total_streams_all']) * 100,2)) + '%)'

                            date['avg_played_seconds_' + st] = seconds_to_hms(qs.avg_played_seconds)
                            date['max_played_seconds_' + st] = seconds_to_hms(qs.max_played_seconds)
                            date['total_played_seconds_' + st] = seconds_to_hms(qs.total_played_seconds)

                rows.append(date)


    # if a GET (or any other method) we'll create a blank form
    else:
        form = ViewsSearchForm()

    # form = ViewsSearchForm()
    return render(request, 'stats/search.html', {'form': form, 'rows': rows})