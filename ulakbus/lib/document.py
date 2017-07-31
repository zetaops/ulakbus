from ulakbus.services.zato_wrapper import ZatoService
import json
from ulakbus.models.document import Template
import os


class RenderDocument(ZatoService):
    """
    Abstract class, for templates.
    """
    def __init__(self):
        super(RenderDocument, self).__init__('document-render.render-document', None)

    def _get_template(self):
        pass

    def _prepare_context(self):
        pass

    def _make_payload(self):
        pass

    def render(self, **kwargs):
        pass


class FooFile(RenderDocument):
    """
    Example template class.
    """

    def __init__(self):
        """
        file_name is stored on database and unique. The template is searched with that.
        """
        self.file_name = "file_foo"
        super(FooFile, self).__init__()

    def _get_template(self):
        """
        Get template information from database.
        Returns: <dict>

        """
        template_info = Template.objects.get(name=self.file_name)

        if template_info is not None:
            return {"template": "{}{}".format(S3_PUBLIC_URL, template_info.template),
                    "modify_date": "{}".format(template_info.modify_date)}
        else:
            return None

    def _prepare_context(self):
        """
        The context data of template. This context data is used by Jinja2
        Returns: <dict>

        """

        title = self.params.pop('title', '')
        date = self.params.pop('date', '')
        content = self.params.pop('content', '')

        context = {"title": title,
                   "date": date,
                   "content": content}

        return context

    def _make_payload(self, template, context, wants_pdf, modify_date):
        """
        Make payload for request.
        Args:
            template:
            context:
            wants_pdf:
            modify_date:

        Returns: <dict>

        """

        payload = {"template": template,
                   "context": context,
                   "pdf": wants_pdf,
                   "modify_date": modify_date}

        return payload

    def render(self, wants_pdf=False, **kwargs):
        """
        Get template, prepare context and make payload before making a zato request to service.
        Args:
            wants_pdf:
            **kwargs:

        Returns: <str>
                http://example.com/example_file

        """

        self.params = kwargs
        template_info = self._get_template()

        context = self._prepare_context()
        payload = self.make_payload(template=template_info['template'],
                          context=context,
                          wants_pdf=wants_pdf,
                          modify_date=template_info['modify_date'])

        self.payload = payload

        response = self.zato_request()
        return response


if __name__ == "__main__":
    """
    Usage of these classes.
    """
    foo_renderer = FooFile()
    result = foo_renderer.render(wants_pdf=True, title="Baslik", content="icerik")
    print result


