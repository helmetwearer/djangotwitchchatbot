import markdown
from django.conf import settings
from django.http import HttpResponse

def readme(request):
	return HttpResponse(markdown.markdown(open('%s/README.MD' % settings.BASE_DIR, 'r').read()))