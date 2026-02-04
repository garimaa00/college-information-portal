# from datetime import date
# from campus.models import CollegeInfo, Event  # Create these models if not exists

# def global_context(request):
#     return {
#         'college_info': CollegeInfo.objects.first() or {'about_bim': 'About BIM...', 'location': 'Kathmandu, Nepal'},
#         'events': Event.objects.filter(date__gte=date.today()).order_by('date')[:3],
#     }


# # myproject/context_processors.py
# from campus.models import CollegeInfo, Event 
# from django.utils import timezone
# from datetime import date

# def some_context_processor(request):
#     return {
#         'college_info': CollegeInfo.objects.first(),  # Example
#         'events': Event.objects.all(),  # Example
#     }
    
# def global_context(request):
#     return {
#         'college_info': CollegeInfo.objects.first() or {'about_bim': 'About BIM...', 'location': 'Kathmandu, Nepal'},
#         'events': Event.objects.filter(date__gte=timezone.now().date()).order_by('date')[:3],
#     }
# myproject/context_processors.py
from campus.models import CollegeInfo, Event

def college_context(request):  # Adjust name to match your setup
    return {
        'college_info': CollegeInfo.objects.first(),
        'events': Event.objects.all(),
    }