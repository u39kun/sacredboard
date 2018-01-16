# coding=utf-8
"""WebAPI module for handling run-related requests."""
import json

from flask import current_app, request, Response, render_template, Blueprint

from sacredboard.app.business import RunFacade
from sacredboard.app.data import DataSourceError

runs = Blueprint("runs", __name__)


@runs.route("/api/run")
def api_runs():
    """Return a list of runs as a JSON object."""
    return get_runs()


@runs.route("/api/run/<run_id>", methods=["DELETE"])
def api_run_delete(run_id):
    """Delete the given run and corresponding entities."""
    data = current_app.config["data"]  # type: DataStorage
    RunFacade(data).delete_run(run_id)
    return "DELETED run %s" % run_id


@runs.route("/api/run/<run_id>", methods=["GET"])
def api_run_get(run_id):
    """Return a single run as a JSON object."""
    data = current_app.config["data"]
    run = data.get_run_dao().get(run_id)
    records_total = 1 if run is not None else 0
    if records_total == 0:
        return Response(
            render_template(
                "api/error.js",
                error_code=404,
                error_message="Run %s not found." % run_id),
            status=404,
            mimetype="application/json")
    records_filtered = records_total
    return Response(render_template("api/runs.js", runs=[run], draw=1,
                                    recordsTotal=records_total,
                                    recordsFiltered=records_filtered,
                                    full_object=True),
                    mimetype="application/json")


def parse_int_arg(name, default):
    """Return a given URL parameter as int or return the default value."""
    return default if request.args.get(name) is None \
        else int(request.args.get(name))


def parse_query_filter():
    """Parse the Run query filter from the URL as a dictionary."""
    query_string = request.args.get("queryFilter")
    if query_string is None:
        return {"type": "and", "filters": []}
    query = json.loads(query_string)
    assert type(query) == dict
    assert type(query.get("type")) == str
    return query


def get_runs():
    """Get all runs, sort it and return a response."""
    data = current_app.config["data"]
    draw = parse_int_arg("draw", 1)
    start = parse_int_arg("start", 0)
    length = parse_int_arg("length", -1)
    length = length if length >= 0 else None
    order_column = request.args.get("order[0][column]")
    order_dir = request.args.get("order[0][dir]")

    query = parse_query_filter()

    if order_column is not None:
        order_column = \
            request.args.get("columns[%d][name]" % int(order_column))
        if order_column == "hostname":
            order_column = "host.hostname"

    runs = data.get_run_dao().get_runs(
        start=start, limit=length,
        sort_by=order_column, sort_direction=order_dir, query=query)
    # records_total should be the total size of the records in the database,
    # not what was returned
    records_total = runs.count()
    records_filtered = runs.count()

    # runs is a filtered set based on the query specified
    # get metrics for these runs
    metrics_dao = data.get_metrics_dao()
    runs_with_metrics = []
    for run in runs:
        if 'metrics' in run['info']:
            run_metrics = run['info']['metrics']
            for run_metric in run_metrics:
                #metric_id = run_metric['id']
                #print(run_metric['id'])
                #print(run_metric['name'])
                if run_metric['name'] == 'val.loss':
                    metric = metrics_dao.get(run['_id'], run_metric['id'])
                    best_val_loss, best_epoch = sorted(zip(metric['values'], metric['steps']))[0]
                    run['config']['best_val_loss'] = best_val_loss
                    run['config']['best_epoch'] = best_epoch
                elif run_metric['name'] == 'train.loss':
                    metric = metrics_dao.get(run['_id'], run_metric['id'])
                    best_train_loss, best_epoch = sorted(zip(metric['values'], metric['steps']))[0]
                    run['config']['best_train_loss'] = best_train_loss

        runs_with_metrics.append(run)

    return Response(render_template(
        "api/runs.js", runs=runs_with_metrics,
        draw=draw, recordsTotal=records_total,
        recordsFiltered=records_filtered),
        mimetype="application/json")


@runs.errorhandler(DataSourceError)
def handle_data_source_error(e: DataSourceError):
    """Handle Exception: DataSource Error."""
    return "Data source error: %s" % e, 500


@runs.errorhandler(NotImplementedError)
def handle_not_implemented_error(e: NotImplementedError):
    """
    Raise exception: not implemented error.

    Raise an exception if the operation is not supported by the backend.
    """
    return "Not Implemented: %s" % e, 510


def initialize(app, app_config):
    """Register the module in Flask."""
    app.register_blueprint(runs)
