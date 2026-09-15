Fix social login for ``social-auth-app-django`` 6.0+ by rendering CSRF-protected POST
forms for ``social:begin`` (and POST disconnect links). Add
``socialprofile.conf.apply_sp_defaults`` for production HTTPS OAuth redirect settings.
