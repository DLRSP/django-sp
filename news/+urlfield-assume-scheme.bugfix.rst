Make the profile homepage URL field assume the ``https`` scheme on Django 5.x,
matching the default that Django 6.0 adopts, so the form no longer raises a
deprecation warning while staying compatible with Django 4.2.
