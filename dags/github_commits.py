from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

# v0.0.1

with DAG(
        dag_id='github_commits_v1',
        schedule_interval=None,
        start_date=datetime(2000, 1, 1),
        catchup=False,
        tags=['github'],
) as dag:
    def scheduler_init_sync_github_commit(ds, **kwargs):
        return 'End scheduler_init_sync_github_commit'


    op_scheduler_init_sync_github_commit = PythonOperator(
        task_id='scheduler_init_sync_github_commit',
        python_callable=scheduler_init_sync_github_commit
    )


    def do_init_sync_github_commit(params):
        from airflow.models import Variable
        from libs.github import commits

        github_tokens = Variable.get("github_infos", deserialize_json=True)
        opensearch_conn_infos = Variable.get("opensearch_conn_data", deserialize_json=True)

        owner = params["owner"]
        repo = params["repo"]
        since = params["since"]
        until = params["until"]

        do_init_sync_info = commits.init_sync_github_commits(github_tokens, opensearch_conn_infos, owner, repo, since,
                                                             until)

        print(do_init_sync_info)
        return "do_init_sync_github_commit-end"


    need_do_inti_sync_ops = []

    from airflow.models import Variable

    need_init_sync_github_commits_list = Variable.get("need_init_sync_github_commits_list", deserialize_json=True)

    for now_need_init_sync_github_commits in need_init_sync_github_commits_list:
        op_do_init_sync_github_commit = PythonOperator(
            task_id='do_init_sync_github_commit_{owner}_{repo}'.format(
                owner=now_need_init_sync_github_commits["owner"],
                repo=now_need_init_sync_github_commits["repo"]),
            python_callable=do_init_sync_github_commit,
            op_kwargs={'params': now_need_init_sync_github_commits},
        )
        op_scheduler_init_sync_github_commit >> op_do_init_sync_github_commit
