{
    "draw": {{draw}},
    "recordsTotal": {{recordsTotal}},
    "recordsFiltered": {{recordsFiltered}},
    "data": [
    {% autoescape false %}
     {%- for run in runs -%}
    {
        "id": {{run._id | tostr | default | tojson}},
        "experiment_name": {{run.experiment.name | default | tojson}},
        "command": {{run.command | default | tojson}},
        "status": {{run.status | default | tojson | safe}},
        "comment": {{run.config.comment | default | tojson}},
        "lr": {{run.config.lr | default | tofloat}},
        "epochs_per_lr_drop": {{run.config.epochs_per_lr_drop | default | tofloat}},
        "optimizer_name": {{run.config.optimizer_name | default | tojson}},
        "augmented": {{run.config.augmented | default | tojson}},
        "rotate": {{run.config.rotate | default | tojson}},
        "batch_norm": {{run.config.batch_norm | default | tojson}},
        "relu_after_conv": {{run.config.relu_after_conv| default | tojson}},
        "model_config": {{run.config.model_config| default | tojson}},
        "best_val_loss": {{run.config.best_val_loss | default | tofloat | tojson}},
        "best_epoch": {{run.config.best_epoch | default | tostr | tojson}},
        "is_alive": {{run.heartbeat | default | timediff  | detect_alive_experiment | tojson }},
        "start_time": {{run.start_time | default | format_datetime | tojson}},
        "heartbeat": {{run.heartbeat | default | format_datetime | tojson}},
        "heartbeat_diff": {{run.heartbeat | default | timediff | tojson}},
        "duration": {{ (run.start_time, run.heartbeat) | default | duration | tojson}},
        "hostname": {{run.host.hostname | default | tojson}},
        {# commented out: "captured_out_last_line": {{run.captured_out | default | last_line | tojson}}, #}
        "result":{{run.result | default | dump_json }}
        {%- if full_object -%},
        "object": {{run | dump_json}}
        {% endif %}
    }
        {%- if not loop.last -%}
            ,
        {% endif %}
    {% endfor %}
    {% endautoescape %}
    ]

}