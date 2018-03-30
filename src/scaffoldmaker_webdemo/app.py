from json import loads
from time import time
from os.path import dirname
from os.path import join
from sanic import Sanic
from sanic.response import json, html
from scaffoldmaker_webdemo import mesheroutput
from scaffoldmaker_webdemo import backend

db_src = 'sqlite://'
app = Sanic()
app.static('/static', join(dirname(__file__), 'static'))
with open(join(dirname(__file__), 'static', 'index.html')) as fd:
    index_html = fd.read()

store = backend.Store(db_src)


def build(options):
    model = mesheroutput.outputModel(options)
    job = backend.Job()
    job.timestamp = int(time())
    for data in model:
        resource = backend.Resource()
        resource.data = data
        job.resources.append(resource)
    response = loads(job.resources[0].data)
    store.add(job)
    for idx, obj in enumerate(response, 1):
        # XXX
        resource_id = job.resources[idx].id
        obj['URL'] = '/output/%d' % resource_id
    return response


@app.route('/output/<resource_id:int>')
async def output(request, resource_id):
    return json(store.query_resource(resource_id))


@app.route('/generator')
async def generator(request):
    options = {}
    for k, values in request.args.items():
        v = values[0]
        if k == 'Use cross derivatives':
            options[k] = v == 'true'
        elif v.isdecimal():
            options[k] = int(v)
        elif v.replace('.', '', 1).isdecimal():
            options[k] = float(v)
    response = build(options)
    return json(response)


@app.route('/')
async def root(request):
    return html(index_html)


def main():
    app.run(host='0.0.0.0', port=8000)


if __name__ == '__main__':
    main()
