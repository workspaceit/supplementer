import json

from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic
from django.template.loader import render_to_string
from adminapp.views.helper import LogHelper
import logging


class UpdateDatabaseView(generic.TemplateView):
    def get(self, request):
        return render(request, 'update_database/index.html')

    def update_database(request):
        logger = logging.getLogger(__name__)
        try:
            logger.debug("============Update Database Start Details===============")
            if request.POST.get('confirm') == "CONFIRM":
                c = connection.cursor()
                try:
                    parent_components_sql = render_to_string('update_database/parent_components.sql')
                    c.execute(parent_components_sql.strip(' \n\r\t'))
                    sub_components_sql = render_to_string('update_database/sub_components.sql')
                    c.execute(sub_components_sql.strip(' \n\r\t'))
                finally:
                    c.close()
                response_data = {'message': 'Database updated Successfully'}
                logger.debug("=============Update Database Start END==============")
            else:
                response_data = {'message': 'Not Confirmed'}
                logger.debug("=============Not Confirmed Database Start END==============")
        except Exception as e:
            logger.debug("============Update Database Start ERROR Details===============")
            LogHelper.efail(e)
            logger.debug("=============Update Database Start ERROR END==============")
            response_data = {
                'error': True,
                'message': 'Something went wrong with update database. Please try again.'
            }
        return HttpResponse(json.dumps(response_data), content_type="application/json")
