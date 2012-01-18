import json
import web

import nvdadb

nvdadb.init()

urls = (r"/LastSnapshot/(\w+)", "LastSnapshot",)
app = web.application(urls, globals(), True)


def jsonify(fun):
    def new(*args, **kwargs):
        ret = fun(*args, **kwargs)
        ret = json.dumps(ret, default=str)
        # Support JSONP requests
        if "callback" in web.input():
            ret = "%s(%s);" % (web.input().get('callback'), ret)
        web.header('content-type', 'application/json')
        return ret
    return new

class LastSnapshot(object):
    @jsonify
    def GET(self,  branch):
        try:
            s = nvdadb.get_last_snapshot(branch)
            i = web.input()
            if 'type' in i and i.type in ('portable', 'installer'):
                web.found(s[i.type])
            else:
                return s
        except IndexError:
            web.NotFound()

application = app.wsgifunc()
if __name__ == '__main__':
    app.run()
