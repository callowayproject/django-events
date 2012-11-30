from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner
from django_coverage.coverage_runner import CoverageRunner


class TestRunner(DjangoTestSuiteRunner):
    def build_suite(self, test_labels, *args, **kwargs):

        APPS_TO_TEST = [app.split('.')[-1] if '.' in app else app for app in settings.PROJECT_APPS]
        return super(TestRunner, self).build_suite(test_labels or APPS_TO_TEST, *args, **kwargs)


class ProjectCoverageRunner(TestRunner, CoverageRunner):
    pass
