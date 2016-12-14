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
import json
import pytz
from .forms import ViewsSearchForm
from django.http import Http404


def date_from_iso(d):
    return datetime.datetime.strptime(d, "%Y-%m-%dT%H:%M:%S").strftime("%d %b %Y %H:%M:%S")


def date_from_iso_utc_to_eastern(d):
    return utc_to_eastern(datetime.datetime.strptime(d, "%Y-%m-%dT%H:%M:%S")).strftime("%d %b %Y %H:%M:%S")


def utc_to_eastern(dt):
    gmt = pytz.timezone('GMT')
    eastern = pytz.timezone('US/Eastern')
    dategmt = gmt.localize(dt)
    dateeastern = dategmt.astimezone(eastern)
    return dateeastern

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

    params = {}
    if request.user.userprofile:
        domain = request.user.userprofile.domain
        params['domain'] = domain

    start = request.GET.get('start', 0)

    page = int((int(start)/int(per_page)) + 1)
    params.update({'per_page': per_page, 'page': page})

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


def _gen_hash(*args):
    private_key = getattr(settings, 'CDN_STATS_PARTNER_KEY')
    ars = list((private_key,))
    ars.extend(args)
    st = ''.join([str(x).lower() for x in ars])
    ars.extend(st)
    st = md5(st.encode('utf-8')).hexdigest()
    return st


@login_required(login_url="/login/")
def show_ts(request):

    stream_id = request.GET['id']
    partnerid = getattr(settings, 'CDN_STATS_PARTNER_ID')
    hashparam = _gen_hash(stream_id)
    params = urllib.parse.urlencode({'partnerid': partnerid,
                                     'streamid': stream_id,
                                     'hashparam': hashparam})

    # views
    url = getattr(settings, 'CDN_STATS_URL') + '/StreamDetail/DetailsJson?%s' % params

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

    jresp = json.loads(resp.decode("utf-8"))

    context = {'resp': jresp}
    return render(request, 'stats/show_ts.html', context)


@login_required(login_url="/login/")
def user_views_json(request):

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
        x['created_utc'] = date_from_iso_utc_to_eastern(i['CreatedUtc'][:19])
        x['media_object_name'] = i['MediaObject']['Name'] if i['MediaObject'] else None
        x['media_packet_name'] = i['MediaPacket']['Name'] if i['MediaPacket'] else None
        x['bitrate_id'] = i['BitrateId']
        x['played_seconds'] = i['PlayedSecondsStr']
        x['avg_bandwidth'] = i['AvgBandwidthStr']
        x['client_ip'] = i['ClientIp']
        x['user_agent'] = i['UserAgent']

        x['location'] = ''
        if i['ClientCountryCode']:
            x['location'] += (i['ClientCountryCode'] + ', ')
        if i['ClientRegionName']:
            x['location'] += (i['ClientRegionName'] + ', ')
        if i['ClientISP']:
            x['location'] += (i['ClientISP'] + ', ')
        if x['location']:
            x['location'] = x['location'][:-2]

        x['id'] = i['PpName']
        x['stream_type'] = 'Live' if i['IsLiveStream'] else 'VOD '

        resp['data'].append(x)

    response = JsonResponse(resp)
    return response

def is_support(user):
    return user.groups.filter(name='support').exists()


def is_management(user):
    return user.groups.filter(name='management').exists()


@user_passes_test(is_support)
@login_required(login_url="/login/")
def user_list(request):
    return render(request, 'stats/user_list.html')


@user_passes_test(is_support)
@login_required(login_url="/login/")
def user_details(request, id):

    resource = UsersResourceClient()
    user_details =  resource.get_one_object(id)

    if user_details['account']['domain'] != request.user.userprofile.get_domain_display():
        raise Http404("User does not exist")

    context = {}
    context['result'] = user_details
    context['date_joined'] = date_from_iso(user_details['date_joined'])
    if user_details['last_login']:
        context['last_login'] = date_from_iso(user_details['last_login'])

    return render(request, 'stats/user_details.html', context)

@user_passes_test(is_management)
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