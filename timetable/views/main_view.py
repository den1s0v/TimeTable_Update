from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def timetable_choose_degree(request):
    degrees = [
        {
            'title': 'Бакалавриат (специалитет)',
            'image': 'bachelor_image.png',
            'params': '?type_timetable=lesson&degree=bachelor',
            'css_class': 'degree-card-bachelor',
            'separator_class': 'degree-card-separator-line-bachelor',
        },
        {
            'title': 'Магистратура',
            'params': '?type_timetable=lesson&degree=master',
            'image': 'master_image.png',
            'css_class': 'degree-card-master',
            'separator_class': 'degree-card-separator-line-master',
        },
        {
            'title': 'Аспирантура',
            'params': '?type_timetable=lesson&degree=postgraduate',
            'image': 'phd_image.png',
            'css_class': 'degree-card-postgraduate',
            'separator_class': 'degree-card-separator-line-postgraduate',
        },
    ]
    return render(request, 'timetable_choose_degree.html', {'degrees': degrees})

def exams_choose_degree(request):
    degrees = [
        {
            'title': 'Бакалавриат (специалитет)',
            'image': 'bachelor_image.png',
            'params': '?type_timetable=exam&degree=bachelor',
            'css_class': 'degree-card-bachelor',
            'separator_class': 'degree-card-separator-line-bachelor',
        },
        {
            'title': 'Магистратура',
            'params': '?type_timetable=exam&degree=master',
            'image': 'master_image.png',
            'css_class': 'degree-card-master',
            'separator_class': 'degree-card-separator-line-master',
        },
        {
            'title': 'Аспирантура',
            'params': '?type_timetable=exam&degree=postgraduate',
            'image': 'phd_image.png',
            'css_class': 'degree-card-postgraduate',
            'separator_class': 'degree-card-separator-line-postgraduate',
        },
    ]
    return render(request, 'exams_choose_degree.html', {'degrees': degrees})


def sports_timetable(request):
    return render(request, 'sports_timetable.html')

def bells_timetable(request):
    return render(request, 'bells_timetable.html')