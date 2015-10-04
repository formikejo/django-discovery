Opinionated Service Discovery for Django
========================================
This project provides a simple workflow for registering services in Django. It is highly opinionated and makes a lot
of assumptions.

Goal
----
When developing a Django application, you often need external services such as a database, a key-value store, a
message broker, etc. etc. I prefer to use `Docker <https://www.docker.com/whatisdocker>`_ and
`Docker-Compose <https://docs.docker.com/compose/>`_ to have those services running when I develop my application.

``django-discovery`` makes it easy to connect to those services, as long as you follow a specific workflow:

- Development is done on your own machine, with the services running under Docker;
- Testing is done by running both the services and the application using Docker Compose;
- The production environment provides an SRV-lookup capable DNS. Examples are:

    + Running everything under `Kubernetes <http://kubernetes.io>`_
    + Running everything on Docker, configured to use an SRV-capable DNS such as `Consul <http://www.consul.io>`_


Requirements
------------
``django-discovery`` requires Python 3 and Django 1.8 because we live in modern times.


Quickstart
----------
The following example assumes a Django application that requires a MySQL database. Add the following to your
``settings.py``:

::

    from discovery import services

    db = services.register('my_db', 'mysql', secrets=['mysql_user', 'mysql_database', 'mysql_password'])

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': db.secrets['mysql_database'],
            'USER': db.secrets['mysql_user'],
            'PASSWORD': db.secrets['mysql_password'],
            'HOST': db.host,
            'PORT': db.port,
        }
    }

    DEBUG = services.debug_mode


You can now run your application on localhost with your database under docker using the following
``docker-compose.yml``:

::

    my_db:
        image: mysql:5.6
        ports:
            - ":3306"
        environment:
            MYSQL_ROOT_PASSWORD: supersecret
            MYSQL_DATABASE: database_name
            MYSQL_USER: database_user
            MYSQL_PASSWORD: alsosecret


You can also run your application in its entirety in docker, using for example the following docker-compose file:

::

    database:
        image: mysql:5.6
        environment:
            MYSQL_ROOT_PASSWORD: supersecret
            MYSQL_DATABASE: database_name
            MYSQL_USER: database_user
            MYSQL_PASSWORD: alsosecret

    application:
        build: .
        links:
            - database:my_db
        ports:
            - "80:8080"
        env:
            DISCOVERY_MODE: env

And still using the same ``settings.py``, you can even run your application under Kubernetes using the following
definitions:

::

    apiVersion: v1
    kind: Service
    metadata:
      name: my_db
    spec:
      ports:
        - protocol: tcp
          port: 3306

::

    apiVersion: v1
    kind: Endpoints
    metadata:
      name: my_db
    subsets:
      - addresses:
        - ip: 1.2.3.4
      - ports:
        - port: 3306

::

    apiVersion: v1
    kind: Pod
    metadata:
      name: my_application
      namespace: my_namespace
    spec:
      containers:
         - name: my_application
           image: my/docker-image
           volumeMounts:
             - name: db_secrets
               mountPath: /etc/secrets/my_db
               readOnly: true
      volumes:
        - name: db_secrets
          secret:
            mysql_database: some_name
            mysql_user: some_user
            mysql_password: secret_password


Full Documentation
------------------
Working on it...

License
-------
This project is licensed under the MIT license.
