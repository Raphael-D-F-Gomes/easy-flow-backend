from dataclasses import dataclass


@dataclass
class SubServiceNames:

    upload_file = "Upload File"
    download_file = "Download File"
    save_data_into_file = "Save Data Into File"
    get_data_from_file = "Get Data From File"

    errors_search = "Errors and Warnings Search"
    format_input = "Format Input"
    build_validation_report = "Build Validation Report"
    convert_to_string = "Convert To String"
    convert_into_json_format = "Convert Into Json Format"

    choose_model = "Choose Model"
    checking_module = "Checking Module"
    build_no_model = "Build Network Optimization Model"
    model_data_processing = "Model Data Processing"
    set_objective = "Construct Objective Function"
    set_const = "Construct Constraint"
    declare_variables = "Declare Variables"
    optimize_data = "Optimize Data"
    init_data_processing_class = f"Init Data Processing Class"

    choose_solver = "Choose Solver"
    construct_solver_output = "Construct Solver Output"
    model_solver = "Model Solver"
    convert_to_lp = "Convert To LP"
    get_solver_info = f"Get Solver Info"
    get_solver = f"Get Solver"

    build_output = "Build Output"
    build_sites_report = "Build Sites Report"
    build_summary_report = "Build Summary Report"
    build_production_summary_report = "Build Production Summary Report"
    build_network_flows_report = "Build Network Flows Report"
    build_expression_costs_report = "Build Expression Costs Report"
    set_solution_reader = "Set Solution Reader"


@dataclass
class SharedServiceNames:

    convert_period_tables_to_string = f"Convert Period Columns To String:-{SubServiceNames.convert_to_string}"
