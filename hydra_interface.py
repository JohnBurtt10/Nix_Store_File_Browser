import random
import sys
from threading import Thread
import time
from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from hydra_client import Hydra
import dependency_analyzer
from extract_earliest_latest_values import extract_earliest_latest_values
import json
import jobset_explorer
import cache_utils
from traverse_jobset import traverse_jobset
from cache_directories import *
from sum_2d_dicts import sum_2d_dicts_of_lists
from sum_dicts import sum_dicts_of_lists
from merge_dicts_with_preference import merge_2d_dicts_with_preference, merge_dicts_with_preference
from new_calculate_entropy import get_cached_or_fetch_store_path_entropy_dict
from cache_directories import *
from get_sorted_jobsets import get_sorted_jobsets
from generate_layers import generate_layers
from update_file_variable_value import update_file_variable_value
import os

# TODO:
# - Clear caches button

app = Flask(__name__)


# hydra config
hydra_url = "http://hydra.clearpath.ai/"
hydra = Hydra(url=hydra_url)

hydra.login(username="administrator", password="clearp@th")

app = Flask(__name__)
socketio = SocketIO(app)


def simulate_progress():
    for i in range(101):
        time.sleep(0.1)  # Simulate a delay
        socketio.emit('progress', {'progress': i}, namespace='/test')


@app.route('/')
def index():
    return render_template('index.html')


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


@app.context_processor
def utility_processor():
    def random():
        return random.randint(1, 1000)  # Adjust the range as needed
    return dict(random=random)


@app.route('/column1')
def column1():

    # hydra config
    hydra_url = "http://hydra.clearpath.ai/"
    hydra = Hydra(url=hydra_url)
    hydra.login(username="administrator", password="clearp@th")

    projects = hydra.get_projects()
    return render_template('column1.html', projects=projects,
                           sort_keys={'dependency_weight',
                                      'entropy', 'file_size', 'reverse_dependency_weight'},
                           top_n_values='',
                           selected_project='',
                           selected_quantity='100',
                           selected_sort_key_1='entropy',
                           selected_sort_key_2='file_size',
                           minimum_entropy=0,
                           minimum_file_size=0)


@app.route('/column2')
def column2():
    return render_template('column2.html')


@app.route('/column3')
def column3():
    return render_template('column3.html')

@app.route('/get_children/<parent_node>')
def get_children(parent_node):
    # return render_template('column3.html')
    print(f"Getting children for parent node: {parent_node}")

    children = dependency_analyzer.get_children(hydra, parent_node)

    print(f"Children for {parent_node}: {children}")

    return jsonify(children)

@app.route('/compare/<project_name>/<base_node>/<compare_node>')
def compare(project_name, base_node, compare_node):
    serialized_jobsets_array = request.args.get('jobsets')

    if serialized_jobsets_array:
        try:
            jobsets = json.loads(serialized_jobsets_array)
        except json.JSONDecodeError as e:
            return jsonify({'result': 'error', 'message': 'Invalid JSON in myArray parameter'})
    else:
        return jsonify({'result': 'error', 'message': 'myArray parameter not provided'})

    print(
        f"Comparing {base_node} and {compare_node} for project {project_name}")
    print(f"Received jobsets: {jobsets}")

    overlap_list, disjoint_list = dependency_analyzer.compare(
        hydra, base_node, compare_node)
    combined_list = dependency_analyzer.combine(
        project_name=project_name, hydra=hydra, jobsets=jobsets, list1=overlap_list, list2=disjoint_list)

    print("Comparison and combination completed successfully.")

    return jsonify(combined_list)


