from fabric.api import *

env.roledefs = {
    "prod": ["craiglabenz.me"],
}
env.user = 'root'
env.use_ssh_config = True

@roles("prod")
def deploy_prod(tag=False):
    code_dir = '/home/django/craigblog/'
    with cd(code_dir):
        run("git fetch")
        run("git checkout master")
        run("git pull origin master")
        with prefix("workon craigblog"):
            run("pip3 install -r requirements/prod.txt")
            with cd("web"):
                run("python manage.py collectstatic --noinput")
                run("python manage.py migrate")
                run("mv templates/_maintenance.html templates/maintenance.html")
                run("/etc/init.d/uwsgi restart")
                run("mv templates/maintenance.html templates/_maintenance.html")
