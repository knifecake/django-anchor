import os
import sys
import shutil

import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.test_settings"
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    test_labels = sys.argv[1:] or ["tests"]
    failures = test_runner.run_tests(test_labels)

    # clear tmp dir
    shutil.rmtree(
        settings.MEDIA_ROOT,
    )
    os.mkdir(settings.MEDIA_ROOT)

    sys.exit(bool(failures))
