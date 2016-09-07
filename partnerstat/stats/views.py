from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from .models import Viewing
import datetime
from django.contrib.auth.decorators import login_required

# Create your views here.

from .forms import ViewsSearchForm


# def index(request):
#     latest_question_list = Viewing.objects.all()
#     template = loader.get_template('stats/index.html')
#     context = {
#         'latest_question_list': latest_question_list,
#     }
#     return HttpResponse(template.render(context, request))

@login_required(login_url="/login/")
def index(request):
    latest_question_list = Viewing.objects.all()
    context = {'latest_question_list': latest_question_list}
    return render(request, 'stats/index.html', context)


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

                qd = views.filter(date=d)
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