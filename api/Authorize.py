import environ

class Authorize:
  def call(self, params):
    env = environ.Env()
    environ.Env.read_env()
    if params.get('username') == env('ADMIN_USERNAME') and params.get('password') == env('ADMIN_PASSWORD'):
      return { "token": env('ADMIN_TOKEN') }
    else:
      return {}