@app.route('/display/<timestamp>')
def display_dict(timestamp):
    print(f"display_dict")
    # Convert timestamp to human-readable format
    human_readable_time = time.strftime(
        '%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))

    # Specify the directory path
    directory = "container_layer_view"

    # Combine directory path with file name
    file_path = os.path.join(directory, str(timestamp) + ".json")

    try:
        # Open the file in read mode
        with open(file_path, "r") as file:
            # Read the contents of the file
            file_content = file.read()

            # Check if the file is empty
            if len(file_content) == 0:
                return render_template('still_generating.html')
            else:
                # Load the JSON content
                loaded_dict = json.loads(file_content)
    except FileNotFoundError:
        print("File not found:", file_path)
        return render_template('display.html', data=[], timestamp=human_readable_time)
    # except TypeError:
    #     return render_template('still_generating.html')
    except json.JSONDecodeError:
        print("Invalid JSON format in file:", file_path)
    except PermissionError:
        print("Permission denied to open file:", file_path)
    except Exception as e:
        print("An error occurred:", e)

    # Define your container data as a Flask variable
    container_data = {
        'container1': [
            {'layer': 'Layer 1', 'packages': [
                'Package A', 'Package B'], 'newData': '10GB'},
            {'layer': 'Layer 2', 'packages': [
                'Package C', 'Package D'], 'newData': '5GB'}
        ],
        'container2': [
            {'layer': 'Layer 1', 'packages': [
                'Package X', 'Package Y'], 'newData': '8GB'},
            {'layer': 'Layer 2', 'packages': ['Package Z'], 'newData': '3GB'}
        ]
        # Add more containers and their layers as needed
    }

    # Generate a new endpoint based on the timestamp

    print(loaded_dict)

    # Render the template with the data and newly generated endpoint
    return render_template('display.html', container_data=loaded_dict)


@socketio.on('start_progress', namespace='/test')
def start_progress(data):
    # Unpack parameters from the data dictionary
    minimum_layer_recursive_file_size = data.get(
        'minimumLayerRecursiveFileSize')
    maximum_layer_recursive_file_size = data.get(
        'maximumLayerRecursiveFileSize')
    coverage_threshold_mode_enabled = data.get('coverageThresholdModeEnabled')
    coverage_threshold = data.get('coverageThreshold')
    package_count_mode_enabled = data.get('packageCountModeEnabled')
    package_count = data.get('packageCount')

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

    answer = generate_layers(hydra, update_progress, report_error, send_layer, update_layer_progress, minimum_layer_recursive_file_size, maximum_layer_recursive_file_size,
                             coverage_threshold_mode_enabled, coverage_threshold, package_count_mode_enabled, package_count)

    # new_dict = {}
    # for combination, is_creating_zero_entropy_layers, i in answer:
    #     key = (combination, is_creating_zero_entropy_layers, i)
    #     new_dict[str(key)] = answer[key]
    #     new_dict[str(key)]['packages'] = list(answer[key]['packages'])
    #     new_dict[str(key)]['combination'] = combination
    #     new_dict[str(key)]['is_creating_zero_entropy_layers'] = is_creating_zero_entropy_layers

    # Open the file and write JSON data to it
    with open(file_path, "w") as file:
        json.dump(answer, file)


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
    projects = hydra.get_projects()
    sort_keys = {'dependency_weight', 'entropy',
                 'file_size', 'reverse_dependency_weight'}

    sorted_jobsets = get_sorted_jobsets(hydra, selected_project)

    latest_jobset = sorted_jobsets[0]

    latest_jobset = 'v2.32.0-20240307124945-0'

    print(f"latest_jobset={latest_jobset}")

    def update_progress(task, progress):
        pass

    def report_error(error):
        pass

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
        "Finding all store paths for packages", None, sum_dicts_of_lists
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
        "Getting the reverse dependencies of packages", [
            latest_jobset], sum_2d_dicts_of_lists
    )[0]

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

    print(f"here")

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
                                                                 #  minimum_entropy=minimum_entropy,
                                                                 #  minimum_file_size=minimum_file_size,
                                                                 print_dependency_weight=False)

    print(f"there")

    socketio.emit('result', [top_n_values, sorted_jobsets,
                  random.randint(1, 1000)], namespace='/test')

    # build_info_cache["gwfiwfqwDO"] = top_n_values
    return [top_n_values, sorted_jobsets]
    return render_template('index.html',
                           projects=projects,
                           sort_keys=sort_keys,
                           top_n_values=top_n_values,
                           selected_quantity=selected_quantity,
                           #    default_minimum_entropy=minimum_entropy,
                           #    default_minimum_file_size=minimum_file_size,
                           selected_sort_key_1=selected_sort_key_1,
                           selected_sort_key_2=selected_sort_key_2,
                           selected_project=selected_project,
                           #   earliest_jobset=earliest_jobset,
                           latest_jobset=latest_jobset,
                           jobsets=jobsets)


if __name__ == '__main__':
    # app.run(debug=True, )
    # Check if two command line arguments are provided
    if len(sys.argv) != 3:
        print("Usage: python script.py <integer_value> <true|false>")
        sys.exit(1)

    # Extract the command line arguments
    try:
        int_value = int(sys.argv[1])
    except ValueError:
        print("First argument must be an integer")
        sys.exit(1)

    bool_value = sys.argv[2].lower() == "true"

    # socketio.run(app, host='0.0.0.0', port=int_value, debug=bool_value)
    socketio.run(app, port=int_value, debug=bool_value)


@app.route('/get_jobsets/<project_name>')
def get_jobsets(project_name):

    print(f"Getting jobsets for project: {project_name}")

    jobsets = hydra.get_jobsets(project=project_name)

    return jsonify(jobsets)

