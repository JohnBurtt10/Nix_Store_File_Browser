from . import cache_utils
from .cache_directories import *

def get_jobset_builds(hydra, project_name, jobset):
    data = cache_utils.get_cached_or_fetch_jobset_evals(
        hydra, jobset_evals_cache, project_name, jobset)
    eval_info = data.get('evals', [])[0]
    builds = eval_info.get('builds', [])
    return builds