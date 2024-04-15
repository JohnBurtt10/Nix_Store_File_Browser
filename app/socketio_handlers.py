from . import cache_utils
from .traverse_jobset import traverse_jobset
from .cache_directories import *
from .sum_2d_dicts import sum_2d_dicts_of_lists
from .sum_dicts import sum_dicts_of_lists
from .merge_dicts_with_preference import merge_2d_dicts_with_preference, merge_dicts_with_preference
from .new_calculate_entropy import get_cached_or_fetch_store_path_entropy_dict
from .get_sorted_jobsets import get_sorted_jobsets
from .generate_layers import generate_layers
from .update_file_variable_value import update_file_variable_value
from .extract_earliest_latest_values import extract_earliest_latest_values
from flask_socketio import emit
from app import socketio
import json
import os
from .hydra_client import Hydra
from . import dependency_analyzer
import time

# hydra config
hydra_url = "http://hydra.clearpath.ai/"
hydra = Hydra(url=hydra_url)

hydra.login(username="administrator", password="clearp@th")


@socketio.on('connect', namespace='/test')
def test_connect():
    print('Client connected')
    emit('message', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


@socketio.on('proceed', namespace='/test')
def proceed():
    update_file_variable_value('proceed', True)


@socketio.on('cancel', namespace='/test')
def cancel():
    update_file_variable_value('cancel', True)


@socketio.on('start_progress', namespace='/test')
def start_progress(data):
    # Unpack parameters from the data dictionary
    start_date = data.get(
        'startDate')
    end_date = data.get(
        'endDate')

    minimum_layer_recursive_file_size = data.get(
        'minimumLayerRecursiveFileSize')
    maximum_layer_recursive_file_size = data.get(
        'maximumLayerRecursiveFileSize')

    update_file_variable_value('cancel', False)

    def update_progress(task, progress):
        socketio.emit(
            'progress', {'task': task, 'progress': round(progress)}, namespace='/test')

    def update_layer_progress(progress):
        # print(f"progress={progress}")
        socketio.emit(
            'layer_progress', progress, namespace='/test')

    def report_error(error):
        socketio.emit('error', {error}, namespace='/test')

    def send_layer(layer):
        # print(f"layer: {layer}")
        # json_data_to_send = json.dumps(layer)
        socketio.emit('result', layer, namespace='/test')

    current_timestamp = int(time.time())

    # Specify the directory path
    directory = "container_layer_view"

    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Combine directory path with file name
    file_path = os.path.join(directory, str(current_timestamp) + ".json")

    with open(file_path, "w") as file:
        pass

    socketio.emit('timestamp', current_timestamp, namespace='/test')

    answer = generate_layers(hydra, update_progress, report_error, send_layer, update_layer_progress,
                             minimum_layer_recursive_file_size, maximum_layer_recursive_file_size, start_date, end_date)

    # Open the file and write JSON data to it
    with open(file_path, "w") as file:
        json.dump(answer, file)

    socketio.emit('done', namespace='/test')


@socketio.on('explore_packages', namespace='/test')
def explore_packages(data):

    # data = request.json  # Assuming the data is in JSON format
    # client input
    # Unpack values into variables
    selected_sort_key_1_order = data.get('sort_key_1_select_order')
    selected_quantity = data.get('quantity')
    selected_sort_key_1 = data.get('sort_key_1_select')
    selected_sort_key_2 = data.get('sort_key_2_select')
    filters = data.get('filters', [])
    selected_project = data.get('selected_project')
    recursive_mode_enabled = data.get('recursive_mode_enabled', False)
    exponential_back_off_enabled = data.get(
        'exponential_back_off_enabled', False)
    # selected_project = request.form.get('selected_project', '')
    advanced_entropy_mode_enabled = data.get(
        'advanced_entropy_mode_enabled', False)
    approximate_uncalculated_jobsets_mode_enabled = data.get(
        'approximate_uncalculated_jobsets_mode_enabled', False)
    print(f"selected_project: {selected_project}")
    print(f"advanced_entropy_mode_enabled: {advanced_entropy_mode_enabled}")

    sorted_jobsets = get_sorted_jobsets(hydra, selected_project)[:5]

    latest_jobset = sorted_jobsets[0]

    # latest_jobset = 'v2.32.0-20240307124945-0'

    print(f"latest_jobset={latest_jobset}")

    def update_progress(task, progress):
        pass

    def report_error(error):
        pass

    if "demo" in cache:
        store_path_jobsets_dict, dependency_all_store_path_dict, store_path_file_size_dict, dependency_store_path_dict, reverse_dependencies_dict = cache[
            "demo"]

    else:
        # Execute cache function 1
        store_path_jobsets_dict = cache_utils.general_cache_function(
            hydra, update_progress, report_error, selected_project, traverse_jobset, store_path_jobsets_dict_cache,
            cache_utils.update_store_path_jobsets_dict, recursive_mode_enabled, exponential_back_off_enabled, True, True,
            "Getting all of the jobsets that packages are in", [
                latest_jobset], sum_2d_dicts_of_lists
        )[0]

        # Execute cache function 2
        dependency_all_store_path_dict = cache_utils.general_cache_function(
            hydra, update_progress, report_error, selected_project, traverse_jobset, dependency_all_store_path_dict_cache,
            cache_utils.update_dependency_all_store_path_dict, recursive_mode_enabled, exponential_back_off_enabled, True, True,
            "Finding all store paths for packages", sorted_jobsets, sum_dicts_of_lists
        )[0]

        # Execute cache function 3
        store_path_file_size_dict = cache_utils.general_cache_function(
            hydra, update_progress, report_error, selected_project, traverse_jobset, store_path_file_size_dict_cache,
            cache_utils.update_store_path_file_size_dict, recursive_mode_enabled, exponential_back_off_enabled, True, True,
            "Getting the file size of packages", [
                latest_jobset], merge_dicts_with_preference
        )[0]

        # Execute cache function 4
        dependency_store_path_dict = cache_utils.general_cache_function(
            hydra, update_progress, report_error, selected_project, traverse_jobset, dependency_store_path_dict_cache,
            cache_utils.update_dependency_store_path_dict, recursive_mode_enabled, exponential_back_off_enabled, True, True,
            "Getting the latest store path of packages", [
                latest_jobset], merge_2d_dicts_with_preference
        )[0]

        # Execute cache function 5
        reverse_dependencies_dict = cache_utils.general_cache_function(
            hydra, update_progress, report_error, selected_project, traverse_jobset, reverse_dependencies_dict_cache,
            cache_utils.update_reverse_dependencies_dict, recursive_mode_enabled, exponential_back_off_enabled, True, True,
            "Getting the reverse dependencies of packages", sorted_jobsets, sum_2d_dicts_of_lists
        )[0]

        cache["demo"] = store_path_jobsets_dict, dependency_all_store_path_dict, store_path_file_size_dict, dependency_store_path_dict, reverse_dependencies_dict

    if advanced_entropy_mode_enabled:
        # advanced entropy
        store_path_entropy_dict = get_cached_or_fetch_store_path_entropy_dict(
            hydra, selected_project, approximate_uncalculated_jobsets_mode_enabled)
    else:
        # basic entropy
        store_path_entropy_dict = cache_utils.get_basic_entropy(
            dependency_all_store_path_dict)

    earliest_latest_values_dict = extract_earliest_latest_values(
        input_dict=reverse_dependencies_dict)

    top_n_values = dependency_analyzer.compute_top_n_information(store_path_entropy_dict,
                                                                 store_path_file_size_dict,
                                                                 earliest_latest_values_dict,
                                                                 dependency_store_path_dict,
                                                                 dependency_all_store_path_dict,
                                                                 store_path_jobsets_dict,
                                                                 project_name=selected_project,
                                                                 hydra=hydra,
                                                                 latest_jobset=latest_jobset,
                                                                 sort_key1=selected_sort_key_1,
                                                                 sort_key2=selected_sort_key_2,
                                                                 sort_order=selected_sort_key_1_order,
                                                                 n=selected_quantity,
                                                                 # TODO fix names
                                                                 filters=filters,
                                                                 print_dependency_weight=False)

    socketio.emit('result', [top_n_values, sorted_jobsets], namespace='/test')

    socketio.emit('done', namespace='/test')

    return [top_n_values, sorted_jobsets]