# TODO: name?


@app.route('/get_whats_new/<project_name>/<jobset1>/<jobset2>')
def get_whats_new(project_name, jobset1, jobset2):
    print(f"get what's new!")

    serialized_jobsets_array = request.args.get('jobs')

    if serialized_jobsets_array:
        try:
            jobs = json.loads(serialized_jobsets_array)
        except json.JSONDecodeError as e:
            return jsonify({'result': 'error', 'message': 'Invalid JSON in myArray parameter'})
    else:
        return jsonify({'result': 'error', 'message': 'myArray parameter not provided'})

    print(
        f"Getting whats new from jobset1: {jobset1} to jobset2: {jobset2} in project: {project_name} for jobs: {jobs}")

    data = jobset_explorer.compare_and_group_job(
        hydra, project_name, jobs, jobset1, jobset2)
    # print(f"get_whats_new returning {data}")

    return jsonify(data)


@app.route('/compare_and_group_references/<store_path1>/<store_path2>')
def compare_and_group_references(store_path1, store_path2):

    if store_path1 == 'null':
        store_path1 = None
    if store_path2 == 'null':
        store_path2 = None
    print(
        f"compare_and_group_references store_path1: {store_path1}, store_path2: {store_path2}")

    data = jobset_explorer.handle_compare_and_group_references(
        hydra, store_path1, store_path2)

    print(f"sending back : {data}")

    return jsonify(data)


@app.route('/get_dependencies_of_jobs/<project_name>/<jobset1>/<jobset2>')
def get_dependencies_of_jobs(project_name, jobset1, jobset2):

    serialized_jobsets_array = request.args.get('jobs')

    if serialized_jobsets_array:
        try:
            jobs = json.loads(serialized_jobsets_array)
        except json.JSONDecodeError as e:
            return jsonify({'result': 'error', 'message': 'Invalid JSON in myArray parameter'})
    else:
        return jsonify({'result': 'error', 'message': 'myArray parameter not provided'})

    print(
        f"get_dependencies_of_jobs project_name: {project_name}, jobs: {jobs} jobset1: {jobset1}, jobset2: {jobset2}")

    (final_hash_map, final_count_hash_map) = jobset_explorer.compare_and_process_builds(
        project_name=project_name, hydra=hydra, jobs=jobs, jobset1=jobset1, jobset2=jobset2)

    # store_path_entropy_dict = cache_utils.get_cached_or_fetch_store_path_entropy_dict(
    #     hydra, project_name, traverse_jobset, False, False, store_path_entropy_dict_cache)

    # Sorting the dictionary by values
    # sorted_dict = dict(
    #     sorted(store_path_entropy_dict.items(), key=lambda item: item[1]))

    entropy_position_dict = {}

    # Creating a new dictionary with positions
    # entropy_position_dict = {key.split('-', 1)[1]: key for position, (key, _) in enumerate(sorted_dict.items(), 1)}

    # combined_dict = {key: {
    #     'file_size': final_hash_map[key], 'count': final_count_hash_map[key], 'entropy_position': entropy_position_dict.get(key, 0)} for key in final_hash_map}

    combined_dict = {key: {
        'file_size': final_hash_map[key], 'count': final_count_hash_map[key]} for key in final_hash_map}

    print(f"get_dependencies_of_jobs: {combined_dict}")
    return jsonify(combined_dict)


@app.route('/get_jobs/<project_name>/<jobset>')
def get_jobs(project_name, jobset):

    jobs = jobset_explorer.get_jobs(hydra, project_name, jobset)

    return jsonify(jobs)


@app.route('/')
def index(test="index"):

    # hydra config
    hydra_url = "http://hydra.clearpath.ai/"
    hydra = Hydra(url=hydra_url)
    hydra.login(username="administrator", password="clearp@th")

    projects = hydra.get_projects()

    return render_template("index" + ".html", projects=projects,
                           sort_keys={'dependency_weight',
                                      'entropy', 'file_size', 'reverse_dependency_weight'},
                           top_n_values='',
                           selected_project='',
                           selected_quantity='100',
                           selected_sort_key_1='entropy',
                           selected_sort_key_2='file_size',
                           minimum_entropy=0,
                           minimum_file_size=0)


def main():
    # store_path_entropy_dict = cache_utils.get_cached_or_fetch_store_path_entropy_dict(
    #     hydra, "v2-32-devel", traverse_jobset, False, False, store_path_entropy_dict_cache)
    # return
    # generate_layers(hydra)
    pass


if __name__ == '__main__':
    main()

    # app.run(host='0.0.0.0', port=5000, debug=False)
