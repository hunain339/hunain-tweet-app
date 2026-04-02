from hunain_project.wsgi import application

def handler(request):
    return application(request)
